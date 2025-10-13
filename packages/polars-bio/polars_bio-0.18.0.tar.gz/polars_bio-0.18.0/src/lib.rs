mod context;
mod operation;
mod option;
mod query;
mod scan;
mod udtf;
mod utils;

use std::string::ToString;
use std::sync::Arc;

use datafusion::arrow::ffi_stream::ArrowArrayStreamReader;
use datafusion::arrow::pyarrow::PyArrowType;
use datafusion::datasource::MemTable;
use datafusion_bio_format_core::object_storage::ObjectStorageOptions;
use datafusion_bio_format_vcf::storage::VcfReader;
use datafusion_python::dataframe::PyDataFrame;
use log::{debug, error, info};
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use tokio::runtime::Runtime;

use crate::context::PyBioSessionContext;
use crate::operation::do_range_operation;
use crate::option::{
    pyobject_storage_options_to_object_storage_options, BamReadOptions, BedReadOptions, BioTable,
    CramReadOptions, FastaReadOptions, FastqReadOptions, FilterOp, GffReadOptions, InputFormat,
    PyObjectStorageOptions, RangeOp, RangeOptions, ReadOptions, VcfReadOptions,
};
use crate::scan::{maybe_register_table, register_frame, register_table};

const LEFT_TABLE: &str = "s1";
const RIGHT_TABLE: &str = "s2";
const DEFAULT_COLUMN_NAMES: [&str; 3] = ["contig", "start", "end"];

#[pyfunction]
#[pyo3(signature = (py_ctx, df1, df2, range_options, limit=None))]
fn range_operation_frame(
    py_ctx: &PyBioSessionContext,
    df1: PyArrowType<ArrowArrayStreamReader>,
    df2: PyArrowType<ArrowArrayStreamReader>,
    range_options: RangeOptions,
    limit: Option<usize>,
) -> PyResult<PyDataFrame> {
    #[allow(clippy::useless_conversion)]
    let rt = Runtime::new()?;
    let ctx = &py_ctx.ctx;
    register_frame(py_ctx, df1, LEFT_TABLE.to_string());
    register_frame(py_ctx, df2, RIGHT_TABLE.to_string());
    match limit {
        Some(l) => Ok(PyDataFrame::new(
            do_range_operation(
                ctx,
                &rt,
                range_options,
                LEFT_TABLE.to_string(),
                RIGHT_TABLE.to_string(),
            )
            .limit(0, Some(l))
            .map_err(|e| PyValueError::new_err(e.to_string()))?,
        )),
        _ => {
            let df = do_range_operation(
                ctx,
                &rt,
                range_options,
                LEFT_TABLE.to_string(),
                RIGHT_TABLE.to_string(),
            );
            let py_df = PyDataFrame::new(df);
            Ok(py_df)
        },
    }
}

#[pyfunction]
#[pyo3(signature = (py_ctx, df_path_or_table1, df_path_or_table2, range_options, read_options1=None, read_options2=None, limit=None))]
fn range_operation_scan(
    py_ctx: &PyBioSessionContext,
    df_path_or_table1: String,
    df_path_or_table2: String,
    range_options: RangeOptions,
    read_options1: Option<ReadOptions>,
    read_options2: Option<ReadOptions>,
    limit: Option<usize>,
) -> PyResult<PyDataFrame> {
    #[allow(clippy::useless_conversion)]
    let rt = Runtime::new()?;
    let ctx = &py_ctx.ctx;
    let left_table = maybe_register_table(
        df_path_or_table1,
        &LEFT_TABLE.to_string(),
        read_options1,
        ctx,
        &rt,
    );
    let right_table = maybe_register_table(
        df_path_or_table2,
        &RIGHT_TABLE.to_string(),
        read_options2,
        ctx,
        &rt,
    );
    match limit {
        Some(l) => Ok(PyDataFrame::new(
            do_range_operation(ctx, &rt, range_options, left_table, right_table)
                .limit(0, Some(l))
                .map_err(|e| PyValueError::new_err(e.to_string()))?,
        )),
        _ => Ok(PyDataFrame::new(do_range_operation(
            ctx,
            &rt,
            range_options,
            left_table,
            right_table,
        ))),
    }
}

#[pyfunction]
#[pyo3(signature = (py_ctx, path, name, input_format, read_options=None))]
fn py_register_table(
    py: Python<'_>,
    py_ctx: &PyBioSessionContext,
    path: String,
    name: Option<String>,
    input_format: InputFormat,
    read_options: Option<ReadOptions>,
) -> PyResult<BioTable> {
    #[allow(clippy::useless_conversion)]
    py.allow_threads(|| {
        let rt = Runtime::new()?;
        let ctx = &py_ctx.ctx;

        let table_name = match name {
            Some(name) => name,
            None => path
                .to_lowercase()
                .split('/')
                .last()
                .unwrap()
                .to_string()
                .replace(&format!(".{}", input_format).to_string().to_lowercase(), "")
                .replace(".", "_")
                .replace("-", "_"),
        };
        rt.block_on(register_table(
            ctx,
            &path,
            &table_name,
            input_format.clone(),
            read_options,
        ));
        match rt.block_on(ctx.table(&table_name)) {
            Ok(table) => {
                let schema = table.schema().as_arrow();
                info!("Table: {} registered for path: {}", table_name, path);
                let bio_table = BioTable {
                    name: table_name,
                    format: input_format,
                    path,
                };
                debug!("Schema: {:?}", schema);
                Ok(bio_table)
            },
            Err(e) => {
                error!("Failed to register table for path {}: {:?}", path, e);
                Err(PyValueError::new_err(format!(
                    "Failed to register table: {}",
                    e
                )))
            },
        }
    })
}

#[pyfunction]
#[pyo3(signature = (py_ctx, sql_text))]
fn py_read_sql(
    py: Python<'_>,
    py_ctx: &PyBioSessionContext,
    sql_text: String,
) -> PyResult<PyDataFrame> {
    #[allow(clippy::useless_conversion)]
    py.allow_threads(|| {
        let rt = Runtime::new()?;
        let ctx = &py_ctx.ctx;
        let df = rt.block_on(ctx.sql(&sql_text)).unwrap();
        Ok(PyDataFrame::new(df))
    })
}

#[pyfunction]
#[pyo3(signature = (py_ctx, table_name))]
fn py_read_table(
    py: Python<'_>,
    py_ctx: &PyBioSessionContext,
    table_name: String,
) -> PyResult<PyDataFrame> {
    #[allow(clippy::useless_conversion)]
    py.allow_threads(|| {
        let rt = Runtime::new()?;
        let ctx = &py_ctx.ctx;
        let df = rt
            .block_on(ctx.sql(&format!("SELECT * FROM {}", table_name)))
            .unwrap();
        Ok(PyDataFrame::new(df))
    })
}

#[pyfunction]
#[pyo3(signature = (py_ctx, path, object_storage_options=None))]
fn py_describe_vcf(
    py: Python<'_>,
    py_ctx: &PyBioSessionContext,
    path: String,
    object_storage_options: Option<PyObjectStorageOptions>,
) -> PyResult<PyDataFrame> {
    py.allow_threads(|| {
        let rt = Runtime::new()?;
        let ctx = &py_ctx.ctx;
        let base_options =
            pyobject_storage_options_to_object_storage_options(object_storage_options)
                .unwrap_or_default();

        // Set specific options for describe, overriding base options
        let desc_object_storage_options = ObjectStorageOptions {
            chunk_size: Some(8),
            concurrent_fetches: Some(1),
            ..base_options
        };
        info!("{}", desc_object_storage_options);

        let df = rt.block_on(async {
            let mut reader = VcfReader::new(path, None, Some(desc_object_storage_options)).await;
            let rb = reader.describe().await.unwrap();
            let mem_table = MemTable::try_new(rb.schema().clone(), vec![vec![rb]]).unwrap();
            let random_table_name = format!("vcf_schema_{}", rand::random::<u32>());
            ctx.register_table(random_table_name.clone(), Arc::new(mem_table))
                .unwrap();
            let df = ctx.table(random_table_name).await.unwrap();
            df
        });
        Ok(PyDataFrame::new(df))
    })
}

#[pyfunction]
#[pyo3(signature = (py_ctx, name, query))]
fn py_register_view(
    py: Python<'_>,
    py_ctx: &PyBioSessionContext,
    name: String,
    query: String,
) -> PyResult<()> {
    py.allow_threads(|| {
        let rt = Runtime::new()?;
        let ctx = &py_ctx.ctx;
        rt.block_on(ctx.sql(&format!("CREATE OR REPLACE VIEW {} AS {}", name, query)))
            .unwrap();
        Ok(())
    })
}

#[pyfunction]
#[pyo3(signature = (py_ctx, name, df))]
fn py_from_polars(
    py: Python<'_>,
    py_ctx: &PyBioSessionContext,
    name: String,
    df: PyArrowType<ArrowArrayStreamReader>,
) {
    py.allow_threads(|| {
        register_frame(py_ctx, df, name);
    })
}

#[pymodule]
fn polars_bio(_py: Python, m: &Bound<PyModule>) -> PyResult<()> {
    pyo3_log::init();
    m.add_function(wrap_pyfunction!(range_operation_frame, m)?)?;
    m.add_function(wrap_pyfunction!(range_operation_scan, m)?)?;
    m.add_function(wrap_pyfunction!(py_register_table, m)?)?;
    m.add_function(wrap_pyfunction!(py_read_table, m)?)?;
    m.add_function(wrap_pyfunction!(py_read_sql, m)?)?;
    m.add_function(wrap_pyfunction!(py_describe_vcf, m)?)?;
    m.add_function(wrap_pyfunction!(py_register_view, m)?)?;
    m.add_function(wrap_pyfunction!(py_from_polars, m)?)?;
    m.add_class::<PyBioSessionContext>()?;
    m.add_class::<FilterOp>()?;
    m.add_class::<RangeOp>()?;
    m.add_class::<RangeOptions>()?;
    m.add_class::<InputFormat>()?;
    m.add_class::<ReadOptions>()?;
    m.add_class::<GffReadOptions>()?;
    m.add_class::<VcfReadOptions>()?;
    m.add_class::<FastqReadOptions>()?;
    m.add_class::<BamReadOptions>()?;
    m.add_class::<CramReadOptions>()?;
    m.add_class::<BedReadOptions>()?;
    m.add_class::<FastaReadOptions>()?;
    m.add_class::<PyObjectStorageOptions>()?;
    Ok(())
}

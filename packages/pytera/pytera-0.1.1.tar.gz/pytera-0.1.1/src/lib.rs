use pyo3::prelude::*;

use pytera::PyTera;

mod pytera;
mod error;
mod utils;



#[pymodule]
fn _core(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyTera>()?;
    Ok(())
}

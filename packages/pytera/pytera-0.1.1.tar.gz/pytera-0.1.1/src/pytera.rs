use crate::error::PyTeraError;
use crate::utils::pyany_to_serde_json_value;
use pyo3::{prelude::*, pyclass, types::PyDict, PyResult};
use tera::{Context, Tera};

#[pyclass]
pub struct PyTera {
    tera: Tera,
}

#[pymethods]
impl PyTera {
    #[new]
    fn new(glob: &str) -> PyResult<Self> {
        let tera = Tera::new(glob).map_err(|e| PyTeraError::from(e))?; // PyTeraError -> PyErr via From
        Ok(PyTera { tera })
    }

    #[pyo3(signature = (template, kwargs=None))]
    fn render_template(
        &self,
        template: &str,
        kwargs: Option<&Bound<'_, PyDict>>,
    ) -> PyResult<String> {
        let mut ctx = Context::new();

        if let Some(kwargs) = kwargs {
            for (k, v) in kwargs.iter() {
                let key = k.extract::<String>().map_err(|_| {
                    PyErr::new::<pyo3::exceptions::PyValueError, _>(format!(
                        "Can't convert {} as a str",
                        k
                    ))
                })?;
                let value = pyany_to_serde_json_value(&v).unwrap_or(serde_json::Value::Null);
                ctx.insert(&key, &value);
            }
        }

        let rendered_result = self
            .tera
            .render(template, &ctx)
            .map_err(PyTeraError::from)?;

        Ok(rendered_result)
    }

    fn templates(&self) -> PyResult<Vec<&String>> {
        let tpls = self.tera.templates.keys().collect();
        Ok(
            tpls
        )
    }
}

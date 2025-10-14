use pyo3::{exceptions::{PyException, PyIOError, PyRuntimeError, PyUnicodeDecodeError, PyValueError}, PyErr};
use tera::ErrorKind as TeraErrorKind;


#[derive(Debug)]
pub struct  PyTeraError {
    pub inner: tera::Error,
}

impl From<tera::Error> for PyTeraError {
    fn from(err: tera::Error) -> Self {
        PyTeraError { inner: err }
    }
}

impl From<PyTeraError> for PyErr {

    fn from(value: PyTeraError) -> Self {
        
        let err = value.inner;

        match err.kind {

            TeraErrorKind::Msg(msg) => {
                if msg.contains("glob") {
                    return PyValueError::new_err(msg);
                }
                if msg.contains("parse") {
                    return PyRuntimeError::new_err(msg);
                }
                return PyException::new_err(msg);
            },
            TeraErrorKind::CircularExtend { tpl, inheritance_chain } => 
                PyRuntimeError::new_err(format!(
                    "Circular inheritance in template '{}': Chain -> {:?}", 
                    tpl, inheritance_chain
                )),
            TeraErrorKind::MissingParent { current, parent } => 
                PyRuntimeError::new_err(format!(
                    "Template '{}' requires missing parent '{}'", 
                    current, parent
                )),
            TeraErrorKind::Utf8Conversion { context } => 
                PyUnicodeDecodeError::new_err(format!("UTF-8 conversion error in {}", context)),
            TeraErrorKind::Json(e) => PyValueError::new_err(format!("JSON error: {}", e)),
            TeraErrorKind::InvalidMacroDefinition(msg) => 
                PyValueError::new_err(format!("Invalid macro: {}", msg)),
            TeraErrorKind::Io(e) => PyIOError::new_err(format!("IO error: {}", e)),
            TeraErrorKind::CallFilter(msg) => 
                PyRuntimeError::new_err(format!("Filter error: {}", msg)),
            TeraErrorKind::CallFunction(msg) => 
                PyRuntimeError::new_err(format!("Function error: {}", msg)),
            TeraErrorKind::CallTest(msg) => 
                PyRuntimeError::new_err(format!("Test error: {}", msg)),
            TeraErrorKind::FilterNotFound(msg) => 
                PyRuntimeError::new_err(format!("Filter '{}' not found", msg)),
            TeraErrorKind::TemplateNotFound(msg) => 
                PyRuntimeError::new_err(format!("Template '{}' not found", msg)),
            TeraErrorKind::TestNotFound(msg) => 
                PyRuntimeError::new_err(format!("Test '{}' not found", msg)),
            TeraErrorKind::FunctionNotFound(msg) => 
                PyRuntimeError::new_err(format!("Function '{}' not found", msg)),
            _ => PyException::new_err(format!("Unknown Tera error: {}", err)),
        }
    }
}
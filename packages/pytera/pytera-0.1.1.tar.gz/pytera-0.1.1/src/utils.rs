use pyo3::types::PyDict;
use pyo3::prelude::*;
use serde_json::{Value, Map};
use pyo3::types::{PyBool, PyFloat, PyInt, PyString, PyList, PyTuple};


/// Helper function to convert Python objects to serde_json::Value
pub(crate) fn pyany_to_serde_json_value(obj: &Bound<'_, PyAny>) -> PyResult<Value> {
    // Check for None
    if obj.is_none() {
        return Ok(Value::Null);
    }
    
    // Check for bool (must be before int check as bool is subclass of int in Python)
    if let Ok(b) = obj.downcast::<PyBool>() {
        return Ok(Value::Bool(b.is_true()));
    }
    
    // Check for int
    if let Ok(i) = obj.downcast::<PyInt>() {
        if let Ok(val) = i.extract::<i64>() {
            return Ok(Value::Number(val.into()));
        }
        // If i64 fails, try u64
        if let Ok(val) = i.extract::<u64>() {
            return Ok(Value::Number(val.into()));
        }
        // If both fail, convert to string as a fallback for very large numbers
        return Ok(Value::String(i.to_string()));
    }
    
    // Check for float
    if let Ok(f) = obj.downcast::<PyFloat>() {
        let val = f.extract::<f64>()?;
        if let Some(num) = serde_json::Number::from_f64(val) {
            return Ok(Value::Number(num));
        } else {
            // Handle special float values (inf, -inf, nan)
            return Ok(Value::String(val.to_string()));
        }
    }
    
    // Check for string
    if let Ok(s) = obj.downcast::<PyString>() {
        return Ok(Value::String(s.to_string()));
    }
    
    // Check for list
    if let Ok(list) = obj.downcast::<PyList>() {
        let mut vec = Vec::new();
        for item in list.iter() {
            vec.push(pyany_to_serde_json_value(&item)?);
        }
        return Ok(Value::Array(vec));
    }
    
    // Check for tuple
    if let Ok(tuple) = obj.downcast::<PyTuple>() {
        let mut vec = Vec::new();
        for item in tuple.iter() {
            vec.push(pyany_to_serde_json_value(&item)?);
        }
        return Ok(Value::Array(vec));
    }
    
    // Check for dict
    if let Ok(dict) = obj.downcast::<PyDict>() {
        let mut map = Map::new();
        for (key, value) in dict.iter() {
            let key_str = key.extract::<String>()?;
            let json_value = pyany_to_serde_json_value(&value)?;
            map.insert(key_str, json_value);
        }
        return Ok(Value::Object(map));
    }
    
    // For other types, try to convert to string
    Ok(Value::String(obj.to_string()))
}

#[cfg(test)]
mod tests {
    use super::*;
    use pyo3::{ffi::c_str, Python};
    use serde_json::json;
    use std::sync::Once;

    // Ensure Python is initialized only once for all tests
    static INIT: Once = Once::new();
    
    fn init_python() {
        INIT.call_once(|| {
            pyo3::prepare_freethreaded_python();
        });
    }

    #[test]
    fn test_kwargs2_serde_value_basic() {
        init_python();
        Python::with_gil(|py| {
            let kwargs = PyDict::new(py);
            kwargs.set_item("name", "Alice").unwrap();
            kwargs.set_item("age", 30).unwrap();
            kwargs.set_item("active", true).unwrap();
            
            let result = pyany_to_serde_json_value(&kwargs).unwrap();
            
            assert!(result.is_object());
            let obj = result.as_object().unwrap();
            assert_eq!(obj.get("name"), Some(&json!("Alice")));
            assert_eq!(obj.get("age"), Some(&json!(30)));
            assert_eq!(obj.get("active"), Some(&json!(true)));
        });
    }

    #[test]
    fn test_kwargs2_serde_value_nested() {
        init_python();
        Python::with_gil(|py| {
            let kwargs = PyDict::new(py);
            let nested_dict = PyDict::new(py);
            nested_dict.set_item("city", "New York").unwrap();
            nested_dict.set_item("zip", 10001).unwrap();
            
            kwargs.set_item("name", "Bob").unwrap();
            kwargs.set_item("address", nested_dict).unwrap();
            
            let result = pyany_to_serde_json_value(&kwargs).unwrap();
            
            assert!(result.is_object());
            let obj = result.as_object().unwrap();
            assert_eq!(obj.get("name"), Some(&json!("Bob")));
            
            let address = obj.get("address").unwrap();
            assert!(address.is_object());
            let address_obj = address.as_object().unwrap();
            assert_eq!(address_obj.get("city"), Some(&json!("New York")));
            assert_eq!(address_obj.get("zip"), Some(&json!(10001)));
        });
    }

    #[test]
    fn test_kwargs2_serde_value_with_none() {
        init_python();
        Python::with_gil(|py| {
            let kwargs = PyDict::new(py);
            kwargs.set_item("name", "Charlie").unwrap();
            kwargs.set_item("middle_name", py.None()).unwrap();
            kwargs.set_item("age", 25).unwrap();
            
            let result = pyany_to_serde_json_value(&kwargs).unwrap();
            
            assert!(result.is_object());
            let obj = result.as_object().unwrap();
            assert_eq!(obj.get("name"), Some(&json!("Charlie")));
            assert_eq!(obj.get("middle_name"), Some(&json!(null)));
            assert_eq!(obj.get("age"), Some(&json!(25)));
        });
    }

    #[test]
    fn test_kwargs2_serde_value_with_list() {
        init_python();
        Python::with_gil(|py| {
            let kwargs = PyDict::new(py);
            let list = PyList::new(py, &[1, 2, 3]);
            
            kwargs.set_item("numbers", list.unwrap()).unwrap();
            kwargs.set_item("name", "David").unwrap();
            
            let result = pyany_to_serde_json_value(&kwargs).unwrap();
            
            assert!(result.is_object());
            let obj = result.as_object().unwrap();
            assert_eq!(obj.get("name"), Some(&json!("David")));
            assert_eq!(obj.get("numbers"), Some(&json!([1, 2, 3])));
        });
    }

    #[test]
    fn test_kwargs2_serde_value_empty() {
        init_python();
        Python::with_gil(|py| {
            let kwargs = PyDict::new(py);
            
            let result = pyany_to_serde_json_value(&kwargs).unwrap();
            
            assert!(result.is_object());
            let obj = result.as_object().unwrap();
            assert!(obj.is_empty());
        });
    }

    #[test]
    fn test_python_to_json_value_float_special_values() {
        init_python();
        Python::with_gil(|py| {
            // Test infinity
            let inf = py.eval(c_str!("float('inf')"), None, None).unwrap();
            let result = pyany_to_serde_json_value(&inf).unwrap();
            assert_eq!(result, json!("inf"));
            
            // Test negative infinity
            let neg_inf = py.eval(c_str!("float('-inf')"), None, None).unwrap();
            let result = pyany_to_serde_json_value(&neg_inf).unwrap();
            assert_eq!(result, json!("-inf"));
            
            // Test NaN - check that it's a string containing "nan" (case insensitive)
            let nan = py.eval(c_str!("float('nan')"), None, None).unwrap();
            let result = pyany_to_serde_json_value(&nan).unwrap();
            assert!(result.is_string());
            let nan_str = result.as_str().unwrap().to_lowercase();
            assert_eq!(nan_str, "nan");
        });
    }

    #[test]
    fn test_python_to_json_value_large_numbers() {
        init_python();
        Python::with_gil(|py| {
            // Test very large integer that exceeds i64/u64
            let large_int = py.eval(c_str!("10**100"), None, None).unwrap();
            let result = pyany_to_serde_json_value(&large_int).unwrap();
            assert!(result.is_string());
            assert!(result.as_str().unwrap().starts_with("1000000"));
        });
    }

    #[test]
    fn test_kwargs2_serde_value_complex_nested() {
        init_python();
        Python::with_gil(|py| {
            let kwargs = PyDict::new(py);
            
            // Create complex nested structure
            let inner_list = PyList::new(py, &[1, 2, 3]);
            let inner_dict = PyDict::new(py);
            inner_dict.set_item("nested_key", "nested_value").unwrap();
            inner_dict.set_item("nested_list", inner_list.unwrap()).unwrap();
            
            let item1 = "item1".into_pyobject(py).unwrap();
            let inner_dict_obj = inner_dict.into_pyobject(py).unwrap();
            
            let outer_list = PyList::new(py, &[item1.as_ref(), inner_dict_obj.as_ref()]).unwrap();
            
            kwargs.set_item("complex", outer_list).unwrap();
            kwargs.set_item("simple", "value").unwrap();
            
            let result = pyany_to_serde_json_value(&kwargs).unwrap();
            
            assert!(result.is_object());
            let obj = result.as_object().unwrap();
            assert_eq!(obj.get("simple"), Some(&json!("value")));
            
            let complex = obj.get("complex").unwrap();
            assert!(complex.is_array());
            let complex_arr = complex.as_array().unwrap();
            assert_eq!(complex_arr[0], json!("item1"));
            
            let nested_dict = &complex_arr[1];
            assert!(nested_dict.is_object());
            let nested_obj = nested_dict.as_object().unwrap();
            assert_eq!(nested_obj.get("nested_key"), Some(&json!("nested_value")));
            assert_eq!(nested_obj.get("nested_list"), Some(&json!([1, 2, 3])));
        });
    }
}
use pyo3::prelude::*;

/// Convert to camel case.
#[pyfunction]
#[inline(always)]
fn to_camel(py: Python, s: &str) -> PyResult<String> {
    py.detach(|| {
        let mut result = String::with_capacity(s.len());
        let mut s_iter = s.chars().peekable();
        while let Some(c) = s_iter.next() {
            match c {
                ' ' | '_' | '-' => {
                    if let Some(c_next) = s_iter.peek() {
                        result.push(c_next.to_ascii_uppercase());
                        s_iter.next();
                    }
                }
                _ => result.push(c.to_ascii_lowercase()),
            }
        }
        Ok(result)
    })
}

/// Convert to snake case.
#[pyfunction]
#[inline(always)]
fn to_snake(py: Python, s: &str) -> PyResult<String> {
    py.detach(move || {
        let mut result = String::with_capacity(s.len());
        let mut upper_count = 0;
        let mut underscore_count = 0;
        for (i, c) in s.chars().enumerate() {
            if c.is_uppercase() {
                upper_count += 1;
                if i > 0 && upper_count < 2 && underscore_count < 1 {
                    result.push('_');
                }
                result.push(c.to_ascii_lowercase());
            } else if c == ' ' || c == '_' || c == '-' {
                if underscore_count < 1 {
                    result.push('_');
                    underscore_count += 1;
                }
                upper_count = 0;
            } else {
                if upper_count > 1 {
                    if let Some(last_c) = result.pop() {
                        if underscore_count < 1 {
                            result.push('_');
                        }
                        result.push(last_c);
                    }
                }
                upper_count = 0;
                underscore_count = 0;
                result.push(c);
            }
        }
        Ok(result)
    })
}

/// Casers package.
#[pymodule]
fn _casers(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(to_camel, m)?)?;
    m.add_function(wrap_pyfunction!(to_snake, m)?)?;
    Ok(())
}

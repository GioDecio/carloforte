use pyo3::prelude::*;

#[pyfunction]
fn find_islands(_py: Python, _grid: Vec<Vec<Option<PyObject>>>) -> PyResult<Vec<PyObject>> {
    Ok(vec![])
}

#[pymodule]
fn _islands_rs(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(find_islands, m)?)?;
    Ok(())
}

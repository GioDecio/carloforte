use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};
use std::collections::VecDeque;

#[pyfunction]
fn find_islands(py: Python, grid: Vec<Vec<Option<PyObject>>>) -> PyResult<Vec<PyObject>> {
    if grid.is_empty() {
        return Ok(vec![]);
    }

    let max_row = grid.len();
    let max_col = grid.iter().map(|r| r.len()).max().unwrap_or(0);

    // Pad rows to equal width
    let padded: Vec<Vec<Option<&PyObject>>> = grid
        .iter()
        .map(|row| {
            let mut r: Vec<Option<&PyObject>> = row.iter().map(|c| c.as_ref()).collect();
            r.resize(max_col, None);
            r
        })
        .collect();

    let mut visited = vec![vec![false; max_col]; max_row];
    let mut islands: Vec<PyObject> = Vec::new();

    for start_r in 0..max_row {
        for start_c in 0..max_col {
            if visited[start_r][start_c] || padded[start_r][start_c].is_none() {
                visited[start_r][start_c] = true;
                continue;
            }

            let mut component: Vec<(usize, usize)> = Vec::new();
            let mut queue: VecDeque<(usize, usize)> = VecDeque::new();
            queue.push_back((start_r, start_c));
            visited[start_r][start_c] = true;

            while let Some((r, c)) = queue.pop_front() {
                component.push((r, c));
                for (dr, dc) in [(-1i64, 0i64), (1, 0), (0, -1), (0, 1)] {
                    let nr = r as i64 + dr;
                    let nc = c as i64 + dc;
                    if nr >= 0
                        && (nr as usize) < max_row
                        && nc >= 0
                        && (nc as usize) < max_col
                    {
                        let nr = nr as usize;
                        let nc = nc as usize;
                        if !visited[nr][nc] && padded[nr][nc].is_some() {
                            visited[nr][nc] = true;
                            queue.push_back((nr, nc));
                        }
                    }
                }
            }

            let min_r = component.iter().map(|(r, _)| *r).min().unwrap();
            let max_r = component.iter().map(|(r, _)| *r).max().unwrap();
            let min_c = component.iter().map(|(_, c)| *c).min().unwrap();
            let max_c = component.iter().map(|(_, c)| *c).max().unwrap();

            let cells = PyList::new(
                py,
                (min_r..=max_r).map(|r| {
                    let row_items: Vec<PyObject> = (min_c..=max_c)
                        .map(|c| match padded[r][c] {
                            Some(v) => v.clone_ref(py).into_pyobject(py).unwrap().unbind(),
                            None => py.None(),
                        })
                        .collect();
                    PyList::new(py, row_items).unwrap()
                })
                .collect::<Vec<_>>(),
            )
            .unwrap();

            let island = PyDict::new(py);
            island.set_item("top_row", min_r + 1)?;
            island.set_item("left_col", min_c + 1)?;
            island.set_item("cells", cells)?;
            islands.push(island.unbind().into());
        }
    }

    Ok(islands)
}

#[pymodule]
fn _islands_rs(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(find_islands, m)?)?;
    Ok(())
}

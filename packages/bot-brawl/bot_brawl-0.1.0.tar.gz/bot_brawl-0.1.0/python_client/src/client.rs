use pyo3::prelude::*;

use crate::tictactoe::TicTacToeClient;

#[pymodule]
fn bot_brawl(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<TicTacToeClient>()?;
    Ok(())
}

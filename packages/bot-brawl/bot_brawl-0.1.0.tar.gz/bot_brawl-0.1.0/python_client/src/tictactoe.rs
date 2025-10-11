use arena_core::{
    client::GameClient,
    games::tictactoe::{TicTacToeBot, TicTacToePlayer, TicTacToePos, TicTacToeState},
};
use pyo3::prelude::*;

/// Wrapper around a Python object implementing handle_turn
#[derive(Clone)]
pub struct PyTicTacToeBot {
    py_bot: Py<PyAny>,
}

// Implement the Rust trait by forwarding to Python
#[async_trait::async_trait]
impl TicTacToeBot for PyTicTacToeBot {
    async fn handle_turn(&mut self, state: &TicTacToeState) -> TicTacToePos {
        Python::with_gil(|py| {
            let py_state = PyTicTacToeState::from_rust(state.clone(), py);
            let py_bot = self.py_bot.as_ref(py);

            pyo3_asyncio::tokio::into_future(
                py_bot.call_method1("handle_turn", (py_state,)).unwrap(),
            )
            .unwrap() // TODO: Fix all these unwraps
        })
        .await
        .and_then(|py_obj| Python::with_gil(|py| py_obj.as_ref(py).extract::<usize>()))
        .map(|index| TicTacToePos::from_index(index).unwrap())
        .unwrap()
    }
}

#[pyclass(subclass)]
#[derive(Clone)]
pub struct TicTacToeClient;

#[pymethods]
impl TicTacToeClient {
    #[new]
    pub fn new() -> Self {
        Self
    }

    pub fn connect<'a>(self_: PyRef<'a, Self>, py: Python<'a>, url: String) -> PyResult<&'a PyAny> {
        let py_bot: Py<PyAny> = self_.into_py(py);

        pyo3_asyncio::tokio::future_into_py(py, async move {
            let bot = PyTicTacToeBot { py_bot };
            bot.start(&url).await;
            Ok(())
        })
    }
}

#[pyclass]
#[derive(Clone)]
pub struct PyTicTacToeState {
    board: Vec<Option<String>>,
}

#[pymethods]
impl PyTicTacToeState {
    #[getter]
    pub fn board(&self) -> Vec<Option<String>> {
        self.board.clone()
    }

    pub fn __repr__(&self) -> String {
        format!("{:?}", self.board)
    }
}

// impl IntoPy<Py<PyTicTacToeState>> for TicTacToeState {}

impl PyTicTacToeState {
    fn from_rust(state: TicTacToeState, py: Python) -> Py<PyTicTacToeState> {
        let board = state
            .board
            .0
            .iter()
            .map(|cell| match cell {
                Some(t) => Some(match t {
                    TicTacToePlayer::Player1 => "X".to_string(),
                    TicTacToePlayer::Player2 => "O".to_string(),
                }),
                None => None,
            })
            .collect();

        Py::new(py, PyTicTacToeState { board }).unwrap()
    }
}

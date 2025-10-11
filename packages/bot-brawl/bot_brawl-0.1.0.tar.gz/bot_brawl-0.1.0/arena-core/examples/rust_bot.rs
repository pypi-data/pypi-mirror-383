use arena_core::{
    client::GameClient,
    games::tictactoe::{TicTacToeBot, TicTacToePos, TicTacToeState},
};

#[derive(Clone)]
struct TestBot {
    move_count: u32,
}

#[async_trait::async_trait]
impl TicTacToeBot for TestBot {
    // Test bot that plays at the first available position
    async fn handle_turn(&mut self, state: &TicTacToeState) -> TicTacToePos {
        println!("{}", state.board);
        self.move_count += 1;
        for (i, cell) in state.board.into_iter().enumerate() {
            if cell.is_none() {
                return TicTacToePos::from_index(i).unwrap();
            }
        }
        unreachable!("Board is full")
    }
}

//TODO: Consider whether we really want to commit to async support
#[tokio::main]
async fn main() {
    // Connect to your server
    TestBot { move_count: 0 }.start("ws://127.0.0.1:9001").await;
}

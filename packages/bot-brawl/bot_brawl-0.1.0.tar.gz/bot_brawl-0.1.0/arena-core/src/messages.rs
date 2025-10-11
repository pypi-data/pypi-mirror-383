use bincode::{Decode, Encode};

use crate::common::GameType;

#[derive(Decode, Encode, Debug, Clone, Copy)]
pub enum ServerMessage {
    StartGame { player_index: usize },
}

#[derive(Decode, Encode, Debug, Clone, Copy)]
pub enum ClientMessage {
    Join { game: GameType },
}

use std::{fmt, time::Duration};

use bincode::{Decode, Encode};

use crate::common::{
    BaseEvent, BotBounds, BotMode, ClientEvent, GameBot, GameLogic, GameType, SendTo,
};

#[derive(Debug, Clone, Copy, PartialEq, Default, Encode, Decode)]
pub struct TicTacToeBoard(pub [Option<TicTacToePlayer>; 9]);

const WIN_LINES_POS: [[TicTacToePos; 3]; 8] = [
    [
        TicTacToePos::TopLeft,
        TicTacToePos::TopMiddle,
        TicTacToePos::TopRight,
    ],
    [
        TicTacToePos::MiddleLeft,
        TicTacToePos::MiddleMiddle,
        TicTacToePos::MiddleRight,
    ],
    [
        TicTacToePos::BottomLeft,
        TicTacToePos::BottomMiddle,
        TicTacToePos::BottomRight,
    ],
    [
        TicTacToePos::TopLeft,
        TicTacToePos::MiddleLeft,
        TicTacToePos::BottomLeft,
    ],
    [
        TicTacToePos::TopMiddle,
        TicTacToePos::MiddleMiddle,
        TicTacToePos::BottomMiddle,
    ],
    [
        TicTacToePos::TopRight,
        TicTacToePos::MiddleRight,
        TicTacToePos::BottomRight,
    ],
    [
        TicTacToePos::TopLeft,
        TicTacToePos::MiddleMiddle,
        TicTacToePos::BottomRight,
    ],
    [
        TicTacToePos::TopRight,
        TicTacToePos::MiddleMiddle,
        TicTacToePos::BottomLeft,
    ],
];

impl TicTacToeBoard {
    pub fn set_cell(&mut self, pos: TicTacToePos, player: TicTacToePlayer) {
        self.0[pos as usize] = Some(player);
    }

    pub fn get_cell(&self, pos: TicTacToePos) -> Option<TicTacToePlayer> {
        self.0[pos as usize]
    }

    pub fn is_full(&self) -> bool {
        self.0.iter().all(|&x| x.is_some())
    }

    pub fn check_winner(&self) -> Option<TicTacToePlayer> {
        for line in WIN_LINES_POS {
            let [a, b, c] = line.map(|p| p as usize);
            if let (Some(x), Some(y), Some(z)) = (self.0[a], self.0[b], self.0[c]) {
                if x == y && y == z {
                    return Some(x);
                }
            }
        }
        None
    }
}

impl fmt::Display for TicTacToeBoard {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        for row in 0..3 {
            for col in 0..3 {
                let idx = row * 3 + col;
                match self.0[idx] {
                    Some(tic) => write!(f, " {} ", tic)?,
                    None => write!(f, " . ")?,
                }
                if col < 2 {
                    write!(f, "|")?;
                }
            }
            writeln!(f)?;
            if row < 2 {
                writeln!(f, "---+---+---")?;
            }
        }
        Ok(())
    }
}

impl IntoIterator for TicTacToeBoard {
    type Item = Option<TicTacToePlayer>;
    type IntoIter = std::array::IntoIter<Option<TicTacToePlayer>, 9>;

    fn into_iter(self) -> Self::IntoIter {
        self.0.into_iter()
    }
}

#[async_trait::async_trait]
pub trait TicTacToeBot: GameBot<TicTacToeState> + BotBounds {
    async fn handle_turn(&mut self, state: &TicTacToeState) -> TicTacToePos;
}

impl<T: TicTacToeBot> GameBot<TicTacToeState> for T {}

#[derive(Debug, Clone, Copy, Encode, Decode)]
#[repr(u8)]
pub enum TicTacToePos {
    TopLeft,
    TopMiddle,
    TopRight,
    MiddleLeft,
    MiddleMiddle,
    MiddleRight,
    BottomLeft,
    BottomMiddle,
    BottomRight,
}

impl TicTacToePos {
    pub fn from_index(i: usize) -> Option<Self> {
        use TicTacToePos::*;
        match i {
            0 => Some(TopLeft),
            1 => Some(TopMiddle),
            2 => Some(TopRight),
            3 => Some(MiddleLeft),
            4 => Some(MiddleMiddle),
            5 => Some(MiddleRight),
            6 => Some(BottomLeft),
            7 => Some(BottomMiddle),
            8 => Some(BottomRight),
            _ => None,
        }
    }
}

impl<TBot: TicTacToeBot> BaseEvent<TBot> for TicTacToePos {
    type Logic = TicTacToeState;
}

#[async_trait::async_trait]
impl<TBot: TicTacToeBot> ClientEvent<TBot> for TicTacToePos {
    fn validate(&self, state: &Self::Logic, from_player: usize) -> bool {
        state.turn as usize == from_player && state.board.get_cell(*self).is_none()
    }

    fn update_state(&self, state: &mut Self::Logic, _: usize, _: bool) {
        state.board.set_cell(*self, state.turn);
        state.next_turn();
    }

    async fn get_from_bot(bot: &mut TBot, state: &mut Self::Logic, _: usize) -> Self {
        bot.handle_turn(&state).await
    }
}

#[derive(Debug, Clone, Copy, Encode, Decode, Default, PartialEq, Eq)]
#[repr(u8)]
pub enum TicTacToePlayer {
    #[default]
    Player1,
    Player2,
}

impl TicTacToePlayer {
    pub fn other_player(&self) -> TicTacToePlayer {
        match &self {
            Self::Player1 => TicTacToePlayer::Player2,
            Self::Player2 => TicTacToePlayer::Player1,
        }
    }
}

impl fmt::Display for TicTacToePlayer {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            TicTacToePlayer::Player1 => write!(f, "X"),
            TicTacToePlayer::Player2 => write!(f, "O"),
        }
    }
}

#[derive(Debug, Clone, Copy, Encode, Decode, Default)]
pub struct TicTacToeState {
    pub board: TicTacToeBoard,
    pub turn: TicTacToePlayer,
}

impl TicTacToeState {
    pub fn is_finished(&self) -> bool {
        self.board.check_winner().is_some() || self.board.is_full()
    }

    pub fn next_turn(&mut self) {
        self.turn = self.turn.other_player();
    }
}

#[async_trait::async_trait]
impl<TBot: TicTacToeBot> GameLogic<TBot> for TicTacToeState {
    fn game_type() -> GameType {
        GameType::TicTacToe
    }

    async fn start_game(&mut self, bots: &mut BotMode<TBot>) {
        //TODO: Randomly pick turn?

        while !self.is_finished() {
            bots.wait_for_action::<TicTacToePos>(
                self,
                self.turn as usize,
                SendTo::One(self.turn.other_player() as usize),
                Some(Duration::from_millis(500)),
            )
            .await;
        }

        if let Some(winner) = self.board.check_winner() {
            println!("{:?} wins!", winner);
        } else {
            println!("Tie")
        }
    }
}

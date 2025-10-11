use bincode::{Decode, Encode};
use std::time::Duration;
use tokio::{
    sync::mpsc::{UnboundedReceiver, UnboundedSender},
    time::timeout,
};
use tokio_tungstenite::tungstenite::Message;

#[derive(Debug, Encode, Decode, Clone, Copy, PartialEq, Eq, Hash)]
pub enum GameType {
    TicTacToe,
    Tycoon,
}

// impl GameType {
//     pub fn get_state(&self) -> GameLogic<_> {

//     }
// }

pub trait GameBot<L: GameLogic<Self>>: BotBounds {}

#[derive(Clone)]
pub enum SendTo {
    All,
    AllExcept(usize),
    One(usize),
    Multiple(Vec<usize>),
    NoOne,
}

impl SendTo {
    pub fn contains(&self, player_index: usize) -> bool {
        match self {
            Self::All => true,
            Self::AllExcept(except) => *except != player_index,
            Self::One(to_player) => *to_player == player_index,
            Self::Multiple(players) => players.contains(&player_index),
            Self::NoOne => false,
        }
    }

    pub fn targets(self, num_players: usize) -> Vec<usize> {
        match self {
            SendTo::All => (0..num_players).collect(),
            SendTo::AllExcept(except) => (0..num_players).filter(|&p| p != except).collect(),
            SendTo::One(p) => vec![p],
            SendTo::Multiple(players) => players,
            SendTo::NoOne => Vec::new(),
        }
    }
}

pub trait BaseEvent<TBot: BotBounds> {
    type Logic: GameLogic<TBot> + Send + Sync;
}

#[async_trait::async_trait]
pub trait ClientEvent<TBot: BotBounds>:
    BaseEvent<TBot> + Decode<()> + Encode + Send + Sync
{
    fn update_state(&self, logic: &mut Self::Logic, from: usize, is_server: bool);
    fn validate(&self, state: &Self::Logic, from: usize) -> bool;
    async fn get_from_bot(bot: &mut TBot, state: &mut Self::Logic, as_player: usize) -> Self;

    //TODO: default(state) -> Self function?
}

pub trait ServerEvent<TBot: BotBounds>:
    BaseEvent<TBot> + Decode<()> + Encode + Send + Sync
{
    fn update_state(&self, logic: &mut Self::Logic, handle_as: usize, is_server: bool);
    fn create(state: &Self::Logic) -> Self;
}

///
/// BOTS
///

pub struct PlayerConnection {
    pub sender: UnboundedSender<Message>,
    pub receiver: UnboundedReceiver<Message>,
}

pub enum BotMode<T: BotBounds> {
    Server {
        connections: Vec<PlayerConnection>,
    },
    Client {
        bot: T,
        player_index: usize,
        connection: PlayerConnection,
    },
}

impl<TBot: BotBounds> BotMode<TBot> {
    pub async fn wait_for_action<T: ClientEvent<TBot>>(
        &mut self,
        logic: &mut T::Logic,
        from_player: usize,
        to_players: SendTo,
        timeout: Option<Duration>, //TODO: Add some defaulting for clients when the timeout is hit, we might need to take a function as input to do this. Maybe we add a new trait to event similar to the Default trait but takes state as input?
    ) -> Option<T> {
        match self {
            BotMode::Client {
                bot,
                player_index,
                connection,
            } => {
                if from_player == *player_index {
                    let event = T::get_from_bot(bot, logic, *player_index).await;
                    //TODO: Validate the event and maybe ask the bot again? Might be more appropriate to just log it as error and revert to default?

                    event.update_state(logic, *player_index, false);
                    send_event(&connection.sender, &event).await;
                    Some(event)
                } else {
                    if to_players.contains(*player_index) {
                        let event = wait_for::<T>(&mut connection.receiver, None).await?; //TODO: TBH I'd rather throw an error in these cases...
                        //TODO: Call method on bot to handle generic messages from other clients? Don't await it though.
                        //      Todo this we would probably need to make a function on the BaseEvent trait to convert itself to a given enum?
                        event.update_state(logic, from_player, false);
                        Some(event)
                    } else {
                        None
                    }
                }
            }
            BotMode::Server { connections } => {
                let event = wait_for::<T>(&mut connections[from_player].receiver, timeout).await?;
                //TODO: Validate the move and revert to default?
                //TODO: Here we assume disconnection or timeout

                event.update_state(logic, from_player, true);

                for player in to_players.targets(connections.len()) {
                    // Never a case where we would need to send the player that sent the event, their event back
                    if player != from_player {
                        send_event(&connections[player].sender, &event).await;
                    }
                }

                Some(event)
            }
        }
    }

    pub async fn wait_for_event<T: ServerEvent<TBot>>(
        &mut self,
        logic: &mut T::Logic,
        who: SendTo,
    ) -> Option<T> {
        match self {
            BotMode::Client {
                bot: _,
                player_index,
                connection,
            } => {
                if who.contains(*player_index) {
                    let event = wait_for::<T>(&mut connection.receiver, None).await?;
                    event.update_state(logic, *player_index, false);
                    Some(event)
                } else {
                    None
                }
            }
            BotMode::Server { connections } => {
                let event = T::create(logic);

                for player in who.targets(connections.len()) {
                    send_event(&connections[player].sender, &event).await;
                    event.update_state(logic, player, true);
                }

                Some(event)
            }
        }
    }
}

async fn wait_for<T: Decode<()>>(
    receiver: &mut UnboundedReceiver<Message>,
    timeout_duration: Option<Duration>,
) -> Option<T> {
    //TODO: We need to handle disconnections, I think they should just cancel the game?

    let msg = if let Some(dur) = timeout_duration {
        timeout(dur, receiver.recv()).await.ok()??
    } else {
        receiver.recv().await?
    };

    match msg {
        Message::Binary(bytes) => {
            bincode::decode_from_slice::<T, _>(&bytes, bincode::config::standard())
                .ok()
                .map(|(t, _)| t) //TODO: Make a helper function for this
        }
        _ => None,
    }
}

async fn send_event<T: Encode>(sender: &UnboundedSender<Message>, event: &T) {
    if let Ok(bytes) = bincode::encode_to_vec(event, bincode::config::standard()) {
        // We send it as a Binary WebSocket message
        let _ = sender.send(Message::Binary(bytes.into()));
    }
}

#[async_trait::async_trait]
pub trait GameLogic<TBot: BotBounds>: Default {
    fn game_type() -> GameType;
    async fn start_game(&mut self, bots: &mut BotMode<TBot>);
}

#[derive(Debug, Encode, Decode, Clone)]
pub enum RevealedValue<TActual, TConcealed> {
    Revealed(TActual),
    Concealed(TConcealed),
}

impl<TActual, TConcealed> RevealedValue<TActual, TConcealed> {
    pub fn is_revealed(&self) -> bool {
        matches!(self, RevealedValue::Revealed(_))
    }

    pub fn is_concealed(&self) -> bool {
        matches!(self, RevealedValue::Concealed(_))
    }

    pub fn as_revealed(&self) -> Option<&TActual> {
        if let RevealedValue::Revealed(v) = self {
            Some(v)
        } else {
            None
        }
    }

    pub fn as_concealed(&self) -> Option<&TConcealed> {
        if let RevealedValue::Concealed(v) = self {
            Some(v)
        } else {
            None
        }
    }
}

impl<V, H: Default> Default for RevealedValue<V, H> {
    fn default() -> Self {
        RevealedValue::Concealed(H::default())
    }
}

pub trait BotBounds: Send + Sync + Clone {}
impl<T: Send + Sync + Clone> BotBounds for T {}

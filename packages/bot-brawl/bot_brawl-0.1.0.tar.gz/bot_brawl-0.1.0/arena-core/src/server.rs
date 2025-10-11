use std::{collections::HashMap, net::SocketAddr, sync::Arc, time::Duration};

use futures::{SinkExt, StreamExt};
use tokio::{
    net::TcpListener,
    sync::{Mutex, mpsc},
    time::timeout,
};
use tokio_tungstenite::{accept_async, tungstenite::Message};

use crate::{
    common::{BotMode, GameLogic, GameType, PlayerConnection},
    games::tictactoe::{TicTacToeBot, TicTacToePos, TicTacToeState},
    games::tycoon::{Cards, PlayerMove, TycoonBot, TycoonState},
    messages::{ClientMessage, ServerMessage},
};

#[derive(Clone)]
pub struct ServerBot {}

//TODO: NOT IMPORTANT, this is probably impossible but maybe refactor in a way that the server does not need to provide a bot type?.
#[async_trait::async_trait]
impl TicTacToeBot for ServerBot {
    async fn handle_turn(&mut self, _: &TicTacToeState) -> TicTacToePos {
        panic!("Should not be called by server")
    }
}

#[async_trait::async_trait]
impl TycoonBot for ServerBot {
    async fn handle_turn(&self, _: &TycoonState) -> PlayerMove {
        panic!("Should not be called by server")
    }
    async fn handle_card_exchange(&self, _: &TycoonState) -> Cards {
        panic!("Should not be called by server")
    }
}

async fn start_game(bots: &mut BotMode<ServerBot>, gametype: GameType) {
    match gametype {
        //TODO: See if theres a way to refactor this that doesn't require this weird game creation logic, although it is still currently simple.
        GameType::TicTacToe => {
            let mut game = TicTacToeState::default();
            game.start_game(bots).await;
        }
        GameType::Tycoon => {
            let mut game = TycoonState::default();
            game.start_game(bots).await;
        }
    };
}
pub struct GameServer {
    queues: Arc<Mutex<HashMap<GameType, Vec<PlayerConnection>>>>,
}

impl GameServer {
    pub fn new() -> Self {
        Self {
            queues: Arc::new(Mutex::new(HashMap::new())),
        }
    }

    /// Start accepting websocket connections on the provided address (e.g. "0.0.0.0:9001").
    /// This method will run until the listener is closed or the task is cancelled.
    pub async fn start_server(&self, addr: &str) -> anyhow::Result<()> {
        let listener = TcpListener::bind(addr).await?;
        println!("GameServer listening on {}", addr);

        loop {
            let (stream, peer) = listener.accept().await?;
            let qs = self.queues.clone();

            // spawn a light-weight handler per connection
            tokio::spawn(async move {
                if let Err(e) = handle_connection(stream, peer, qs).await {
                    eprintln!("Connection handler error ({}): {:?}", peer, e);
                }
            });
        }
    }
}

/// Read the first message (Join) with timeout, then enqueue connection.
/// If enough players for that game are available, notify them and spawn the game.
async fn handle_connection(
    raw_stream: tokio::net::TcpStream,
    peer: SocketAddr,
    queues: Arc<Mutex<HashMap<GameType, Vec<PlayerConnection>>>>,
) -> anyhow::Result<()> {
    // Accept websocket
    let ws_stream = accept_async(raw_stream).await?;
    println!("Accepted websocket connection from {}", peer);

    // Split and wire up forwarding channels
    let (ws_sink, mut ws_stream) = ws_stream.split();

    // outgoing -> websocket sender
    let (tx_out, mut rx_out) = mpsc::unbounded_channel::<Message>();
    // incoming from websocket -> server
    let (tx_incoming, rx_incoming) = mpsc::unbounded_channel::<Message>();

    // spawn write task
    tokio::spawn(async move {
        let mut ws_sink = ws_sink;
        while let Some(msg) = rx_out.recv().await {
            if ws_sink.send(msg).await.is_err() {
                break;
            }
        }
    });

    // spawn read task
    tokio::spawn(async move {
        while let Some(Ok(msg)) = ws_stream.next().await {
            // push incoming message to server-side receiver
            if tx_incoming.send(msg).is_err() {
                break;
            }
        }
    });

    // Build PlayerConnection expected by game logic
    let mut player_conn = PlayerConnection {
        sender: tx_out.clone(),
        receiver: rx_incoming,
    };

    // Wait up to 5 seconds for a Join message
    let join_msg = timeout(Duration::from_secs(5), wait_for_join(&mut player_conn)).await;
    let join_msg = match join_msg {
        Ok(Ok(msg)) => msg,
        Ok(Err(e)) => {
            // failed to decode or receive join
            eprintln!("Failed to parse join from {}: {:?}", peer, e);
            let _ = tx_out.send(Message::Close(None)); //TODO: Better error handling for the client
            return Err(anyhow::anyhow!(e));
        }
        Err(_) => {
            eprintln!("Timeout waiting for Join from {}", peer);
            let _ = tx_out.send(Message::Close(None));
            return Ok(());
        }
    };

    // enqueue into the corresponding game queue
    match join_msg {
        ClientMessage::Join { game } => {
            let mut queues_lock = queues.lock().await;
            let queue = queues_lock.entry(game).or_default();

            queue.push(player_conn);

            let required = required_players_for_game(&game);

            // If we have enough players, pop them out, notify, and start the game
            if queue.len() >= required {
                // take the first `required` players
                let mut selected = Vec::with_capacity(required);
                for _ in 0..required {
                    let qc = queue.remove(0);
                    selected.push(qc);
                }
                // release the lock before heavy lifting
                drop(queues_lock);

                // Send StartGame messages to selected players and collect connections
                for (i, qc) in selected.iter().enumerate() {
                    let msg = ServerMessage::StartGame {
                        player_index: i as usize,
                    };
                    let bytes =
                        bincode::encode_to_vec(&msg, bincode::config::standard()).expect("encode");
                    // ignore send error; if it fails, we still try to start the game with best-effort connections
                    let _ = qc.sender.send(Message::Binary(bytes.into()));
                }

                // Build BotMode::Server with the selected PlayerConnection list
                let mut server_mode: BotMode<ServerBot> = BotMode::Server {
                    connections: selected,
                };

                // Spawn the game task. `start_game` will consume/borrow `server_mode` mutably.
                let game_clone = game;
                tokio::spawn(async move {
                    println!("Starting game {:?} with {} players", game_clone, required);
                    start_game(&mut server_mode, game_clone).await;

                    // After the game finishes, close all player connections cleanly.
                    // We try to send a Close message for each connection.
                    if let BotMode::Server { mut connections } = server_mode {
                        for conn in connections.iter_mut() {
                            let _ = conn.sender.send(Message::Close(None));
                        }
                    }
                    println!("Game {:?} finished", game_clone);
                });
            } else {
                // keep queued; lock will be released on drop
                println!(
                    "Queued connection from {} for {:?} ({}/{})",
                    peer,
                    game,
                    queue.len(),
                    required
                );
            }
        }
    }

    Ok(())
}

/// Helper: wait for a single incoming binary message and decode it as ClientMessage
async fn wait_for_join(
    conn: &mut PlayerConnection,
) -> Result<ClientMessage, Box<dyn std::error::Error + Send + Sync>> {
    // wait for the next message
    while let Some(msg) = conn.receiver.recv().await {
        if let Message::Binary(bytes) = msg {
            let decoded = bincode::decode_from_slice::<ClientMessage, _>(
                &bytes,
                bincode::config::standard(),
            )?;
            return Ok(decoded.0);
        }
        // ignore non-binary frames until we get the join
    }
    Err("connection closed before join".into())
}

// Move this onto the GameType enum
fn required_players_for_game(game: &GameType) -> usize {
    match game {
        GameType::TicTacToe => 2,
        GameType::Tycoon => 4,
    }
}

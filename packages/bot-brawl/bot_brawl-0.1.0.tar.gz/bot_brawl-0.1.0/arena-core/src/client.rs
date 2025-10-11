use crate::common::{BotBounds, BotMode, GameBot, GameLogic, PlayerConnection};
use crate::messages::{ClientMessage, ServerMessage};
use futures::{SinkExt, StreamExt};
use tokio::sync::mpsc;
use tokio_tungstenite::connect_async;
use tokio_tungstenite::tungstenite::Message;

#[async_trait::async_trait]
pub trait GameClient<TBot: BotBounds, L: GameLogic<TBot>> {
    async fn start(&self, url: &str);
}

#[async_trait::async_trait]
impl<TBot, L> GameClient<TBot, L> for TBot
where
    TBot: GameBot<L>,
    L: GameLogic<TBot> + Send + Sync,
{
    async fn start(&self, url: &str) {
        // Connect to the WebSocket server
        let (ws_stream, _) = match connect_async(url).await {
            Ok(conn) => conn,
            Err(e) => {
                eprintln!("Failed to connect to {url}: {e}");
                return;
            }
        };

        let (mut ws_sender, mut ws_receiver) = ws_stream.split();

        let (tx, mut rx) = mpsc::unbounded_channel::<Message>();
        let (tx_incoming, rx_incoming) = mpsc::unbounded_channel::<Message>();

        // Task to forward outgoing messages to the WebSocket
        tokio::spawn(async move {
            while let Some(msg) = rx.recv().await {
                if ws_sender.send(msg).await.is_err() {
                    break;
                }
            }
        });

        // Task to forward incoming WebSocket messages into our receiver channel
        tokio::spawn(async move {
            while let Some(Ok(msg)) = ws_receiver.next().await {
                if tx_incoming.send(msg).is_err() {
                    break;
                }
            }
        });

        let mut connection = PlayerConnection {
            sender: tx,
            receiver: rx_incoming,
        };

        println!("Connected to {url}");

        // Send join message
        let join_msg = ClientMessage::Join {
            game: L::game_type(),
        };
        let bytes = bincode::encode_to_vec(&join_msg, bincode::config::standard()).unwrap();
        connection
            .sender
            .send(Message::Binary(bytes.into()))
            .unwrap();

        let mut state = L::default();

        println!("Waiting for game to start");
        let player_index = loop {
            if let Some(msg) = connection.receiver.recv().await {
                if let Message::Binary(bytes) = msg {
                    if let Ok(event) = bincode::decode_from_slice::<ServerMessage, _>(
                        //TODO: Make helper for this
                        &bytes,
                        bincode::config::standard(),
                    ) {
                        let ServerMessage::StartGame { player_index } = event.0;
                        println!("Game started, player id: {player_index}");
                        break player_index;
                    }
                }
            }
        };

        // For now, default player index = 0
        let mut client: BotMode<TBot> = BotMode::Client {
            bot: self.clone(),
            player_index,
            connection,
        };

        state.start_game(&mut client).await;
    }
}

use bincode::{Decode, Encode};

use crate::common::{
    BaseEvent, BotBounds, BotMode, ClientEvent, GameBot, GameLogic, GameType, RevealedValue, SendTo,
};
use std::time::Duration;

#[derive(Debug, Clone, Copy, PartialEq, Eq, Encode, Decode)]
pub struct Cards(pub u64);

#[derive(Debug, Clone, Encode, Decode)]
pub enum TycoonServerEvent {
    RoundStart {
        your_cards: Cards,
        totals: [u8; 4],
        turn: usize,
    },
}

// Bot trait
#[async_trait::async_trait]
pub trait TycoonBot: GameBot<TycoonState> + BotBounds {
    async fn handle_turn(&self, state: &TycoonState) -> PlayerMove;
    async fn handle_card_exchange(&self, state: &TycoonState) -> Cards;
}

impl<T: TycoonBot> GameBot<TycoonState> for T {}

// Requests / Events
#[derive(Debug, Clone, Encode, Decode)]
pub struct CardsExchanged {
    pub cards: Cards,
    pub to: usize,
}

impl<T: TycoonBot> BaseEvent<T> for CardsExchanged {
    type Logic = TycoonState;
}

#[async_trait::async_trait]
impl<T: TycoonBot> ClientEvent<T> for CardsExchanged {
    fn validate(&self, state: &Self::Logic, from: usize) -> bool {
        todo!("Validate card exchange")
    }

    fn update_state(&self, logic: &mut Self::Logic, from_player: usize, _: bool) {
        logic.players[from_player].hand.remove_cards(self.cards);
        logic.players[self.to].hand.add_cards(self.cards);
    }

    async fn get_from_bot(bot: &mut T, state: &mut Self::Logic, as_player: usize) -> Self {
        CardsExchanged {
            cards: bot.handle_card_exchange(state).await,
            to: state
                .get_player_with_role(state.players[as_player].role.opposite())
                .expect("There should be a player with the opposite role to use"),
        }
    }
}

#[derive(Debug, Clone, Encode, Decode)]
pub enum PlayerMove {
    CardsPlayed(Cards),
    Pass,
}

impl<T: TycoonBot> BaseEvent<T> for PlayerMove {
    type Logic = TycoonState;
}

#[async_trait::async_trait]
impl<T: TycoonBot> ClientEvent<T> for PlayerMove {
    fn validate(&self, state: &Self::Logic, _: usize) -> bool {
        todo!("Validate player move")
    }

    fn update_state(&self, logic: &mut Self::Logic, _: usize, _: bool) {
        logic.past_moves.push(TycoonPastMove {
            player: logic.turn as u8,
            action: self.clone(),
        });

        if let PlayerMove::CardsPlayed(cards) = self {
            logic.players[logic.turn].hand.remove_cards(*cards);

            // Revolution play
            if cards.count() >= 4 {
                logic.is_revolution = !logic.is_revolution;
            }

            // Case: All 8's ignoring jokers
            if cards.contains_rank(Rank::Eight) && cards.all_same_rank(true) {
                if logic.clear_last_move_and_keep_turn() {
                    return;
                }
            }
            // Case: 3♠ on joker
            else if let Some(last_move) = logic.last_move {
                if last_move.0.num_jokers() == 1
                    && *cards == Cards::from_rank_and_suit(Rank::Three, Suit::Spades)
                {
                    if logic.clear_last_move_and_keep_turn() {
                        return;
                    }
                }
            }
            // Case: Non cutting play
            else {
                logic.last_move = Some((*cards, logic.turn as u8));
            }

            todo!("Check if the player has won and give them their appropriate rank")
        }

        logic.next_turn();
    }

    async fn get_from_bot(bot: &mut T, state: &mut Self::Logic, _: usize) -> Self {
        bot.handle_turn(state).await
    }
}

#[derive(Debug, Clone, Encode, Decode, Default, PartialEq, Eq, Copy)]
pub enum TycoonRole {
    Millionaire,
    Rich,
    Poor,
    Beggar,
    #[default]
    None,
}

impl TycoonRole {
    pub fn opposite(&self) -> Self {
        match self {
            Self::Millionaire => Self::Beggar,
            Self::Rich => Self::Poor,
            Self::Poor => Self::Rich,
            Self::Beggar => Self::Millionaire,
            Self::None => Self::None,
        }
    }

    pub fn cards_to_exchange(&self) -> u8 {
        match self {
            Self::Millionaire | Self::Beggar => 2,
            Self::Rich | Self::Poor => 1,
            Self::None => 0,
        }
    }

    pub fn is_upper_class(&self) -> bool {
        matches!(self, Self::Millionaire | Self::Rich)
    }
}

#[derive(Debug, Clone, Encode, Decode)]
pub struct TycoonPastMove {
    player: u8,
    action: PlayerMove,
    // last_play: Option<Cards>,
}

#[derive(Debug, Clone, Encode, Decode, Default)]
pub struct TycoonPlayer {
    hand: RevealedValue<Cards, u8>,
    role: TycoonRole,
}

#[derive(Debug, Clone, Encode, Decode, Default)]
pub struct TycoonState {
    players: [TycoonPlayer; 4],
    turn: usize,
    is_revolution: bool,
    last_move: Option<(Cards, u8)>,
    past_moves: Vec<TycoonPastMove>,
    round: u32,
}

#[async_trait::async_trait]
pub trait TycoonClients {
    async fn get_player_move(&self, player_index: usize, timeout: Option<Duration>);
    async fn get_cards_for_exchange(&self, player_index: usize, timeout: Option<Duration>);
}

#[async_trait::async_trait]
impl<TBot: TycoonBot> GameLogic<TBot> for TycoonState {
    fn game_type() -> GameType {
        GameType::Tycoon
    }

    // The game loop
    async fn start_game(&mut self, bots: &mut BotMode<TBot>) {
        //todo!("Add game reset logic");

        // Card exchange.
        self.handle_card_exchange(bots).await;

        // Main game loop
        while !self.is_finished() {
            bots.wait_for_action::<PlayerMove>(
                self,
                self.turn,
                SendTo::All,
                Some(Duration::from_secs(1)),
            )
            .await;
        }
    }
}

impl TycoonState {
    async fn handle_card_exchange<TBot: TycoonBot>(&mut self, bots: &mut BotMode<TBot>) {
        for idx in 0..self.players.len() {
            let player_role = self.players[idx].role;
            if player_role.cards_to_exchange() > 0 && player_role.is_upper_class() {
                if let Some(lower_idx) = self.get_player_with_role(player_role.opposite()) {
                    // Request cards from the lower class player first
                    bots.wait_for_action::<CardsExchanged>(
                        self,
                        lower_idx,
                        SendTo::One(idx),
                        Some(Duration::from_secs(1)),
                    )
                    .await;

                    // Now the upper class player gets to react to their received cards
                    bots.wait_for_action::<CardsExchanged>(
                        self,
                        idx,
                        SendTo::One(lower_idx),
                        Some(Duration::from_secs(1)),
                    )
                    .await;
                }
            }
        }
    }

    fn next_turn(&mut self) {
        if self.is_finished() {
            return;
        }

        todo!(
            "If there are roles assigned, i.e this is not the first round, we need to use roles to determine turn order"
        );

        self.turn = (self.turn + 1) % 4;
        todo!("Handle player finished case")
    }

    // Returns true if the current player still has cards to play
    fn clear_last_move_and_keep_turn(&mut self) -> bool {
        self.last_move = None;
        self.players[self.turn].hand.count() != 0
    }

    fn is_finished(&self) -> bool {
        let mut active_players = 0;
        for player in &self.players {
            if player.hand.count() > 0 {
                active_players += 1;
            }
        }
        active_players > 1
    }

    pub fn get_player_with_role(&self, role: TycoonRole) -> Option<usize> {
        self.players
            .iter()
            .enumerate()
            .find(|(_, p)| p.role == role)
            .map(|(i, _)| i)
    }
}

impl RevealedValue<Cards, u8> {
    pub fn count(&self) -> u8 {
        match &self {
            RevealedValue::Concealed(count) => *count,
            RevealedValue::Revealed(cards) => cards.count(),
        }
    }

    pub fn add_cards(&mut self, cards: Cards) {
        match self {
            RevealedValue::Concealed(count) => *count += cards.count(),
            RevealedValue::Revealed(current_cards) => current_cards.add_cards(cards),
        };
    }

    pub fn remove_cards(&mut self, cards: Cards) {
        match self {
            RevealedValue::Concealed(count) => *count -= cards.count(),
            RevealedValue::Revealed(current_cards) => current_cards.remove_cards(cards),
        };
    }
}

#[derive(Copy, Clone, Debug, PartialEq, Eq)]
pub enum Rank {
    Ace = 0,
    Two = 1,
    Three = 2,
    Four = 3,
    Five = 4,
    Six = 5,
    Seven = 6,
    Eight = 7,
    Nine = 8,
    Ten = 9,
    Jack = 10,
    Queen = 11,
    King = 12,
}

#[derive(Copy, Clone, Debug, PartialEq, Eq)]
pub enum Suit {
    Clubs = 0,
    Diamonds = 1,
    Hearts = 2,
    Spades = 3,
}

impl Cards {
    pub fn add_cards(&mut self, cards: Cards) {
        self.0 |= cards.0
    }

    pub fn remove_cards(&mut self, cards: Cards) {
        self.0 &= !cards.0;
    }

    pub fn contains_all(&self, other: Cards) -> bool {
        (self.0 & other.0) == other.0
    }

    /// Check if the hand contains *any* card from the given set
    pub fn contains_any(&self, other: Cards) -> bool {
        (self.0 & other.0) != 0
    }

    /// Contains any card from rank
    pub fn contains_rank(&self, rank: Rank) -> bool {
        self.contains_any(Cards::from_rank(rank))
    }

    /// Count the number of cards in the hand
    pub fn count(&self) -> u8 {
        self.0.count_ones() as u8
    }

    /// Make a mask for all cards of a given rank (0 = Ace, 12 = King for example)
    pub fn from_rank(rank: Rank) -> Self {
        // 4 suits per rank
        let mask = 0b1111u64 << ((rank as u8) * 4);
        Cards(mask)
    }

    /// Mask for a single card (rank + suit)
    pub fn from_rank_and_suit(rank: Rank, suit: Suit) -> Self {
        let bit = 1u64 << ((rank as u8) * 4 + (suit as u8));
        Cards(bit)
    }

    /// Mask for all 13 cards of a suit
    pub fn from_suit(suit: Suit) -> Self {
        let mut mask = 0u64;
        for rank in 0..13 {
            mask |= 1u64 << (rank * 4 + (suit as u8));
        }
        Cards(mask)
    }

    /// Check if the hand is empty
    pub fn is_empty(&self) -> bool {
        self.0 == 0
    }

    pub fn num_jokers(&self) -> u8 {
        ((self.0 >> 52) & 0b11) as u8
    }

    pub fn all_same_rank(&self, exclude_jokers: bool) -> bool {
        if self.is_empty() {
            return false;
        }

        let num_cards = self.count() - self.num_jokers() * exclude_jokers as u8;

        for rank in 0..13 {
            let bits = (self.0 >> (rank * 4)) & 0b1111;
            if bits != 0 {
                return bits.count_ones() == num_cards as u32;
            }
        }

        // In this case its only jokers
        true
    }

    pub fn full_deck(num_jokers: u8) -> Self {
        // 52 cards (bits 0–51)
        let mask = (1u64 << 52) - 1;

        // Jokers are stored in bits 52 and 53
        let jokers_mask = match num_jokers {
            0 => 0,
            1 => 1u64 << 52,
            2 => (1u64 << 52) | (1u64 << 53),
            _ => panic!("A deck can have at most 2 jokers"),
        };

        Cards(mask | jokers_mask)
    }
}

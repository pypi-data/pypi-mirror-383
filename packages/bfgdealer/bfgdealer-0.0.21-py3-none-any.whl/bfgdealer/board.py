"""
    Board class extends bridgeobjects Board
"""

from datetime import datetime
import json
from termcolor import cprint

from endplay import config as endplay_config
from endplay.dds import calc_dd_table
from endplay.types import Deal, Player as endplayPlayer, Denom

from bfgbidding import Player, Hand
from bridgeobjects import (Board as bfg_Board, RANKS, SEATS, SUITS, SUIT_NAMES,
                           parse_pbn, Contract,
                           Auction, Trick)

MODULE_COLOUR = 'green'
DEFAULT_SUIT_ORDER = ['S', 'H', 'C', 'D']
SEPARATOR = 100


class Board(bfg_Board):
    """Define BfG Board class."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.auction = Auction()
        self.description = ''
        self.bid_history = []
        self.warning = None
        self.active_bid_history = []
        self._stage = None
        self.players = {}
        for index in range(4):
            self.players[index] = Player(self, None, index)
            self.players[SEATS[index]] = Player(self, None, index)
        self._dealer = None
        self.leader = None
        self.current_trick = Trick()
        self.unplayed_cards = {seat: [] for seat in SEATS}
        self.hands = {seat: Hand(board=self) for seat in SEATS}
        self.hand_cards = {
            seat: [card.name for card in self.hands[seat].cards]
            for seat in SEATS}
        self.unplayed_card_names = []
        self.current_player = ''
        self.NS_tricks = 0
        self.EW_tricks = 0
        self.score = 0
        self.suit_order = self._get_suit_order()
        self.vulnerable = False
        self.source = 0
        self.initialise_tricks()
        self._contract = Contract()
        self._makeable_tricks = None

    def __repr__(self):
        """Return a string representation of the deal."""
        return f"Board: North's hand {self.hands[0]}"

    def __str__(self):
        """Return a string representation of the deal."""
        return f"Board: North's hand {self.hands[0]}"

    def initialise_tricks(self):
        """Inialise the board's tricks."""
        if len(self.tricks) > 1 or (self.tricks and self.tricks[-1].leader):
            return
        self.tricks = []
        if self._contract.declarer:
            declarer_index = SEATS.index(self._contract.declarer)
            leader = SEATS[(declarer_index - 3) % 4]
        else:
            leader = ''
        trick = Trick([], leader)
        self.tricks.append(trick)

    def to_json(self):
        """Return object as json string."""
        self.update_state()

        # Objects
        hands = {}
        for key, hand in self.hands.items():
            hands[key] = hand.to_json()
        tricks = []
        for trick in self.tricks:
            tricks.append(trick.to_json())
        current_trick = self.current_trick.to_json()

        # Strings
        json_str = json.dumps({
            'auction': self._auction.to_json(),
            'bid_history': self.bid_history,
            'warning': self.warning,
            'contract': self._contract.to_json(),
            'current_player': self.current_player,
            'current_trick': current_trick,
            'declarer': self.declarer,
            'declarer_index': self.declarer_index,
            'declarers_tricks': self.declarers_tricks,
            'dealer': self.dealer,
            'dealer_index': self.dealer_index,
            'description': self.description,
            'east': self.east,
            'EW_tricks': self.EW_tricks,
            'hands': hands,
            'identifier': self.identifier,
            'north': self.north,
            'NS_tricks': self.NS_tricks,
            'south': self.south,
            'stage': self._stage,
            'tricks': tricks,
            'vulnerable': self.vulnerable,
            'west': self.west,

            # Board state
            'max_suit_length': self.max_suit_length,
            'hand_suit_length': self.hand_suit_length,
            'score': self.score,
            'suit_order': self.suit_order,
            'source': self.source,
            'makeable_tricks': self._makeable_tricks
        })
        return json_str

    def from_json(self, json_str):
        """Populate attributes from json string."""
        board_dict = dict(json.loads(json_str))

        self._auction = Auction().from_json(board_dict['auction'])
        self.bid_history = self._update_attribute(
            board_dict, 'bid_history', [])
        self.warning = self._update_attribute(board_dict, 'warning')
        self._contract = Contract().from_json(board_dict['contract'])
        self.current_player = self._update_attribute(
            board_dict, 'current_player')
        self.declarer = self._update_attribute(board_dict, 'declarer')
        self.declarer_index = self._update_attribute(
            board_dict, 'declarer_index')
        self.declarers_tricks = int(self._update_attribute(
            board_dict, 'declarers_tricks', 0))
        self.dealer = self._update_attribute(board_dict, 'dealer', '')
        self.dealer_index = self._update_attribute(board_dict, 'dealer_index')
        self.description = self._update_attribute(board_dict, 'description')
        self.east = self._update_attribute(board_dict, 'east')
        self.EW_tricks = int(self._update_attribute(
            board_dict, 'EW_tricks', 0))
        self.hands = self._get_hands_from_json(board_dict)
        if board_dict['identifier'] == '':
            board_dict['identifier'] = 0
        self.identifier = int(self._update_attribute(
            board_dict, 'identifier', 0))
        self.north = self._update_attribute(board_dict, 'north')
        self.NS_tricks = int(self._update_attribute(
            board_dict, 'NS_tricks', 0))
        self.south = self._update_attribute(board_dict, 'south')
        self._stage = self._update_attribute(board_dict, 'stage')
        self.source = self._update_attribute(board_dict, 'source')
        self.tricks = self._get_tricks_from_json(board_dict)
        self.current_trick = self._get_current_trick_from_json(board_dict)
        self.vulnerable = self._update_attribute(board_dict, 'vulnerable')
        self.west = self._update_attribute(board_dict, 'west')
        self.initialise_tricks()
        self._makeable_tricks = self._update_attribute(
            board_dict, 'makeable_tricks')
        return self

    def _get_hands_from_json(self, board_dict):
        hands_json = self._update_attribute(board_dict, 'hands', {})
        hands = {}
        for key, raw_hand in hands_json.items():
            hand = Hand(board=self)
            hand.from_json(raw_hand)
            if key.isnumeric():
                key = int(key)
            self.players[key].hand = hand
            hands[key] = hand
        return hands

    def _get_tricks_from_json(self, board_dict):
        tricks_json = self._update_attribute(board_dict, 'tricks', [])
        tricks = []
        for raw_trick in tricks_json:
            trick = Trick()
            trick.from_json(raw_trick)
            tricks.append(trick)
        return tricks

    def _get_current_trick_from_json(self, board_dict):
        current_trick_json = self._update_attribute(
            board_dict, 'current_trick', '')
        trick = Trick()
        if current_trick_json:
            return trick.from_json(board_dict['current_trick'])
        else:
            return trick

    @staticmethod
    def _update_attribute(board_dict, key, default=None):
        if key in board_dict:
            return board_dict[key]
        return default

    @property
    def dealer(self):
        return self._dealer

    @dealer.setter
    def dealer(self, value):
        assert value in SEATS, f'Invalid dealer: {value}'
        self._dealer = value
        self.dealer_index = SEATS.index(value)

    @property
    def auction(self):
        """Return auction property."""
        return self._auction

    @auction.setter
    def auction(self, value):
        """Set auction property."""
        self._auction = value
        if value:
            self._contract = self.get_contract()

    @property
    def contract(self):
        """Return contract property."""
        return self._contract

    @contract.setter
    def contract(self, value):
        """Set contract property."""
        self._contract = value
        self.initialise_tricks()
        self.current_player = self._get_leader()

    def _get_leader(self) -> str:
        """Return the board leader."""
        declarer = self.contract.declarer
        if declarer == '':
            return ''
        seat_index = SEATS.index(declarer)
        leader_index = (seat_index + 1) % 4
        leader = SEATS[leader_index]
        return leader

    @property
    def stage(self):
        """Assign stage property."""
        return self._stage

    @property
    def makeable_tricks(self) -> str:
        """Return makeable tricks for the board."""
        if not self._makeable_tricks:
            # deal = self.endplay_deal
            deal = Deal(f'{self.dealer}:{self.get_deal_hands_pbn()}')
            makeable = str(calc_dd_table(deal))
            contracts = makeable.split(';')

            output = {}
            for seat in contracts[1:]:
                levels = seat[2:].split(',')
                output[seat[0]] = levels
            self._makeable_tricks = output
        return self._makeable_tricks

    @property
    def endplay_deal(self) -> Deal:
        """Return endplay deal for the board, with trick cards played."""
        deal = Deal(f'{self.dealer}:{self.get_deal_hands_pbn()}')
        endplay_config.use_unicode = False
        if self.contract.denomination:
            deal.trump = Denom.find(self.contract.denomination.name[0])
            deal.declarer = endplayPlayer.find(self.contract.declarer)

        self._play_dds_cards(deal)
        return deal

    def _play_dds_cards(self, deal: endplay_deal) -> None:
        for trick in self.tricks:
            deal.first = endplayPlayer.find(trick.leader)
            for card in trick.cards:
                card_name = f'{card.name[1]}{card.name[0]}'
                try:
                    deal.play(card_name)
                except RuntimeError:
                    cprint(
                        (f'RuntimeError playing card: '
                         f'{card_name} {deal.first} {endplayPlayer.west}'), 'red')

    def get_deal_hands_pbn(self, delimiter: str = ' ') -> str:
        """Return a board's hands as a string in pbn format."""
        hands_list = []
        seat_count = 4
        for index in range(seat_count):
            seat = self._get_seat_from_index(index)
            hand_string = self._prepare_hand_string(seat)
            hands_list.append(hand_string)
        return delimiter.join(hands_list)

    def _prepare_hand_string(self, seat: str) -> str:
        """Return a string representing the hands unplayed cards."""
        suit_count = 4
        hand = self.hands[seat]
        hand_list = [['']*13 for _ in range(suit_count)]

        for card in hand.cards:
            suit = 3 - card.suit.rank
            rank = 13 - RANKS.index(card.rank)
            hand_list[suit][rank] = card.name[0]
        for suit in range(suit_count):
            hand_list[suit] = ''.join(hand_list[suit])
        return '.'.join(hand_list)

    def _get_seat_from_index(self, index: str) -> int:
        """Return the seat index based on dealer."""
        dealer_index = SEATS.index(self.dealer)
        seat_index = dealer_index + index
        if seat_index > 3:
            seat_index -= 4
        return SEATS[seat_index]

    def _get_played_cards(self) -> list:
        """Return a list of cards that have been played."""
        played_cards = []
        for trick in self.tricks:
            played_cards.extend([card for card in trick.cards])
        return played_cards

    @stage.setter
    def stage(self, value):
        """Set stage property."""
        self._stage = value

    def deal_from_pbn(self, pbn_string):
        """Create a deal from pbn_string."""
        pass

    def set_description(self, description):
        """Set the Board description."""
        self.description = description

    def get_auction(self, test=False):
        """Generate the auction."""
        if test:
            player_index = 0
        else:
            player_index = self.dealer_index
        auction_calls = []

        bid_history, self.bid_history = self.bid_history, []
        while not self.three_final_passes(auction_calls):
            player = self.players[player_index]
            bid = player.make_bid()
            auction_calls.append(bid)
            player_index += 1
            player_index %= 4
        auction = Auction()
        auction.calls = auction_calls
        auction.first_caller = self.dealer
        self.bid_history = bid_history
        return auction

    def _default_hands(self):
        hands = []
        dummy_hand = ['AS', 'KS', 'QS', 'JS', 'TS', '9S', '8S',
                      '7S', '6S', '5S', '4S', '3S', '2S']
        hands.append(Hand(dummy_hand, board=self))
        dummy_hand = [hand.replace('S', 'H') for hand in dummy_hand]
        hands.append(Hand(dummy_hand, board=self))
        dummy_hand = [hand.replace('H', 'D') for hand in dummy_hand]
        hands.append(Hand(dummy_hand, board=self))
        dummy_hand = [hand.replace('D', 'C') for hand in dummy_hand]
        hands.append(Hand(dummy_hand, board=self))
        return hands

    def parse_pbn_board(self, pbn_board, delimiter = ':'):
        """Return a list of hands from a pbn deal string."""
        events = parse_pbn(pbn_board)
        board = events[0].boards[0]
        self.description = board.description
        self.dealer = board.dealer
        self.hands = {}
        for key, hand in board.hands.items():
            self.hands[key] = Hand(hand.cards, board=self)
        for index in range(4):
            self.players[index].hand = self.hands[index]
        return board.hands

    def _get_pbn_dealer_index(self, deal):
        """
            Return the first hand index to ensure that the first hand
            assigned to the board's hands list is that of the board dealer.
        """
        # first_hand is the position index of the first hand given in the deal
        first_hand = SEATS.index(deal[0])

        # dealer_index is the position index of the dealer
        dealer_index = SEATS.index(self.dealer)

        # rotate the hand index to ensure that the
        # first hand created is the dealer's
        hand_index = (first_hand - dealer_index) % 4
        return hand_index

    def create_pbn_list(self):
        """Return a board as a list of strings in pbn format."""
        date = datetime.now().strftime('%Y.%m.%d')
        deal_list = ['[Event "bfg generated deal"]',
                     f'[Date "{date}"]',
                     f'[Board "{self.description}"]',
                     f'[Dealer "{self.dealer}"]',
                     f'[Deal "{self.dealer}:{self._get_deal_pbn()}"]',
                     '']
        return deal_list

    def _get_deal_pbn(self, delimiter: str = ' ') -> str:
        """Return a board's hands as a string in pbn format."""
        hands_list = []
        seat_index = SEATS.index(self.dealer)
        for index in range(4):
            seat_index += index
            seat_index %= 4
            seat = SEATS[seat_index]
            hand = self.hands[seat]
            hand_list = [['']*13 for _ in range(4)]

            for card in hand.cards:
                suit = 3 - card.suit.rank
                rank = 13 - RANKS.index(card.rank)
                hand_list[suit][rank] = card.name[0]
            for index in range(4):
                hand_list[index] = ''.join(hand_list[index])
            hands_list.append('.'.join(hand_list))
        return delimiter.join(hands_list)

    @staticmethod
    def rotate_board_hands(board, increment=1):
        """Return the hands rotated through increment clockwise."""
        rotated_hands = {}
        hands = board.hands
        for index in range(4):
            rotated_index = (index + increment) % 4
            if index in hands:
                rotated_hands[rotated_index] = hands[index]
                board.players[rotated_index].hand = hands[index]
            if SEATS[index] in hands:
                rotated_hands[SEATS[rotated_index]] = hands[SEATS[index]]
        board.hands = rotated_hands
        return board

    def get_contract(self):
        """Return a contract from the auction."""
        contract = Contract()
        if not self._auction:
            return contract

        if not (self.three_final_passes(self._auction.calls) and
                not self._passed_out(self._auction.calls)):
            return contract

        (call, modifier, declarer_partition) = self._analyse_auction()

        declarer_index = self._get_declarer_index(call, declarer_partition)
        declarer = SEATS[declarer_index]
        contract = Contract(f'{call.name}{modifier}', declarer)
        self.initialise_tricks()
        return contract

    def _analyse_auction(self):
        auction_calls = list(self._auction.calls)
        auction_calls.reverse()
        modifier = ''
        for call in auction_calls:
            if call.name == 'R':
                modifier = 'R'
            if call.name == 'D':
                modifier = 'D'
            if call.is_value_call:
                break
        declarer_partition = self._auction.calls.index(call)

        return (call, modifier, declarer_partition)

    def _get_declarer_index(self, call, declarer_partition):
        for index, check_call in enumerate(self._auction.calls):
            if (check_call.denomination == call.denomination and
                    (declarer_partition - index) % 2 == 0):
                break
        dealer_index = SEATS.index(self.dealer)
        declarer_index = (dealer_index + index) % 4
        return declarer_index

    @staticmethod
    def _passed_out(calls):
        """Return True if the board has been passed out."""
        if len(calls) != 4:
            return False
        for call in calls:
            if not call.is_pass:
                return False
        return True

    @staticmethod
    def three_final_passes(calls):
        """Return True if there have been three consecutive passes."""
        three_passes = False
        if len(calls) >= 4:
            if calls[-1].is_pass and calls[-2].is_pass and calls[-3].is_pass:
                three_passes = True
        return three_passes

    def get_attributes_from_board(self, board):
        """Set the attributes from a bridgeobjects board instance."""
        self.convert(board)

    def convert(self, board):
        """Set the attributes from a bridgeobjects board instance."""
        for key, item in board.__dict__.items():
            self.__dict__[key] = item

        self.hands = {}
        for seat, hand in board.hands.items():
            self.hands[seat] = Hand(hand.cards, board=self)

        for index in range(4):
            self.players[index].hand = board.hands[index]

        self.auction = Auction()
        for key, item in board.auction.__dict__.items():
            self.auction.__dict__[key] = item

        self._contract = Contract()
        for key, item in board.contract.__dict__.items():
            self._contract.__dict__[key] = item

        self.tricks = []
        for raw_trick in board.tricks:
            trick = Trick()
            for key, item in raw_trick.__dict__.items():
                trick.__dict__[key] = item
            self.tricks.append(trick)
        self.initialise_tricks()

        self.get_unplayed_cards()
        self.current_player = self._get_leader()

    def get_unplayed_cards(self):
        """Update the hands' unplayed cards."""
        played_cards = []
        for trick in self.tricks:
            for card in trick.cards:
                played_cards.append(card)
        for seat, hand in self.hands.items():
            cards = [card for card in hand.cards if card not in played_cards]
            hand.unplayed_cards = cards

    def get_current_trick(self):
        """Return the current trick or create one if necessary."""
        if self.tricks:
            trick = self.tricks[-1]
        else:
            trick = self.setup_first_trick_for_board()
            self.tricks.append(trick)
        return trick

    def setup_first_trick_for_board(self) -> Trick:
        """Set up and return the first trick for a board."""
        trick = Trick()
        if self.contract.declarer:
            self.current_player = self._get_leader()
            trick.leader = self.current_player
        return trick

    def update_state(self):
        """Return a context with the current state of the board."""
        # These variables (dicts) are all natural ('N' etc. based on SEATS)
        (hand_suit_length, max_suit_length, unplayed_cards) = self._hand_shape_details()
        score = 0
        if self.NS_tricks + self.EW_tricks == 13:
            score = self._get_score()

        self.hand_cards = {
            seat: [card.name for card in self.hands[seat].cards]
            for seat in SEATS}
        self.unplayed_card_names = unplayed_cards
        self.max_suit_length = max_suit_length
        self.hand_suit_length = hand_suit_length
        self.current_player = self.current_player
        self.NS_tricks = self.NS_tricks
        self.EW_tricks = self.EW_tricks
        self.score = score
        context = {
            'hand_cards': {
                seat: [card.name for card in self.hands[seat].cards]
                for seat in SEATS},
            'unplayed_card_names': unplayed_cards,
            'max_suit_length': max_suit_length,
            'hand_suit_length': hand_suit_length,
            'current_player': self.current_player,
            'NS_tricks': self.NS_tricks,
            'EW_tricks': self.EW_tricks,
            # 'board_status': self.status,
            # 'play_status': self.play_status,
            # 'play_master': self.play_master,
            'score': score,
        }
        return context

    def _hand_shape_details(self):
        """Return hand shape details used to
        calculate E/W display in card play."""
        # unplayed_cards: dict keyed on seat of the unplayed cards in that hand
        unplayed_cards = {}

        # hand_suit_length: dict keyed on seat of list of suit lengths
        # (in suit_order) by hand
        hand_suit_length = {}

        # max_suit_length: dict keyed on seat with max suit length
        # for that seat
        max_suit_length = {}
        for seat in SEATS:
            # print(board.hands)
            hand = self.hands[seat]
            # Get the shape depending on unplayed_cards
            hand_for_shape = Hand(hand.unplayed_cards, board=self)
            hand_for_shape.cards = [card for card in hand.unplayed_cards]
            unplayed = Hand.sort_card_list(
                hand_for_shape.cards, self.suit_order)
            unplayed_cards[seat] = [card.name for card in unplayed]
            suit_length = []
            for suit_name in self.suit_order:
                suit = SUITS[suit_name]
                suit_length.append(hand_for_shape.suit_length(suit))
            hand_suit_length[seat] = suit_length
            max_suit_length[seat] = hand_for_shape.shape[0]
        return (hand_suit_length, max_suit_length, unplayed_cards)

    def _get_suit_order(self):
        """Return a list of suit order."""
        if self.three_passes(self.bid_history):
            bid_history = self.bid_history[:-3]
            while bid_history and bid_history[-1] in ['D', 'R']:
                bid_history = self.bid_history[:-1]
            contract = bid_history[-1]
            suit = contract[-1]
            if suit in DEFAULT_SUIT_ORDER:
                if suit == 'S':
                    return DEFAULT_SUIT_ORDER
                if suit == 'H':
                    return ['H', 'S', 'D', 'C']
                if suit == 'D':
                    return ['D', 'S', 'H', 'C']
                if suit == 'C':
                    return ['C', 'H', 'S', 'D']
            else:
                return DEFAULT_SUIT_ORDER
        else:
            return DEFAULT_SUIT_ORDER

    @staticmethod
    def three_passes(bid_history: list[str]) -> bool:  # X
        """Return True if there are 3 passes."""
        if len(bid_history) >= 4:
            if (bid_history[-1] == 'P' and
                    bid_history[-2] == 'P' and
                    bid_history[-3] == 'P'):
                return True
        return False

    def _get_score(self):
        """Return the score for the board."""
        vulnerable = False
        if self._contract.declarer in 'NS':
            declarers_tricks = self.NS_tricks
            if self.vulnerable in ['NS', 'Both', 'All']:
                vulnerable = True
        else:
            declarers_tricks = self.EW_tricks
            if self.vulnerable in ['EW', 'Both', 'All']:
                vulnerable = True
        return self._contract.score(declarers_tricks, vulnerable)

    def display_stats(self):
        hand_card_dict = self._get_hand_card_dict()
        # suits = [suit for suit in SUIT_NAMES]
        # suits.reverse()
        max_cards = self._get_suit_lengths(hand_card_dict)
        auction = self.auction
        if not self.auction.calls:
            auction = self.get_auction([])
        calls = [call.name for call in auction.calls]
        contract = Contract('', '', auction)
        self._display(hand_card_dict, max_cards, calls, contract)

    def _display(self, hand_card_dict, max_cards, calls, contract):
        cprint(f"{'='*SEPARATOR}", MODULE_COLOUR)
        spades = f"{'S':-<{max_cards['S']}}"
        hearts = f"{'H':-<{max_cards['H']}}"
        diams = f"{'D':-<{max_cards['D']}}"
        clubs = f"{'C':-<{max_cards['C']}}"
        cprint(f"{' '} {spades} {hearts} {diams} {clubs}", MODULE_COLOUR)

        for seat in range(4):
            hand = self.hands[seat]
            hand_cards = hand_card_dict[seat]
            spades = f"{hand_cards['S']:<{max_cards['S']}}"
            hearts = f"{hand_cards['H']:<{max_cards['H']}}"
            clubs = f"{hand_cards['C']:<{max_cards['C']}}"
            diams = f"{hand_cards['D']:<{max_cards['D']}}"
            cards = f'{spades} {hearts} {diams} {clubs}'
            hand_details = f'{SEATS[seat]} {cards} {hand.shape} {hand.hcp:>2}'
            cprint(hand_details, MODULE_COLOUR)

        cprint(f"{'-'*SEPARATOR}", MODULE_COLOUR)
        cprint(f"Dealer: {self.dealer}", MODULE_COLOUR)

        cprint(f"{', '.join(calls)}", MODULE_COLOUR)
        cprint(f"{contract}", MODULE_COLOUR)
        cprint(f"{'='*SEPARATOR}", MODULE_COLOUR)

    def _get_hand_cards(self):
        suits = [suit for suit in SUIT_NAMES]
        suits.reverse()
        hand_cards_list = self._sort_hand_cards()
        hands = {}
        for seat in range(4):
            hand_cards = hand_cards_list[seat]
            cards = {}
            for suit in suits:
                suit_cards = [
                    card[0] for card in hand_cards if card[1] == suit]
                cards[suit] = ('').join(suit_cards)
            hands[seat] = cards
        return hands

    def _get_hand_card_dict(self):
        hands = self._sort_hand_cards()
        hand_card_dict = {}
        for seat in range(4):
            cards = {}
            for suit in SUIT_NAMES:
                card_list = []
                for card in hands[seat]:
                    if card[1] == suit:
                        card_list.append(card[0])
                cards[suit] = ''.join(card_list)
            hand_card_dict[seat] = cards
        return hand_card_dict

    @staticmethod
    def _get_suit_lengths(hands):
        max_cards = {'S': 0, 'H': 0, 'D': 0, 'C': 0}
        for seat in range(4):
            cards = hands[seat]
            for suit in SUIT_NAMES:
                if len(cards[suit]) > max_cards[suit]:
                    max_cards[suit] = len(cards[suit])
        return max_cards

    def _sort_hand_cards(self) -> list[str]:
        hands = []
        hand_cards = []
        suit_order = self._get_suit_order()
        for index in range(4):
            hand = str(self.hands[index])
            hands.append(hand.replace(
                'Hand(', '').replace(')', '').replace('"', ''))
            sorted_hand = Hand.sort_card_list(
                self.hands[index].cards, suit_order)
            hand_cards.append([card.name for card in sorted_hand])
        return hand_cards

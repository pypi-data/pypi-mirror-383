import random
from termcolor import cprint

from .dealer import Dealer as DealerBase
from bridgeobjects import SEATS, BALANCED_SHAPES, SUITS, SHAPES

from bfgdealer.constants import WEAK_TWO_SHAPES

MODULE_COLOUR = 'red'


class Dealer(DealerBase):
    """Generate deals for Duo stages."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.set_hands = [
            ('Weak NT', self.weak_nt_hand),
            ('Strong NT', self.strong_nt_hand),
            # ('5 card majors', self.five_card_major_opening),
            ('20+ points hand', self.twenty_plus_hand),
            ('23+ points hand', self.twenty_three_plus_hand),
            ('Benji 2C opening hand', self.benji_two_club_hand),
            ('Slam potential', self.slam_potential_hand),
            ('Jacoby 2NT', self.jacoby_2nt_board),
            ('Negative doubles', self.negative_double_hand),
            ('Splinters', self.splinter_board),
            ('Unassuming cue bids', self.unassuming_cue_bid_board),
            ('Take-out doubles', self.take_out_double_board),
            ('Defending against weak 1NT', self.defend_weak_nt_board),
            ('Fourth suit forcing', self.fourth_suit_forcing_board),
            ('Response to preemptive opening', self.respond_to_preempt_board),
            ('Defending preemptive opening', self.defend_preempt_board),
            ('Support for a minor', self.minor_support_board),
            ('Multi-2D', self.multi_two_diamond),
            ('Lucas-2s', self.lucas_2s),
        ]
        self.generate_hand = self.engine.get_hand_from_points_and_shape
        self.create_board = self.engine.create_board_from_hands
        self.random_shape = self.engine.select_random_shape_from_list
        self._dealer = ''

    def get_set_hand(self, stages, dealer):
        """Return a board relevant to set stages."""
        self._dealer = dealer
        stage = int(random.choice(stages))
        board = self.set_hands[stage][1]()
        board.dealer = self._dealer
        board.stage = stage
        return board

    def _first_seat(self):
        if self._dealer in 'EW':
            return (SEATS.index(self._dealer) + 1) % 4
        return SEATS.index(self._dealer)

    def twenty_plus_hand(self):
        """Return a board with 20+ points."""
        hand = self.generate_hand([20, 35])
        hands = {self._first_seat(): hand}
        board = self.create_board(hands)
        return board

    def twenty_three_plus_hand(self):
        """Return a board with 20+ points."""
        hand = self.generate_hand([23, 35])
        hands = {self._first_seat(): hand}
        board = self.create_board(hands)
        return board

    def weak_nt_hand(self):
        """Deal a balanced hand with 12-14 points."""
        hand = self.generate_hand([12, 14], BALANCED_SHAPES)
        hands = {self._first_seat(): hand}
        board = self.create_board(hands)
        return board

    def strong_nt_hand(self):
        """Deal a balanced hand with 15-17 points."""
        hand = self.generate_hand([15, 17], BALANCED_SHAPES)
        hands = {self._first_seat(): hand}
        board = self.create_board(hands)
        return board

    def five_card_major_opening(self):
        """Deal a hand with 5 card major 12 + points."""
        found = False
        hand = None
        while not found:
            hand = self.generate_hand([12, 35])
            if hand.spades >= 5 or hand.hearts >= 5:
                found = True
        hands = {self._first_seat(): hand}
        board = self.create_board(hands)
        return board

    def benji_two_club_hand(self):
        """
            Deal a hand with Benji 2C opener.

            Either balanced 19-20 or
            long suit 16-22.
        """
        hand = self._get_benji_hand()
        hands = {self._first_seat(): hand}
        board = self.create_board(hands)
        return board

    def _get_benji_hand(self):
        selection = random.randint(0, 2)
        hand = None
        if selection == 2:
            return self.generate_hand([19, 20], BALANCED_SHAPES)

        while True:
            hand = self.generate_hand([16, 22], WEAK_TWO_SHAPES)
            if hand.suit_points(hand.longest_suit) >= 9:
                if (hand.shape[0] != 6 and hand.aces < 2):
                    return hand

    def slam_potential_hand(self):
        """Deal a hand with slam potential."""
        found = False
        board = None
        while not found:
            hand = self.generate_hand([16, 35])
            hands = {self._first_seat(): hand}
            board = self.create_board(hands)
            auction = self._get_auction_calls(board)
            if auction[-4].level >= 6:
                found = True
        return board

    def jacoby_2nt_board(self):
        """
            Deal a hand with jacoby 2NT response.

            The Jacoby 2NT convention is an artificial, game-forcing response to
            a 1H or 1S opening bid. The 2NT response shows 4+ trump support with
            13+ (or a good 12) points. The bid asks partner to describe her hand further so
            that slam prospects can be judged accordingly.
        """
        found = False
        board = None
        while not found:
            openers_hand = self.generate_hand([12, 19])
            opener = self._first_seat()
            responder = (opener + 2) % 4
            hands = {opener: openers_hand}
            if openers_hand.spades < 4 and openers_hand.hearts < 4:
                continue
            if openers_hand.shape[0] == 4 and openers_hand.hcp <= 14:
                continue
            board = self.create_board(hands)

            # board.dealer = self._dealer
            # cprint(f"{board.dealer}", MODULE_COLOUR)
            auction = self._get_auction_calls(board)
            # if self._dealer in 'EW': # and auction.calls[0].name != 'P':
            #     auction_2 = self._get_auction_calls(board)
            #     cprint(f"{board.dealer=}", MODULE_COLOUR)
            #     cprint(f"{auction}", MODULE_COLOUR)
            #     cprint(f"{auction_2}", 'green')
            #     continue

            partners_hand = board.hands[responder]
            if partners_hand.spades < 4 and partners_hand.hearts < 4:
                continue
            if not (partners_hand.hcp >= 12 and partners_hand.shape[3] >= 2):
                continue
            if self._four_of_openers_major(partners_hand, auction):
                found = True
        return board

    @staticmethod
    def _four_of_openers_major(partner, auction):
        """Return True if hand has 4 of partner's major."""
        if ((auction[0].name == '1S' and partner.spades >= 4) or
           (auction[0].name == '1H' and partner.hearts >= 4)):
            return True
        return False

    def negative_double_hand(self):
        """
            Deal a hand with negative double response.

            The negative double (aka "Sputnik") is a conventional double
            used by responder after opener starts the bidding with
            one-of-a-suit and the next player makes a suit overcall.

            The double always promises 6+ points and,
            depending on the auction, at least
            four cards in at least one of the unbid suits.

            If both minors are bid, the double promises both majors.
            If both majors are bid, the double promises both minors.
            If a minor and a major are bid, the double promises the other major.
        """
        found = False
        board = None
        while not found:
            (board, opener) = self._get_opener_overcaller_board()
            responder = (opener + 2) % 4
            responders_hand = board.hands[responder]
            if responders_hand.hcp < 6:
                continue

            # Eliminate obviously inappropriate hands before checking auction
            openers_hand = board.hands[opener]
            if openers_hand.spades >= 5 and responders_hand.spades >= 4:
                continue
            if openers_hand.hearts >= 5 and responders_hand.hearts >= 4:
                continue

            (openers_bid, overcallers_bid) = self._negative_double_auction(board)

            if not openers_bid or not overcallers_bid:
                # Need to do this check before the others!
                continue
            if not openers_bid.is_suit_call or openers_bid.level != 1:
                continue
            if not overcallers_bid.is_suit_call or overcallers_bid.level > 2:
                continue

            # Check no support for opener's major.
            if (openers_bid.denomination.name == 'S' and
                    responders_hand.spades >= 4):
                continue
            if (openers_bid.denomination.name == 'H' and
                    responders_hand.hearts >= 4):
                continue
            if not overcallers_bid.is_suit_call:
                continue

            # Check holding in unbid suits.
            if not self._valid_negative_double_suit_holding(openers_bid,
                                                            overcallers_bid,
                                                            responders_hand):
                continue
            found = True
        return board

    def _negative_double_auction(self, board):
        """Return the first two relevant bids in the auction."""
        auction = self._get_auction_calls(board)
        if board.dealer in ('N', 'S'):
            start = 0
        else:
            start = 1
        # openers_bid is the first bid on our side
        openers_bid = auction[start]
        overcallers_bid = auction[start+1]

        # Ensure that either N or S are opener.
        if board.dealer in ('E', 'W') and auction[0].name != 'P':
            openers_bid, overcallers_bid = None, None
        return (openers_bid, overcallers_bid)

    def _valid_negative_double_suit_holding(self, openers_bid, overcallers_bid, responders_hand):
        """
            Return True if responder's suit holding is valid for neg double.

            If both minors are bid, the double promises both majors.
            If both majors are bid, the double promises both minors.
            If a minor and a major are bid, the double promises the other major.
        """
        # Check S and a minor bid
        if ((openers_bid.denomination.name == 'S' and
                overcallers_bid.denomination.is_minor) or
                (overcallers_bid.denomination.name == 'S' and
                 openers_bid.denomination.is_minor) and
                responders_hand.hearts != 4):
            return False

        # Check H and a minor bid
        if ((openers_bid.denomination.name == 'H' and
                overcallers_bid.denomination.is_minor) or
                (overcallers_bid.denomination.name == 'H' and
                 openers_bid.denomination.is_minor) and
                responders_hand.spades != 4):
            return False

        # Check 2 minors bid
        if (openers_bid.denomination.is_minor and
                overcallers_bid.denomination.is_minor and
                (responders_hand.hearts != 4 or
                    responders_hand.spades != 4)):
            return False

        # Check 2 majors bid
        if (openers_bid.denomination.is_major and
                overcallers_bid.denomination.is_major and
                (responders_hand.diamonds != 4 or
                    responders_hand.clubs != 4)):
            return False
        return True

    def splinter_board(self):
        """Deal a hand with splinter response.

            A splinter bid is a way of agreeing partner’s suit,
            limiting your hand (say a seven-loser hand with around 9-12 HCP),
            and showing a shortage in a specific side suit, all at the same time.

            The most common splinter situation occurs when
            opener opens with a major and responder makes a
            double jump with 4+ card support.

            Game forcing.
        """
        found = False
        board = None
        dealer_index = SEATS.index(self._dealer)
        while not found:
            (board, opener) = self._get_splinter_board(responders_min_hcp=9)

            # Responders hand
            responder = (opener + 2) % 4
            responders_hand = board.hands[responder]

            # Eliminate obviously inappropriate hands before checking auction
            openers_hand = board.hands[opener]
            if openers_hand.spades >= 5 and responders_hand.spades < 4:
                continue
            if openers_hand.hearts >= 5 and responders_hand.hearts < 4:
                continue
            if responders_hand.shape[3] > 1:
                continue
            if responders_hand.hcp > 12:
                continue
            if not 6 < responders_hand.losers < 8:
                continue
            # print(responders_hand.losers)

            # Ensure N or S are the opener
            auction = self._get_auction_calls(board)
            openers_call = (opener - dealer_index) % 4
            if not self._opener_is_ns(auction, openers_call):
                continue

            # Opener' call
            if not self._opener_is_suit_at_level_one(auction[openers_call]):
                continue
            if not auction[openers_call].is_major:
                continue
            suit = auction[openers_call].denomination

            if responders_hand.suit_holding[suit] < 4:
                continue
            # Check shortage last to allow some unsuitable hands through
            if responders_hand.shape[3] > 1:
                choice = random.randint(0, 10)
                if choice < 10:
                    continue
            found = True
        return board

    def _get_splinter_board(self, responders_min_hcp):
        """Return a board with suitable NS hands."""
        found = False
        while not found:
            openers_hand = self.generate_hand([12, 19])
            responders_hand_max = 34 - openers_hand.hcp
            responders_hand = self.generate_hand([0, responders_hand_max],
                                                 partners_hand=openers_hand)
            distribution_points = self._get_distribution_points(responders_hand)
            if responders_hand.hcp + distribution_points >= responders_min_hcp:
                found = True
        # The first hand to bid on NS gets the opening hand.
        (check_bid, opener, responder) = self._opener_given_dealer(ns_opener=True)
        del check_bid
        hands = {
            opener: openers_hand,
            responder: responders_hand,
        }
        board = self.create_board(hands)
        board.dealer = self._dealer
        return (board, opener)

    @staticmethod
    def _get_distribution_points(hand):
        """Return the distribution points for a hand."""
        distribution_points = 0
        distribution_points += 5 * hand.shape.count(0)
        distribution_points += 3 * hand.shape.count(1)
        distribution_points += 1 * hand.shape.count(2)
        return distribution_points

    def unassuming_cue_bid_board(self):
        """
            Deal a hand suitable for unassuming cue bids.

            An “Unassuming Cue Bid” (UCB) shows 10+ points and
            3+ card support for partner's overcall.

            Can be slow: difficut to find hands where EW open, NS overcalls and partner ash 10+hcp.
        """
        found = False
        board = None
        dealer_index = SEATS.index(self._dealer)
        while not found:
            (board, opener) = self._get_opener_overcaller_board(ns_opener=False)
            # Advancer's suit holding
            advancer = (opener + 3) % 4
            if board.hands[advancer].hcp < 10:
                continue

            auction = self._get_auction_calls(board)

            # Ensure that N/S pass if they are the opener.
            if self._dealer in ('N', 'S') and auction[0].name != 'P':
                continue

            # Ensure E or W are the opener
            openers_call = (opener - dealer_index) % 4
            if not self._opener_is_ns(auction, openers_call):
                continue

            # Check East/West's first call
            if not auction[openers_call].is_suit_call:
                continue

            # Ensure overcaller's bid is a suit
            overcallers_call = openers_call + 1
            if not auction[overcallers_call].is_suit_call:
                continue

            # Advancer's suit holding
            suit = auction[overcallers_call].denomination
            if board.hands[advancer].suit_holding[suit] < 4:
                continue
            found = True
        return board

    def take_out_double_board(self):
        """
            Deal a hand suitable for Takeout doubles.

            The takeout double by overcaller asks partner to bid
            one of the unbid suits. The double usually shows 11+ points and
            3+ cards in each unbid suit. A takeout double can also be used
            with a 5+ card suit if it would mean bidding at too high a level.
        """
        found = False
        board = None
        dealer_index = SEATS.index(self._dealer)
        while not found:
            (board, opener) = self._get_opener_overcaller_board(ns_opener=False)
            hands = {
                opener: board.hands[opener],
            }
            # generate a new board where either N or S might be overcaller.
            board = self.create_board(hands)
            board.dealer = self._dealer

            # These checks seem to slow it down!
            # Responders hand
            # responder = (opener + 2) % 4
            # responders_hand = board.hands[responder]
            # if responders_hand.hcp < 11:
            #     continue
            # if responders_hand.shape[2] < 3:
            #     continue

            auction = self._get_auction_calls(board)

            # Ensure that N/S pass if they are the opener.
            if self._dealer in ('N', 'S') and auction[0].name != 'P':
                continue

            # Ensure E or W are the opener
            openers_call = (opener - dealer_index) % 4
            if not self._opener_is_ns(auction, openers_call):
                continue

            # Check East/West's first call
            if not auction[openers_call].is_suit_call:
                continue

            overcaller1 = (opener + 1) % 4
            overcaller3 = (opener + 3) % 4

            overcaller1_hand = board.hands[overcaller1]
            overcaller3_hand = board.hands[overcaller3]
            if overcaller1_hand.hcp < 11 and overcaller3_hand.hcp < 11:
                continue
            if overcaller1_hand.hcp >= 11:
                overcallers_hand = overcaller1_hand
            else:
                overcallers_hand = overcaller3_hand

            # Check 3 or 4 cards in unbid suits.
            unbid_suits = [suit for suit in SUITS]
            openers_suit = auction[openers_call].denomination.name
            # overcallers_suit = auction[openers_call + 1].denomination.name
            unbid_suits.remove(openers_suit)
            # unbid_suits.remove(overcallers_suit)
            suit_test = True
            for suit in unbid_suits:
                if overcallers_hand.suit_holding[suit] <= 2:
                    suit_test = False
                    break
            if not suit_test:
                continue
            found = True
        return board

    def defend_weak_nt_board(self):
        """Opposition opens 1NT."""
        found = False
        board = None

        (check_bid, opener, responder) = self._opener_given_dealer(ns_opener=False)
        del responder
        overcaller = (opener + 1) % 4

        while not found:
            hand = self.generate_hand([12, 14], BALANCED_SHAPES)
            hands = {opener: hand}
            # generate a new board where E or W open 1NT.
            board = self.create_board(hands)
            board.dealer = self._dealer

            auction = self._get_auction_calls(board)
            if auction[check_bid].name != '1NT':
                found = False
            elif board.hands[overcaller].hcp < 9 or board.hands[overcaller].shape[0] < 5:
                found = False
            else:
                found = True
        return board

    def fourth_suit_forcing_board(self):
        """Generate a board to test fourth suit forcing."""
        found = False
        board = None

        (check_bid, opener, responder) = self._opener_given_dealer(ns_opener=True)
        del responder

        while not found:
            hand = self.generate_hand([12, 19])
            hands = {opener: hand}
            board = self.create_board(hands)
            board.dealer = self._dealer
            auction = self._get_auction_calls(board)

            denominations = []
            nt_bid = False
            for index, call in enumerate(auction):
                # Get a list of suits called in the auction by N/S
                if not (index + check_bid) % 2:
                    if call.is_suit_call:
                        if call.denomination not in denominations:
                            denominations.append(call.denomination)
                    elif call.is_nt:
                        nt_bid = True
                        break

                # Ensure there is no interfering bid.
                else:
                    if call.name != 'P':
                        break

            # If 3 suits bid, accept the board
            if len(denominations) == 3 and not nt_bid:
                found = True
        return board

    def respond_to_preempt_board(self):
        """Generate a board to test response to a preemptive opening."""
        found = False
        board = None

        # Get shape and points range
        shapes = [shape for shape in SHAPES if shape[0] >= 6]
        shape = self.random_shape(shapes)
        if shape[0] == 6:
            points = [6, 9]
        else:
            points = [0, 9]

        (check_bid, opener, responder) = self._opener_given_dealer(ns_opener=True)

        while not found:
            openers_hand = self.generate_hand(points, [shape])
            if openers_hand.suit_length(SUITS['C']) >= 6:
                continue
            responders_hand = self.generate_hand([14, 25], partners_hand=openers_hand)
            hands = {
                opener: openers_hand,
                responder: responders_hand,
                }
            board = self.create_board(hands)
            board.dealer = self._dealer
            auction = self._get_auction_calls(board)

            # Check first bid is valid
            call = auction[check_bid]
            if call.level in (2, 3, 4):
                found = True
        return board

    def defend_preempt_board(self):
        """Generate a board to test response to a preemptive opening."""
        found = False
        board = None

        # Get shape and points range
        shapes = [shape for shape in SHAPES if shape[0] >= 6]
        shape = self.random_shape(shapes)
        if shape[0] == 6:
            points = [6, 9]
        else:
            points = [0, 9]

        (check_bid, opener, responder) = self._opener_given_dealer(ns_opener=False)

        while not found:
            openers_hand = self.generate_hand(points, [shape])
            if openers_hand.suit_length(SUITS['C']) == 6:
                continue
            responders_hand = self.generate_hand([0, 8], partners_hand=openers_hand)
            hands = {
                opener: openers_hand,
                responder: responders_hand,
                }
            board = self.create_board(hands)
            board.dealer = self._dealer
            auction = self._get_auction_calls(board)

            # Check first bid is valid
            if check_bid:
                if auction[0].name != 'P':
                    continue
            if auction[check_bid].level in (2, 3, 4):
                found = True
        return board

    def minor_support_board(self):
        """Minor support look for NT."""
        found = False
        board = None
        (check_bid, opener, responder) = self._opener_given_dealer(ns_opener=True)
        while not found:
            openers_hand = self.generate_hand([12, 19])
            responders_min_points = 25 - openers_hand.hcp
            responders_points = [responders_min_points, 19]
            responders_hand = self.generate_hand(responders_points, partners_hand=openers_hand)
            hands = {
                opener: openers_hand,
                responder: responders_hand,
                }
            board = self.create_board(hands)
            board.dealer = self._dealer
            auction = self._get_auction_calls(board)

            # Check first bid is valid
            if check_bid:
                if auction[0].name != 'P':
                    continue
            if auction[check_bid].is_minor:
                suit = auction[check_bid].denomination.name
                if responders_hand.suit_holding[suit] >= 4:
                    found = True
        return board

    def multi_two_diamond(self):
        """Return 19-20 balanced or weak 6 card major."""
        choice = random.randint(0, 1)
        if choice == 0:
            hand = self.generate_hand([19, 20], BALANCED_SHAPES)
        else:
            found = False
            while not found:
                hand = self.generate_hand([6, 10])
                if hand.spades == 6 or hand.hearts == 6:
                    found = True
        hands = {self._first_seat(): hand}
        board = self.create_board(hands)
        return board

    def lucas_2s(self):
        """Generate hand suitable for Lucas 2 opening."""
        found = False
        while not found:
            hand = self.generate_hand([6, 10])
            if hand.spades == 5 or hand.hearts == 5:
                if hand.shape[1] == 4:
                    hands = {self._first_seat(): hand}
                    board = self.create_board(hands)
                    board.dealer = self._dealer
                    auction = self._get_auction_calls(board)
                    if board.dealer in 'NS':
                        found = True
                    else:
                        if auction[0].name == 'P':
                            found = True
        return board

    def _opener_given_dealer(self, ns_opener):
        """Return the seat indices given dealer and opener orientation."""
        # E.g if we want N or S to bid and E is dealer then the opener will be S.
        # If on the other hand W is dealer, the opener will be N.

        # check_bid returns True (1) if N/S are to be opener and E/W are dealer
        # or if E/W are to be opener and N/S are dealer
        if ns_opener:
            check_bid_orientation = ['E', 'W']
        else:
            check_bid_orientation = ['N', 'S']
        check_bid = self._dealer in check_bid_orientation

        # opener is the index of the opening hand
        # e.g. if N/S are opener and E is dealer, it returns 2 (S)
        opener = (SEATS.index(self._dealer) + check_bid) % 4
        responder = (opener + 2) % 4
        return (check_bid, opener, responder)

    def _get_opener_overcaller_board(self, ns_opener=True):
        """Return a board with suitable opener and overcaller hands."""
        openers_hand = self.generate_hand([12, 19])
        overcallers_hand = self.generate_hand([11, 19], partners_hand=openers_hand)
        # The first hand to bid gets the opening hand.
        (check_bid, opener, responder) = self._opener_given_dealer(ns_opener)
        del check_bid, responder
        overcaller = (opener + 1) % 4
        hands = {
            opener: openers_hand,
            overcaller: overcallers_hand,
        }
        board = self.create_board(hands)
        board.dealer = self._dealer
        return (board, opener)

    @staticmethod
    def _opener_is_ns(auction, openers_call):
        """Return True if N or S make the first bid."""
        for index in range(openers_call):
            if not auction[index].is_pass:
                return False
        return True

    @staticmethod
    def _opener_is_suit_at_level_one(openers_call):
        """Return True if opener's bid is a suit bid at level one."""
        if openers_call.level != 1:
            return False
        if not openers_call.is_suit_call:
            return False
        return True

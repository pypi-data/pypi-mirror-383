"""Expose the classes in the API."""
try:
    from icecream import ic, install
    ic.configureOutput(includeContext=True)
    install()
except ImportError:  # Graceful fallback if IceCream isn't installed.
    ic = lambda *a: None if not a else (a[0] if len(a) == 1 else a)  # noqa

from ._version import __version__
VERSION = __version__

from .board import Board, Trick, Contract, Auction
from .dealer import Dealer
from .dealer_solo import Dealer as DealerSolo
from .dealer_duo import Dealer as DealerDuo

SOLO_SET_HANDS = {index: item[0] for index, item in enumerate(DealerSolo().set_hands)}
DUO_SET_HANDS = {index: item[0] for index, item in enumerate(DealerDuo().set_hands)}

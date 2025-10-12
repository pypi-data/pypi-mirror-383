from .models import Group, Person, Room
from .util.search import Indexable, SearchIndex


class PersonIndex(SearchIndex, Indexable):
    """Haystack index for searching persons."""

    model = Person


class GroupIndex(SearchIndex, Indexable):
    """Haystack index for searching groups."""

    model = Group


class RoomIndex(SearchIndex, Indexable):
    """Haystack index for searching rooms."""

    model = Room

"""Pipes statistics."""
from . import Counter


class CounterLength(Counter):
    """Class for counting items with length."""

    def __init__(self, tube_length):
        """Make new tube counter with total length."""
        Counter.__init__(self)
        self.length = tube_length

    def __str__(self):
        """Text representation."""
        return "{} len: {}".format(Counter.__str__(self), self.length)

    def increase(self, tube_length):
        """Add new tube data."""
        Counter.increment(self)
        self.length += tube_length


class TubeProperty:
    """Class for one tubes property statistics."""

    def __init__(self):
        """Make new tube property."""
        self.data = {}
        self.number = 0
        self.length = 0

    def __str__(self):
        """Text representation."""
        return ''.join((
          "total_num: {} total_len: {}".format(self.number, self.length),
          '\n',
          '\n'.join(["{} {}".format(key, self.data[key]) for key in sorted(self.data.keys())]),
        ))

    def add_data(self, val, tube_length):
        """Add tube property to statistics."""
        self.number += 1
        self.length += tube_length

        if val in self.data:
            self.data[val].increase(tube_length)
        else:
            self.data[val] = CounterLength(tube_length)


class Totals:
    """Class for tubes report statistics."""

    def __init__(self):
        """Make new tube total object."""
        self.number = 0
        self.length = 0

        self.thick = TubeProperty()
        self.category = TubeProperty()
        self.types = TubeProperty()

    def __str__(self):
        """Text representation."""
        return ''.join((
          "total_num: {} total_len: {}".format(self.number, self.length),
          '\n\n',
          "thick {}".format(self.thick),
          '\n\n',
          "category {}".format(self.category),
          '\n\n',
          "types {}".format(self.types),
        ))

    def add_data(self, tube):
        """Add tube data to statistics parts."""
        self.number += 1
        self.length += tube.length

        self.thick.add_data(tube.thick, tube.length)
        self.category.add_data(tube.category, tube.length)
        self.types.add_data(tube.typ, tube.length)

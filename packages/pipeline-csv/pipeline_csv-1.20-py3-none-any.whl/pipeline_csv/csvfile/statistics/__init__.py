"""Statistics for CSV file objects."""


class Counter:
    """Class for counting items."""

    def __init__(self):
        """Make new object counter."""
        self.number = 1

    def __str__(self):
        """As text."""
        return "num: {}".format(self.number)

    def increment(self):
        """Add new tube data."""
        self.number += 1


class PropertyCounter:
    """Class for counting objects by field values."""

    def __init__(self):
        """Make new object with empty properies."""
        self.data = {}
        self.tubes = {}
        self.number = 0

    def __str__(self):
        """As text."""
        return ''.join((
          "total_num: {}".format(self.number), '\n',
          '\n'.join(["{} {}".format(key, self.data[key]) for key in sorted(self.data.keys())]),
        ))

    def tubes_with(self, val):
        """Return number of tubes with given item."""
        return len(self.tubes[val])

    def tubes_all(self):
        """Return number of tubes for all item."""
        all_pipes = {}
        for i in self.tubes.values():
            all_pipes.update(i)

        return len(all_pipes)

    def add_item(self, val, tube):
        """Add item by field value to statistics."""
        self.number += 1

        if val in self.data:
            self.data[val].increment()
            self.tubes[val][tube.number] = True
        else:
            self.data[val] = Counter()
            self.tubes[val] = {tube.number: True}

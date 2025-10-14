"""Main class for CSV file statistics."""
from . import PropertyCounter
from .pipes import Totals as TotalsPipes
from .defects import Totals as TotalsDefects


class Totals:
    """Class for overall CSV file statistics."""

    def __init__(self, pipes_class=TotalsPipes, defects_class=TotalsDefects):
        """Make instance with given custom subclasses for pipes and defects."""
        self.defects_class = defects_class
        self.pipes_class = pipes_class
        self.pipes = None
        self.liners = None
        self.markers = None
        self.start = None
        self.length = None
        self.defects = None

    def init_fill(self):
        """Create fields needed by fill method."""
        self.pipes = self.pipes_class()
        self.liners = PropertyCounter()
        self.markers = []
        self.start = None
        self.length = None

    def fill(self, deftable, warns):
        """Make statistics for given deftable."""
        self.init_fill()
        last_tube = None

        for tube in deftable.get_tubes(warns):
            if last_tube is None:
                self.start = tube.dist
            last_tube = tube
            self.add_data(tube)
            for item in tube.lineobjects:
                if item.marker == item.get_bool(True):
                    self.markers.append(item)

        self.length = last_tube.dist + int(last_tube.length)
        self.defects = self.defects_class(self.start, self.length, self.markers)

        for tube in deftable.get_tubes():
            self.defects.add_data(tube, warns)

    def __str__(self):
        """Text representation."""
        return ''.join((
          "Tubes: {}".format(self.pipes),
          '\n\n',
          "Liners: {}".format(self.liners),
          '\n\n',
          "Defects: {}".format(self.defects),
        ))

    def add_data(self, tube):
        """Add tube data to report statistics."""
        for obj in tube.lineobjects:
            self.liners.add_item(int(obj.object_code), tube)

        self.pipes.add_data(tube)

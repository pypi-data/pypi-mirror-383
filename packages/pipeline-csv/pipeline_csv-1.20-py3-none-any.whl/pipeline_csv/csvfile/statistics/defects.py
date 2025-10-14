"""Defects statistics."""
from . import PropertyCounter

GRADE_OVER_MAX = "OVER_MAX"


def stub_for_child(cls, method_name):
    """Stub for child implementation."""
    raise NotImplementedError("{}: {} not implemented".format(cls.__class__.__name__, method_name))


def get_hour(minutes):
    """Return hour for given minutes."""
    hour = int(minutes / 60)
    minute = minutes % 60
    if minute > 30:
        hour += 1
    if hour >= 12:
        hour -= 12

    return hour


def at_hours(minutes_start, minutes_end):
    """Return list of hours where segment present."""
    if minutes_start < 0:
        return []

    start = get_hour(minutes_start)
    hours = [start]

    if (minutes_end is None) or (minutes_end < 0):
        return hours

    end = get_hour(minutes_end)
    if start == end:
        return hours

    minutes_start += 60
    curr = get_hour(minutes_start)

    while curr != end:
        hours.append(curr)
        minutes_start += 60
        curr = get_hour(minutes_start)

    hours.append(end)

    return hours


class Angles:
    """Class for counting defects by angles."""

    def __init__(self):
        """Make new defect counter by angles object."""
        self.hours = {i: 0 for i in range(12)}

    def add_data(self, defect):
        """Add defect to angle statistics."""
        if defect.row.orient1:
            for i in at_hours(defect.row.orient1, defect.row.orient2):
                self.hours[i] += 1


class GradeBase:
    """Class for counting defects by grade."""

    grades = []

    def __init__(self, grades=None):
        """Make new defect counter by grade object."""
        if grades is not None:
            self.grades = grades

        self.number = 0
        self.data = {}
        self.grade_init()

    def grade_init(self):
        """Stub for chield classes."""
        stub_for_child(self, "grade_init")

    def get_grade(self, _defect, _tube):
        """Stub for chield classes."""
        stub_for_child(self, "get_grade")

    def add_item(self, _grade, _defect, _tube):
        """Stub for chield classes."""
        stub_for_child(self, "add_item")

    def add_data(self, defect):
        """Add defect with grade to statistics."""
        val = self.get_grade(defect, defect.pipe) or 0
        self.number += 1
        for grade in self.grades:
            if float(val) < float(grade):
                self.add_item(grade, defect, defect.pipe)
                return

        self.add_item(GRADE_OVER_MAX, defect, defect.pipe)

    def extended_number(self, _grade):
        """Additional number for grade."""
        return 0


class GradeHolder(GradeBase):
    """Class for collecting defects divided by grades."""

    def grade_init(self):
        """Init containers for defects."""
        self.data = {i: [] for i in self.grades}
        self.data[GRADE_OVER_MAX] = []

    def add_item(self, grade, defect, _tube):
        """Add to container."""
        self.data[grade].append(defect)


class SingleDist(GradeHolder):
    """Class for collecting items without grades."""

    single_grade = True
    grades = [single_grade]

    def add_data(self, defect):
        """Add defect with fixed grade to statistics."""
        self.number += 1
        self.add_item(self.single_grade, defect, defect.pipe)


class GradeTube(GradeBase):
    """Class for counting defects at tubes by grade."""

    def grade_init(self):
        """Init counters ant tubes data."""
        self.data = {i: 0 for i in self.grades}
        self.data[GRADE_OVER_MAX] = 0

        self.tubes = {i: {} for i in self.grades}
        self.tubes[GRADE_OVER_MAX] = {}

    def add_item(self, grade, _defect, tube):
        """Add to counter and tubes."""
        self.data[grade] += 1
        self.tubes[grade][tube.number] = True

    def __str__(self):
        """Text representation."""
        return "total_num: {}".format(self.number)

    def pipes_with_grade(self, grade):
        """Return number of pipes for grade."""
        return len(self.tubes[grade])


class Dents(GradeTube):
    """Class for counting dents by grade."""

    grades = [10]

    def get_grade(self, defect, _tube):
        """Return percent for dent depth from diameter."""
        return defect.depth_percent or 0


class Depth(GradeTube):
    """Class for counting defects by depth."""

    grades = [80]

    def __init__(self, grades=None):
        """Make new metal losses object."""
        super().__init__(grades=grades)
        self.max_percent = 0

    def add_item(self, grade, defect, tube):
        """Add to container."""
        super().add_item(grade, defect, tube)
        self.max_percent = max((defect.depth_percent or 0), self.max_percent)

    def get_grade(self, defect, _tube):
        """Return depth in percents for defect."""
        return defect.depth_percent or 0


class Dist(GradeTube):
    """Class for counting defects by distance."""

    grades = []
    part_length = 0

    def __init__(self, total_length, parts_number=40):
        """Make new defect counter object."""
        self.parts_number = parts_number
        self.part_length = int(total_length / self.parts_number)
        self.grades = [i * self.part_length for i in range(self.parts_number)]
        self.names = {}
        GradeTube.__init__(self)

    def valves_init(self, markers):
        """Generate distance grades for valves."""
        self.grades = []
        self.names = {}
        for i in markers:
            if i.is_valve:
                self.grades.append(i.dist)
                self.names[i.dist] = i.object_name

        GradeTube.__init__(self)


class DistDanger(Dist):
    """Class for counting defects by distance with stacked danger levels."""

    def add_data(self, defect):
        """Add defect with distance to statistics."""
        val = defect.row.dist_od
        self.number += 1

        for grade in self.grades:
            if int(val) < grade:
                self.data[grade] += 1
                return

        self.data[GRADE_OVER_MAX] += 1


class DangerValve(DistDanger):
    """Class for counting defects with stacked danger levels between valves."""

    def __init__(self, markers):  # pylint: disable=super-init-not-called
        """Make new defect counter object."""
        self.valves_init(markers)


class PropertyCodeCounter(PropertyCounter):
    """Class for property field with code and text."""

    def __init__(self):
        """Make new property with code object."""
        super().__init__()
        self.code2text = {}

    def add_code(self, text, code, tube):
        """Add item wit text and code (dent)."""
        self.add_item(code, tube)
        self.code2text[code] = text


class DistBarStacked:
    """Counter by given property."""

    def __init__(self):
        """Count by prop."""
        self.number = 0
        self.data = {}

    def __str__(self):
        """Return as text."""
        return "all {} data {}".format(self.number, self.data)

    def add_data(self, item, prop):
        """Add item with by property."""
        val = prop.get_val(item)
        if val not in self.data:
            self.data[val] = 0
        self.data[val] += 1
        self.number += 1


class DistStacked:  # pylint: disable=too-many-instance-attributes
    """Class for stacked items bars."""

    def __init__(self, start, length, bars_num):
        """Defect bars by dist with data divided by given prop_func."""
        self.number = 0
        self.start = start
        self.length = length

        self.bar_length = float(length) / bars_num
        self.data = {self.start + i * self.bar_length: DistBarStacked() for i in range(bars_num)}
        self.nodes = list(sorted(self.data.keys()))
        self.before_start = []
        self.after_end = []

    def __str__(self):
        """Return as text."""
        return '\n'.join(["total {}".format(self.number)] + [
          "{}-{}: {}".format(int(i), int(i + self.bar_length), str(self.data[i])) for i in self.nodes
        ])

    def get_val(self, _item):
        """Return property value for count."""
        stub_for_child(self, "get_val")

    def get_node(self, dist):
        """Return statr point of segment (node) for given dist."""
        if dist >= self.nodes[-1]:
            return self.nodes[-1]

        first = 0
        second = len(self.nodes) - 1
        while (second - first) > 1:
            indx = first + int((second - first) / 2)
            # input('{} ({}) <- {} ({}) -> {} ({})'.format(
            #   first, self.nodes[first],
            #   indx, self.nodes[indx],
            #   second, self.nodes[second],
            # ))
            val = self.nodes[indx]
            if val == dist:
                return val
            if val < dist:
                first = indx
            else:
                second = indx

        return self.nodes[first]

    def add_data(self, item):
        """Add item with distance."""
        if item.row.dist < self.start:
            self.before_start.append(item)
            return

        if item.row.dist > (self.start + self.length):
            self.after_end.append(item)
            return

        self.data[self.get_node(item.row.dist)].add_data(item, self)
        self.number += 1


class DistWallside(DistStacked):
    """Class for stacked defect bars with wallside parts."""

    def get_val(self, item):
        """Return wallside property value of defect."""
        return int(item.row.type_def)


class DistSingle(DistStacked):
    """Class for single level defect bars."""

    def get_val(self, _item):
        """Return constant for single level."""
        return True


class Totals:
    """Class for defects statistic."""

    def __init__(self, start, length, markers):
        """Make new defects total object."""
        self.number = 0
        self.start = start
        self.length = length
        self.markers = markers

        self.base_types = PropertyCounter()
        self.base_wallside = PropertyCounter()
        self.base_angle_anomalies = Angles()

    def __str__(self):
        """Text representation."""
        return ''.join((
          "total_num: {}".format(self.number),
          '\n\n', "types {}".format(self.base_types),
          '\n\n', "wallside {}".format(self.base_wallside),
        ))

    def add_defect(self, defect, tube, _warns):
        """Add defect to statistics."""
        row = defect.row
        self.base_wallside.add_item(int(row.type_def), tube)
        self.base_types.add_item(int(row.object_code), tube)
        self.base_angle_anomalies.add_data(defect)

    def add_data(self, tube, warns):
        """Add tube defects to statistics."""
        for defect in tube.defects:
            self.number += 1
            self.add_defect(defect, tube, warns)

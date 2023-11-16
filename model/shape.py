from _decimal import Decimal


class Point:
    def __init__(self, latitude: Decimal, longitude: Decimal):
        self.latitude = latitude
        self.longitude = longitude

    def __eq__(self, other):
        if not isinstance(other, Point):
            return False
        return self.latitude == other.latitude and self.longitude == other.longitude


class Line:
    def __init__(self, point1: Point, point2: Point):
        self.point1 = point1
        self.point2 = point2

    def __eq__(self, other):
        if not isinstance(other, Line):
            return False
        return ((self.point1 == other.point1 and self.point2 == other.point2)
                or (self.point2 == other.point1 and self.point1 == other.point2))

    def contains(self, point: Point) -> bool:
        latitudes = self.get_latitudes()
        longitudes = self.get_longitudes()
        return ((point.latitude == self.point1.latitude == self.point2.latitude
                 and min(longitudes) < point.longitude < max(longitudes))
                or (point.longitude == self.point1.longitude == self.point2.longitude
                    and min(latitudes) < point.latitude < max(latitudes)))

    def get_points(self) -> set:
        return {self.point1, self.point2}

    def get_latitudes(self) -> set:
        return {self.point1.latitude, self.point2.latitude}

    def get_longitudes(self) -> set:
        return {self.point1.longitude, self.point2.longitude}


class Box:
    def __init__(self, lower: Point, upper: Point):
        self.lower = lower
        self.upper = upper

    def __eq__(self, other):
        if not isinstance(other, Box):
            return False
        return self.lower == other.lower and self.upper == other.upper

    def get_latitudes(self) -> [Decimal]:
        return {self.lower.latitude, self.upper.latitude}

    def get_longitudes(self) -> [Decimal]:
        return {self.lower.longitude, self.upper.longitude}

    def get_vertices(self) -> [Point]:
        return [self.lower, Point(self.lower.latitude, self.upper.longitude),
                self.upper, Point(self.upper.latitude, self.lower.longitude)]

    def get_lines(self) -> [Line]:
        lines = list()
        vertices = self.get_vertices()
        vertex_count = len(vertices)
        for i in range(0, vertex_count):
            lines.append(Line(vertices[i], vertices[(i + 1) % vertex_count]))
        return lines

    def contains_point(self, point: Point) -> bool:
        return (self.lower.latitude <= point.latitude <= self.upper.latitude
                and self.lower.longitude <= point.longitude <= self.upper.longitude)

    def contains_line(self, line: Line) -> bool:
        if not (self.contains_point(line.point1) or self.contains_point(line.point2)):
            return False
        line_lats = line.get_latitudes()
        line_longs = line.get_longitudes()
        if ((len(line_lats) == 1 and list(line_lats)[0] in self.get_latitudes())
                or (len(line_longs) == 1 and list(line_longs)[0] in self.get_longitudes())):
            return False
        return True

    def contains_box(self, other) -> bool:
        if not isinstance(other, Box):
            return False
        return self.contains_point(other.lower) and self.contains_point(other.upper)

    def find_vertices_within(self, other) -> [Point]:
        if not isinstance(other, Box):
            return list()
        vertices = list()
        for vertex in self.get_vertices():
            if other.contains_point(vertex):
                vertices.append(vertex)
        return vertices

    def overlaps(self, other) -> bool:
        if not isinstance(other, Box):
            return False
        if self == other or self.contains_box(other) or other.contains_box(self):
            return True
        for line in self.get_lines():
            if other.contains_line(line):
                return True
        return False



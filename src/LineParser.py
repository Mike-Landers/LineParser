# Observations about the problem:
# 1. this is inherently an order n^2 time complexity problem since the graph of points is fully connected
# 2. vertical lines are possible, but their representation in a standard 2d coordinate system results in a divide by 0
#    - I'm supporting the detection of vertical lines
# 3. floating point imprecision issues need to be dealt with since the input reads decimal fp numbers
#    - I'm handling this using the Fraction library by storing decimal floating point numbers as exact fractions
#
# Assumptions:
# 1. input file is correctly formatted, and exists
# 2. input csv and output csv file paths are hardcoded vs reading csv file paths from stdin

# Strategy:
# 1. parse points from csv file, de-duping with a set since duplicate points don't mean anything in this context
# 2. convert points into lines: approximately (n^2)/2 iterations
#    - populate a dictionary of lines to set of points and a list of 3-point lines
# 3. convert dictionary of lines to set of points into list of strings in output csv format
# 4. create output csv from list of strings

from fractions import Fraction


class Point:
    def __init__(self, x1, y1):
        self.x = x1
        self.y = y1

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.x == other.x and self.y == other.y
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.x, self.y))

    def to_string(self):
        return '{},{}'.format(float(self.x), float(self.y))


class Line:
    def __init__(self, pt1, pt2):
        self.m = (pt1.y - pt2.y)/(pt1.x - pt2.x)
        self.b = pt1.y - self.m * pt1.x

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.m == other.m and self.b == other.b
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.m, self.b))

    def to_string(self):
        return 'y = {} x + {}'.format(float(self.m), float(self.b))


class LineParser:
    def __init__(self):
        self.points = set()
        self.lines_to_points = {}
        self.vertical_x_to_y = {}
        self.three_point_lines = set()

    # convert dictionary of lines to set of points into list of strings in output csv format
    def get_3_point_lines(self, file_path):
        self.parse_points_from_csv(file_path)
        self.get_lines_from_points()

        results = []
        index = 1

        # add non-vertical 3 point lines
        for line in self.three_point_lines:
            line.to_string()
            return_line = str(index)
            index += 1
            for point in self.lines_to_points[line]:
                return_line += ',' + point.to_string()
            results.append(return_line)

        # add vertical 3 point lines
        for x in self.vertical_x_to_y:
            y_list = self.vertical_x_to_y[x]
            if len(y_list) >= 3:
                return_line = str(index)
                index += 1
                for y in y_list:
                    return_line += ',{},{}'.format(float(x), float(y))
                results.append(return_line)

        return results

    # convert points into lines: approximately (n^2)/2 iterations
    def get_lines_from_points(self):
        start_index = 1
        point_list = list(self.points)
        for pt1 in point_list:
            # start_index increments after each iteration, resulting in approximately (n^2)/2 iterations
            for i in xrange(start_index, len(point_list)):
                pt2 = point_list[i]

                # if the denominator is not 0 (this line is not a vertical line)
                if pt1.x - pt2.x != 0:
                    line = Line(pt1, pt2)

                    if line in self.lines_to_points:
                        self.lines_to_points[line].add(pt1)
                        self.lines_to_points[line].add(pt2)
                        if len(self.lines_to_points[line]) >= 3 and line not in self.three_point_lines:
                            self.three_point_lines.add(line)
                    else:
                        self.lines_to_points[line] = set()
                        self.lines_to_points[line].add(pt1)
                        self.lines_to_points[line].add(pt2)
                # else handle the vertical line
                else:
                    if pt2.x in self.vertical_x_to_y:
                        self.vertical_x_to_y[pt2.x].add(pt1.y)
                        self.vertical_x_to_y[pt2.x].add(pt2.y)
                    else:
                        self.vertical_x_to_y[pt2.x] = set()
                        self.vertical_x_to_y[pt2.x].add(pt1.y)
                        self.vertical_x_to_y[pt2.x].add(pt2.y)
            start_index += 1

    # parse points from file, de-duping with a set since duplicate points don't mean anything
    def parse_points_from_csv(self, file_path):
        try:
            fo = open(file_path, "rb+")
            lines = fo.readlines()
            lines = [x.strip() for x in lines]
            fo.close()

            # create dictionary of Lines to list of Points
            for line in lines:
                x1, y1 = line.split(',')
                self.points.add(Point(Fraction(x1), Fraction(y1)))

        except Exception as e:
            print(e.message)

    # create output csv from list of strings
    def write_lines_to_csv(self, lines, file_path):
        try:
            fo = open(file_path, "wb+")
            for line in lines:
                fo.write(line + '\n')
            fo.close()
        except Exception as e:
            print(e.message)


# run a simple test using test_input.csv
parser = LineParser()
three_pt_lines = parser.get_3_point_lines('test_input.csv')
for item in three_pt_lines:
    print item
parser.write_lines_to_csv(three_pt_lines, 'test_output.csv')

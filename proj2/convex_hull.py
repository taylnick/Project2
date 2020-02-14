from proj2.which_pyqt import PYQT_VER

if PYQT_VER == 'PYQT5':
    from PyQt5.QtCore import QLineF, QPointF, QObject
# elif PYQT_VER == 'PYQT4':
#     from PyQt4.QtCore import QLineF, QPointF, QObject
else:
    raise Exception('Unsupported Version of PyQt: {}'.format(PYQT_VER))

import time

# Some global color constants that might be useful
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Global variable that controls the speed of the recursion automation, in seconds
#
PAUSE = 0.5


#
# This is the class you have to complete.
#
class ConvexHullSolver(QObject):

    # Class constructor
    def __init__(self):
        super().__init__()
        self.pause = False

    # Some helper methods that make calls to the GUI, allowing us to send updates
    # to be displayed.

    def showTangent(self, line, color):
        self.view.addLines(line, color)
        if self.pause:
            time.sleep(PAUSE)

    def eraseTangent(self, line):
        self.view.clearLines(line)

    def blinkTangent(self, line, color):
        self.showTangent(line, color)
        self.eraseTangent(line)

    def showHull(self, polygon, color):
        self.view.addLines(polygon, color)
        if self.pause:
            time.sleep(PAUSE)

    def eraseHull(self, polygon):
        self.view.clearLines(polygon)

    def showText(self, text):
        self.view.displayStatusText(text)

    # This is the method that gets called by the GUI and actually executes
    # the finding of the hull
    def compute_hull(self, points, pause, view):
        self.pause = pause
        self.view = view
        assert (type(points) == list and type(points[0]) == QPointF)

        t1 = time.time()
        points.sort(key=lambda points: points.x())
        # TODO: SORT THE POINTS BY INCREASING X-VALUE
        t2 = time.time()

        t3 = time.time()
        # this is a dummy polygon of the first 3 unsorted points
        hull = self.find_convex_hull(points)
        polygon = self.make_poly(hull)
        # polygon = [QLineF(points[i],points[(i+1)%3]) for i in range(3)]
        # polygon = self.find_convex_hull(points)
        # TODO: REPLACE THE LINE ABOVE WITH A CALL TO YOUR DIVIDE-AND-CONQUER CONVEX HULL SOLVER
        t4 = time.time()

        # when passing lines to the display, pass a list of QLineF objects.  Each QLineF
        # object can be created with two QPointF objects corresponding to the endpoints
        self.showHull(polygon, RED)
        self.showText('Time Elapsed (Convex Hull): {:3.3f} sec'.format(t4 - t3))

    def find_convex_hull(self, points):
        length = len(points)
        if length == 1:
            return points
        midpoint = int(length / 2)
        leftHull = self.find_convex_hull(points[0:midpoint])
        rightHull = self.find_convex_hull(points[midpoint:])
        newHull = self.merge(leftHull, rightHull)
        self.show_poly(leftHull, GREEN)
        self.show_poly(rightHull, RED)
        self.show_poly(newHull, BLUE)

        self.eraseHull(leftHull)
        self.eraseHull(rightHull)
        self.eraseHull(newHull)
        return newHull

    def show_poly(self, hull, color):
        poly = self.make_poly(hull)
        self.showHull(poly, color)

    def make_poly(self, hull):
        poly = [QLineF(hull[i], hull[(i + 1) % len(hull)]) for i in range(len(hull))]
        return poly

    def merge(self, left, right):
        lt = left[0]
        lb = left[0]
        rt = right[0]
        rb = right[0]

        l_len = len(left)
        r_len = len(right)

        rt_found = False
        lt_found = False
        rb_found = False
        lb_found = False
        # find left top and bottom
        while True:
            while not rt_found or not lt_found:
                for p in left:
                    if self.find_slope(rt, p) < self.find_slope(rt, lt):
                        lt = p
                        lt_found = True
                        rt_found = False
                    elif self.find_slope(rt, p) >= self.find_slope(rt, lt):
                        lt_found = True
                for q in right:
                    if self.find_slope(q, lt) > self.find_slope(rt, lt):
                        rt = q
                        lt_found = False
                        rt_found = True
                    elif self.find_slope(q, lt) <= self.find_slope(rt, lt):
                        rt_found = True

            while not lb_found or not rb_found:
                # find lbottom
                for p in left:
                    if self.find_slope(rb, p) > self.find_slope(rb, lb):
                        lb = p
                        lb_found = True
                        rb_found = False
                    elif self.find_slope(rb, p) <= self.find_slope(rb, lb):
                        lb_found = True
                for q in right:
                    # find rbottom using lbottom
                    if self.find_slope(q, lb) < self.find_slope(rb, lb):
                        rb = q
                        rb_found = True
                        lb_found = False
                    elif self.find_slope(q, lb) >= self.find_slope(rb, lb):
                        rb_found = True
            if lb_found and rb_found and rt_found and lt_found:
                break

        lbegin = left.index(lb)
        lend = left.index(lt)
        if lend > lbegin:
            new_left = left[lbegin: lend + 1]
        else:
            # new_left = [left[i % l_len] for i in range(lbegin, l_len + lend + 1)]
            new_left = left[lbegin:] + left[:lend + 1]
        # new_right = right[right.index(rt): right.index(rb) + 1]

        rbegin = right.index(rt)
        rend = right.index(rb)
        if rend > rbegin:
            new_right = right[rbegin: rend + 1]
        else:
            # new_right = [right[i % r_len] for i in range(rbegin, r_len + rend + 1)]
            new_right = right[rbegin:] + right[:rend + 1]
        # poly = [QLineF(hull[i], hull[(i + 1) % len(hull)]) for i in range(len(hull))]
        # new_right = [[right[i + 1 % r_len] for i in range(right.index(rt), right.index(rb))]]
        return new_left + new_right

    def find_slope(self, p1, p2):
        # line = QLineF(p1, p2)
        # angle = line.angle()
        slope = (p2.y() - p1.y()) / (p2.x() - p1.x())
        return slope

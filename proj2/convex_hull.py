from proj2.which_pyqt import PYQT_VER

if PYQT_VER == 'PYQT5':
    from PyQt5.QtCore import QLineF, QPointF, QObject
elif PYQT_VER == 'PYQT4':
    from PyQt4.QtCore import QLineF, QPointF, QObject
else:
    raise Exception('Unsupported Version of PyQt: {}'.format(PYQT_VER))

import time

# Some global color constants that might be useful
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Global variable that controls the speed of the recursion automation, in seconds
#
PAUSE = 0.25


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
        polygon = [QLineF(hull[i],hull[(i+1)%len(hull)]) for i in range(len(hull))]
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
        poly = [QLineF(newHull[i],newHull[(i+1)%len(newHull)]) for i in range(len(newHull))]
        self.showHull(poly, color=BLUE)
        return newHull

    def merge(self, left, right):
        ltop = left[-1]
        lbottom = left[-1]
        rtop = right[0]
        rbottom = right[0]

        # find left top and bottom
        if len(left) > 2:
            for i in left:
                if i.x() < ltop.x() and i.y() > ltop.y():
                    temp = ltop
                    ltop = i
                    if temp != lbottom:
                        left.remove(temp)
                elif i.x() < lbottom.x() and i.y() < lbottom.y():
                    temp = lbottom
                    lbottom = i
                    left.remove(temp)

        # find right top and bottom
        if len(right) > 2:
            for i in right:
                if i.x() > rtop.x() and i.y() > rtop.y():
                    temp = rtop
                    rtop = i
                    if temp != rbottom:
                        right.remove(temp)
                elif i.x() > rbottom.x() and i.y() < rbottom.y():
                    temp = rbottom
                    rbottom = i
                    right.remove(temp)

        return left + right

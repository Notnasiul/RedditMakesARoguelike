
class Node:
    def __init__(self, value, point):
        self.value = value
        self.point = point
        self.parent = None
        self.H = 0
        self.G = 0

    def move_cost(self, other):
        return 0 if self.value == '.' else 1


def children(point, grid):
    x, y = point.point
    links = [grid[d[0]][d[1]]
             for d in [(x-1, y), (x, y - 1), (x, y + 1), (x+1, y)]]
    return [link for link in links if link.value != '%']



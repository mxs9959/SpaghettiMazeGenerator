class Node:
    def __init__(self, x, y, is_start=False, is_end=False):
        self.x, self.y = x, y
        self.is_start = is_start
        self.is_end = is_end
    def __repr__(self):
        return f"Node({self.x}, {self.y})"


class Edge:
    def __init__(self, node1, node2, color="white"):
        if not (isinstance(node1, Node) and isinstance(node2, Node)):
            raise TypeError("Both arguments must be instances of Node.")
        self.node1, self.node2 = node1, node2
        self.color = color

    def is_sub_edge(self, other):
        # Check if the edges are on the same line (either horizontal or vertical)
        is_horizontal_line = (self.node1.y == self.node2.y == other.node1.y == other.node2.y)
        is_vertical_line = (self.node1.x == self.node2.x == other.node1.x == other.node2.x)

        if not (is_horizontal_line or is_vertical_line):
            return False

        # Determine the shared coordinate and the ranges
        if is_horizontal_line:
            self_range = sorted([self.node1.x, self.node2.x])
            other_range = sorted([other.node1.x, other.node2.x])
        else:  # vertical line
            self_range = sorted([self.node1.y, self.node2.y])
            other_range = sorted([other.node1.y, other.node2.y])

        # Check for overlap
        return not (self_range[1] <= other_range[0] or self_range[0] >= other_range[1])
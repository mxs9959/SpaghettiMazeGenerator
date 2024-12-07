# File: node.py
class Node:
    """
    Represents a single node in the maze grid.

    Attributes:
        x (int): X-coordinate of the node in the grid
        y (int): Y-coordinate of the node in the grid
    """
    def __init__(self, x, y):
        # Store the node's coordinates
        self.x = x
        self.y = y

class Edge:
    def __init__(self, node1, node2):
        if not isinstance(node1, Node) or not isinstance(node2, Node):
            raise TypeError("Both arguments must be instances of Node.")
        self.node1 = node1
        self.node2 = node2

    def connects(self):
        return {self.node1, self.node2}  # Return a set for easy comparison

    def is_sub_edge(self, other):
        # Check if all nodes share either x or y coordinate
        if not (
                self.node1.x == other.node1.x == self.node2.x == other.node2.x
                or self.node1.y == other.node1.y == self.node2.y == other.node2.y
        ):
            return False

        # Determine the shared coordinate (x or y)
        if self.node1.x == other.node1.x:  # x is shared
            # Check if the ranges of y-coordinates overlap
            self_range = sorted([self.node1.y, self.node2.y])
            other_range = sorted([other.node1.y, other.node2.y])
            return not (self_range[1] <= other_range[0] or self_range[0] >= other_range[1])
        elif self.node1.y == other.node1.y:  # y is shared
            # Check if the ranges of x-coordinates overlap
            self_range = sorted([self.node1.x, self.node2.x])
            other_range = sorted([other.node1.x, other.node2.x])
            return not (self_range[1] <= other_range[0] or self_range[0] >= other_range[1])

        return False
import random
from node import Edge
import time

class MazeAlgorithm:
    def __init__(self, canvas, width, height, master):
        # Store canvas and grid parameters
        self.canvas = canvas
        self.width = width
        self.height = height
        self.master = master
        # Calculate cell dimensions based on canvas size
        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()
        self.cell_width = canvas_width // width
        self.cell_height = canvas_height // height
        self.edges = []
        self.visited = set()
        self.directions = []
        for i in range(-width//4, width//4):
            self.directions.append((i, 0))
        for j in range(-height//4, height//4):
            self.directions.append((0, j))
    def get_unvisited_neighbors(self, node, grid):
        neighbors = []
        # Possible movement directions: Down, Right, Up, Left
        random.shuffle(self.directions)
        # Check each direction for valid, unvisited neighbors
        for dx, dy in self.directions:
            new_x, new_y = node.x + dx, node.y + dy
            # Ensure neighbor is within grid and not visited
            if (0 <= new_x < self.width and 0 <= new_y < self.height and
                    grid[new_y][new_x] not in self.visited and self.add_edge(grid[new_y][new_x], node)):
                neighbors.append(grid[new_y][new_x])
        return neighbors

    def generate_maze(self, grid, speed_var):
        # Identify start and end nodes
        start_node = grid[0][0]
        end_node = grid[self.height-1][self.width-1]
        # Tracking sets and list
        self.visited = set()
        path = []

        def dfs(current_node):
            # Slight delay for visualization
            time.sleep(speed_var.get())
            self.master.update()
            # Mark node as visited and add to path
            self.visited.add(current_node)
            path.append(current_node)
            # Draw path to previous node
            if len(path) > 1:
                prev_node = path[-2]
                self.animate_rectangle(self.canvas, prev_node, current_node, self.cell_width//2, speed_var.get())
            # Explore unvisited neighbors
            neighbors = self.get_unvisited_neighbors(current_node, grid)
            for neighbor in neighbors:
                if neighbor not in self.visited:
                    if len(path) < 5 or random.random() < 0.75:
                        dfs(neighbor)
            # Backtrack
            path.pop()
        # Start depth-first search from top-left corner
        dfs(start_node)
        return start_node, end_node

    def draw_path(self, x1, y1, x2, y2):
        x1 *= self.cell_width
        y1 *= self.cell_height
        x2 *= self.cell_width
        y2 *= self.cell_height
        x1 += self.cell_width//2
        y1 += self.cell_height//2
        x2 += self.cell_width//2
        y2 += self.cell_height//2
        w = 0.45*min(self.cell_height, self.cell_width)

        if x1 == x2:  # Vertical case
            white_x1 = x1 - w // 8
            white_x2 = x1 + w // 8
            self.canvas.create_rectangle(white_x1, y1, white_x2, y2, fill="white", outline="white")
        elif y1 == y2:  # Horizontal case
            white_y1 = y1 - w // 8
            white_y2 = y1 + w // 8
            self.canvas.create_rectangle(x1, white_y1, x2, white_y2, fill="white", outline="white")

    def add_edge(self, node1, node2):
        new_edge = Edge(node1, node2)
        for edge in self.edges:
            if edge.is_sub_edge(new_edge) or new_edge.is_sub_edge(edge):
                return False  # Edge already exists
        self.edges.append(new_edge)
        return True

    def animate_rectangle(self, canvas, node1, node2, width, delay):
        black_border = 3
        mag_d = 5 #Adjusts drawing speed
        x1, y1 = node1.x*self.cell_width+self.cell_width/2, node1.y*self.cell_width+self.cell_width/2
        x2, y2 = node2.x*self.cell_width+self.cell_width/2, node2.y*self.cell_width+self.cell_width/2

        # Draw start and end squares
        canvas.create_rectangle(
            x1 - width // 2+black_border, y1 - width // 2+black_border, x1 + width // 2-black_border, y1 + width // 2-black_border,
            fill="white", outline=""
        )
        canvas.create_rectangle(
            x2 - width // 2 +black_border, y2 - width // 2+black_border, x2 + width // 2-black_border, y2 + width // 2-black_border,
            fill="blue", outline=""
        )
        canvas.update()

        # Determine the step direction
        dx = mag_d if x2 > x1 else -mag_d if x2 < x1 else 0
        dy = mag_d if y2 > y1 else -mag_d if y2 < y1 else 0

        # Current position for animation
        current_x, current_y = x1, y1

        while current_x != x2 or current_y != y2:
                # Draw the black rectangle behind the white rectangle
            if dx==0:
                if is_between(current_x, x1, x2, self.cell_width//5) or is_between(current_y, y1, y2, self.cell_width//5):
                    self.canvas.create_rectangle(
                        current_x - width // 2, current_y,
                        current_x + width // 2, current_y + dy,
                        fill="black", outline=""
                    )
                # Draw the white rectangle on top
                self.canvas.create_rectangle(
                    current_x - (width // 2 - black_border), current_y,
                    current_x + (width // 2 - black_border), current_y + dy,
                    fill="white", outline=""
                )
            else:
                if is_between(current_x, x1, x2, self.cell_width//5) or is_between(current_y, y1, y2, self.cell_width//5):
                    canvas.create_rectangle(
                        current_x, current_y - width // 2,
                        current_x + dx, current_y + width // 2,
                        fill="black", outline=""
                    )
                # Draw the white rectangle on top
                canvas.create_rectangle(
                    current_x, current_y - (width // 2 - black_border),
                    current_x+dx, current_y + (width // 2 - black_border),
                    fill="white", outline=""
                )
            canvas.update()

            # Move to the next position
            current_x += dx
            current_y += dy

            # Add a delay for animation speed
            #time.sleep(delay/100000)

        canvas.create_rectangle(
            x2 - width // 2, y2 - width // 2, x2 + width // 2, y2 + width // 2,
            fill="black", outline=""
        )
        if dx>0 or dy>0:
            bb = black_border
            nbb = 0
        else:
            bb = 0
            nbb = -black_border
        if dx == 0:
            canvas.create_rectangle(
                x2 - width // 2 + black_border, y2 - width//2 -nbb, x2 + width // 2-black_border, y2 + width // 2 - bb,
                fill="white", outline=""
            )
        else:
            canvas.create_rectangle(
                x2 - width // 2 - nbb, y2 - width // 2+black_border, x2 + width // 2 - bb, y2 + width // 2-black_border,
                fill="white", outline=""
            )
        canvas.update()

def is_between(value, bound1, bound2, margin):
    """
    Checks if a value falls between two other values, inclusive.

    Args:
        value (float or int): The value to check.
        bound1 (float or int): One boundary value.
        bound2 (float or int): The other boundary value.

    Returns:
        bool: True if the value is between or equal to the boundaries, False otherwise.
    """
    lower_bound = min(bound1, bound2)
    upper_bound = max(bound1, bound2)
    return lower_bound+margin <= value <= upper_bound-margin

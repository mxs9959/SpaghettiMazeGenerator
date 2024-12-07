import random
import time
from node import Edge

class MazeAlgorithm:
    def __init__(self, canvas, width, height, master, canvas_width=None, canvas_height=None):
        self.canvas = canvas
        self.width, self.height = width, height
        self.master = master

        # Use provided canvas dimensions or default to canvas's current width/height
        canvas_width = canvas_width or canvas.winfo_width()
        canvas_height = canvas_height or canvas.winfo_height()

        # Adjust cell size to fit entire maze in canvas
        self.cell_width = min(canvas_width // width, canvas_height // height)
        self.cell_height = self.cell_width

        # Center the maze in the canvas
        self.offset_x = (canvas_width - (self.cell_width * width)) // 2
        self.offset_y = (canvas_height - (self.cell_height * height)) // 2

        self.edges = []
        self.visited = set()

        # Corrected directions initialization
        self.directions = [
                              (dx, 0) for dx in range(-width//4, width//4)
                          ] + [
                              (0, dy) for dy in range(-height//4, height//4)
                          ]

    def get_unvisited_neighbors(self, node, grid):
        random.shuffle(self.directions)
        return [
            grid[new_y][new_x] for dx, dy in self.directions
            if (0 <= (new_x := node.x + dx) < self.width and
                0 <= (new_y := node.y + dy) < self.height and
                grid[new_y][new_x] not in self.visited and
                self.add_edge(grid[new_y][new_x], node))
        ]

    def generate_maze(self, grid, speed_var):
        # Randomly select start and end nodes on opposite edges
        start_side = random.choice(['top', 'bottom', 'left', 'right'])
        end_side = {'top': 'bottom', 'bottom': 'top', 'left': 'right', 'right': 'left'}[start_side]

        # Select start node
        if start_side == 'top':
            start_node = grid[0][random.randint(0, self.width-1)]
        elif start_side == 'bottom':
            start_node = grid[self.height-1][random.randint(0, self.width-1)]
        elif start_side == 'left':
            start_node = grid[random.randint(0, self.height-1)][0]
        else:  # right
            start_node = grid[random.randint(0, self.height-1)][self.width-1]

        # Select end node
        if end_side == 'top':
            end_node = grid[0][random.randint(0, self.width-1)]
        elif end_side == 'bottom':
            end_node = grid[self.height-1][random.randint(0, self.width-1)]
        elif end_side == 'left':
            end_node = grid[random.randint(0, self.height-1)][0]
        else:  # right
            end_node = grid[random.randint(0, self.height-1)][self.width-1]

        # Mark start and end nodes
        start_node.is_start = True
        end_node.is_end = True

        self.visited = set()
        path = []

        def dfs(current_node):
            self.master.update()
            self.visited.add(current_node)
            path.append(current_node)

            if len(path) > 1:
                prev_node = path[-2]
                self.animate_rectangle(self.canvas, prev_node, current_node,
                                       self.cell_width//2, speed_var.get())

            neighbors = self.get_unvisited_neighbors(current_node, grid)
            for neighbor in neighbors:
                if neighbor not in self.visited and (
                        len(path) < 5 or random.random() < 1
                ):
                    dfs(neighbor)

            path.pop()

        dfs(start_node)
        x = end_node.x * self.cell_width + self.cell_width/2 + self.offset_x
        y = end_node.y * self.cell_width + self.cell_width/2 + self.offset_y
        width = self.cell_width//2
        black_border = 3
        self.canvas.create_rectangle(
            x - width // 2 + black_border,
            y - width // 2 + black_border,
            x + width // 2 - black_border,
            y + width // 2 - black_border,
            fill="red",
            outline=""
        )
        print("Maze generation completed.")
        return start_node, end_node

    def add_edge(self, node1, node2):
        new_edge = Edge(node1, node2)
        if not any(edge.is_sub_edge(new_edge) or new_edge.is_sub_edge(edge)
                   for edge in self.edges):
            self.edges.append(new_edge)
            return True
        return False

    def animate_rectangle(self, canvas, node1, node2, width, delay, end=False):
        black_border, mag_d = 3, delay
        x1 = node1.x * self.cell_width + self.cell_width/2 + self.offset_x
        y1 = node1.y * self.cell_width + self.cell_width/2 + self.offset_y
        x2 = node2.x * self.cell_width + self.cell_width/2 + self.offset_x
        y2 = node2.y * self.cell_width + self.cell_width/2 + self.offset_y

        def draw_colored_rectangle(x, y, is_start=False):
            canvas.create_rectangle(
                x - width // 2 + black_border,
                y - width // 2 + black_border,
                x + width // 2 - black_border,
                y + width // 2 - black_border,
                fill="green" if node1.is_start and is_start else "white" if is_start else "blue",
                outline=""
            )

        draw_colored_rectangle(x2, y2)

        dx = mag_d if x2 > x1 else -mag_d if x2 < x1 else 0
        dy = mag_d if y2 > y1 else -mag_d if y2 < y1 else 0

        current_x, current_y = x1, y1

        while current_x != x2 or current_y != y2:
            def is_between(value, bound1, bound2, margin=self.cell_width//5):
                lower, upper = min(bound1, bound2), max(bound1, bound2)
                return lower + margin <= value <= upper - margin

            if dx == 0:
                if is_between(current_x, x1, x2) or is_between(current_y, y1, y2):
                    canvas.create_rectangle(
                        current_x - width // 2, current_y,
                        current_x + width // 2, current_y + dy,
                        fill="black", outline=""
                    )
                canvas.create_rectangle(
                    current_x - (width // 2 - black_border), current_y,
                    current_x + (width // 2 - black_border), current_y + dy,
                    fill="white", outline=""
                )
            else:
                if is_between(current_x, x1, x2) or is_between(current_y, y1, y2):
                    canvas.create_rectangle(
                        current_x, current_y - width // 2,
                                   current_x + dx, current_y + width // 2,
                        fill="black", outline=""
                    )
                canvas.create_rectangle(
                    current_x, current_y - (width // 2 - black_border),
                               current_x+dx, current_y + (width // 2 - black_border),
                    fill="white", outline=""
                )
            canvas.update()

            current_x += dx
            current_y += dy

        canvas.create_rectangle(
            x2 - width // 2, y2 - width // 2,
            x2 + width // 2, y2 + width // 2,
            fill="black", outline=""
        )

        bb = black_border if dx > 0 or dy > 0 else 0
        nbb = 0 if bb else -black_border
        draw_colored_rectangle(x1, y1, is_start=True)

        if dx == 0:
            canvas.create_rectangle(
                x2 - width // 2 + black_border,
                y2 - width//2 - nbb,
                x2 + width // 2 - black_border,
                y2 + width // 2 - bb,
                fill="white", outline=""
            )
        else:
            canvas.create_rectangle(
                x2 - width // 2 - nbb,
                y2 - width // 2 + black_border,
                x2 + width // 2 - bb,
                y2 + width // 2 - black_border,
                fill="white", outline=""
            )
        canvas.update()
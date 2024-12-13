import random
from node import Edge
from load import MazeImage
from math import floor

class MazeAlgorithm:
    def __init__(self, ui, width, height, canvas_width=None, canvas_height=None):
        self.canvas = ui.canvas
        self.width, self.height = width, height
        self.master = ui.master
        self.ui = ui

        self.end_node = None
        self.start_node = None

        self.reach_var = ui.reach_var
        self.speed_var = ui.speed_var

        # Use provided canvas dimensions or default to canvas's current width/height
        canvas_width = canvas_width or ui.canvas.winfo_width()
        canvas_height = canvas_height or ui.canvas.winfo_height()

        # Adjust cell size to fit entire maze in canvas
        self.cell_width = min(canvas_width // width, canvas_height // height)
        self.cell_height = self.cell_width

        # Center the maze in the canvas
        self.offset_x = (canvas_width - (self.cell_width * width)) // 2
        self.offset_y = (canvas_height - (self.cell_height * height)) // 2

        self.edges = []
        self.visited = set()

        # Directions initialization
        self.directions = [
                              (dx, 0) for dx in range(-floor(width*ui.reach_var.get()/100), floor(width*ui.reach_var.get()/100))
                          ] + [
                              (0, dy) for dy in range(-floor(height*ui.reach_var.get()/100), floor(height*ui.reach_var.get()/100))
                          ]

        self.image = MazeImage(canvas_width, canvas_height)

    def get_unvisited_neighbors(self, node, grid):
        random.shuffle(self.directions)
        return [
            grid[new_y][new_x] for dx, dy in self.directions
            if (0 <= (new_x := node.x + dx) < self.width and
                0 <= (new_y := node.y + dy) < self.height and
                grid[new_y][new_x] not in self.visited and
                self.add_edge(grid[new_y][new_x], node))
        ]

    def parallel_bias(self, neighbors, grid):
        """
        Reorder adjacent nodes based on how many already-explored nodes are touched by each.

        Args:
            neighbors (list): List of adjacent nodes returned by get_unvisited_neighbors.
            grid (list): 2D array of nodes representing the maze grid.

        Returns:
            list: Reordered list of adjacent nodes.
        """
        def count_explored_neighbors(node):
            explored_count = 0
            directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Up, Down, Left, Right

            for dx, dy in directions:
                nx, ny = node.x + dx, node.y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    neighbor = grid[ny][nx]
                    if neighbor in self.visited:
                        explored_count += 1

            return explored_count

        # Sort the neighbors based on the number of explored neighbors (descending order)
        return sorted(neighbors, key=count_explored_neighbors, reverse=True)

    def is_connected(self, node_1, node_2):
        # Check if there's already an edge between node_1 and node_2
        return any(
            {edge.node1, edge.node2} == {node_1, node_2}  # Compare nodes in the edge
            for edge in self.edges
        )
    def generate_maze(self, grid):
        # Randomly select start and end nodes on opposite edges
        start_side = random.choice(['top', 'bottom', 'left', 'right'])
        end_side = {'top': 'bottom', 'bottom': 'top', 'left': 'right', 'right': 'left'}[start_side]

        # Select start node
        if start_side == 'top':
            self.start_node = grid[0][random.randint(0, self.width-1)]
        elif start_side == 'bottom':
            self.start_node = grid[self.height-1][random.randint(0, self.width-1)]
        elif start_side == 'left':
            self.start_node = grid[random.randint(0, self.height-1)][0]
        else:  # right
            self.start_node = grid[random.randint(0, self.height-1)][self.width-1]

        # Select end node
        if end_side == 'top':
            self.end_node = grid[0][random.randint(0, self.width-1)]
        elif end_side == 'bottom':
            self.end_node = grid[self.height-1][random.randint(0, self.width-1)]
        elif end_side == 'left':
            self.end_node = grid[random.randint(0, self.height-1)][0]
        else:  # right
            self.end_node = grid[random.randint(0, self.height-1)][self.width-1]

        # Mark start and end nodes
        self.start_node.is_start = True
        self.end_node.is_end = True

        self.visited = set()
        path = []

        def dfs(current_node):
            self.master.update()
            self.visited.add(current_node)
            path.append(current_node)

            if len(path) > 1:
                prev_node = path[-2]
                self.animate_rectangle(self.canvas, prev_node, current_node,
                                       self.cell_width//2, self.canvas.create_rectangle)
                self.quick_rectangle(self.canvas, prev_node, current_node,
                                       self.cell_width//2, self.image.draw_rectangle)
                self.edges.append(Edge(prev_node, current_node))

            neighbors = self.get_unvisited_neighbors(current_node, grid)
            if self.ui.bias.get()/100>random.random():
                neighbors = self.parallel_bias(neighbors, grid)
            for neighbor in neighbors:
                if neighbor not in self.visited and self.add_edge(neighbor, current_node):
                    dfs(neighbor)
            path.pop()
        dfs(self.start_node)
        print("Maze generation completed.")
        return self.start_node, self.end_node

    def add_edge(self, node1, node2):
        new_edge = Edge(node1, node2)
        return not any(edge.is_sub_edge(new_edge) or new_edge.is_sub_edge(edge)
                   for edge in self.edges)

    def animate_rectangle(self, canvas, node1, node2, width, draw_rectangle_func=None, color="white"):
        # If no custom draw function provided, use default canvas.create_rectangle
        dist = self.speed_var.get()
        if draw_rectangle_func is None:
            draw_rectangle_func = canvas.create_rectangle

        def grid2Coord(node):
            return (node.x * self.cell_width + self.cell_width/2 + self.offset_x, node.y * self.cell_width + self.cell_width/2 + self.offset_y)

        black_border = 3
        MAX_SPEED = 60
        d = max(round(dist/100*MAX_SPEED), 1)
        x1, y1 = grid2Coord(node1)
        x2, y2 = grid2Coord(node2)

        def draw_cell(x, y, color="white"):
            draw_rectangle_func(
                x - width // 2 + black_border,
                y - width // 2 + black_border,
                x + width // 2 - black_border,
                y + width // 2 - black_border,
                fill=color,
                outline=""
            )

        dx = d if x2 > x1 else -d if x2 < x1 else 0
        dy = d if y2 > y1 else -d if y2 < y1 else 0

        current_x, current_y = x1, y1

        while abs(current_x - x2)>abs(dx) or abs(current_y - y2)>abs(dy):

            if dx == 0:
                if abs(current_y - y1)>abs(width):
                    draw_rectangle_func(
                        current_x - width // 2, max(y1, current_y)-width//2,
                        current_x + width // 2, min(y1, current_y)+width//2,
                        fill="black", outline=""
                    )
                draw_rectangle_func(
                    current_x - (width // 2 - black_border), min(y1, current_y),
                    current_x + (width // 2 - black_border), max(current_y, y1),
                    fill=color, outline=""
                )
            else:
                if abs(current_x - x1)>abs(width):
                    draw_rectangle_func(
                        max(x1, current_x)-width//2, current_y - width // 2,
                        min(x1, current_x)+width//2, current_y + width // 2,
                        fill="black", outline=""
                    )
                draw_rectangle_func(
                    min(x1, current_x), current_y - (width // 2 - black_border),
                    max(current_x, x1), current_y + (width // 2 - black_border),
                    fill=color, outline=""
                )
            draw_cell(x2, y2, color="blue")
            canvas.update()

            current_x += dx
            current_y += dy

        draw_rectangle_func(
            x2 - width // 2, y2 - width // 2,
            x2 + width // 2, y2 + width // 2,
            fill="black", outline=""
        )

        bb = black_border if dx > 0 or dy > 0 else 0
        nbb = 0 if bb else -black_border
        if dx == 0:
            draw_rectangle_func(
                x2 - width // 2,
                min(y2, y1) + width//2,
                x2 + width // 2,
                max(y2, y1) - width//2,
                fill="black", outline=""
            )
            draw_rectangle_func(
                x2 - width // 2 + black_border,
                y2 - width//2 - nbb,
                x2 + width // 2 - black_border,
                y2 + width // 2 - bb,
                fill=color, outline=""
            )
            draw_rectangle_func(
                x2 - width // 2 + black_border,
                min(y2, y1),
                x2 + width // 2 - black_border,
                max(y2, y1),
                fill=color, outline=""
            )
        else:
            draw_rectangle_func(
                min(x2, x1) + width // 2,
                y2 - width // 2,
                max(x2, x1) - width//2,
                y2 + width // 2,
                fill="black", outline=""
            )
            draw_rectangle_func(
                x2 - width // 2 - nbb,
                y2 - width // 2 + black_border,
                x2 + width // 2 - bb,
                y2 + width // 2 - black_border,
                fill=color, outline=""
            )
            draw_rectangle_func(
                min(x2, x1),
                y2 - width // 2 + black_border,
                max(x2, x1),
                y2 + width // 2 - black_border,
                fill=color, outline=""
            )

        draw_cell(grid2Coord(self.start_node)[0], grid2Coord(self.start_node)[1], color="green")
        draw_cell(grid2Coord(self.end_node)[0], grid2Coord(self.end_node)[1], color="red")
        canvas.update()

    def quick_rectangle(self, canvas, node1, node2, width, draw_rectangle_func=None, color="white"):
        # If no custom draw function provided, use default canvas.create_rectangle
        if draw_rectangle_func is None:
            draw_rectangle_func = canvas.create_rectangle

        def grid2Coord(node):
            return (node.x * self.cell_width + self.cell_width/2 + self.offset_x, node.y * self.cell_width + self.cell_width/2 + self.offset_y)

        black_border = 3
        x1, y1 = grid2Coord(node1)
        x2, y2 = grid2Coord(node2)

        dx = 1 if x2 > x1 else -1 if x2 < x1 else 0
        dy = 1 if y2 > y1 else -1 if y2 < y1 else 0

        def draw_cell(x, y, color="white"):
            draw_rectangle_func(
                x - width // 2 + black_border,
                y - width // 2 + black_border,
                x + width // 2 - black_border,
                y + width // 2 - black_border,
                fill=color,
                outline=""
            )

        draw_rectangle_func(
            x2 - width // 2, y2 - width // 2,
            x2 + width // 2, y2 + width // 2,
            fill="black", outline=""
        )

        bb = black_border if dx > 0 or dy > 0 else 0
        nbb = 0 if bb else -black_border
        if dx == 0:
            draw_rectangle_func(
                x2 - width // 2,
                min(y2, y1) + width//2,
                x2 + width // 2,
                max(y2, y1) - width//2,
                fill="black", outline=""
            )
            draw_rectangle_func(
                x2 - width // 2 + black_border,
                y2 - width//2 - nbb,
                x2 + width // 2 - black_border,
                y2 + width // 2 - bb,
                fill=color, outline=""
            )
            draw_rectangle_func(
                x2 - width // 2 + black_border,
                min(y2, y1),
                x2 + width // 2 - black_border,
                max(y2, y1),
                fill=color, outline=""
            )
        else:
            draw_rectangle_func(
                min(x2, x1) + width // 2,
                y2 - width // 2,
                max(x2, x1) - width//2,
                y2 + width // 2,
                fill="black", outline=""
            )
            draw_rectangle_func(
                x2 - width // 2 - nbb,
                y2 - width // 2 + black_border,
                x2 + width // 2 - bb,
                y2 + width // 2 - black_border,
                fill=color, outline=""
            )
            draw_rectangle_func(
                min(x2, x1),
                y2 - width // 2 + black_border,
                max(x2, x1),
                y2 + width // 2 - black_border,
                fill=color, outline=""
            )

        draw_cell(grid2Coord(self.start_node)[0], grid2Coord(self.start_node)[1], color="green")
        draw_cell(grid2Coord(self.end_node)[0], grid2Coord(self.end_node)[1], color="red")
        canvas.update()
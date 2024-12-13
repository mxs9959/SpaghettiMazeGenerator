import tkinter as tk
from collections import deque, defaultdict
import tkinter.messagebox as messagebox

class BreadthFirstSolver:
    def __init__(self, ui, csv_file):

        self.canvas = ui.canvas
        self.master = ui.master
        self.nodes = []
        self.graph = defaultdict(list)
        self.start_node = None
        self.end_node = None

        # UI configuration
        self.cell_width = ui.current_maze_algorithm.cell_width
        self.offset_x = ui.current_maze_algorithm.offset_x
        self.offset_y = ui.current_maze_algorithm.offset_y

        # Read the maze graph from CSV
        self._parse_csv(csv_file)

    def _parse_csv(self, csv_file):
        """
        Parse the CSV file to create nodes and graph structure

        Args:
            csv_file (str): Path to the CSV file
        """
        # Reset data structures
        self.nodes = []
        self.graph = defaultdict(list)
        self.start_node = None
        self.end_node = None

        with open(csv_file, 'r') as f:
            # Read entire file content
            content = f.readlines()

        # Find the start of nodes and edges sections
        nodes_start = content.index("# Nodes\n") + 2  # Skip header
        edges_start = content.index("# Edges (Adjacency List)\n") + 2  # Skip header

        # Parse Nodes
        for line in content[nodes_start:edges_start - 2]:
            row = line.strip().split(',')
            if len(row) < 4:
                continue

            try:
                x = int(row[0])
                y = int(row[1])
                x2,y2 = int(row[4]),int(row[5])
                is_start = row[2].lower() == 'true'
                is_end = row[7].lower() == 'true'

                # Mark start and end nodes
                if is_start:
                    node = (x,y)
                    self.start_node = node
                    print(f"Found start node: {self.start_node}")
                    self.nodes.append(node)
                if is_end:
                    node = (x2,y2)
                    self.end_node = node
                    print(f"Found end node: {self.end_node}")
                    self.nodes.append(node)
                if not is_start and not is_end:
                    node = (x, y)
                    self.nodes.append(node)


            except (ValueError, IndexError) as e:
                print(f"Error parsing node row {row}: {e}")
                continue

        # Parse Edges
        for line in content[edges_start:]:
            row = line.strip().split(',')

            # Ensure the row has exactly 4 values (source_x, source_y, neighbor_x, neighbor_y)
            if len(row) != 4:
                print(f"Skipping invalid edge row: {row}")
                continue

            try:
                # Parse source and neighbor coordinates
                source_x, source_y, neighbor_x, neighbor_y = map(int, row)
                source = (source_x, source_y)
                neighbor = (neighbor_x, neighbor_y)

                # Add bidirectional connections
                self.graph[source].append(neighbor)
                self.graph[neighbor].append(source)

            except ValueError as e:
                print(f"Error parsing edge row {row}: {e}")
                continue

        # Detailed debugging information
        print(f"Total nodes: {len(self.nodes)}")
        print(f"Total graph connections: {len(self.graph)}")
        print("Graph connections:")
        for node, neighbors in self.graph.items():
            print(f"{node}: {neighbors}")
    def solve_with_visualization(self):
        """
        Solve the maze using Breadth-First Search with step-by-step visualization

        Returns:
            list: Path from start to end node, or None if no path exists
        """
        # Extensive validation and debugging
        if not self.start_node:
            print("ERROR: No start node found!")
            messagebox.showerror("Solve Error", "No start node found in the maze!")
            return None

        if not self.end_node:
            print("ERROR: No end node found!")
            messagebox.showerror("Solve Error", "No end node found in the maze!")
            return None

        if self.start_node not in self.graph:
            print(f"ERROR: Start node {self.start_node} not in graph!")
            messagebox.showerror("Solve Error", f"Start node {self.start_node} not connected to any nodes!")
            return None

        if self.end_node not in self.graph:
            print(f"ERROR: End node {self.end_node} not in graph!")
            messagebox.showerror("Solve Error", f"End node {self.end_node} not connected to any nodes!")
            return None

        print(f"Solving from {self.start_node} to {self.end_node}")
        print(f"Start node neighbors: {self.graph[self.start_node]}")
        # BFS queue and visited set
        queue = deque()
        queue.append((self.start_node, [self.start_node]))

        # Set to track visited nodes
        visited = set()
        visited.add(self.start_node)  # Mark the start node as visited

        def grid2Coord(node):
            """Convert grid coordinates to canvas coordinates"""
            x, y = node
            return (x * self.cell_width + self.cell_width / 2 + self.offset_x,
                    y * self.cell_width + self.cell_width / 2 + self.offset_y)

        def draw_line(node1, node2, color):
            """
            Draw a line on the canvas between two nodes with the given color.

            Args:
                node1 (tuple): Coordinates of the first node (x1, y1).
                node2 (tuple): Coordinates of the second node (x2, y2).
                color (str): Color of the line to draw.
            """
            x1, y1 = grid2Coord(node1)
            x2, y2 = grid2Coord(node2)

            self.canvas.create_line(
                x1, y1, x2, y2,
                fill=color,
                width=5,
                tags="solution"
            )
            radius = self.cell_width // 12

            self.canvas.create_oval(
                x2 - radius, y2 - radius,
                x2 + radius, y2 + radius,
                fill=color, outline="", tags="solution"
            )
            self.master.update()
            self.master.after(50)  # Small delay for visualization

        while queue:
            # Dequeue the first element
            current_node, path = queue.popleft()

            # Check if we've reached the end node
            if current_node == self.end_node:
                print(f"Path found: {path}")

                # Visualize the final path with yellow lines
                for i in range(len(path) - 1):
                    draw_line(path[i], path[i + 1], color="blue")
                return path

            # Explore neighbors
            for neighbor in self.graph[current_node]:
                if neighbor not in visited:
                    # Mark the neighbor as visited
                    visited.add(neighbor)

                    # Visualize the exploration with purple lines
                    draw_line(current_node, neighbor, color="purple")

                    # Add the neighbor and updated path to the queue
                    queue.append((neighbor, path + [neighbor]))

            print(f"Explored node: {current_node}, Path so far: {path}")

        # No path found
        print("No path found!")
        messagebox.showinfo("Solve Result", "No path found between start and end nodes!")
        return None

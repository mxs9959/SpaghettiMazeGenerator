import csv
import tkinter as tk
from collections import deque, defaultdict
import random
import tkinter.messagebox as messagebox


class BreadthFirstSolver:
    def __init__(self, ui, csv_file):
        """
        Initialize the maze solver by reading the CSV file and setting up UI

        Args:
            ui (tk.Tk): The main UI window
            csv_file (str): Path to the CSV file containing maze graph data
        """
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
                is_start = row[2].lower() == 'true'
                is_end = row[3].lower() == 'true'

                node = (x, y)
                self.nodes.append(node)

                # Mark start and end nodes
                if is_start:
                    self.start_node = node
                    print(f"Found start node: {self.start_node}")
                if is_end:
                    self.end_node = node
                    print(f"Found end node: {self.end_node}")

            except (ValueError, IndexError) as e:
                print(f"Error parsing node row {row}: {e}")
                continue

        # Parse Edges
        for line in content[edges_start:]:
            row = line.strip().split(',')
            if len(row) < 4:
                continue

            try:
                source_x = int(row[0])
                source_y = int(row[1])
                neighbor_x = int(row[2])
                neighbor_y = int(row[3])

                source = (source_x, source_y)
                neighbor = (neighbor_x, neighbor_y)

                # Ensure bidirectional connections
                if source not in self.graph[neighbor]:
                    self.graph[source].append(neighbor)
                if neighbor not in self.graph[source]:
                    self.graph[neighbor].append(source)

            except (ValueError, IndexError) as e:
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
        print(f"End node neighbors: {self.graph[self.end_node]}")

        # BFS queue and visited set
        queue = deque([(self.start_node, [self.start_node])])
        visited = set([self.start_node])
        explored_nodes = set()

        def grid2Coord(node):
            """Convert grid coordinates to canvas coordinates"""
            x, y = node
            return (x * self.cell_width + self.cell_width / 2 + self.offset_x,
                    y * self.cell_width + self.cell_width / 2 + self.offset_y)

        def animate_node_exploration(node, is_path=False):
            """Animate node exploration on the canvas"""
            x, y = grid2Coord(node)
            color = "yellow" if is_path else "purple"
            radius = self.cell_width // 4

            self.canvas.create_oval(
                x - radius, y - radius,
                x + radius, y + radius,
                fill=color, outline="", tags="solution"
            )
            self.master.update()
            self.master.after(50)  # Small delay for visualization

        while queue:
            current_node, path = queue.popleft()

            # Visualize explored node (not part of final path)
            animate_node_exploration(current_node)
            explored_nodes.add(current_node)

            # Check if reached the end
            if current_node == self.end_node:
                # Visualize solution path
                for node in path:
                    animate_node_exploration(node, is_path=True)
                return path

            # Explore neighbors
            neighbors = self.graph[current_node]
            print(f"Exploring node {current_node}, neighbors: {neighbors}")

            for neighbor in neighbors:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))

        # No path found
        print("No path found between start and end nodes!")
        messagebox.showinfo("Solve Result", "No path found between start and end nodes!")
        return None


def main():
    # Example usage can be implemented in the UI's solve method
    pass


if __name__ == "__main__":
    main()
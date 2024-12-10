import csv
from collections import deque, defaultdict


class BreadthFirstSolver:
    def __init__(self, csv_file):
        """
        Initialize the maze solver by reading the CSV file

        Args:
            csv_file (str): Path to the CSV file containing maze graph data
        """
        self.nodes = []
        self.graph = defaultdict(list)
        self.start_node = None
        self.end_node = None

        # Read the maze graph from CSV
        self._parse_csv(csv_file)

    def _parse_csv(self, csv_file):
        """
        Parse the CSV file to create nodes and graph structure

        Args:
            csv_file (str): Path to the CSV file
        """
        with open(csv_file, 'r') as f:
            # Skip to node section
            while True:
                line = f.readline().strip()
                if line == "# Nodes":
                    break

            # Read node header
            f.readline()

            # Read nodes
            for line in f:
                if line.startswith("# Edges"):
                    break

                x, y, is_start, is_end = line.strip().split(',')
                node = (int(x), int(y))
                self.nodes.append(node)

                # Mark start and end nodes
                if is_start == 'True':
                    self.start_node = node
                if is_end == 'True':
                    self.end_node = node

            # Read edges
            f.readline()  # Skip header
            for line in f:
                source_x, source_y, neighbor_x, neighbor_y = map(int, line.strip().split(','))
                source = (source_x, source_y)
                neighbor = (neighbor_x, neighbor_y)
                self.graph[source].append(neighbor)
                self.graph[neighbor].append(source)

    def solve(self):
        """
        Solve the maze using Breadth-First Search

        Returns:
            list: Path from start to end node, or None if no path exists
        """
        if not self.start_node or not self.end_node:
            raise ValueError("Start or end node not found in the maze")

        # BFS queue and visited set
        queue = deque([(self.start_node, [self.start_node])])
        visited = set([self.start_node])

        while queue:
            current_node, path = queue.popleft()

            # Check if reached the end
            if current_node == self.end_node:
                return path

            # Explore neighbors
            for neighbor in self.graph[current_node]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))

        # No path found
        return None


def main():
    # Example usage
    try:
        solver = BreadthFirstSolver('maze_exports/maze_export_TIMESTAMP.csv')
        path = solver.solve()

        if path:
            print("Maze solved! Path:")
            for node in path:
                print(f"Node: {node}")
        else:
            print("No path found between start and end nodes.")

    except FileNotFoundError:
        print("Maze CSV file not found. Ensure the file exists.")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
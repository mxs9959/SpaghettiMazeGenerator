import csv
import os
from datetime import datetime

def export_maze_to_csv(maze_algorithm):
    """
    Export maze graph to CSV with nodes and edges information

    Args:
        maze_algorithm (MazeAlgorithm): The maze algorithm instance containing graph data

    Returns:
        str: Path to the exported CSV file
    """
    # Create export directory if it doesn't exist
    export_dir = 'maze_exports'
    os.makedirs(export_dir, exist_ok=True)

    # Generate unique filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f'maze_export_{timestamp}.csv'
    filepath = os.path.join(export_dir, filename)

    # Prepare node and edge data
    nodes = []
    edge_dict = {}

    # Collect all unique nodes and create adjacency list
    for edge in maze_algorithm.edges:
        node1, node2 = edge.node1, edge.node2

        # Add nodes if not already in the dictionary
        if node1 not in edge_dict:
            edge_dict[node1] = []
            nodes.append({
                'x': node1.x,
                'y': node1.y,
                'is_start': node1.is_start,
                'is_end': node1.is_end
            })
        if node2 not in edge_dict:
            edge_dict[node2] = []
            nodes.append({
                'x': node2.x,
                'y': node2.y,
                'is_start': node2.is_start,
                'is_end': node2.is_end
            })

        # Add edges to adjacency list
        edge_dict[node1].append((node2.x, node2.y))
        edge_dict[node2].append((node1.x, node1.y))

    # Write to CSV
    with open(filepath, 'w', newline='') as csvfile:
        # Write nodes header
        csvfile.write("# Nodes\n")
        node_writer = csv.DictWriter(csvfile, fieldnames=['x', 'y', 'is_start', 'is_end'])
        node_writer.writeheader()
        node_writer.writerows(nodes)

        # Write edges header
        csvfile.write("\n# Edges (Adjacency List)\n")
        csvfile.write("source_x,source_y,neighbor_x,neighbor_y\n")

        # Write edges
        for node, neighbors in edge_dict.items():
            for neighbor in neighbors:
                csvfile.write(f"{node.x},{node.y},{neighbor[0]},{neighbor[1]}\n")

    return filepath
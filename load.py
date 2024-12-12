import os
import io
import csv
from datetime import datetime
import tkinter as tk
from PIL import Image, ImageTk

def export_maze_to_png(canvas_widget, image):
    # Create export directory if it doesn't exist
    export_dir = 'maze_exports'
    os.makedirs(export_dir, exist_ok=True)

    # Generate unique filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    png_filename = os.path.join(export_dir, f'maze_export_{timestamp}.png')

    # Ensure the canvas is updated and fully rendered
    canvas_widget.update()

    # Get canvas dimensions
    x = canvas_widget.winfo_rootx() + canvas_widget.winfo_x()
    y = canvas_widget.winfo_rooty() + canvas_widget.winfo_y()
    width = canvas_widget.winfo_width()
    height = canvas_widget.winfo_height()

    image.save_image(png_filename)

    return png_filename

def export_maze_to_csv(maze_algorithm):
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

from PIL import Image, ImageDraw

class MazeImage:
    def __init__(self, width, height):
        """
        Initializes a blank PNG image with the specified width and height.

        :param width: Width of the image
        :param height: Height of the image
        """
        self.width = width
        self.height = height
        self.image = Image.new("RGB", (width, height), "black")
        self.draw = ImageDraw.Draw(self.image)

    def draw_rectangle(self, x1, y1, x2, y2, fill="white", outline=""):
        """
        Draws a rectangle on the image.

        :param top_left: Tuple (x, y) for the top-left corner of the rectangle
        :param bottom_right: Tuple (x, y) for the bottom-right corner of the rectangle
        :param color: Color of the rectangle (e.g., "red", "#FF5733", (255, 87, 51))
        """
        self.draw.rectangle([(min(x1, x2), min(y1, y2)), (max(x1, x2), max(y1, y2))], fill=fill, outline=fill)

    def save_image(self, file_name):
        """
        Saves the image to a file.

        :param file_name: Name of the file to save the image
        """
        self.image.save(file_name, "PNG")

import os
import csv
from PIL import Image, ImageDraw
from datetime import datetime
from node import Node, Edge
from tkinter import filedialog


def export_maze_to_png(canvas_widget, image):
    # Create export directory if it doesn't exist
    export_dir = 'maze_exports'
    os.makedirs(export_dir, exist_ok=True)

    # Generate unique filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    png_filename = os.path.join(export_dir, f'maze_export_{timestamp}.png')

    # Ensure the canvas is updated and fully rendered
    canvas_widget.update()

    image.save_image(png_filename)

    return png_filename


def export_maze_to_csv(maze, output_filename='maze.csv'):
    edges = set()

    # Ensure the export directory exists
    export_dir = './maze_exports'
    os.makedirs(export_dir, exist_ok=True)

    # Full path for the output file
    full_path = os.path.join(export_dir, output_filename)
    for edge in maze.edges:
        node1, node2 = edge.node1, edge.node2
        if maze.is_connected(node1, node2):  # Assuming `edge.is_connected` determines if the nodes are connected
            edges.add(((node1.x, node1.y), (node2.x, node2.y)))
            edges.add(((node2.x, node2.y), (node1.x, node1.y)))  # Bidirectional edge

    # Write the CSV file
    with open(full_path, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)

        # Write header
        csv_writer.writerow(['# Nodes'])
        csv_writer.writerow([
            'Node0_X', 'Node0_Y', 'Node0_IsStart', 'Node0_IsEnd',
            'Node1_X', 'Node1_Y', 'Node1_IsStart', 'Node1_IsEnd',
            'Edge_Color'
        ])
        for edge in maze.edges:
            node1, node2 = edge.node1, edge.node2
            csv_writer.writerow([
                node1.x, node1.y,
                str(node1.is_start), str(node1.is_end),
                node2.x, node2.y,
                str(node2.is_start), str(node2.is_end),
                edge.color
            ])

        csvfile.write("\n# Edges (Adjacency List)\n")
        csvfile.write("source_x,source_y,neighbor_x,neighbor_y\n")

        # Write edges from the set
        written_edges = set()  # Track written edges to avoid duplicates
        for (source, target) in edges:
            if (source, target) not in written_edges:  # Avoid duplicates
                csvfile.write(f"{source[0]},{source[1]},{target[0]},{target[1]}\n")
                written_edges.add((source, target))
                written_edges.add((target, source))


    return full_path


def import_maze_from_csv(ui):
    ui.generate_maze(True)
    # Open file dialog
    file_path = filedialog.askopenfilename(
        title="Select CSV File to Import Edges",
        filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        initialdir='./maze_exports'
    )

    # If no file selected, return empty list
    if not file_path:
        print("No file selected.")
        return []

    # List to store imported edges
    imported_edges = []

    # Read the CSV file
    try:
        with open(file_path, 'r') as csvfile:
            csv_reader = csv.reader(csvfile)

            # Skip the header row
            next(csv_reader)

            # Process each row
            for row in csv_reader:
                # Convert string representations to appropriate types
                node0 = Node(
                    x=float(row[0]),
                    y=float(row[1]),
                    is_start=row[2].lower() == 'true',
                    is_end=row[3].lower() == 'true'
                )

                node1 = Node(
                    x=float(row[4]),
                    y=float(row[5]),
                    is_start=row[6].lower() == 'true',
                    is_end=row[7].lower() == 'true'
                )

                if node0.is_start:
                    ui.current_maze_algorithm.start_node = node0
                if node1.is_start:
                    ui.current_maze_algorithm.start_node = node1
                if node0.is_end:
                    ui.current_maze_algorithm.end_node = node0
                if node1.is_end:
                    ui.current_maze_algorithm.end_node = node1

                # Create edge with the two nodes and color
                edge = Edge(node0, node1, row[8])

                # Add to list of imported edges
                imported_edges.append(edge)

    except Exception as e:
        print(f"Error importing edges: {e}")
        return []

    print(f"Imported maze of {len(imported_edges)} paths from {file_path}")

    for edge in imported_edges:
        ui.current_maze_algorithm.quick_rectangle(ui.current_maze_algorithm.canvas, edge.node1, edge.node2,
                                                  ui.current_maze_algorithm.cell_width // 2, color=edge.color)
        ui.current_maze_algorithm.quick_rectangle(ui.current_maze_algorithm.canvas, edge.node1, edge.node2,
                                                  ui.current_maze_algorithm.cell_width // 2,
                                                  draw_rectangle_func=ui.current_maze_algorithm.image.draw_rectangle,
                                                  color=edge.color)


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

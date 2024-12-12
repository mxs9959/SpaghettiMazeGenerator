import csv
import os
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import tkinter as tk

def export_maze_to_csv(maze_algorithm):
    """
    Export maze graph to CSV with nodes and edges information.

    Args:
        maze_algorithm (MazeAlgorithm): The maze algorithm instance containing graph data.

    Returns:
        str: Path to the exported CSV file.
    """
    # Create export directory if it doesn't exist
    export_dir = 'maze_exports'
    os.makedirs(export_dir, exist_ok=True)

    # Generate unique filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f'maze_export_{timestamp}.csv'
    filepath = os.path.join(export_dir, filename)

    # Prepare nodes and adjacency list for edges
    nodes = {}
    edges = set()  # Use a set to avoid duplicate edges

    for edge in maze_algorithm.edges:
        node1, node2 = edge.node1, edge.node2

        # Add nodes to the dictionary with their attributes
        if (node1.x, node1.y) not in nodes:
            nodes[(node1.x, node1.y)] = {
                'x': node1.x,
                'y': node1.y,
                'is_start': node1.is_start,
                'is_end': node1.is_end
            }
        if (node2.x, node2.y) not in nodes:
            nodes[(node2.x, node2.y)] = {
                'x': node2.x,
                'y': node2.y,
                'is_start': node2.is_start,
                'is_end': node2.is_end
            }

        # Add edge to the set (ensure bidirectional consistency)
        edges.add(((node1.x, node1.y), (node2.x, node2.y)))
        edges.add(((node2.x, node2.y), (node1.x, node1.y)))  # Bidirectional edge

    # Write to CSV
    with open(filepath, 'w', newline='') as csvfile:
        # Write nodes header
        csvfile.write("# Nodes\n")
        node_writer = csv.DictWriter(csvfile, fieldnames=['x', 'y', 'is_start', 'is_end'])
        node_writer.writeheader()
        node_writer.writerows(nodes.values())

        # Write edges header
        csvfile.write("\n# Edges (Adjacency List)\n")
        csvfile.write("source_x,source_y,neighbor_x,neighbor_y\n")

        # Write edges from the set
        written_edges = set()  # Track written edges to avoid duplicates
        for (source, target) in edges:
            if (source, target) not in written_edges:  # Avoid duplicates
                csvfile.write(f"{source[0]},{source[1]},{target[0]},{target[1]}\n")
                written_edges.add((source, target))
                written_edges.add((target, source))  # Mark reverse edge as written

    return filepath
def export_maze_to_pdf(canvas_widget):
    """
    Export maze canvas as a PDF with a screenshot of the canvas

    Args:
        canvas_widget (tk.Canvas): The Tkinter canvas containing the maze

    Returns:
        str: Path to the exported PDF file
    """
    # Create export directory if it doesn't exist
    export_dir = 'maze_exports'
    os.makedirs(export_dir, exist_ok=True)

    # Generate unique filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Capture canvas as an image
    # Draw canvas content on a PostScript file first
    ps_filename = os.path.join(export_dir, f'maze_image_{timestamp}.ps')
    canvas_widget.postscript(
        file=ps_filename,
        colormode='color',
        pageanchor='center',
        pagex=canvas_widget.winfo_width()/2,
        pagey=canvas_widget.winfo_height()/2
    )

    # Convert PostScript to PNG using Pillow
    image_filename = os.path.join(export_dir, f'maze_image_{timestamp}.png')
    pdf_filename = os.path.join(export_dir, f'maze_export_{timestamp}.pdf')

    # Open PostScript file and convert to image
    from PIL import Image, ImageTk
    import ghostscript

    # Use ghostscript to convert PS to PNG
    gs_args = [
        "gs",
        "-dNOPAUSE",
        "-dBATCH",
        "-dSAFER",
        "-sDEVICE=pngalpha",
        f"-sOutputFile={image_filename}",
        ps_filename
    ]
    ghostscript.import_gs()
    gs_args = [arg.encode('utf-8') for arg in gs_args]
    ghostscript.commandline(gs_args)

    # Create PDF with the image
    pdf_canvas = canvas.Canvas(pdf_filename, pagesize=(8.5*inch, 11*inch))

    # Calculate scaling to fit image on letter-sized page
    pdf_width, pdf_height = 8.5*inch, 11*inch
    image = Image.open(image_filename)
    image_width, image_height = image.size
    image_aspect = image_width / image_height
    page_aspect = pdf_width / pdf_height

    if image_aspect > page_aspect:
        # Image is wider relative to page
        draw_width = pdf_width
        draw_height = draw_width / image_aspect
    else:
        # Image is taller relative to page
        draw_height = pdf_height
        draw_width = draw_height * image_aspect

    # Center the image on the page
    x_centered = (pdf_width - draw_width) / 2
    y_centered = (pdf_height - draw_height) / 2

    # Draw image on PDF
    pdf_canvas.drawImage(
        image_filename,
        x_centered, y_centered,
        width=draw_width,
        height=draw_height
    )

    # Add text description
    pdf_canvas.setFont("Helvetica", 12)
    pdf_canvas.drawCentredString(pdf_width/2, 0.5*inch, f"Maze Generated: {timestamp}")

    pdf_canvas.save()

    # Optional: Remove intermediate files
    os.remove(ps_filename)

    return pdf_filename
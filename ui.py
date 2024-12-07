import tkinter as tk
import tkinter.messagebox
from maze import MazeAlgorithm
from node import Node

class MazeGeneratorUI:
    def __init__(self, master):
        self.master = master  # master (tk.Tk): Root Tkinter window
        master.title("Spaghetti")

        # Configuration Frame
        self.config_frame = tk.Frame(master)
        self.config_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        # Width Input
        tk.Label(self.config_frame, text="Width:").pack(side=tk.LEFT)
        self.width_entry = tk.Entry(self.config_frame, width=5)
        self.width_entry.pack(side=tk.LEFT, padx=5)
        self.width_entry.insert(0, "10")

        # Height Input
        tk.Label(self.config_frame, text="Height:").pack(side=tk.LEFT, padx=(10, 0))
        self.height_entry = tk.Entry(self.config_frame, width=5)
        self.height_entry.pack(side=tk.LEFT, padx=5)
        self.height_entry.insert(0, "10")

        # Delay Slider
        tk.Label(self.config_frame, text="Delay:").pack(side=tk.LEFT, padx=(10, 0))
        self.speed_var = tk.DoubleVar(value=0.1)
        self.speed_slider = tk.Scale(
            self.config_frame, from_=0.01, to=1,
            resolution=0.01, orient=tk.HORIZONTAL,
            variable=self.speed_var, length=100
        )
        self.speed_slider.pack(side=tk.LEFT, padx=5)

        # Generate Button
        self.generate_btn = tk.Button(
            self.config_frame, text="Generate",
            command=self.generate_maze
        )
        self.generate_btn.pack(side=tk.LEFT, padx=(10, 0))

        # Container Frame for Centered Canvas
        self.canvas_frame = tk.Frame(master)
        self.canvas_frame.pack(expand=True, fill=tk.BOTH)

        # Canvas for maze drawing
        self.canvas = tk.Canvas(self.canvas_frame, width=600, height=600, bg='black')
        self.canvas.pack(expand=True)  # Center the canvas in its frame

    def generate_maze(self):
        # Clear previous maze
        self.canvas.delete("all")

        # Validate and get width and height
        try:
            width = int(self.width_entry.get())
            height = int(self.height_entry.get())
        except ValueError:
            tk.messagebox.showerror("Error", "Please enter valid width and height")
            return

        # Create grid of nodes
        grid = [[Node(x, y) for x in range(width)] for y in range(height)]

        # Initialize maze generation algorithm and generate
        MazeAlgorithm(self.canvas, width, height, self.master).generate_maze(grid, self.speed_var)

# Run the app
if __name__ == "__main__":
    root = tk.Tk()
    app = MazeGeneratorUI(root)
    root.mainloop()

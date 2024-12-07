import tkinter as tk
import tkinter.messagebox
from maze import MazeAlgorithm
from node import Node
from load import export_maze_to_csv, export_maze_to_pdf

class MazeGeneratorUI:
    def __init__(self, master):
        self.master = master
        master.title("Spaghetti Maze Generator")

        self._create_config_frame()
        self._create_canvas_frame()
        self._setup_zoom_pan()

        # Flag to track maze generation
        self.maze_generating = False
        self.current_maze_algorithm = None

    def _create_config_frame(self):
        self.config_frame = tk.Frame(self.master)
        self.config_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        # Width Input
        tk.Label(self.config_frame, text="Width:").pack(side=tk.LEFT)
        self.width_entry = self._create_entry(default="10")

        # Height Input
        tk.Label(self.config_frame, text="Height:").pack(side=tk.LEFT, padx=(10, 0))
        self.height_entry = self._create_entry(default="10")

        # Delay Slider
        tk.Label(self.config_frame, text="Speed:").pack(side=tk.LEFT, padx=(10, 0))
        self.speed_var = tk.DoubleVar(value=5)
        self.speed_slider = tk.Scale(
            self.config_frame, from_=1, to=30,
            resolution=1, orient=tk.HORIZONTAL,
            variable=self.speed_var, length=100
        )
        self.speed_slider.pack(side=tk.LEFT, padx=5)

        # Generate Button
        self.generate_btn = tk.Button(
            self.config_frame, text="Generate",
            command=self.generate_maze
        )
        self.generate_btn.pack(side=tk.LEFT, padx=(10, 0))

        # Export Button
        self.export_btn = tk.Button(
            self.config_frame, text="Export as CSV",
            command=self.export_maze
        )
        self.export_btn.pack(side=tk.LEFT, padx=(10, 0))
        self.export_btn.config(state=tk.DISABLED)  # Initially disabled

        # Print Button
        self.print_btn = tk.Button(
            self.config_frame, text="Print",
            command=self.print_maze
        )
        self.print_btn.pack(side=tk.LEFT, padx=(10, 0))
        self.print_btn.config(state=tk.DISABLED)  # Initially disabled

        # Status Banner
        self.status_banner = tk.Label(
            self.config_frame,
            text="Wait for maze generation before zooming/panning",
            bg="red",
            fg="white",
            font=('Arial', 10),
            padx=10,
            pady=5
        )

    def _create_canvas_frame(self):
        self.canvas_frame = tk.Frame(self.master)
        self.canvas_frame.pack(expand=True, fill=tk.BOTH)

        self.canvas = tk.Canvas(self.canvas_frame, width=600, height=600, bg='black')
        self.canvas.pack(expand=True, fill=tk.BOTH)

    def _setup_zoom_pan(self):
        # Zoom and pan setup
        self.canvas.bind('<MouseWheel>', self._on_mousewheel)
        self.canvas.bind('<Button-4>', self._on_mousewheel)  # For Linux
        self.canvas.bind('<Button-5>', self._on_mousewheel)  # For Linux

        # Pan setup
        self.canvas.bind('<ButtonPress-1>', self._on_pan_start)
        self.canvas.bind('<B1-Motion>', self._on_pan_motion)

        # Initial zoom and pan state
        self.zoom_factor = 1.0
        self.pan_x = 0
        self.pan_y = 0

    def _show_banner(self, banner_text, bg_color='red'):
        """
        Show a single banner, removing any existing banners

        Args:
            banner_text (str): Text to display on the banner
            bg_color (str, optional): Background color of the banner. Defaults to 'red'.
        """
        # Remove any existing banners
        try:
            self.status_banner.pack_forget()
        except:
            pass

        # Reconfigure the status banner
        self.status_banner.config(
            text=banner_text,
            bg=bg_color
        )

        # Show the banner
        self.status_banner.pack(side=tk.LEFT, padx=(10, 0))

    def _create_entry(self, default=""):
        entry = tk.Entry(self.config_frame, width=5)
        entry.insert(0, default)
        entry.pack(side=tk.LEFT, padx=5)
        return entry

    def _on_mousewheel(self, event):
        # Prevent zooming during maze generation
        if self.maze_generating:
            self._show_banner("Wait for maze generation before zooming/panning")
            return

        # Zoom logic with more precise scaling
        scale_factor = 1.1
        if event.num == 5 or event.delta < 0:  # Zoom out
            scale_factor = 0.9

        # Apply zoom
        x, y = event.x, event.y
        self.canvas.scan_mark(x, y)
        self.canvas.scale('all', x, y, scale_factor, scale_factor)

    def _on_pan_start(self, event):
        # Prevent panning during maze generation
        if self.maze_generating:
            self._show_banner("Wait for maze generation before zooming/panning")
            return

        # Record the start point of pan
        self.canvas.scan_mark(event.x, event.y)

    def _on_pan_motion(self, event):
        # Prevent panning during maze generation
        if self.maze_generating:
            return

        # Pan the canvas
        self.canvas.scan_dragto(event.x, event.y, gain=1)

    def generate_maze(self):
        # Clear any existing banners
        try:
            self.status_banner.pack_forget()
        except:
            pass

        # Set generation flag
        self.maze_generating = True

        # Disable export and print buttons
        self.export_btn.config(state=tk.DISABLED)
        self.print_btn.config(state=tk.DISABLED)

        # Clear canvas
        self.canvas.delete("all")

        try:
            width = int(self.width_entry.get())
            height = int(self.height_entry.get())
        except ValueError:
            tk.messagebox.showerror("Error", "Please enter valid width and height")
            self.maze_generating = False
            return

        # Show generation banner
        self._show_banner("Generating maze...", bg_color='blue')

        # Fit canvas to window size
        window_width = self.canvas.winfo_width()
        window_height = self.canvas.winfo_height()

        # Create maze algorithm with adjusted canvas dimensions
        self.current_maze_algorithm = MazeAlgorithm(
            self.canvas, width, height, self.master,
            canvas_width=window_width,
            canvas_height=window_height
        )

        # Wrapper to reset generation flag after maze is complete
        def maze_generation_complete(grid, speed_var):
            start_node, end_node = self.current_maze_algorithm.generate_maze(grid, speed_var)

            # Reset UI state
            self.maze_generating = False
            self.export_btn.config(state=tk.NORMAL)
            self.print_btn.config(state=tk.NORMAL)

            # Remove generation banner
            try:
                self.status_banner.pack_forget()
            except:
                pass

            return start_node, end_node

        grid = [[Node(x, y) for x in range(width)] for y in range(height)]
        maze_generation_complete(grid, self.speed_var)

    def export_maze(self):
        if not self.current_maze_algorithm:
            tk.messagebox.showerror("Error", "Generate a maze first!")
            return

        try:
            # Export maze and get filepath
            filepath = export_maze_to_csv(self.current_maze_algorithm)

            # Show export success banner
            self._show_banner(f"Exported maze to {filepath}", bg_color='green')
        except Exception as e:
            tk.messagebox.showerror("Export Error", str(e))

    def print_maze(self):
        if not self.current_maze_algorithm:
            tk.messagebox.showerror("Error", "Generate a maze first!")
            return

        try:
            # Export maze to PDF and get filepath
            filepath = export_maze_to_pdf(self.canvas)

            # Show export success banner
            self._show_banner(f"Maze PDF exported to {filepath}", bg_color='green')
        except Exception as e:
            tk.messagebox.showerror("Print Error", str(e))
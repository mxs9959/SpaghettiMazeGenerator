import tkinter as tk
import tkinter.messagebox
import tkinter.ttk as ttk
from maze import MazeAlgorithm
from node import Node
from load import export_maze_to_csv, export_maze_to_png, import_maze_from_csv

class MazeGeneratorUI:
    def __init__(self, master):
        self.master = master
        master.title("Spaghetti Supper")

        self._create_config_frame()
        self._create_canvas_frame()
        self._setup_zoom_pan()
        self.current_maze_algorithm = None

        # Flag to track maze generation
        self.maze_generating = False
        self.export_dropdown['values'] = ["CSV", "PNG"]

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
        tk.Label(self.config_frame, text="Speed (%):").pack(side=tk.LEFT, padx=(10, 0))
        self.speed_var = tk.DoubleVar(value=15)
        self.speed_slider = tk.Scale(
            self.config_frame, from_=1, to=100,
            resolution=1, orient=tk.HORIZONTAL,
            variable=self.speed_var, length=100
        )
        self.speed_slider.pack(side=tk.LEFT, padx=5)

        # Reach limit Slider
        tk.Label(self.config_frame, text="Reach (%):").pack(side=tk.LEFT, padx=(10, 0))
        self.reach_var = tk.DoubleVar(value=25)
        self.reach_slider = tk.Scale(
            self.config_frame, from_=1, to=100,
            resolution=1, orient=tk.HORIZONTAL,
            variable=self.reach_var, length=100
        )
        self.reach_slider.pack(side=tk.LEFT, padx=5)

        # Bias probability Slider
        tk.Label(self.config_frame, text="Parallel Bias (%):").pack(side=tk.LEFT, padx=(10, 0))
        self.bias = tk.DoubleVar(value=0)
        self.reach_slider = tk.Scale(
            self.config_frame, from_=0, to=100,
            resolution=1, orient=tk.HORIZONTAL,
            variable=self.bias, length=100
        )
        self.reach_slider.pack(side=tk.LEFT, padx=5)

        # Generate Button
        self.generate_btn = tk.Button(
            self.config_frame, text="Generate",
            command=self.generate_maze
        )
        self.generate_btn.pack(side=tk.LEFT, padx=(10, 0))

        # Export Dropdown
        self.export_menu = tk.StringVar(value="Export")
        self.export_dropdown = ttk.Combobox(
            self.config_frame,
            textvariable=self.export_menu,
            values=["CSV", "PDF"],
            state="readonly",
            width=5
        )
        self.export_dropdown.pack(side=tk.LEFT, padx=(10, 0))
        self.export_dropdown.bind('<<ComboboxSelected>>', self.export_selected)

        # Load Button
        self.solve_btn = tk.Button(
            self.config_frame, text="Load CSV",
            command=self.import_maze
        )
        self.solve_btn.pack(side=tk.LEFT, padx=(10, 0))

        self.solve_menu = tk.StringVar(value="Solve")
        self.solve_dropdown = ttk.Combobox(
            self.config_frame,
            textvariable=self.solve_menu,
            values=["BFS", "DFS"],
            state="readonly",
            width=5
        )
        self.solve_dropdown.pack(side=tk.LEFT, padx=(10, 0))
        self.solve_dropdown.bind('<<ComboboxSelected>>', self.solve_selected)

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
    def solve_selected(self, event):
        solve_type = self.solve_menu.get()
        if solve_type == "BFS":
            import_maze_from_csv(self, "bfs", True)
        elif solve_type == "DFS":
            import_maze_from_csv(self, "dfs", True)

        # Reset dropdown
        self.solve_menu.set("Solve")

    def import_maze(self):
        import_maze_from_csv(self,"dfs")

    def export_selected(self, event):
        """Handle export based on selected option"""
        export_type = self.export_menu.get()
        if export_type == "CSV":
            self.export_maze_csv()
        elif export_type == "PNG":
            self.export_maze_png()

        # Reset dropdown
        self.export_menu.set("Export")

    def export_maze_csv(self):
        """Export maze to CSV"""
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

    def export_maze_png(self):
        """Export maze to PNG"""
        if not self.current_maze_algorithm:
            tk.messagebox.showerror("Error", "Generate a maze first!")
            return

        try:
            # Export maze to PNG and get filepath
            filepath = export_maze_to_png(self.canvas, self.current_maze_algorithm.image)

            # Show export success banner
            self._show_banner(f"Maze PNG exported to {filepath}", bg_color='green')
        except Exception as e:
            tk.messagebox.showerror("Export Error", str(e))

    def generate_maze(self, load=False):
        # Clear any existing banners
        try:
            self.status_banner.pack_forget()
        except:
            pass

        # Set generation flag
        self.maze_generating = True

        # Clear canvas
        self.canvas.delete("all")

        try:
            width = int(self.width_entry.get())
            height = int(self.height_entry.get())
        except ValueError:
            tk.messagebox.showerror("Error", "Please enter valid width and height")
            self.maze_generating = False
            return

        # Fit canvas to window size
        window_width = self.canvas.winfo_width()
        window_height = self.canvas.winfo_height()

        # Create maze algorithm with adjusted canvas dimensions
        self.current_maze_algorithm = MazeAlgorithm(
            self, width, height,
            canvas_width=window_width,
            canvas_height=window_height
        )

        if load:
            return

        # Show generation banner
        self._show_banner("Generating maze...", bg_color='blue')
        grid = [[Node(x, y) for x in range(self.current_maze_algorithm.width)] for y in range(self.current_maze_algorithm.height)]
        self.current_maze_algorithm.generate_maze(grid)
        self.maze_generation_complete()

    def maze_generation_complete(self):

        # Reset UI state
        self.maze_generating = False

        # Remove generation banner
        try:
            self.status_banner.pack_forget()
        except:
            pass

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

    # In case there are any leftover PDF export references, replace with PNG
    def print_maze(self):
        if not self.current_maze_algorithm:
            tk.messagebox.showerror("Error", "Generate a maze first!")
            return

        try:
            # Export maze to PNG and get filepath
            filepath = export_maze_to_png(self.canvas)

            # Show export success banner
            self._show_banner(f"Maze PNG exported to {filepath}", bg_color='green')
        except Exception as e:
            tk.messagebox.showerror("Export Error", str(e))
import tkinter as tk
from ui import MazeGeneratorUI

def main():
    # Create root window
    root = tk.Tk()
    root.geometry("600x700")
    # Initialize UI
    MazeGeneratorUI(root)
    # Start main event loop
    root.mainloop()

if __name__ == "__main__":
    main()
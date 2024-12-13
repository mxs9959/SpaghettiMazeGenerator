import tkinter as tk
from ui import MazeGeneratorUI

def center_window(root, width, height):
    # Get screen width and height
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # Calculate position x and y coordinates
    x = (screen_width/2) - (width/2)
    y = (screen_height/2) - (height/2)
    root.geometry('%dx%d+%d+%d' % (width, height, x, y))

def main():
    root = tk.Tk()
    root.title("Spaghetti Supper")

    # Increase window size by 75%
    window_width = int(750 * 1.75)
    window_height = int(700 * 1.75)

    # Center the window
    center_window(root, window_width, window_height)

    MazeGeneratorUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
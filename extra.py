def animate_rectangle(self, canvas, node1, node2, width, d, end=False):
    black_border = 3
    x1 = node1.x * self.cell_width + self.cell_width/2 + self.offset_x
    y1 = node1.y * self.cell_width + self.cell_width/2 + self.offset_y
    x2 = node2.x * self.cell_width + self.cell_width/2 + self.offset_x
    y2 = node2.y * self.cell_width + self.cell_width/2 + self.offset_y

    # Determine movement direction and distance
    dx = 0 if x2==x1 else abs(x2 - x1)/(x2 - x1)*d
    dy = 0 if y2==y1 else abs(y2 - y1)/(y2 - y1)*d

    x1 += dx//2
    x2 -= dx//2
    y1 += dy//2
    y2 -= dy//2

    current_x, current_y = x1, y1

    def draw_path(x, y, l, direction, color="white", border=False):
        if l==0:
            l=width
        if direction == "h":
            if border:
                canvas.create_rectangle(
                    x - l // 2,
                    y - width // 2,
                    x + l // 2,
                    y + width // 2,
                    fill="black", outline=""
                )
            canvas.create_rectangle(
                x - l // 2 -1,
                y - width // 2 + black_border,
                x + l // 2 +1,
                y + width // 2 - black_border,
                fill=color, outline=""
            )
        elif direction == "v":
            if border:
                canvas.create_rectangle(
                    x - width // 2,
                    y - l // 2 -1,
                    x + width // 2,
                    y + l // 2 +1,
                    fill="black", outline=""
                )
            canvas.create_rectangle(
                x - width // 2 + black_border,
                y - l // 2,
                x + width // 2 - black_border,
                y + l // 2,
                fill=color, outline=""
            )
        else:
            canvas.create_rectangle(
                x - width // 2 + black_border,
                y - width // 2 + black_border,
                x + width // 2 - black_border,
                y + width // 2 - black_border,
                fill=color, outline=""
            )

    # Initial start/end cell coloring
    draw_path(x1, y1, 0, "x", "green" if node1.is_start else "white")
    draw_path(x2, y2, 0, "x", "blue")

    # Animate movement
    while abs(current_x - x2) > abs(dx) or abs(current_y - y2) > abs(dy):
        current_x += dx
        current_y += dy
        border = abs(current_x-x1) > abs(dx) or abs(current_y-y1) > abs(dy)
        if dx != 0:
            draw_path(current_x, current_y, dx, "h", border=border)
        else:
            draw_path(current_x, current_y, dy, "v", border=border)
        canvas.update()

    # Ensure final position
    draw_path(x2, y2, 0, "x")
    canvas.update()
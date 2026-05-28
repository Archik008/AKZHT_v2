import tkinter as tk

from configs import positions, segments


WINDOW_W = 1500
WINDOW_H = 900
PADDING = 80


def split_positions():
    """Разделяем объекты по типу, чтобы рисовать разными цветами."""
    points = {}
    signals = {}
    other = {}

    for name, coords in positions.items():
        if name.startswith("point"):
            points[name] = coords
        elif name.startswith("signal"):
            signals[name] = coords
        else:
            other[name] = coords

    return points, signals, other


def build_transform(items):
    """Подгоняем координаты под размер окна с одинаковым масштабом."""
    all_x = [x for x, _ in items.values()]
    all_y = [y for _, y in items.values()]

    min_x = min(all_x)
    max_x = max(all_x)
    min_y = min(all_y)
    max_y = max(all_y)

    data_w = max(max_x - min_x, 1)
    data_h = max(max_y - min_y, 1)

    scale_x = (WINDOW_W - PADDING * 2) / data_w
    scale_y = (WINDOW_H - PADDING * 2) / data_h
    scale = min(scale_x, scale_y)

    def to_canvas(x, y):
        canvas_x = PADDING + (x - min_x) * scale
        canvas_y = PADDING + (y - min_y) * scale
        return canvas_x, canvas_y

    return to_canvas


def draw_grid(canvas, transform):
    """Рисуем простую сетку, чтобы было легче смотреть координаты."""
    grid_color = "#9fc7c1"

    for x in range(0, 1001, 100):
        x1, y1 = transform(x, 0)
        x2, y2 = transform(x, 400)
        canvas.create_line(x1, y1, x2, y2, fill=grid_color, dash=(2, 4))
        canvas.create_text(x1, 25, text=str(x), fill="#58726e", font=("Arial", 9))

    for y in range(0, 451, 50):
        x1, y1 = transform(0, y)
        x2, y2 = transform(1000, y)
        canvas.create_line(x1, y1, x2, y2, fill=grid_color, dash=(2, 4))
        canvas.create_text(25, y1, text=str(y), fill="#58726e", font=("Arial", 9))


def draw_items(canvas, items, transform, color, radius, text_dx=0, text_dy=0):
    for name, (x, y) in items.items():
        cx, cy = transform(x, y)
        canvas.create_oval(
            cx - radius,
            cy - radius,
            cx + radius,
            cy + radius,
            fill=color,
            outline="black",
        )
        canvas.create_text(
            cx + text_dx,
            cy + text_dy,
            text=f"{name}",
            anchor="w",
            fill="#1b1b1b",
            font=("Arial", 10, "bold"),
        )


def draw_segments(canvas, transform):
    """Рисуем сегменты, которые зашиты в `configs.py`."""
    missing = []

    for start_name, end_name in segments:
        start = positions.get(start_name)
        end = positions.get(end_name)

        if start is None or end is None:
            missing.append((start_name, end_name))
            continue

        x1, y1 = transform(*start)
        x2, y2 = transform(*end)
        canvas.create_line(x1, y1, x2, y2, fill="#1f1f1f", width=3)

    return missing


def main():
    root = tk.Tk()
    root.title("АКЖТ - просмотр координат")
    root.geometry(f"{WINDOW_W}x{WINDOW_H}")

    info = tk.Label(
        root,
        text=(
            "Красные точки - светофоры, синие - стрелки, черные линии - сегменты. "
            "Подписи показывают имя и координаты."
        ),
        bg="#dcefed",
        anchor="w",
        padx=12,
        pady=8,
        font=("Arial", 11),
    )
    info.pack(fill="x")

    canvas = tk.Canvas(root, width=WINDOW_W, height=WINDOW_H, bg="#8ebfb9")
    canvas.pack(fill="both", expand=True)

    points, signals, other = split_positions()
    transform = build_transform(positions)

    draw_grid(canvas, transform)
    missing_segments = draw_segments(canvas, transform)
    draw_items(canvas, signals, transform, color="#d9534f", radius=7, text_dx=12, text_dy=-12)
    draw_items(canvas, points, transform, color="#0275d8", radius=6, text_dx=12, text_dy=12)
    draw_items(canvas, other, transform, color="#5cb85c", radius=6, text_dx=12, text_dy=0)

    canvas.create_text(
        20,
        WINDOW_H - 30,
        anchor="w",
        text=(
            f"Всего объектов: {len(positions)} | "
            f"светофоров: {len(signals)} | стрелок: {len(points)} | "
            f"сегментов: {len(segments)}"
        ),
        fill="#1b1b1b",
        font=("Arial", 11, "bold"),
    )

    if missing_segments:
        canvas.create_text(
            20,
            WINDOW_H - 55,
            anchor="w",
            text=f"Не найдены точки для сегментов: {missing_segments}",
            fill="#8b1e1e",
            font=("Arial", 10, "bold"),
        )

    root.mainloop()


if __name__ == "__main__":
    main()

import tkinter as tk

from configs import positions, segments, diagonals


WINDOW_W = 1500
WINDOW_H = 900
PADDING = 80


def split_positions():
    """Разделяем объекты по типу, чтобы рисовать разными цветами."""
    points = {}
    signals = {}
    junctions = {}
    other = {}

    for name, coords in positions.items():
        if name.startswith("j_"):
            junctions[name] = coords
        elif name.startswith("point"):
            points[name] = coords
        elif name.startswith("signal"):
            signals[name] = coords
        else:
            other[name] = coords

    return points, signals, junctions, other


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


def get_coords(item, key):
    """Берём координаты: имя из positions, кортеж (x, y) или блок coords."""
    value = item.get(key)

    if isinstance(value, (tuple, list)) and len(value) == 2:
        return tuple(value)

    if isinstance(value, str) and value in positions:
        return positions[value]

    coords = item.get("coords", {})
    point = coords.get(key)
    if isinstance(point, (tuple, list)) and len(point) == 2:
        return tuple(point)
    return None


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


def draw_diagonal(canvas, transform, item):
    """Обычная диагональ: два конца + горизонтальные «усики»."""
    start = get_coords(item, "start")
    end = get_coords(item, "end")
    if start is None or end is None:
        return False

    offset_left = item.get("offset_left", 0)
    offset_right = item.get("offset_right", 0)
    color = item.get("color", "#8b4513")

    x1, y1 = transform(*start)
    x2, y2 = transform(*end)
    lx, ly = transform(start[0] - offset_left, start[1])
    rx, ry = transform(end[0] + offset_right, end[1])

    canvas.create_line(x1, y1, lx, ly, fill=color, width=3)
    canvas.create_line(x2, y2, rx, ry, fill=color, width=3)
    canvas.create_line(x1, y1, x2, y2, fill=color, width=3)

    name = item.get("name")
    if name:
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        canvas.create_text(mx, my - 10, text=name, fill=color, font=("Arial", 9, "bold"))
    return True


def draw_split_diagonal(canvas, transform, item):
    """Разделённая диагональ: start -> mid -> end + усики по краям."""
    start = get_coords(item, "start")
    mid = get_coords(item, "mid")
    end = get_coords(item, "end")
    if start is None or mid is None or end is None:
        return False

    offset_left = item.get("offset_left", 0)
    offset_right = item.get("offset_right", 0)
    color = item.get("color", "#8b4513")

    x1, y1 = transform(*start)
    x2, y2 = transform(*mid)
    x3, y3 = transform(*end)
    lx, ly = transform(start[0] - offset_left, start[1])
    rx, ry = transform(end[0] + offset_right, end[1])

    canvas.create_line(x1, y1, lx, ly, fill=color, width=3)
    canvas.create_line(x1, y1, x2, y2, fill=color, width=3)
    canvas.create_line(x2, y2, x3, y3, fill=color, width=3)
    canvas.create_line(x3, y3, rx, ry, fill=color, width=3)

    part_a = item.get("part_a")
    part_b = item.get("part_b")
    if part_a:
        canvas.create_text(x1 - 8, y1 - 14, text=part_a, fill=color, font=("Arial", 9, "bold"))
    if part_b:
        canvas.create_text(x3 + 8, y3 - 14, text=part_b, fill=color, font=("Arial", 9, "bold"))
    return True


def draw_diagonals(canvas, transform):
    """Рисуем диагонали из `configs.py`."""
    missing = []

    for item in diagonals:
        diag_type = item.get("type")
        name = item.get("name", "?")

        if diag_type == "Diagonal":
            ok = draw_diagonal(canvas, transform, item)
        elif diag_type == "SplitDiagonal":
            ok = draw_split_diagonal(canvas, transform, item)
        else:
            missing.append((name, f"неизвестный type: {diag_type}"))
            continue

        if not ok:
            missing.append((name, diag_type))

    return missing


def main():
    root = tk.Tk()
    root.title("АКЖТ - просмотр координат")
    root.geometry(f"{WINDOW_W}x{WINDOW_H}")

    info = tk.Label(
        root,
        text=(
            "Зелёные - светофоры/пути, серые j_* - узлы стыковки стрелок, "
            "чёрные - сегменты, коричневые - диагонали."
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

    points, signals, junctions, other = split_positions()
    transform = build_transform(positions)

    draw_grid(canvas, transform)
    missing_segments = draw_segments(canvas, transform)
    missing_diagonals = draw_diagonals(canvas, transform)
    draw_items(canvas, junctions, transform, color="#888888", radius=4, text_dx=8, text_dy=8)
    draw_items(canvas, other, transform, color="#5cb85c", radius=6, text_dx=12, text_dy=0)
    draw_items(canvas, signals, transform, color="#d9534f", radius=5, text_dx=12, text_dy=-12)
    draw_items(canvas, points, transform, color="#0275d8", radius=6, text_dx=12, text_dy=12)

    canvas.create_text(
        20,
        WINDOW_H - 30,
        anchor="w",
        text=(
            f"Всего объектов: {len(positions)} | "
            f"узлов j_*: {len(junctions)} | стрелок point*: {len(points)} | "
            f"сегментов: {len(segments)} | диагоналей: {len(diagonals)}"
        ),
        fill="#1b1b1b",
        font=("Arial", 11, "bold"),
    )

    warning_y = WINDOW_H - 55
    if missing_segments:
        canvas.create_text(
            20,
            warning_y,
            anchor="w",
            text=f"Не найдены точки для сегментов: {missing_segments}",
            fill="#8b1e1e",
            font=("Arial", 10, "bold"),
        )
        warning_y -= 22

    if missing_diagonals:
        canvas.create_text(
            20,
            warning_y,
            anchor="w",
            text=f"Ошибки диагоналей: {missing_diagonals}",
            fill="#8b1e1e",
            font=("Arial", 10, "bold"),
        )

    root.mainloop()


if __name__ == "__main__":
    main()

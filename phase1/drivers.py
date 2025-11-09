import random


def load_drivers(path: str) -> list[dict]:
    """
    Manually parse drivers CSV → [{'id', 'x', 'y'}] (ints).
    Accept x/px/#initial px → x and y/py → y. Skip negatives; warn if x>50 or y>30.
    IDs start at 1. Raise if file is empty or headers missing.
    """
    max_x, max_y = 50, 30
    drivers: list[dict] = []

    try:
        # Read entire file and split into lines
        with open(path, "r", encoding="utf-8-sig") as f:
            lines = f.read().splitlines()

        # Empty file → hard error
        if not lines:
            raise ValueError(f"{path}: file is empty (no header row).")

        # Parse header row
        headers = [h.strip() for h in lines[0].split(",")]
        norm = [h.lstrip("#").strip().lower() for h in headers]

        # Helper: find original header name by trying candidates
        def find_original(candidates):
            for cand in candidates:
                if cand in norm:
                    j = norm.index(cand)
                    return headers[j]  # return ORIGINAL header text
            return None

        # Map headers to x,y
        x_key = find_original(["x", "px", "initial px"])
        y_key = find_original(["y", "py"])
        if x_key is None or y_key is None:
            raise ValueError(f"{path}: missing px/py (mapped to x/y). Found headers: {headers}")

        # Go through data rows
        next_id = 1  # compact ids for kept rows: 1,2,3,...
        for lineno, line in enumerate(lines[1:], start=2):
            if not line.strip():
                continue
            values = [v.strip() for v in line.split(",")]
            row = {headers[j]: values[j] for j in range(min(len(headers), len(values)))}

            # Parse numbers as ints
            try:
                x = int(row.get(x_key, ""))
                y = int(row.get(y_key, ""))
            except ValueError:
                raise ValueError(f"{path}: row {lineno}: x or y is not a number.")

            # Group rule: skip negatives
            if x < 0 or y < 0:
                print(f"Warning: {path} row {lineno}: negative coord (x={x}, y={y}) -> row ignored.")
                continue

            # Warn on large values, but keep
            if x > max_x or y > max_y:
                print(f"Warning: {path} row {lineno}: (x={x}, y={y}) looks outside 50x30.")

            drivers.append({
                "id": next_id,
                "x": x,
                "y": y,
                "vx": 0,
                "vy": 0,
                "tx": 0,
                "ty": 0,
                "target_id": None,
            })
            next_id += 1

        return drivers

    except FileNotFoundError:
        print(f"Error: The file at path '{path}' was not found.")
        return []


def generate_drivers(n: int, width: int = 50, height: int = 30) -> list[dict]:
    """
    Generates n drivers randomly for the grid. Used initially to
    generate drivers for the simulation, i.e., n is fixed throughout
    the simulation. Default grid size is 30 x 50, but can be modified.
    """
    try:
        n, width, height = int(n), int(width), int(height)
    except ValueError:
        return []
    drivers = []
    for i in range(n):
        drivers.append({
            "id": i,
            "x": random.randint(0, width),
            "y": random.randint(0, height),
            "vx": 0,
            "vy": 0,
            "tx": None,
            "ty": None,
            "target_id": None,
            "status": "waiting"
        })
    return drivers

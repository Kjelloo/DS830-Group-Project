def load_drivers(path: str) -> list[dict]:
    """Read drivers from a CSV.

- Use x/px/#initial px for x. Use y/py for y.
- Skip rows with bad numbers, negatives, or out of bounds (0<=x<=50, 0<=y<=30).
- IDs start at 1 for kept rows.
- Error if no header or missing x/y.

Examples
--------
File not found → empty list (hide prints):
>>> import io, contextlib
>>> buf = io.StringIO()
>>> with contextlib.redirect_stdout(buf):
...     out = load_drivers("data/no_such_file.csv")
>>> out
[]

Wrong headers → ValueError:
>>> import tempfile, os
>>> bad = "a,b\\n1,2\\n"
>>> f = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
>>> _ = f.write(bad.encode()); f.close()
>>> try:
...     _ = load_drivers(f.name)
... except ValueError:
...     print("ValueError")
ValueError
>>> os.unlink(f.name)

Header aliases (px, py) work:
>>> txt = "px,py\\n4,5\\n"
>>> f = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
>>> _ = f.write(txt.encode()); f.close()
>>> rows = load_drivers(f.name)
>>> len(rows)
1
>>> rows[0]["x"], rows[0]["y"]
(4, 5)
>>> os.unlink(f.name)

Skip negatives / out-of-bounds; keep the good row (hide prints):
>>> txt = "x,y\\n-1,5\\n5,31\\n50,30\\n"
>>> f = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
>>> _ = f.write(txt.encode()); f.close()
>>> buf = io.StringIO()
>>> with contextlib.redirect_stdout(buf):
...     rows = load_drivers(f.name)
>>> len(rows)
1
>>> rows[0]["x"], rows[0]["y"]
(50, 30)
>>> os.unlink(f.name)

Skip non-integers; keep the good row (hide prints):
>>> txt = "x,y\\nhello,2\\n3,world\\n4,5\\n"
>>> f = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
>>> _ = f.write(txt.encode()); f.close()
>>> buf = io.StringIO()
>>> with contextlib.redirect_stdout(buf):
...     rows = load_drivers(f.name)
>>> len(rows)
1
>>> rows[0]["x"], rows[0]["y"]
(4, 5)
>>> os.unlink(f.name)

Output shape and types:
>>> txt = "x,y\\n0,0\\n25,10\\n"
>>> f = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
>>> _ = f.write(txt.encode()); f.close()
>>> rows = load_drivers(f.name)
>>> len(rows)
2
>>> rows[0]["id"], rows[1]["id"]
(1, 2)
>>> all(isinstance(rows[0][k], int) for k in ["x","y","vx","vy","tx","ty"])
True
>>> rows[0]["target_id"] is None
True
>>> os.unlink(f.name)

    """

    max_x, max_y = 50, 30
    drivers: list[dict] = []

    try:
        with open(path, "r") as f:  
            header_line = f.readline()
            if not header_line:
                raise ValueError(f"{path}: file is empty (no header row).")

            headers = [h.strip() for h in header_line.strip().split(",")]
            norm = [h.lstrip("#").strip().lower() for h in headers]

            def find_original(cands: list[str]):
                for c in cands:
                    if c in norm:
                        j = norm.index(c)
                        return headers[j]
                return None

            x_key = find_original(["x", "px", "initial px"])
            y_key = find_original(["y", "py"])
            if x_key is None or y_key is None:
                raise ValueError(
                    f"{path}: missing required x/y headers. "
                    f"Accepted: x/px/#initial px and y/py. Found: {headers}"
                )

            next_id = 1
            for lineno, line in enumerate(f, start=2):
                if not line.strip():
                    continue
                values = [v.strip() for v in line.strip().split(",")]
                row = {headers[j]: values[j] for j in range(min(len(headers), len(values)))}

                try:
                    x = int(row.get(x_key, ""))
                    y = int(row.get(y_key, ""))
                except ValueError:
                    print(f"Warning: {path} row {lineno}: x or y not an integer -> skipped.")
                    continue

                if x < 0 or y < 0:
                    print(f"Warning: {path} row {lineno}: negative coord (x={x}, y={y}) -> skipped.")
                    continue

                if not (0 <= x <= max_x and 0 <= y <= max_y):
                    print(f"Warning: {path} row {lineno}: out of bounds (x={x}, y={y}) -> skipped.")
                    continue

                drivers.append({
                    "id": next_id,
                    "x": x, "y": y,
                    "vx": 0, "vy": 0,
                    "tx": 0, "ty": 0,
                    "target_id": None,
                })
                next_id += 1

    except FileNotFoundError:
        print(f"Error: The file at path '{path}' was not found.")
        return []

    return drivers




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

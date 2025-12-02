import random


def load_drivers(path: str) -> list[dict]:
    """ Read drivers from a CSV.
    - Use x/px/#initial px for x. Use y/py for y.
    - Skip rows with bad numbers, negatives, or out of bounds (0<=x<=50, 0<=y<=30).
    - IDs start at 1 for kept rows.
    - Error if no header or missing x/y.

    Tests
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
    the simulation. Default grid size is 30 x 50, but can be modified with width and height.

    Expected input for n, width and height is type int larger than or equal to 0.
    The function will accept whole  floats, e.g., 15.0 as 15, but not string type input,
    e.g. "15" or "15.0".

    Returns a list of dictionaries where each dictionary represents a driver,
    or crashes the simulation if TypeErrors or ValueErrors are raised.

    Tests
    --------
    >>> import random
    >>> random.seed(20)
    >>> drivers = generate_drivers(n=3, width=50, height=50)
    >>> for driver in drivers:
    ...     print(driver)
    ...
    {'id': 0, 'x': 46, 'y': 43, 'vx': 0, 'vy': 0, 'tx': None, 'ty': None, 'target_id': None}
    {'id': 1, 'x': 50, 'y': 49, 'vx': 0, 'vy': 0, 'tx': None, 'ty': None, 'target_id': None}
    {'id': 2, 'x': 9, 'y': 16, 'vx': 0, 'vy': 0, 'tx': None, 'ty': None, 'target_id': None}
    """
    # Type and value handling of parameters.
    params = {
        "n": n,
        "width": width,
        "height": height
    }
    for key, val in params.items():
        if not (isinstance(val, int) or (isinstance(val, float) and val.is_integer())):
            raise TypeError(f"{key} must be an integer.")
        if 0 > val:
            raise ValueError(f"{key} must be larger than or equal to 0.")

    # Conversion of parameters
    n, width, height = int(n), int(width), int(height)

    # Generate drivers randomly
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
            "target_id": None
        })
    return drivers


def load_requests(path: str) -> list[dict]:
    """
    Load and validate delivery requests from a CSV file, converting them
    into request in a dictionary.

    Each request represents a delivery with pickup and delivery
    coordinates, with a request time.

    The resulting schema for each request is: \n
    {
        'id': int,              # unique sequential identifier \n
        't': int,               # request time \n
        'px': int,              # pickup x-coordinate \n
        'py': int,              # pickup y-coordinate \n
        'dx': int,              # delivery x-coordinate \n
        'dy': int,              # delivery y-coordinate \n
        'driver_id': None,      # driver associated with the request (None if unassigned) \n
        'status': 'waiting'     # request status
    }

    Args:
        path (str): Path to the CSV file containing request data.

    Returns:
        list[dict]: A list of request dictionaries following the above schema.

    Notes:
        - The grid boundaries are fixed at max_x = 50 and max_y = 30.
        - Requests with out-of-bounds coordinates are skipped.
        - The unique `id` field is assigned incrementally starting from 1.


    Tests
    --------
    Simple good row:
    >>> import tempfile, os
    >>> txt = "#request time,pickup x,pickup y,delivery x,delivery y\\n7,5,5,5,5\\n"
    >>> f = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
    >>> _ = f.write(txt.encode()); f.close()
    >>> out = load_requests(f.name)
    >>> len(out)
    1
    >>> out[0]["t"], out[0]["px"], out[0]["py"], out[0]["dx"], out[0]["dy"]
    (7, 5, 5, 5, 5)
    >>> os.unlink(f.name)

    Non-integer value -> ValueError:
    >>> bad = "#request time,pickup x,pickup y,delivery x,delivery y\\nhello,1,2,3,4\\n"
    >>> f = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
    >>> _ = f.write(bad.encode()); f.close()
    >>> try:
    ...     _ = load_requests(f.name)
    ... except ValueError:
    ...     print("ValueError")
    ValueError
    >>> os.unlink(f.name)

    Drop bad rows (t<0 or out of bounds). Keep only the valid one:
    >>> txt = (
    ...     "#request time,pickup x,pickup y,delivery x,delivery y\\n"
    ...     "-1,0,0,0,0\\n"    # drop: t < 0
    ...     "0,60,0,0,0\\n"    # drop: px > 50
    ...     "0,0,0,0,31\\n"    # drop: dy > 30
    ...     "0,1,2,3,4\\n"     # keep
    ... )
    >>> f = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
    >>> _ = f.write(txt.encode()); f.close()
    >>> out = load_requests(f.name)
    >>> len(out)
    1
    >>> out[0]["t"], out[0]["px"], out[0]["py"], out[0]["dx"], out[0]["dy"]
    (0, 1, 2, 3, 4)
    >>> os.unlink(f.name)

            Wrong or missing headers → Exception:
    >>> import tempfile, os
    >>> bad = "a,b\\n1,2\\n"
    >>> f = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
    >>> _ = f.write(bad.encode()); f.close()
    >>> try:
    ...     _ = load_requests(f.name)
    ... except Exception:
    ...     print("Exception")
    Exception
    >>> os.unlink(f.name)
    """
    # Define grid boundaries for valid coordinates
    max_x, max_y = 50, 30

    requests = []

    try:
        with open(path, 'r') as file:
            # Read headers and split by commas
            headers = file.readline().strip().split(',')

            # Iterate through each remaining line in the file
            for i, line in enumerate(file, start=1):
                values = line.strip().split(',')

                # Create a dictionary, mapping each header to its corresponding value, converted to int
                request_data = {headers[j].strip(): int(values[j]) for j in range(len(headers))}

                # Validate that pickup and delivery coordinates are within grid bounds
                # and that request time is zero or positive
                if (request_data['#request time'] >= 0 and
                        0 <= request_data['pickup x'] <= max_x and
                        0 <= request_data['pickup y'] <= max_y and
                        0 <= request_data['delivery x'] <= max_x and
                        0 <= request_data['delivery y'] <= max_y):
                    # Build a structured request dictionary following the defined schema
                    request = {
                        'id': i,
                        't': request_data['#request time'],
                        'px': request_data['pickup x'],
                        'py': request_data['pickup y'],
                        'dx': request_data['delivery x'],
                        'dy': request_data['delivery y'],
                        'driver_id': None,
                        'status': 'waiting',
                        't_wait': 0,
                    }

                    requests.append(request)
    except FileNotFoundError:
        print(f"Error: The file at path '{path}' was not found.")
        return []

    return requests


def generate_requests(start_t: int, out_list: list,
                      req_rate: int, width: int = 50, height: int = 30) -> None:
    """
    Generates delivery requests probabilistically based on req_rate within grid bounds.
    Is used throughout the simulation to generate requests continually.

    Expected input for start_t, req_rate, width, and height is type int (or float fore req_rate)
    larger than or equal to 0. The function will accept whole  floats, e.g., 15.0 as 15,
    but not string type input, e.g. "15" or "15.0". Expected input for out_list is type list.

    Probabilistically appends requests to out_list if input is correct or raises ValueError
    or TypeError if needed and crashes the simulation.

    Tests
    --------
    >>> import random
    >>> reqs = []
    >>> random.seed(20)
    >>> generate_requests(start_t=0,out_list=reqs,req_rate=40,width=50,height=30)
    >>> generate_requests(start_t=1,out_list=reqs,req_rate=40,width=50,height=30)
    >>> generate_requests(start_t=2,out_list=reqs,req_rate=40,width=50,height=30)
    >>> for req in reqs:
    ...     print(req)
    ...
    {'id': 0, 't': 0, 'px': 43, 'py': 25, 'dx': 49, 'dy': 28, 't_wait': 0, 'status': 'waiting', 'driver_id': None}
    {'id': 1, 't': 1, 'px': 16, 'py': 21, 'dx': 40, 'dy': 27, 't_wait': 0, 'status': 'waiting', 'driver_id': None}
    {'id': 2, 't': 2, 'px': 20, 'py': 18, 'dx': 10, 'dy': 0, 't_wait': 0, 'status': 'waiting', 'driver_id': None}
    """

    # Type handling of out_list
    if not (isinstance(out_list, list)):
        raise TypeError("out_list must be of type list.")

    # Validate start_t
    if not (isinstance(start_t, int) or (isinstance(start_t, float) and start_t.is_integer())):
        raise TypeError("start_t must be an integer.")
    if start_t < 0:
        raise ValueError("start_t must be larger than or equal to 0.")

    # Validate req_rate
    if not (isinstance(req_rate, int) or isinstance(req_rate, float)):
        raise TypeError("req_rate must be of type int/float.")
    if req_rate < 0:
        raise ValueError("req_rate must be larger than or equal to 0.")

    # Validate width
    if not (isinstance(width, int) or (isinstance(width, float) and width.is_integer())):
        raise TypeError("width must be an integer.")
    if width < 0:
        raise ValueError("width must be larger than or equal to 0.")

    # Validate height
    if not (isinstance(height, int) or (isinstance(height, float) and height.is_integer())):
        raise TypeError("height must be an integer.")
    if height < 0:
        raise ValueError("height must be larger than or equal to 0.")

    # Probabilistic generation of requests
    largest_id = max((d["id"] for d in out_list), default=-1)
    if random.random() < req_rate:
        req = {
            "id": 0 if largest_id == -1 else largest_id + 1,
            "t": start_t,
            "px": random.randint(0, width),
            "py": random.randint(0, height),
            "dx": random.randint(0, width),
            "dy": random.randint(0, height),
            "t_wait": 0,
            "status": "waiting",
            "driver_id": None
        }
        out_list.append(req)


if __name__ == "__main__":
    import doctest

    doctest.testmod()

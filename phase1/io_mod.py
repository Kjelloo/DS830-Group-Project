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

                # Create a dictionary mapping each header to its corresponding value, converted to int
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

def init_logger(log_dir: str = "logs", filename: str = None) -> None:
    pass

def log_event(event_type: str, t: int, driver_id: int, request_id: int, total_distance: float) -> None:
    pass

def generate_drivers(n: int, width: int=50, height: int=30) -> list[dict]:
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
            "id":i,
            "x":random.randint(0,width),
            "y":random.randint(0,height),
            "vx": 0,
            "vy": 0,
            "tx": None,
            "ty": None,
            "target_id": None,
            "status": "waiting"
        })
    return drivers

def generate_requests(start_t: int, out_list: list,
                      req_rate: int, width: int=50, height: int=30) -> None:
    """
    Generates delivery requests probabilistically based on req_rate.
    """
    # Error handling
    try:
        start_t = int(start_t)
        req_rate = int(req_rate)
        width = int(width)
        height = int(height)
    except ValueError:
        return None
    if start_t < 0: return None
    if type(out_list) == list: pass
    else: return
    # Probabilistic generation
    req_per_step = req_rate
    largest_id = max((d["id"] for d in out_list), default=-1)
    if random.random() < req_per_step:
        req = {
            "id": 0 if largest_id == -1 else largest_id + 1,
            "t": start_t,
            "px": random.randint(0,width),
            "py": random.randint(0,height),
            "dx": random.randint(0,width),
            "dy": random.randint(0,height),
            "t_wait": 0,
            "status": "waiting",
            "driver_id": None
        }
        out_list.append(req)


def main():
    #Testing 'generate_drivers'
    print("generate_drivers")
    drivers = generate_drivers(5)
    for i in drivers:
        print(i)

    # Testing 'generate_requests'
    print("generate_requests")
    out_list = []
    generate_requests(0,out_list, 30, 30, 50)
    for i in out_list:
        for key, value in i.items():
            print(key, value)

# Run main function if not imported.
if __name__ == '__main__':
    main()
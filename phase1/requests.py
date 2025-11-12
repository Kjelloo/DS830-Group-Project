import random


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

                    Examples
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
    if type(out_list) == list:
        pass
    else:
        return
    # Probabilistic generation
    req_per_step = req_rate
    largest_id = max((d["id"] for d in out_list), default=-1)
    if random.random() < req_per_step:
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

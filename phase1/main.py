# from dispatch_ui import main

drivers_placeholder = [
    {'id': 1, 'x': 10, 'y': 10, "speed": 1.0, "target_id": None|int},
    {'id': 2, 'x': 20, 'y': 20, "speed": 1.0, "target_id": None|int},
    {'id': 3, 'x': 30, 'y': 30, "speed": 1.0, "target_id": None|int},
]

requests_placeholder = [
    {'id': 1, 't': 0, 'px': 1, 'py': 6, 'dx': 41, 'dy': 20, 'driver_id': None|int, 'status': 'waiting'},
    {'id': 2, 't': 1, 'px': 4, 'py': 25, 'dx': 3, 'dy': 21, 'driver_id': None|int, 'status': 'waiting'},
    {'id': 3, 't': 2, 'px': 10, 'py': 22, 'dx': 41, 'dy': 25, 'driver_id': None|int, 'status': 'waiting'},
    {'id': 4, 't': 5, 'px': 44, 'py': 30, 'dx': 45, 'dy': 29, 'driver_id': None|int, 'status': 'waiting'},
    {'id': 5, 't': 10, 'px': 34, 'py': 6, 'dx': 39, 'dy': 27, 'driver_id': None|int, 'status': 'waiting'},
    {'id': 6, 't': 20, 'px': 16, 'py': 25, 'dx': 50, 'dy': 28, 'driver_id': None|int, 'status': 'waiting'},
    {'id': 7, 't': 30, 'px': 17, 'py': 17, 'dx': 18, 'dy': 2, 'driver_id': None|int, 'status': 'waiting'},
    {'id': 8, 't': 45, 'px': 9, 'py': 29, 'dx': 44, 'dy': 22, 'driver_id': None|int, 'status': 'waiting'},
    {'id': 9, 't': 60, 'px': 47, 'py': 30, 'dx': 3, 'dy': 7, 'driver_id': None|int, 'status': 'waiting'},
    {'id': 10, 't': 90, 'px': 0, 'py': 12, 'dx': 15, 'dy': 1, 'driver_id': None|int, 'status': 'waiting'},
    {'id': 11, 't': 110, 'px': 29, 'py': 23, 'dx': 41, 'dy': 5, 'driver_id': None|int, 'status': 'waiting'}
]

state_placeholder = {
    "t": 0,
    "drivers": drivers_placeholder,
    "req_pending": [],
    "req_future": requests_placeholder,
    "served": 0,
    "expired": 0,
    "timeout": 0,
    "served_waits": [],
    "req_rate": 1.0,
    "width": 50,
    "height": 30,
}

metrics = {
    "served": 0,
    "expired": 0,
    "avg_wait": 0.0,
}

def load_request(path: str) -> list[dict]:
    """
    Load and validate delivery requests from a CSV file, converting them
    into request in a dictionary.

    Each request represents a delivery with pickup and delivery
    coordinates, with a request time.

    The resulting schema for each request is: \n
    {
        "id": int,              # unique sequential identifier \n
        "t": int,               # request time \n
        "px": int,              # pickup x-coordinate \n
        "py": int,              # pickup y-coordinate \n
        "dx": int,              # delivery x-coordinate \n
        "dy": int,              # delivery y-coordinate \n
        "driver_id": None,      # driver associated with the request (None if unassigned) \n
        "status": "waiting"     # request status
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
                if (request_data["#request time"] >= 0 and
                    0 <= request_data['pickup x'] <= max_x and
                    0 <= request_data['pickup y'] <= max_y and
                    0 <= request_data['delivery x'] <= max_x and
                    0 <= request_data['delivery y'] <= max_y):

                    # Build a structured request dictionary following the defined schema
                    request = {
                        "id": i,
                        "t": request_data['#request time'],
                        "px": request_data['pickup x'],
                        "py": request_data['pickup y'],
                        "dx": request_data['delivery x'],
                        "dy": request_data['delivery y'],
                        "driver_id": None,
                        "status": "waiting"
                    }

                    requests.append(request)
    except FileNotFoundError:
        print(f"Error: The file at path '{path}' was not found.")
        return []

    return requests

def simulate_step(state: dict) -> (state, metrics):
    """
    Simulate a single time step in the delivery system.

    Args:
        state (dict): The current state of the delivery system.
    Returns:
        dict: The updated state after simulating one time step.
    """

    # If there are future requests scheduled for the current time, move them to pending
    for req in state["req_future"][:]:
        if req["t"] == state["t"]:
            state["req_pending"].append(req)
            state["req_future"].remove(req)

    # Todo: refactor into helper function
    # Assign available drivers to pending requests based on proximity
    for req in state["req_pending"]:
        if req["t"] == state["t"]:
            if req["status"] == "waiting":
                closest_driver = None

                # use a large initial value for minimum distance
                min_distance = float('inf')

                # Iterate through drivers to find the closest available one
                for driver in state["drivers"]:
                    if driver["target_id"] is not type(int):
                        # Calculate Euclidean plane distance between driver and request pickup location
                        # sqrt((x2 - x1)^2 + (y2 - y1)^2)
                        distance = ((driver["x"] - req["px"]) ** 2 + (driver["y"] - req["py"]) ** 2) ** 0.5

                        # Determine if this driver is closer than the current closest
                        if distance < min_distance:
                            min_distance = distance
                            closest_driver = driver

                if closest_driver:
                    req["driver_id"] = closest_driver["id"]
                    req["status"] = "assigned"
                    closest_driver["target_id"] = req["id"]
                else:
                    # No available drivers; request remains waiting
                    # TODO: Maybe add wait time increment here?
                    continue

    # If requests have expired, update their status and increment expired count

    # Move active drivers toward their assigned requests

    # If drivers reach their pickup location, update drivers and requests accordingly

    # If drivers reach their delivery location, update drivers and requests accordingly

    # Update average wait time for served requests

    # Increment the time step

    # Return the updated state and metrics

    return state, metrics

# TODO: Add stubs for the other functions here
backend = {
    "load_requests": load_request,
}

if __name__ == "__main__":
    # print(load_request("data/requests.csv"))
    print(simulate_step(state_placeholder)[0]["drivers"])
    # main(backend) TODO: Uncomment when all six functions are done
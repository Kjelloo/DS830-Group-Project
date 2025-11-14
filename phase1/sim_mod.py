if __name__ == "__main__":
    # To allow for direct testing of this module
    import metrics, io_mod
else:
    from phase1 import metrics
    from phase1 import io_mod
from typing import Optional

def _is_driver_dict(d: dict) -> bool:
    """
    Check if a dictionary has all required keys for a driver.

    Return:
        bool: True if all required keys are present, False otherwise.

    """
    required_keys = {"id", "x", "y", "vx", "vy", "tx", "ty"}
    return required_keys.issubset(d.keys())


def _is_request_dict(r: dict) -> bool:
    """
    Check if a dictionary has all required keys for a request.

    Returns:
        bool: True if all required keys are present, False otherwise.
    """
    required_keys = {"id", "t", "px", "py", "dx", "dy", "driver_id", "status", "t_wait"}
    return required_keys.issubset(r.keys())


def _is_state_dict(s: dict) -> bool:
    """
    Check if a dictionary has all required keys for the simulation state.

    Returns:
        bool: True if all required keys are present, False otherwise.
    """
    required_keys = {"t", "drivers", "pending", "future", "served", "expired", "timeout", "served_waits", "req_rate", "width", "height"}
    return required_keys.issubset(s.keys())


def init_state(drivers: list[dict], requests: list[dict], timeout: int, req_rate: float, width: int = 50, height: int = 30) -> dict:
    """
    Build the initial simulation state (t = 0), put requests into pending or future based on t.

    Args:
        drivers (list[dict]): List of driver dictionaries.
        requests (list[dict]): List of request dictionaries.
        timeout (int): Maximum waiting time for requests.
        req_rate (float): Request generation rate.
        width (int): Width of the simulation grid.
        height (int): Height of the simulation grid.

    Returns:
        dict: The initial state of the simulation.

    Test valid initialization with one driver and one immediate request (t = 0):
    >>> drivers = [{"id": 1, "x": 0, "y": 0, "vx": 0, "vy": 0, "tx": 0, "ty": 0}]
    >>> requests = [{"id": 10, "t": 0, "px": 5, "py": 5, "dx": 10, "dy": 10, "driver_id": None, "status": "waiting", "t_wait": 0}]
    >>> state = init_state(drivers, requests, 30, 0.5, 100, 100)

    >>> len(state["drivers"])
    1
    >>> len(state["pending"])
    1
    >>> len(state["future"])
    0

    Test with future requests (t > 0):
    >>> requests_future = [{"id": 20, "t": 5, "px": 2, "py": 3, "dx": 8, "dy": 9, "driver_id": None, "status": "waiting", "t_wait": 0}]
    >>> state2 = init_state([], requests_future, 20, 1.0, 50, 50)
    >>> len(state2["pending"])
    0
    >>> len(state2["future"])
    1
    >>> state2["future"][0]["t"]
    5

    Test with invalid driver dictionary (missing keys):
    >>> init_state([{"id": 1, "x": 0, "y": 0}], requests, 30, 0.5, 100, 100)
    Traceback (most recent call last):
        ...
    ValueError: All driver dictionaries must contain the required keys: 'id', 'x', 'y', 'vx', 'vy', 'tx', 'ty'.

    Test with invalid request dictionary (missing keys):
    >>> init_state(drivers, [{"id": 10, "t": 0, "px": 5, "py": 5}], 30, 0.5, 100, 100)
    Traceback (most recent call last):
        ...
    ValueError: All request dictionaries must contain the required keys: 'id', 't', 'px', 'py', 'dx', 'dy', 'driver_id', 'status', 't_wait'.

    Test output state structure:
    >>> state3 = init_state(drivers, requests, 30, 0.5, 100, 100)
    >>> isinstance(state3, dict)
    True
    >>> _is_state_dict(state3)
    True
    """

    if not isinstance(drivers, list):
        raise ValueError("Drivers must be provided as lists of dictionaries.")

    if not isinstance(requests, list):
        raise ValueError("Requests must be provided as a list of dictionaries.")

    if not all(isinstance(d, dict) for d in drivers):
        raise ValueError("All drivers must be dictionaries.")

    if not all(_is_driver_dict(d) for d in drivers):
        raise ValueError("All driver dictionaries must contain the required keys: 'id', 'x', 'y', 'vx', 'vy', 'tx', 'ty'.")

    if not all(_is_request_dict(r) for r in requests):
        raise ValueError("All request dictionaries must contain the required keys: 'id', 't', 'px', 'py', 'dx', 'dy', 'driver_id', 'status', 't_wait'.")

    if not all(isinstance(r, dict) for r in requests):
        raise ValueError("All requests must be dictionaries.")

    if not isinstance(timeout, int) or timeout <= 0:
        raise ValueError("Timeout must be a positive integer.")

    if not isinstance(req_rate, (int, float)) or req_rate <= 0:
        raise ValueError("Request rate must be a non-negative number.")

    if not isinstance(width, int) or width <= 0:
        raise ValueError("Width must be a positive integer.")

    if not isinstance(height, int) or height <= 0:
        raise ValueError("Height must be a positive integer.")

    # Start a new simulation log file
    metrics.start_new_simulation_log()

    return {
        "t": 0,
        "drivers": drivers,
        "pending": requests,
        "future": [],
        "served": 0,
        "expired": 0,
        "timeout": int(timeout),
        "served_waits": [],
        "req_rate": float(req_rate),
        "width": int(width),
        "height": int(height),
    }


def simulate_step(state: dict) -> tuple[dict, dict]:
    """
    Simulates a step in the simulation. Updates the state and computes metrics.

    It performs the following operations in order:

    1. Increments the simulation time.
    2. Generates new requests based on the request rate.
    3. Assigns requests to available drivers.
    4. Moves drivers towards their targets.
    5. Updates waiting times for pending requests.
    6. Handles request expirations.

    Args:
        state (dict): The current state of the simulation.
    Returns:
        tuple[dict, dict]: Updated state and metrics dictionary.

    Test with a simple scenario of one driver and one request:
    >>> drivers = [{"id": 1, "x": 1, "y": 1, "vx": 0, "vy": 0, "tx": 0, "ty": 0}]
    >>> requests_list = [{"id": 10, "t": 0, "px": 5, "py": 5, "dx": 10, "dy": 10, "driver_id": None, "status": "waiting", "t_wait": 0}]
    >>> state = init_state(drivers, requests_list, 30, 0.5, 100, 100)
    >>> new_state, metrics_dict = simulate_step(state)
    >>> new_state["t"]
    1

    >>> isinstance(new_state, dict)
    True

    >>> isinstance(metrics_dict, dict)
    True

    >>> _is_state_dict(new_state)
    True

    >>> simulate_step({})
    Traceback (most recent call last):
        ...
    ValueError: State dictionary is missing required keys.
    """
    if not isinstance(state, dict):
        raise ValueError("State must be provided as a dictionary.")

    if not _is_state_dict(state):
        raise ValueError("State dictionary is missing required keys.")

    state["t"] += 1
    io_mod.generate_requests(state["t"], state["pending"], state["req_rate"])
    _assign_requests(state["drivers"], state["pending"])
    _move_drivers(state["drivers"], state["pending"], state)
    _update_waits(state["pending"])
    _handle_expirations(state)

    # handle metrics
    metrics_dict = {
        "served": state["served"],
        "expired": state["expired"],
        "avg_wait": sum(state["served_waits"]) / state["served"] if len(state["served_waits"]) > 0 else 0
    }

    # Record metrics for visualization
    metrics.record_step_to_file(state, metrics_dict)

    # Remove expired and delivered requests from pending list
    state["pending"] = [r for r in state["pending"] if r["status"] not in ("expired", "delivered")]

    return state, metrics_dict


def _assign_requests(drivers: list[dict], requests: list[dict]) -> None:
    """
    For each request iteratively assign the closest available driver.
    """

    # Type checking of drivers and requests.
    if not type(drivers) is list or not type(requests) is list:
        raise TypeError("drivers and requests must be of type list.")
    # Returning if no requests are present.
    if len(requests) == 0:
        return

    # Making sure drivers and requests are lists of dicts. Check can be removed if needed.
    for r in requests:
        if not _is_request_dict(r):
            raise ValueError("Request dictionary is missing required keys.")
    for d in drivers:
        if not _is_driver_dict(d):
            raise ValueError("Driver dictionary is missing required keys.")


    # Iteratively assigns driver to request if requests exists and drivers are available.
    for request in requests:
        if request["status"] == "waiting":
            closest_driver = _calculate_closest_driver(request, drivers)
            if closest_driver is not None:

                closest_driver.update({
                    "target_id": request["id"],
                    "tx": request["px"],
                    "ty": request["py"]
                })
                request.update({
                    "driver_id": closest_driver["id"],
                    "status": "assigned"
                })
                _compute_velocity_vector(closest_driver)


def _compute_velocity_vector(driver: dict, velocity: int = 5) -> None:
    """
    Computes a velocity vector based on a drivers position and his target.

    Example:
        >>> driver = {"id":0,"x":14,"y":10,"vx":None,"vy":None,"tx":30,"ty":45,"target_id":None}
        >>> driver
        {'id': 0, 'x': 14, 'y': 10, 'vx': None, 'vy': None, 'tx': 30, 'ty': 45, 'target_id': None}
        >>> _compute_velocity_vector(driver, velocity = 5)
        >>> driver
        {'id': 0, 'x': 14, 'y': 10, 'vx': 2.078798801338972, 'vy': 4.547372377929001, 'tx': 30, 'ty': 45, 'target_id': None}
    """

    # Type and Value error handling
    if not type(driver) is dict:
        raise TypeError("driver must be of type dict.")
    if not (isinstance(velocity, int) or (isinstance(velocity, float) and velocity % 1 == 0.0)):
        raise TypeError("velocity must be an integer.")
    if 0 > velocity:
        raise ValueError("velocity must be larger than or equal to 0.")
    velocity = int(velocity)

    d_vector = (driver["tx"] - driver["x"], driver["ty"] - driver["y"])  # compute direction vector
    d_magnitude = (d_vector[0] ** 2 + d_vector[1] ** 2) ** 0.5  # compute magnitude of D
    if d_magnitude == 0:
        driver["vx"], driver["vy"] = 0, 0
        return
    d_normalized = (d_vector[0] / d_magnitude, d_vector[1] / d_magnitude)  # normalize D
    d_velocity = (d_normalized[0] * velocity, d_normalized[1] * velocity)  # Multiply with velocity
    driver["vx"], driver["vy"] = d_velocity  # update vx and vx in driver dict


def _calculate_closest_driver(req: dict, drivers: list[dict]) -> Optional[dict]:
    """
    Calculate the closest available driver to the request.

    Args:
        req (dict): The request dictionary.
        drivers (list[dict]): List of driver dictionaries.

    Returns:
        dict | None: The closest available driver dictionary or None if no drivers are available.
    """

    # Checking if input are correct types
    if not _is_request_dict(req):
        raise TypeError("Request dictionary is missing required keys.")

    if not type(drivers) is list:
        raise TypeError("drivers must be of type list.")

    for d in drivers:
        if not _is_driver_dict(d):
            raise ValueError("Driver dictionary is missing required keys.")

    closest_driver = None
    min_distance = float('inf')

    for driver in (d for d in drivers if d["target_id"] is None):
        x_dist = driver["x"] - req["px"]
        y_dist = driver["y"] - req["py"]
        driver_dist = (x_dist ** 2 + y_dist ** 2) ** 0.5
        if driver_dist < min_distance:
            min_distance = driver_dist
            closest_driver = driver

    return closest_driver # Har testet denne funktion og den virker som den skal.


def _within_one_step(driver: dict) -> bool:
    """
    Boolean function that checks if the drivers distance to his target is less than
    the distance he can travel within one step. Used as a helper function
    for handle_transactions - transactions happens if this function returns True.
    """

    # Input handling
    if not type(driver) is dict:
        raise TypeError("driver must be of type dict.")
    if driver["tx"] is None or driver["ty"] is None or driver["vx"] is None or driver["vy"] is None:
        return False

    one_step_distance = (driver["vx"] ** 2 + driver["vy"] ** 2) ** 0.5
    actual_distance = ((driver["tx"] - driver["x"]) ** 2 + (driver["ty"] - driver["y"]) ** 2) ** 0.5
    return actual_distance < one_step_distance


def _handle_driver_transaction(driver: dict, requests: list[dict], state: dict) -> bool:
    """
    Handles pick-up or drop-off for a single driver if within one step of target.
    Returns True if a transaction occurred (to prevent movement in same step).
    """

    # Handle type errors
    if not type(driver) is dict:
        raise TypeError("driver must be of type dict.")
    if not type(requests) is list:
        raise TypeError("requests must be of type list.")
    if not type(state) is dict:
        raise TypeError("state must be of type dict.")

    if driver["target_id"] is None:
        return False

    if not _within_one_step(driver):
        return False

    req = next((r for r in requests if r["id"] == driver["target_id"]), None)
    if req is None:
        return False

    if req["status"] == "assigned":  # pick up
        # Move driver to exact pickup location
        driver["x"] = req["px"]
        driver["y"] = req["py"]
        # Set new target to drop-off location
        driver["tx"], driver["ty"] = req["dx"], req["dy"]
        driver["vx"], driver["vy"] = 0, 0
        req["status"] = "picked"
        return True

    elif req["status"] == "picked":  # deliver
        # Move driver to exact drop-off location
        driver["x"] = req["dx"]
        driver["y"] = req["dy"]
        req["status"] = "delivered"
        driver.update({
            "target_id": None,
            "tx": None,
            "ty": None,
            "vx": 0,
            "vy": 0,
        })
        state["served"] += 1
        state["served_waits"].append(req["t_wait"])
        return True

    return False


def _move_drivers(drivers: list[dict], requests: list[dict], state: dict) -> None:
    """
    Handles transactions and moves drivers towards their targets.
    Transactions and movement are separated into different steps.
    """

    # Handle type error for drivers
    if not type(drivers) is list:
        raise TypeError("drivers must be a list.")
    # Handle type error for requests
    if not type(requests) is list:
        raise TypeError("requests must be a list.")
    # handle type error for state
    if not type(state) is dict:
        raise TypeError("state must be a dictionary.")

    for driver in drivers:
        if not _is_driver_dict(driver):
            raise ValueError("Driver dict is missing required keys.")
    for request in requests:
        if not _is_request_dict(request):
            raise ValueError("Request dict is missing required keys.")

    for driver in drivers:
        if driver["target_id"] is not None:
            # First check if a transaction should occur
            transaction_occurred = _handle_driver_transaction(driver, requests, state)

            # If transaction occurred, skip movement this step
            if transaction_occurred:
                continue

            # If driver has no velocity but has target, compute velocity first (don't move this step)
            if driver["vx"] == 0 and driver["vy"] == 0:
                _compute_velocity_vector(driver)
            else:
                # Move one step in target direction
                driver["x"] += driver["vx"]
                driver["y"] += driver["vy"]


def _handle_expirations(state: dict) -> None:
    """
    Checks if requests exceed max waiting time (timeout). If that is the case, requests are dropped
    and drivers are freed up.
    """

    # TypeError handling.
    if not type(state) is dict:
        raise TypeError("state must be a dictionary.")

    requests = state["pending"]
    drivers = state["drivers"]
    for request in requests:
        if request["status"] not in ("expired", "delivered"):
            if request["t_wait"] >= state["timeout"]:
                request["status"] = "expired"
                state["expired"] += 1
                driver_id = request.get("driver_id", None)
                if driver_id is not None:
                    driver = next((d for d in drivers if d["id"] == driver_id), None)
                    if driver:
                        driver.update({
                            "target_id": None,
                            "tx": None,
                            "ty": None,
                            "vx": 0,
                            "vy": 0
                        })


def _update_waits(requests: list[dict]):
    """
    Updates the waiting times of requests iteratively.
    """

    # Handling of type error
    if not type(requests) is list:
        raise TypeError("requests must be a list.")
    if len(requests) == 0:
        return

    # Iteratively update request waits
    for request in requests:
        if request["status"] not in ("expired", "delivered"):
            request["t_wait"] += 1


if __name__ == "__main__":
    import doctest
    doctest.testmod()
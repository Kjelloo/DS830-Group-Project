from phase1 import metrics
from phase1 import io_mod
from typing import Optional


def init_state(drivers, requests, timeout, req_rate, width, height) -> dict:
    """Build the starting simulation state (t = 0) compatible with simulate_step."""
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
    Simulates a step in the simulation.
    """
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

    # Har testet funktionen og den virker som den skal - requests bliver iterativt assigned til
    # den driver, der er tættest på.


    # Type checking of drivers and requests.
    if not type(drivers) is list or not type(requests) is list:
        raise TypeError("drivers and requests must be of type list.")
    # Returning if no requests are present.
    if len(requests) == 0:
        return

    # Making sure drivers and requests are lists of dicts. Check can be removed if needed.
    for r in requests:
        if not type(r) is dict:
            raise TypeError("request must be of type dict.")
    for d in drivers:
        if not type(d) is dict:
            raise TypeError("driver must be of type dict.")

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
    if not type(req) is dict:
        raise TypeError("req must be of type dict.")
    if not type(drivers) is list:
        raise TypeError("drivers must be of type list.")
    for d in drivers: # Ved ikke om det bliver for meget at iterere gennem alle drivers hver gang... slet hvis det er dumt.
        if type(d) is not dict:
            raise TypeError("driver must be of type dict.")

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

    # Handle type errors for drivers
    if not type(drivers) is list:
        raise TypeError("drivers must be a list.")
    for driver in drivers:
        if not type(driver) is dict:
            raise TypeError("driver must be a dictionary.")
    # Handle type errors for requests
    if not type(requests) is list:
        raise TypeError("requests must be a list.")
    for request in requests:
        if not type(request) is dict:
            raise TypeError("request must be a dictionary.")
    # handle type error for state
    if not type(state) is dict:
        raise TypeError("state must be a dictionary.")

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

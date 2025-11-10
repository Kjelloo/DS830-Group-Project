from phase1 import requests
from phase1 import metrics


def init_state(drivers, requests, timeout, req_rate, width, height) -> dict:
    """Build the starting simulation state (t = 0) compatible with simulate_step."""
    # Start a new simulation log file
    metrics.start_new_simulation_log()

    ds = [{
        "id": int(d["id"]),
        "x": float(d["x"]),
        "y": float(d["y"]),
        "vx": float(d["vx"]),
        "vy": float(d["vy"]),
        "target_id": d.get("target_id", None),
    } for d in drivers]

    pending, future = [], []
    for r in requests:
        req = {
            "id": int(r["id"]),
            "t": int(r["t"]),
            "px": int(r["px"]), "py": int(r["py"]),
            "dx": int(r["dx"]), "dy": int(r["dy"]),
            "driver_id": None,
            "status": "waiting",
            "t_wait": 0,
        }
        (pending if req["t"] <= 0 else future).append(req)

    return {
        "t": 0,
        "drivers": ds,
        "pending": pending,
        "future": future,
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
    requests.generate_requests(state["t"], state["pending"], state["req_rate"])
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
    Assigns requests to the closest available drivers based on proximity.
    """
    for request in requests:
        if request["status"] == "waiting":
            closest_driver = _calculate_closest_driver(request, drivers)
            if closest_driver is not None:
                closest_driver["target_id"] = request["id"]
                closest_driver["tx"] = request["px"]
                closest_driver["ty"] = request["py"]
                request["driver_id"] = closest_driver["id"]
                request["status"] = "assigned"
                _compute_velocity_vector(closest_driver)


def _compute_velocity_vector(driver: dict, velocity: int = 5) -> None:
    """
    Computes a velocity vector based on a drivers position and his target.
    """
    D = (driver["tx"] - driver["x"], driver["ty"] - driver["y"])  # compute direction vector
    D_magnitude = (D[0] ** 2 + D[1] ** 2) ** 0.5  # compute magnitude of D
    if D_magnitude == 0:
        driver["vx"], driver["vy"] = 0, 0
        return
    D_normalized = (D[0] / D_magnitude, D[1] / D_magnitude)  # normalize D
    D_velocity = (D_normalized[0] * velocity, D_normalized[1] * velocity)  # Multiply with velocity
    driver["vx"], driver["vy"] = D_velocity  # update vx and vx in driver dict


def _calculate_closest_driver(req: dict, drivers: list[dict]) -> dict | None:
    """
    Calculate the closest available driver to the request.

    Args:
        req (dict): The request dictionary.
        drivers (list[dict]): List of driver dictionaries.

    Returns:
        dict | None: The closest available driver dictionary or None if no drivers are available.
    """
    closest_driver = None
    min_distance = float('inf')

    for driver in drivers:
        if driver['target_id'] is None:
            distance = ((req['px'] - driver['x']) ** 2 + (req['py'] - driver['y']) ** 2) ** 0.5
            if distance < min_distance:
                min_distance = distance
                closest_driver = driver

    return closest_driver


def _within_one_step(driver: dict) -> bool:
    """
    Boolean function that checks if the drivers distance to his target is less than
    the distance he can travel within one step. Used as a helper function
    for handle_transactions - transactions happens if this function returns True.
    """
    one_step_distance = (driver["vx"] ** 2 + driver["vy"] ** 2) ** 0.5
    actual_distance = ((driver["tx"] - driver["x"]) ** 2 + (driver["ty"] - driver["y"]) ** 2) ** 0.5
    return actual_distance < one_step_distance


def _handle_driver_transaction(driver: dict, requests: list[dict], state: dict) -> bool:
    """
    Handles pick-up or drop-off for a single driver if within one step of target.
    Returns True if a transaction occurred (to prevent movement in same step).
    """
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
    Updates the waiting times of drivers iteratively.
    """
    for request in requests:
        if request["status"] not in ("expired", "delivered"):
            request["t_wait"] += 1

from phase1 import io_mod


def init_state(drivers, requests, timeout, rate, w, h):
    state = {
        "t": 0,
        "drivers": drivers,
        "pending": requests,
        "future": requests,
        "served": 0,
        "expired": 0,
        "timeout": timeout,
        "served_waits": [],
        "req_rate": rate,
        "width": w,
        "height": h
    }
    return state

def simulate_step(state: dict) -> tuple[dict, dict]:
    """
    Simulates a step in the simulation.
    """
    io_mod.generate_requests(state["t"], state["pending"], state["req_rate"])
    assign_requests(state["drivers"], state["pending"])
    handle_transactions(state["drivers"], state["pending"], state)
    move_drivers(state["drivers"])
    update_waits(state["pending"])
    handle_expirations(state)
    state["t"] += 1

    # handle metrics
    metrics = {
        "served": state["served"],
        "expired": state["expired"],
        "avg_wait": sum(state["served_waits"]) / state["served"] if len(state["served_waits"]) > 0 else 0
    }
    # Remove expired and delivered requests from pending list
    state["pending"] = [r for r in state["pending"] if r["status"] not in ("expired", "delivered")]

    return state, metrics

def assign_requests(drivers: list[dict], requests: list[dict]) -> None:
    """
    Assigns requests iteratively to drivers if drivers are not busy
    and if there exists waiting requests.
    """
    for driver in drivers:
        if driver["target_id"] is None:
            for request in requests:
                if request["status"] == "waiting":
                    # Could be written as a separate function.
                    driver["target_id"] = request["id"]
                    driver["tx"] = request["px"]
                    driver["ty"] = request["py"]
                    request["driver_id"] = driver["id"]
                    request["status"] = "assigned"
                    compute_velocity_vector(driver)
                    break

def compute_velocity_vector(driver: dict, velocity: int = 5) -> None:
    """
    Computes a velocity vector based on a drivers position and his target.
    """
    D = (driver["tx"] - driver["x"], driver["ty"] - driver["y"]) # compute direction vector
    D_magnitude = (D[0] ** 2 + D[1] ** 2)**0.5 # compute magnitude of D
    if D_magnitude == 0:
        driver["vx"], driver["vy"] = 0, 0
        return
    D_normalized = (D[0] / D_magnitude, D[1] / D_magnitude) # normalize D
    D_velocity = (D_normalized[0] * velocity, D_normalized[1] * velocity) # Multiply with velocity
    driver["vx"], driver["vy"] = D_velocity # update vx and vx in driver dict

def within_one_step(driver: dict) -> bool:
    """
    Boolean function that checks if the drivers distance to his target is less than
    the distance he can travel within one step. Used as a helper function
    for handle_transactions - transactions happens if this function returns True.
    """
    one_step_distance = (driver["vx"]**2 + driver["vy"]**2)**0.5
    actual_distance = ((driver["tx"] - driver["x"])**2 + (driver["ty"] - driver["y"])**2)**0.5
    return actual_distance < one_step_distance

def handle_transactions(drivers: list[dict], requests: list[dict], state: dict) -> None:
    """
    Handles pick-ups and drop-offs iteratively. For every driver, the function checks if
    an order can be picked up or dropped off, if that is the case it does just that.
    """
    for driver in drivers:
        if driver["target_id"] is not None:
            if within_one_step(driver):
                req = next((r for r in requests if r["id"] == driver["target_id"]), None) # expand this part
                if req is None:
                    continue

                if req["status"] == "assigned":  # pick up
                    driver["tx"], driver["ty"] = req["dx"], req["dy"]
                    compute_velocity_vector(driver)
                    req["status"] = "picked"

                elif req["status"] == "picked":  # deliver
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

def move_drivers(drivers: list[dict]) -> None:
    """
    Moves drivers towards their targets iteratively if a target exists.
    """
    for driver in drivers:
        if driver["target_id"] is not None:
            # Move one step in target direction
            driver["x"] += driver["vx"]
            driver["y"] += driver["vy"]

def handle_expirations(state: dict) -> None:
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

def update_waits(requests: list[dict]):
    """
    Updates the waiting times of drivers iteratively.
    """
    for request in requests:
        if request["status"] not in ("expired", "delivered"):
            request["t_wait"] += 1

"""Build the starting simulation state (t = 0) compatible with simulate_step."""

def init_state(drivers, requests, timeout, req_rate, width, height):
    ds = [{
        "id": int(d["id"]),
        "x": float(d["x"]),
        "y": float(d["y"]),
        "speed": float(d.get("speed", 2.0)),
        "target_id": d.get("target_id", None),
    } for d in drivers]

    req_pending, req_future = [], []
    for r in requests:
        rr = {
            "id": int(r["id"]),
            "t": int(r["t"]),
            "px": int(r["px"]), "py": int(r["py"]),
            "dx": int(r["dx"]), "dy": int(r["dy"]),
            "driver_id": None,
            "status": "waiting",
            "t_wait": 0,
        }
        (req_pending if rr["t"] <= 0 else req_future).append(rr)

    return {
        "t": 0,
        "drivers": ds,
        "req_pending": req_pending,
        "req_future": req_future,
        "served": 0,
        "expired": 0,
        "timeout": int(timeout),
        "served_waits": [],
        "req_rate": float(req_rate),
        "width": int(width),
        "height": int(height),
    }

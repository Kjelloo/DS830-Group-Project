"""Build the starting simulation state (time = 0)."""

def init_state(drivers, requests, timeout, req_rate, width, height):
    ds = [{"id": d["id"], "x": int(d["x"]), "y": int(d["y"]), "available": True}
          for d in drivers]

    pending, future = [], []
    for r in requests:
        rr = {
            "id": r["id"],
            "t": int(r["t"]),
            "px": int(r["px"]), "py": int(r["py"]),
            "dx": int(r["dx"]), "dy": int(r["dy"]),
            "driver_id": None,
            "status": "waiting",
        }
        (pending if rr["t"] <= 0 else future).append(rr)

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

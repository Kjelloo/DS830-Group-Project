from __future__ import annotations

from random import choice
from typing import List, Dict, Any, Optional

from phase2.DeliverySimulation import DeliverySimulation
from phase2.Driver import Driver, DriverStatus
from phase2.DriverGenerator import DriverGenerator
from phase2.Point import Point
from phase2.Request import Request, RequestStatus
from phase2.RequestGenerator import RequestGenerator
from phase2.behaviour.EarningsMaxBehaviour import EarningsMaxBehaviour
from phase2.behaviour.GreedyDistanceBehaviour import GreedyDistanceBehaviour


class GUIAdapter:
    """
    Adapter class to interface between the old GUI and the DeliverySimulation.

    This adapter implements the procedural backend contract expected by
    `gui._engine.BackendFns` so functions return UI-friendly plain dicts/lists
    (not None) and `init_state` returns the state dictionary used by the UI.
    """

    def __init__(self,
                 run_id: str,
                 delivery_simulation: DeliverySimulation):
        self.run_id = run_id
        self.simulation = delivery_simulation

    # ---------------------- CSV / I/O helpers ----------------------
    def load_drivers(self, path: str) -> List[Dict[str, Any]]:
        """Load drivers from a simple CSV and return a list of UI driver dicts.

        The UI expects a list of dicts (with at least 'x' and 'y'). We do not
        mutate the simulation here; the list is passed to `init_state` later.
        """
        out: List[Dict[str, Any]] = []
        try:
            with open(path, 'r') as f:
                lines = [ln.strip() for ln in f.readlines() if ln.strip()]
                if not lines:
                    return out
                # skip header if present
                start = 1 if ',' in lines[0] else 0
                for i, line in enumerate(lines[start:], start=1):
                    parts = line.split(',')
                    try:
                        x = float(parts[0])
                        y = float(parts[1])
                    except Exception:
                        continue
                    out.append({
                        'id': i,
                        'x': x,
                        'y': y,
                        'status': 'idle'
                    })
        except FileNotFoundError:
            print(f"Error: The file at path '{path}' was not found.")
        return out

    def load_requests(self, path: str) -> List[Dict[str, Any]]:
        """Load requests from a CSV and return a list of UI request dicts.

        Expected CSV columns: t,px,py,dx,dy (time, pickup x/y, dropoff x/y)
        """
        out: List[Dict[str, Any]] = []
        try:
            with open(path, 'r') as f:
                lines = [ln.strip() for ln in f.readlines() if ln.strip()]
                if not lines:
                    return out
                # assume header in first line if non-numeric
                start = 1 if any(c.isalpha() for c in lines[0]) else 0
                for i, line in enumerate(lines[start:], start=1):
                    parts = line.split(',')
                    if len(parts) < 5:
                        continue
                    try:
                        t = int(parts[0])
                        px = float(parts[1])
                        py = float(parts[2])
                        dx = float(parts[3])
                        dy = float(parts[4])
                    except Exception:
                        continue
                    out.append({
                        'id': i,
                        't': t,
                        'px': px,
                        'py': py,
                        'dx': dx,
                        'dy': dy,
                        'status': 'waiting'
                    })
        except FileNotFoundError:
            print(f"Error: The file at path '{path}' was not found.")
        return out

    # ---------------------- Generators used by UI ----------------------
    def generate_drivers(self, n: int, width: int = 50, height: int = 30) -> List[Dict[str, Any]]:
        """Return `n` randomly generated drivers as UI dicts.

        The UI expects a list of dicts; do not mutate the simulation here.
        """
        out: List[Dict[str, Any]] = []
        gen = DriverGenerator(run_id=self.run_id)
        drivers = gen.generate(amount=n, width=width, height=height, speed=3.0, start_id=1)
        for d in drivers:
            out.append({'id': d.id, 'x': float(d.position.x), 'y': float(d.position.y), 'status': d.status.name.lower()})
        return out

    def generate_requests(self,
                          start_t: int,
                          out_list: list,
                          req_rate: float,
                          width: int = 50,
                          height: int = 30) -> None:
        """Append generated request dicts into `out_list` (UI format).

        This matches the signature the UI expects: the generator should append
        plain dicts describing requests.
        """
        gen = RequestGenerator(rate=req_rate, width=width, height=height, start_id=1, run_id=self.run_id)
        new = gen.maybe_generate(start_t)
        for r in new:
            out_list.append({
                'id': r.id,
                't': int(r.creation_time),
                'px': float(r.pickup.x),
                'py': float(r.pickup.y),
                'dx': float(r.dropoff.x),
                'dy': float(r.dropoff.y),
                'status': r.status.name.lower()
            })

    # ---------------------- Converters between UI dicts and domain objs ----------------------
    def _dict_to_driver(self, d: Dict[str, Any]) -> Driver:
        if isinstance(d, Driver):
            return d
        x = float(d.get('x', d.get('px', 0.0)))
        y = float(d.get('y', d.get('py', 0.0)))
        drv_id = int(d.get('id', len(self.simulation.drivers) + 1))
        speed = float(d.get('speed', 1.0))
        behaviour = d.get('behaviour', None)
        # Normalize behaviour: accept an instance, a class, or a string name
        if behaviour is None:
            behaviour = GreedyDistanceBehaviour()
        else:
            # if behaviour is a class, instantiate it
            try:
                if isinstance(behaviour, type):
                    behaviour = behaviour()
                # if behaviour is a string, map by class name
                elif isinstance(behaviour, str):
                    name = behaviour.lower()
                    if 'greedy' in name:
                        behaviour = GreedyDistanceBehaviour()
                    elif 'earn' in name or 'earning' in name:
                        behaviour = EarningsMaxBehaviour()
                    else:
                        behaviour = GreedyDistanceBehaviour()
                # otherwise assume it's already an instance
            except Exception:
                behaviour = GreedyDistanceBehaviour()
        status = d.get('status', 'idle')
        try:
            status_enum = DriverStatus[status.upper()]
        except Exception:
            status_enum = DriverStatus.IDLE
        return Driver(id=drv_id, position=Point(x, y), speed=speed, behaviour=behaviour,
                      status=status_enum, current_request=None, history=[], run_id=self.run_id)

    def _dict_to_request(self, r: Dict[str, Any]) -> Request:
        if isinstance(r, Request):
            return r
        rid = int(r.get('id', len(self.simulation.requests) + 1))
        px = float(r.get('px', r.get('pickup_x', 0.0)))
        py = float(r.get('py', r.get('pickup_y', 0.0)))
        dx = float(r.get('dx', r.get('dropoff_x', 0.0)))
        dy = float(r.get('dy', r.get('dropoff_y', 0.0)))
        t = int(r.get('t', r.get('creation_time', 0)))
        status_str = str(r.get('status', 'waiting')).lower()
        if status_str == 'waiting':
            status = RequestStatus.WAITING
        elif status_str == 'assigned':
            status = RequestStatus.ASSIGNED
        elif status_str == 'picked':
            status = RequestStatus.PICKED
        elif status_str == 'delivered':
            status = RequestStatus.DELIVERED
        elif status_str == 'expired':
            status = RequestStatus.EXPIRED
        else:
            status = RequestStatus.WAITING
        return Request(id=rid, pickup=Point(px, py), dropoff=Point(dx, dy), creation_time=t,
                       status=status, assigned_driver=None, wait_time=0, run_id=self.run_id)

    # ---------------------- Backend API expected by gui._engine ----------------------
    def init_state(self,
                   drivers: List[Dict[str, Any]],
                   requests: List[Dict[str, Any]],
                   timeout: int,
                   req_rate: float,
                   width: int = 50,
                   height: int = 30) -> Dict[str, Any]:
        """Initialize the DeliverySimulation and return the UI state dict.

        Accepts UI-style dict lists (or domain objects) and converts them to the
        phase2 domain objects used by the simulation. Returns a dictionary with
        the keys the GUI expects (t, drivers, pending, served, expired, ...).
        """
        # convert drivers
        drv_objs: List[Driver] = [self._dict_to_driver(d) for d in drivers]

        # convert requests
        req_objs: List[Request] = [self._dict_to_request(r) for r in requests]

        # configure simulation
        self.simulation.drivers = drv_objs
        self.simulation.requests = req_objs
        self.simulation.time = 0
        self.simulation.width = width
        self.simulation.height = height
        self.simulation.request_generator = RequestGenerator(rate=req_rate, width=width, height=height,
                                                             start_id=(len(req_objs) + 1), run_id=self.run_id)
        self.simulation.timeout = timeout
        self.simulation.run_id = self.run_id
        # reset statistics container
        self.simulation.statistics = {"served": 0, "expired": 0, "served_waits": []}

        # build UI-friendly state dict
        ui_drivers = []
        for d in self.simulation.drivers:
            # ensure driver's direction vector is up-to-date
            if getattr(d, 'dir_vector', None) is None:
                d.compute_direction_vector()
            dir_vector = d.dir_vector if d.dir_vector is not None else (0.0, 0.0)
            target_pt = d.target_point()
            tx = float(target_pt.x) if target_pt is not None else 0.0
            ty = float(target_pt.y) if target_pt is not None else 0.0
            target_id = d.current_request.id if getattr(d, 'current_request', None) is not None else None
            ui_drivers.append({
                'id': d.id,
                'x': float(d.position.x),
                'y': float(d.position.y),
                'status': d.status.name.lower(),
                'vx': float(dir_vector[0]),
                'vy': float(dir_vector[1]),
                'tx': tx,
                'ty': ty,
                'target_id': target_id
            })

        ui_pending = []
        for r in self.simulation.requests:
            ui_pending.append({'id': r.id, 't': int(r.creation_time), 'px': float(r.pickup.x), 'py': float(r.pickup.y), 'dx': float(r.dropoff.x), 'dy': float(r.dropoff.y), 'status': r.status.name.lower()})

        state = {
            't': self.simulation.time,
            'drivers': ui_drivers,
            'pending': ui_pending,
            'served': 0,
            'expired': 0,
            'timeout': self.simulation.timeout,
            'served_waits': [],
            'req_rate': req_rate,
            'width': width,
            'height': height,
        }
        return state

    def simulate_step(self, state: Dict[str, Any]) -> tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Advance the simulation by one tick and return (state, metrics).
        """
        self.simulation.tick()

        # Build drivers list from actual Driver objects so we can include richer fields
        ui_drivers = []
        for d in self.simulation.drivers:
            if getattr(d, 'dir_vector', None) is None:
                d.compute_direction_vector()
            dir_vector = d.dir_vector if d.dir_vector is not None else (0.0, 0.0)
            target_pt = d.target_point()
            tx = float(target_pt.x) if target_pt is not None else 0.0
            ty = float(target_pt.y) if target_pt is not None else 0.0
            target_id = d.current_request.id if getattr(d, 'current_request', None) is not None else None
            ui_drivers.append({
                'id': d.id,
                'x': float(d.position.x),
                'y': float(d.position.y),
                'status': d.status.name.lower(),
                'vx': float(dir_vector[0]),
                'vy': float(dir_vector[1]),
                'tx': tx,
                'ty': ty,
                'target_id': target_id
            })

        # pickups: snapshot['pickups'] is list of (x,y)
        ui_pending = []
        # try to reconstruct pending request dicts from simulation.requests
        for r in self.simulation.requests:
            ui_pending.append({'id': r.id, 't': int(r.creation_time), 'px': float(r.pickup.x), 'py': float(r.pickup.y), 'dx': float(r.dropoff.x), 'dy': float(r.dropoff.y), 'status': r.status.name.lower()})

        stats = self.simulation.statistics if isinstance(self.simulation.statistics, dict) else {}
        served = int(stats.get('served', 0))
        expired = int(stats.get('expired', 0))
        served_waits = list(stats.get('served_waits', []))
        avg_wait = (sum(served_waits) / len(served_waits)) if served_waits else 0.0

        new_state = {
            't': self.simulation.time,
            'drivers': ui_drivers,
            'pending': ui_pending,
            'served': served,
            'expired': expired,
            'timeout': self.simulation.timeout,
            'served_waits': served_waits,
            'req_rate': state.get('req_rate', self.simulation.request_generator.rate if self.simulation.request_generator else 0.0),
            'width': state.get('width', self.simulation.width),
            'height': state.get('height', self.simulation.height),
        }

        metrics = {
            'served': served,
            'expired': expired,
            'avg_wait': float(avg_wait),
        }

        return new_state, metrics

    def get_plot_data(self) -> Dict[str, Any]:
        """
        Returns positions of drivers and requests for plotting (convenience function).
        """
        drivers_data = [{
            'id': driver.id,
            'position': (driver.position.x, driver.position.y),
            'status': driver.status.name
        } for driver in self.simulation.drivers]

        requests_data = [{
            'id': request.id,
            'pickup': (request.pickup.x, request.pickup.y),
            'dropoff': (request.dropoff.x, request.dropoff.y),
            'status': request.status.name
        } for request in self.simulation.requests]

        return {
            'drivers': drivers_data,
            'requests': requests_data
        }
from __future__ import annotations

from random import choice

from phase2.DeliverySimulation import DeliverySimulation
from phase2.Driver import Driver, DriverStatus
from phase2.DriverGenerator import DriverGenerator
from phase2.Point import Point
from phase2.Request import Request, RequestStatus
from phase2.RequestGenerator import RequestGenerator
from phase2.behaviour.EarningsMaxBehaviour import EarningsMaxBehaviour
from phase2.behaviour.GreedyDistanceBehaviour import GreedyDistanceBehaviour
from phase2.metrics.Event import Event, EventType
from phase2.metrics.EventManager import EventManager


class GUIAdapter:
    """
    Adapter class to interface between the old GUI and the DeliverySimulation.
    """

    def __init__(self,
                 run_id: str,
                 delivery_simulation: DeliverySimulation):
        self.run_id = run_id
        self.simulation = delivery_simulation

    def load_drivers(self, path: str) -> list[dict]:
        """
        Load drivers from a simple CSV and return a list of UI driver dicts.

        Args:
            path (str): Path to the CSV file containing driver data.

        Returns:
            list[dict]: A list of driver dictionaries in UI format.
        """
        drivers: list[dict] = []

        try:
            with open(path, 'r') as file:
                # Read headers and split by commas
                headers = file.readline().strip().split(',')

                # Iterate through each remaining line in the file
                for i, line in enumerate(file, start=1):
                    values = line.strip().split(',')

                    # Create a dictionary, mapping each header to its corresponding value, converted to int
                    driver_data = {headers[j].strip(): float(values[j]) for j in range(len(headers))}

                    # Validate that pickup coordinates are within grid bounds
                    if (0 <= driver_data['#initial px'] <= self.simulation.width and
                            0 <= driver_data['py'] <= self.simulation.height):
                        driver = {
                            'id': i,
                            'x': driver_data['#initial px'],
                            'y': driver_data['py'],
                            'vx': 0,
                            'vy': 0,
                            'tx': 0,
                            'ty': 0,
                            'target_id': None,
                        }

                        drivers.append(driver)
                return drivers
        except FileNotFoundError:
            print(f"Error: The file at path '{path}' was not found.")
            return []

    def load_requests(self, path: str) -> list[dict]:
        """
        Load requests from a CSV and return a list of UI request dicts.

        Args:
            path (str): Path to the CSV file containing request data.

        Returns:
            list[dict]: A list of request dictionaries in UI format.
        """
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
                            0 <= request_data['pickup x'] <= self.simulation.width and
                            0 <= request_data['pickup y'] <= self.simulation.height and
                            0 <= request_data['delivery x'] <= self.simulation.width and
                            0 <= request_data['delivery y'] <= self.simulation.height):
                        # Build a structured request dictionary following the UI format
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
                return requests
        except FileNotFoundError:
            print(f"Error: The file at path '{path}' was not found.")
            return []

    def generate_drivers(self, n: int, width: int = 50, height: int = 30) -> list[dict]:
        """
        Return `n` randomly generated drivers as UI dicts.

        Args:
            n (int): Number of drivers to generate.
            width (int): Width of the simulation area.
            height (int): Height of the simulation area.

        Returns:
            list[dict]: A list of driver dictionaries in UI format.
        """
        out: list[dict] = []
        gen = DriverGenerator(run_id=self.run_id)
        drivers = gen.generate(amount=n, width=width, height=height, speed=3.0, start_id=1)
        for d in drivers:
            out.append(
                {'id': d.id,
                 'x': float(d.position.x),
                 'y': float(d.position.y),
                 'status': d.status.name.lower()})
        return out

    def generate_requests(self,
                          start_t: int,
                          out_list: list,
                          req_rate: float,
                          width: int = 50,
                          height: int = 30) -> None:
        """
        Append generated request dicts into `out_list` (UI format).

        This matches the signature the UI expects: the generator should append
        plain dicts describing requests.

        Args:
            start_t (int): The simulation time to generate requests for.
            out_list (list): The list to append generated request dicts to.
            req_rate (float): The request generation rate.
            width (int): Width of the simulation area.
            height (int): Height of the simulation area.
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

    def init_state(self,
                   drivers: list[dict],
                   requests: list[dict],
                   timeout: int,
                   req_rate: float,
                   width: int = 50,
                   height: int = 30) -> dict:
        """
        Initialize the DeliverySimulation and return the UI state dict.
        Args:
            drivers (list[dict]): List of driver dicts in UI format.
            requests (list[dict]): List of request dicts in UI format.
            timeout (int): Request timeout in ticks.
            req_rate (float): Request generation rate.
            width (int): Width of the simulation area.
            height (int): Height of the simulation area.

        Returns:
            dict: The initial state of the simulation in UI format.
        """
        # Clear any existing events, to avoid mixing runs
        self.simulation.event_manager.clear_events()

        # Convert UI dicts to domain objects
        drv_objs: list[Driver] = [self._dict_to_driver(d) for d in drivers]
        req_objs: list[Request] = [self._dict_to_request(r) for r in requests]

        # Put into simulation
        self.simulation.drivers = drv_objs
        self.simulation.requests = req_objs
        self.simulation.time = 0
        self.simulation.width = width
        self.simulation.height = height
        self.simulation.request_generator = RequestGenerator(rate=req_rate, width=width, height=height,
                                                             start_id=(len(req_objs) + 1), run_id=self.run_id)
        self.simulation.timeout = timeout
        self.simulation.statistics = {"served": 0, "expired": 0, "served_waits": []}

        # Build UI-shaped lists
        ui_drivers = []
        for d in self.simulation.drivers:
            ui_drivers.append(self._driver_to_dict(d))

        ui_pending = []
        for r in self.simulation.requests:
            ui_pending.append({'id': r.id,
                               't': int(r.creation_time),
                               'px': float(r.pickup.x),
                               'py': float(r.pickup.y),
                               'dx': float(r.dropoff.x),
                               'dy': float(r.dropoff.y),
                               'status': r.status.name.lower()})

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

        # log initial behaviour for each driver so early deliveries are attributed correctly
        # this is only necessary due to the need of the gui adapter to re-create the simulation
        em = EventManager(self.run_id)
        for d in self.simulation.drivers:
            try:
                behaviour_name = type(d.behaviour).__name__
            except Exception:
                behaviour_name = 'Unknown'

            em.add_event(Event(timestamp=self.simulation.time,
                               event_type=EventType.DRIVER_GENERATED_BEHAVIOUR,
                               driver_id=d.id,
                               request_id=None,
                               wait_time=None,
                               behaviour_name=behaviour_name))

        return state

    def simulate_step(self, state: dict) -> tuple[dict, dict]:
        """
        Advance the simulation by one tick and return (state, metrics).

        Args:
            state (dict): Current simulation state in UI format.

        Returns:
            tuple[dict, dict]: A tuple containing the new state and metrics dictionaries.
        """
        self.simulation.tick()

        ui_drivers = []

        for d in self.simulation.drivers:
            dir_vector = d.dir_vector if d.dir_vector is not None else Point(0.0, 0.0)
            target_pt = d.target_point()

            tx = float(target_pt.x) if target_pt is not None else Point(0.0, 0.0)
            ty = float(target_pt.y) if target_pt is not None else Point(0.0, 0.0)

            target_id = d.current_request.id if getattr(d, 'current_request', None) is not None else None

            ui_drivers.append({
                'id': d.id,
                'x': float(d.position.x),
                'y': float(d.position.y),
                'status': d.status.name.lower(),
                'vx': float(dir_vector.x),
                'vy': float(dir_vector.y),
                'tx': tx,
                'ty': ty,
                'target_id': target_id
            })

        ui_pending = []

        # pending request dicts from simulation.requests
        for r in self.simulation.requests:
            ui_pending.append({'id': r.id,
                               't': int(r.creation_time),
                               'px': float(r.pickup.x),
                               'py': float(r.pickup.y),
                               'dx': float(r.dropoff.x),
                               'dy': float(r.dropoff.y),
                               'status': r.status.name.lower()})

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
            'req_rate': state.get('req_rate',
                                  self.simulation.request_generator.rate if self.simulation.request_generator else 0.0),
            'width': state.get('width', self.simulation.width),
            'height': state.get('height', self.simulation.height),
        }

        metrics = {
            'served': served,
            'expired': expired,
            'avg_wait': float(avg_wait),
        }

        return new_state, metrics

    def get_plot_data(self) -> dict:
        """
        Return plotting positions for drivers and requests.

        Returns:
            dict: A dictionary containing driver and request positions.
        """
        drivers_data: list[dict] = []
        for driver in self.simulation.drivers:
            item = {
                'id': driver.id,
                'position': (driver.position.x, driver.position.y),
                'status': driver.status.name
            }
            drivers_data.append(item)

        requests_data: list[dict] = []

        for request in self.simulation.requests:
            item = {
                'id': request.id,
                'pickup': (request.pickup.x, request.pickup.y),
                'dropoff': (request.dropoff.x, request.dropoff.y),
                'status': request.status.name
            }
            requests_data.append(item)

        return {
            'drivers': drivers_data,
            'requests': requests_data
        }

    def _dict_to_driver(self, driver: dict) -> Driver:
        """
        Convert a UI driver dict to a Driver object.

        Args:
            driver (dict): Driver dictionary in UI format.

        Returns:
            Driver: The corresponding Driver object.
        """
        if isinstance(driver, Driver):
            return driver

        x = float(driver.get('x', driver.get('px', 0.0)))
        y = float(driver.get('y', driver.get('py', 0.0)))

        drv_id = int(driver.get('id', len(self.simulation.drivers) + 1))
        speed = float(driver.get('speed', 1.0))

        behaviour = choice([EarningsMaxBehaviour(), GreedyDistanceBehaviour()])

        status = driver.get('status', 'idle')

        try:
            status_enum = DriverStatus[status.upper()]
        except Exception:
            status_enum = DriverStatus.IDLE

        return Driver(id=drv_id,
                      position=Point(x, y),
                      speed=speed,
                      behaviour=behaviour,
                      status=status_enum,
                      current_request=None,
                      history=[],
                      run_id=self.run_id)

    def _dict_to_request(self, request: dict) -> Request:
        """
        Convert a UI request dict to a Request object.

        Args:
            request (dict): Request dictionary in UI format.

        Returns:
            Request: The corresponding Request object.
        """
        if isinstance(request, Request):
            return request

        req_id = int(request.get('id', len(self.simulation.requests) + 1))
        px = float(request.get('px', request.get('pickup_x', 0.0)))
        py = float(request.get('py', request.get('pickup_y', 0.0)))
        dx = float(request.get('dx', request.get('dropoff_x', 0.0)))
        dy = float(request.get('dy', request.get('dropoff_y', 0.0)))
        t = int(request.get('t', request.get('creation_time', 0)))

        status_str = str(request.get('status', 'waiting')).lower()

        status_map = {
            'waiting': RequestStatus.WAITING,
            'assigned': RequestStatus.ASSIGNED,
            'picked': RequestStatus.PICKED,
            'delivered': RequestStatus.DELIVERED,
            'expired': RequestStatus.EXPIRED,
        }

        status = status_map.get(status_str, RequestStatus.WAITING)

        return Request(
            id=req_id,
            pickup=Point(px, py),
            dropoff=Point(dx, dy),
            creation_time=t,
            status=status,
            assigned_driver=None,
            wait_time=0,
            run_id=self.run_id,
        )

    def _driver_to_dict(self, d: Driver) -> dict:
        """
        Convert a Driver object to a UI driver dict.

        Args:
            d (Driver): The Driver object to convert.

        Returns:
            dict: The corresponding driver dictionary in UI format.
        """
        dir_vector = d.dir_vector if d.dir_vector is not None else (0.0, 0.0)
        target_pt = d.target_point()

        tx = float(target_pt.x) if target_pt is not None else 0.0
        ty = float(target_pt.y) if target_pt is not None else 0.0

        target_id = d.current_request.id if getattr(d, 'current_request', None) is not None else None

        return {
            'id': d.id,
            'x': float(d.position.x),
            'y': float(d.position.y),
            'status': d.status.name.lower(),
            'vx': float(dir_vector[0]),
            'vy': float(dir_vector[1]),
            'tx': tx,
            'ty': ty,
            'target_id': target_id
        }

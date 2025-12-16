from phase2.Point import Point
from phase2.Driver import Driver, DriverStatus
from phase2.Request import Request, RequestStatus
from phase2.dispatch.NearestNeighborPolicy import NearestNeighborPolicy
from phase2.behaviour.LazyBehaviour import LazyBehaviour

def main():
    run_id = "test"

    drivers = [
        Driver(id=1, position=Point(0, 0), speed=1.0, behaviour=LazyBehaviour(),
               status=DriverStatus.IDLE, current_request=None, history=[], run_id=run_id),
        Driver(id=2, position=Point(10, 0), speed=1.0, behaviour=LazyBehaviour(),
               status=DriverStatus.IDLE, current_request=None, history=[], run_id=run_id),
    ]

    requests = [
        Request(id=1, pickup=Point(1, 0), dropoff=Point(5, 0), creation_time=0,
                status=RequestStatus.WAITING, assigned_driver=None, wait_time=0, run_id=run_id),
        Request(id=2, pickup=Point(9, 0), dropoff=Point(5, 0), creation_time=0,
                status=RequestStatus.WAITING, assigned_driver=None, wait_time=0, run_id=run_id),
    ]

    policy = NearestNeighborPolicy()
    pairs = policy.assign(drivers, requests, time=0, run_id=run_id)

    print("Proposals:", [(d.id, r.id) for d, r in pairs])

if __name__ == "__main__":
    main()

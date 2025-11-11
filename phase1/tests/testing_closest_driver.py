from drivers import generate_drivers
from simulation import _calculate_closest_driver



def main():
    req = {
        "id":0,
        "t":0,
        "px":10,
        "py":10,
        "dx":30,
        "dy":30,
        "t_wait":0,
        "status":"waiting",
        "driver_id":None
    }

    drivers = generate_drivers(10)

    dist_dict = {}

    for d in drivers:
        dist = ((req["px"]-d["x"])**2 + (req["py"]-d["y"])**2)**0.5
        dist_dict[d["id"]] = dist
        print(f"{d['id']}: {dist}")

    closest_driver = _calculate_closest_driver(req, drivers)
    if closest_driver is not None:
        print(f"Closest driver id: {closest_driver['id']}")

if __name__ == '__main__':
    main()




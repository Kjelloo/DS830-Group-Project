from simulation import _assign_requests
from drivers import generate_drivers
from requests import generate_requests

def main():
	drivers = generate_drivers(3)
	requests = []
	for i in range(3):
		generate_requests(0, requests, 60)

	print("Requests before drivers are assigned:")
	for r in requests:
		print(r)
	print()

	print("Distance between each driver and each pickup:")
	for r in requests:
		for d in drivers:
			dist = ((r["px"]-d["x"])**2 + (r["py"]-d["y"])**2)**0.5
			print(f"\tDist between request {r['id']} and driver {d['id']}:")
			print(f"\t\t{dist}")
		print()

	_assign_requests(drivers, requests)

	print("Requests after drivers are assigned:")
	for r in requests:
		print(r)	

if __name__ == '__main__':
	main()
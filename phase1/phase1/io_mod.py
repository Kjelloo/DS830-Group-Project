import random

def load_drivers():
    pass

def load_requests():
    pass

def init_logger(log_dir: str = "logs", filename: str = None) -> None:
    pass

def log_event(event_type: str, t: int, driver_id: int, request_id: int, total_distance: float) -> None:
    pass


def generate_drivers(n: int, width: int=50, height: int=30) -> list[dict]:
	"""
	Generates n drivers randomly for the grid. Used initially to
	generate drivers for the simulation, i.e., n is fixed throughout
	the simulation. Default grid size is 30 x 50, but can be modified.
	"""
	try:
		n, width, height = int(n), int(width), int(height)
	except ValueError:
		return []
	drivers = []
	for i in range(n):
		drivers.append({
			"id":i, 
			"x":random.randint(0,width), 
			"y":random.randint(0,height),
            "vx": 0,
            "vy": 0,
            "tx": None,
            "ty": None,
            "target_id": None,
            "status": "waiting"
		})
	return drivers

def generate_requests(start_t: int, out_list: list, 
		req_rate: int, width: int=50, height: int=30) -> None:
	"""
	Generates delivery requests probabilistically based on req_rate.
	"""
	# Error handling
	try:
		start_t = int(start_t)
		req_rate = int(req_rate)
		width = int(width)
		height = int(height)
	except ValueError:
		return None
	if start_t < 0: return None
	if type(out_list) == list: pass
	else: return
	# Probabilistic generation
	req_per_step = req_rate
	largest_id = max((d["id"] for d in out_list), default=-1)
	if random.random() < req_per_step:
		req = {
			"id": 0 if largest_id == -1 else largest_id + 1,
			"px": random.randint(0,width),
			"py": random.randint(0,height),
			"dx": random.randint(0,width),
			"dy": random.randint(0,height),
			"t_wait": 0,
			"status": "waiting",
			"driver_id": None
		}
		out_list.append(req)


def main():
	#Testing 'generate_drivers'
	print("generate_drivers")
	drivers = generate_drivers(5)
	for i in drivers:
		print(i)

	# Testing 'generate_requests'
	print("generate_requests")
	out_list = []
	generate_requests(0,out_list, 30, 30, 50)
	for i in out_list:
		for key, value in i.items():
			print(key, value)

# Run main function if not imported.
if __name__ == '__main__':
	main()
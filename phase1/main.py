# from dispatch_ui import main

def load_request(path: str) -> list[dict]:
    """
    Load and validate delivery requests from a CSV file, converting them
    into request in a dictionary.

    Each request represents a delivery with pickup and delivery
    coordinates, with a request time.

    The resulting schema for each request is: \n
    {
        "id": int,              # unique sequential identifier \n
        "t": int,               # request time \n
        "px": int,              # pickup x-coordinate \n
        "py": int,              # pickup y-coordinate \n
        "dx": int,              # delivery x-coordinate \n
        "dy": int,              # delivery y-coordinate \n
        "driver_id": None,      # driver associated with the request (None if unassigned) \n
        "status": "waiting"     # request status
    }

    Args:
        path (str): Path to the CSV file containing request data.

    Returns:
        list[dict]: A list of request dictionaries following the above schema.

    Notes:
        - The grid boundaries are fixed at max_x = 50 and max_y = 30.
        - Requests with out-of-bounds coordinates are skipped.
        - The unique `id` field is assigned incrementally starting from 1.
    """
    # Define grid boundaries for valid coordinates
    max_x, max_y = 50, 30

    requests = []

    try:
        with open(path, 'r') as file:
            # Read headers and split by commas
            headers = file.readline().strip().split(',')

            # Iterate through each remaining line in the file
            for i, line in enumerate(file, start=1):
                values = line.strip().split(',')

                # Create a dictionary mapping each header to its corresponding value, converted to int
                request_data = {headers[j].strip(): int(values[j]) for j in range(len(headers))}

                # Validate that pickup and delivery coordinates are within grid bounds
                # and that request time is zero or positive
                if (request_data["#request time"] >= 0 and
                    0 <= request_data['pickup x'] <= max_x and
                    0 <= request_data['pickup y'] <= max_y and
                    0 <= request_data['delivery x'] <= max_x and
                    0 <= request_data['delivery y'] <= max_y):

                    # Build a structured request dictionary following the defined schema
                    request = {
                        "id": i,
                        "t": request_data['#request time'],
                        "px": request_data['pickup x'],
                        "py": request_data['pickup y'],
                        "dx": request_data['delivery x'],
                        "dy": request_data['delivery y'],
                        "driver_id": None,
                        "status": "waiting"
                    }

                    requests.append(request)
    except FileNotFoundError:
        print(f"Error: The file at path '{path}' was not found.")
        return []

    return requests

# TODO: Add stubs for the other functions here
backend = {
    "load_requests": load_request,
}

if __name__ == "__main__":
    print(load_request("data/r.csv"))
    # main(backend) TODO: Uncomment when all six functions are done
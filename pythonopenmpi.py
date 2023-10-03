import signal
import time
from mpi4py import MPI
import random

# Define the duration of each light color in seconds
DURATION_GREEN = 10
DURATION_YELLOW = 3
DURATION_RED = 10

# Define the probability of a car arriving at each intersection during each second
PROBABILITY_ARRIVAL = 0.3

# Define the maximum number of cars that can wait at each intersection
MAX_WAITING_CARS = 5

# Define the duration of a green light extension when there are waiting cars
EXTENSION_GREEN = 5

def change_lights(signum, frame):
    global current_light, waiting_cars, extension_time
    # 0: Red, 1: Green, 2: Yellow
    if current_light == 0:
        print("Green light ON")
        time.sleep(DURATION_GREEN)
        print("Green light OFF")
        current_light = 2
    elif current_light == 2:
        print("Yellow light ON")
        time.sleep(DURATION_YELLOW)
        print("Yellow light OFF")
        current_light = 1
    elif current_light == 1:
        print("Red light ON")
        time.sleep(DURATION_RED)
        print("Red light OFF")
        current_light = 0

    # Check if there are waiting cars and extend the green light if necessary
    if current_light == 1 and waiting_cars > 0 and extension_time > 0:
        print(f"Extending green light for {extension_time} seconds due to waiting cars")
        time.sleep(extension_time)
        extension_time = 0

def simulate_traffic(comm, rank):
    global current_light, waiting_cars, extension_time
    current_light = rank % 3
    waiting_cars = 0
    extension_time = 0

    while True:
        # Simulate the arrival of a car at the intersection with a certain probability
        if random.random() < PROBABILITY_ARRIVAL:
            if waiting_cars < MAX_WAITING_CARS:
                waiting_cars += 1
                print(f"Car arrived at intersection {rank}, waiting cars: {waiting_cars}")
            else:
                print(f"Car arrived at intersection {rank}, but no space to wait")

        # Wait for one second to simulate the passage of time
        time.sleep(1)

        # Check if the traffic light is green and there are waiting cars
        if current_light == 1 and waiting_cars > 0:
            # Extend the green light for a certain duration to allow waiting cars to pass
            extension_time = EXTENSION_GREEN
            waiting_cars -= 1
            print(f"Green light extended for {EXTENSION_GREEN} seconds at intersection {rank}, waiting cars: {waiting_cars}")

if __name__ == "__main__":
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    # Ensure we have at least 3 processes for simulating traffic lights
    if size < 3:
        if rank == 0:
            print("At least 3 processes are required for traffic light simulation.")
        MPI.Finalize()
        exit(1)

    signal.signal(signal.SIGALRM, change_lights)

    # Set the timer interval to one second
    signal.setitimer(signal.ITIMER_REAL, 1, 1)

    # Run the traffic light simulation for the process's assigned intersection
    simulate_traffic(comm, rank)

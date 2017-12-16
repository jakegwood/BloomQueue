# Each data structure should theoretically require 40,000 bits
TOTAL_BITS = 40000

# Both
WIDTH = 10000

# Queue
DEPTH = int(TOTAL_BITS / WIDTH)
RESOLUTION = 100

# Counting
BITS = int(TOTAL_BITS / WIDTH)

# The default time used for simulation, long enough for the
# entire bloom queue to cycle through twice
TIME = RESOLUTION * DEPTH * 2

# So that TTL << TIME
TTL = int(RESOLUTION)

# Enough objects at a speed to theoretically saturate the filter
NUMBER_OF_OBJECTS = TOTAL_BITS
RATE = int(NUMBER_OF_OBJECTS / (TTL * 10))
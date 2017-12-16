from BloomQueue import BloomQueue
from CountingFilter import CountingFilter
import Constants
import random
import matplotlib.pyplot as plt
import pprint

# Bloom Queue false positives
bqfp = []
# Counting Filter false positives
cffp = []

# Total number of requests made
requests = 0

bq = BloomQueue(Constants.DEPTH, Constants.RESOLUTION, Constants.WIDTH)
cf = CountingFilter(Constants.BITS, Constants.WIDTH)

# Sweep through time
for x in range(0, Constants.TIME):
  for y in range(0, Constants.RATE):
    # Generate a random object and inert it into the filter
    data = random.randrange(0, Constants.NUMBER_OF_OBJECTS)
    requests += 1
    for filter in [cf, bq]:
      filter.request(data, Constants.TTL)
  
  bqfp.append(bq.falsePositives / requests)
  cffp.append(cf.falsePositives / requests)
  # Advance time for both filters
  for filter in [cf, bq]:
    filter.stepForwardInTime()

# Plot
plt.plot(range(0, Constants.TIME), bqfp, 'r-', range(0, Constants.TIME), cffp, 'b--')
plt.legend(['Bloom Queue', 'Counting Filter'])
plt.title('False Positive Performance Over Time')
plt.ylabel('# False Positives / # Requests\n(Percent)')
plt.xlabel('Time (arbitrary units)')
plt.show()
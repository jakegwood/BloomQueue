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
# Relative total run time of the two queues
runTimeRatios = []

for ttl in range(1, Constants.TTL * 3):
  print(ttl)
  bq = BloomQueue(Constants.DEPTH, Constants.RESOLUTION, Constants.WIDTH)
  cf = CountingFilter(Constants.BITS, Constants.WIDTH)
  # Total number of requests made
  requests = 0
  # Sweep through time
  for x in range(0, Constants.TIME):
    for y in range(0, Constants.RATE):
      # Generate a random object and inert it into the filter
      data = random.randrange(0, Constants.NUMBER_OF_OBJECTS)
      requests += 1
      for filter in [cf, bq]:
        filter.request(data, ttl)
    
    # Advance time for both filters
    for filter in [cf, bq]:
      filter.stepForwardInTime()

  bqfp.append(100 * bq.falsePositives / requests)
  cffp.append(100 * cf.falsePositives / requests)
  runTimeRatios.append(100 * bq.runTime / cf.runTime)

xaxis = [ 100 * x / Constants.RESOLUTION for x in range(1, Constants.TTL * 3)]

# Plot
plt.subplot(211)
plt.plot(xaxis, bqfp, 'r-', xaxis, cffp, 'b--')
plt.legend(['Bloom Queue', 'Counting Filter'])
plt.title('False Positive Performance with Varying TTL\'s')
plt.ylabel('# False Positives / # Requests\n(Percent)')
plt.xlabel('Time (arbitrary units)')
plt.subplot(212)
plt.plot(xaxis, runTimeRatios, 'r-')
plt.ylabel('Relative Compute Time\nBloom Queue / Counting Filter\n(Percent)')
plt.xlabel('TTL as a Percentage of the Resolution')
plt.show()
from BloomQueue import BloomQueue
from CountingFilter import CountingFilter
import Constants
import random
import matplotlib.pyplot as plt
import pprint

spreads = []
# Bloom Queue false positives
bqfp = []
# Counting Filter false positives
cffp = []

runTimeRatios = []

# Spread indicates how much of the RESOLUTION interval requests are spread across
# Sweep through them all (i.e. only the first time unit of each resolution up to the entire thing)
for spread in range(1, Constants.RESOLUTION + 1):
  bq = BloomQueue(Constants.DEPTH, Constants.RESOLUTION, Constants.WIDTH)
  cf = CountingFilter(Constants.BITS, Constants.WIDTH)
  # Total number of requests made
  requests = 0
  for x in range(0, Constants.TIME):
    # Make it so there are only requests during the first 'spread' seconds of each resolution
    if x % Constants.RESOLUTION >= spread:
      # We want the same average overall rate, but only during the 'spread'
      for y in range(0, Constants.RATE * max(int(Constants.RESOLUTION / spread), 1)):
        # Generate a random object and inert it into the filter
        data = random.randrange(0, Constants.NUMBER_OF_OBJECTS)
        requests += 1
        for filter in [cf, bq]:
          filter.request(data, Constants.TTL)
    
    # Advance time for both filters
    for filter in [cf, bq]:
      filter.stepForwardInTime()

  print("---SPREAD---")
  print(spread / Constants.RESOLUTION)
  print("---BLOOM QUEUE STATS---")
  bq.printStats()
  print("---COUNTING FILTER STATS---")
  cf.printStats()

  # Collect the data at the end of each spread
  if requests != 0:
    bqfp.append(100 * bq.falsePositives / requests)
    cffp.append(100 * cf.falsePositives / requests)
    spreads.append(100 * spread / Constants.RESOLUTION)
    runTimeRatios.append(100 * bq.runTime / cf.runTime)

# Plot
plt.subplot(211)
plt.plot(spreads, bqfp, 'r-', spreads, cffp, 'b--')
plt.legend(['Bloom Queue', 'Counting Filter'])
plt.title('Affects of Spreading Requests Over a Limited Portion of Resolution')
plt.ylabel('# False Positives / # Requests\n(Percent)')
plt.subplot(212)
plt.plot(spreads, runTimeRatios, 'r-')
plt.ylabel('Relative Compute Time\nBloom Queue / Counting Filter\n(Percent)')
plt.xlabel('Spread as a Percentage of the Resolution')
plt.show()
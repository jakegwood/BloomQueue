import time

class BloomQueue:
  def __init__(self, depth, resolution, width):
    # Properly deep copy the rows of the matrix
    self.filters = [ [ 0 ] * int(width) for _ in range(int(depth)) ]
    self.cache = {}
    self.resolution = resolution
    self.depth = depth
    self.width = width
    self.currentFilter = 0
    self.runTime = 0
    self.time = 0
    self.cacheHits = 0
    self.cacheMisses = 0
    self.falsePositives = 0
    self.falseNegatives = 0
    self.requests = 0

  def stepForwardInTime(self):
    start = time.time()
    self.time += 1
    
    newCurrentFilter = int(self.time / self.resolution) % self.depth
    if newCurrentFilter != self.currentFilter:
      self.filters[self.currentFilter] = [ 0 ] * self.width
      self.currentFilter = newCurrentFilter

    stop = time.time()
    self.runTime += (stop - start)

  def request(self, data, ttl):
    start = time.time()
    self.requests += 1

    # Where within the width the flag would be placed
    location = hash(data) % self.width

    # Check to see if data is in the current filter
    if self.filters[self.currentFilter][location] == 1:
      if data in self.cache and self.cache[data] > self.time:
        self.cacheHits += 1
      else:
        self.falsePositives += 1
    else:
      if data not in self.cache or self.cache[data] <= self.time:
        self.cacheMisses += 1
      else:
        self.falseNegatives += 1
        # This should never happen. Report an error and exit.
        print("Bloom queue error: false negative.")
        exit()

    # Store the item in the dictionary with the absolute time at which it will expire
    # If it's already in the dictionary, update the entry if will expire sooner than the
    # new version
    if (data not in self.cache) or (self.cache[data] < self.time + ttl):
      self.cache[data] = self.time + ttl
    # If we already have seen this data, and the existing version has a longer TTL, we're done
    # This is an edge case though, realistically, you shouldn't get a new request for data
    # that would say it has a shorter time to live than a previous request for the same data
    else:
      stop = time.time()
      self.runTime += (stop - start)
      return
    
    # Initialize the index that we'll use to step through the filters in the queue
    filterIndex = self.currentFilter
    self.filters[filterIndex % self.depth][location] = 1
    ttl -= (self.resolution - (self.time % self.resolution))
    
    while ttl > 0:
      filterIndex += 1
      self.filters[filterIndex % self.depth][location] = 1
      ttl -= self.resolution

    stop = time.time()
    self.runTime += (stop - start)

  def printStats(self):
    print("Cache hits: %d" % self.cacheHits)
    print("Cache misses: %d" % self.cacheMisses)
    print("False positives: %d" % self.falsePositives)
    print("False negatives: %d" % self.falseNegatives)
    print("Time: %d" % self.time)
    print("Run time: %f (seconds)" % self.runTime)


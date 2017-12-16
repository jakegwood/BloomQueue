import time

class CountingFilter:
  def __init__(self, bits, width):
    # Properly deep copy the rows of the matrix
    self.filter = [ 0 ] * int(width)
    self.cache = {}
    self.maxValue = 2 ** bits - 1
    self.width = width
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

    # There are two ways to manage expiration:
    # 1) Have a dictionary indexed on both data and TTL so
    #    so we can sort by TTL and immediately know if
    #    any data should expire. This method requires more
    #    time to insert a new data as we would need to insert
    #    it into TTL-ordered list, but saves time when expiring.
    # 2) Only keep a dictionary indexed by the data, as I do in 
    #    with the bloom queue. This allows for faster insert
    #    (no sorting by TTL) but we then need to iterate through
    #    all data when deciding what to expire.
    #
    # I use option 2 only because option 1 would mean that this
    # counting filter implementation would require more memory
    # than than the Bloom Queue (i.e. the counting filter needs
    # an extra index on TTL or TTL-sorted list which the Bloom
    # Queue doesn't use) so it wouldn't be a fair comparison by
    # overall size of the structure.

    # Having to do this copy is just an artifact of not being
    # able to modify for loop iterables within the for loop
    # in python3, so don't penalize performance for it.

    copyStart = time.time()
    keys = list(self.cache.keys())
    copyEnd = time.time()

    for key in keys:
      if self.cache[key] <= self.time:
        location = hash(key) % self.width
        # Remove it from the dictionary so we don't try to remove
        # it from the filter again when we step forward in time
        # again
        del self.cache[key]
        # Only decrement if we haven't saturated the bits yet
        if self.filter[location] < self.maxValue:
          self.filter[location] -= 1
        if self.filter[location] < 0:
          print("Counting filter. Counting bits less than one.")
          exit()
    
    stop = time.time()
    self.runTime += ((stop - start) - (copyEnd - copyStart))

  def request(self, data, ttl):
    start = time.time()
    self.requests += 1
    # Where within the width the flag would be placed
    location = hash(data) % self.width

    # Check to see if data is in the current filter
    if data in self.cache and self.cache[data] > self.time:
      if self.filter[location] > 0:
        self.cacheHits += 1
      else:
        self.falseNegatives += 1
        # This should never happen. Report an error and exit.
        print("Counting filter error: false negative.")
        exit()
    else:
      if self.filter[location] > 0:
        self.falsePositives += 1
      else:
        self.cacheMisses += 1
      self.filter[location] = min(self.maxValue, self.filter[location] + 1)

    # Store the item in the dictionary with the absolute time at which it will expire
    # If it's already in the dictionary, update the entry if will expire sooner than the
    # new version
    if (data not in self.cache) or (self.cache[data] < self.time + ttl):
      self.cache[data] = self.time + ttl
    # If we already have seen this data, and the existing version has a longer TTL, we're done
    # This is an edge case though, realistically, you shouldn't get a new request for data
    # that would say it has a shorter time to live than a previous request for the same data
    else:
      pass

    stop = time.time()
    self.runTime += (stop - start)

  def printStats(self):
    print("Cache hits: %d" % self.cacheHits)
    print("Cache misses: %d" % self.cacheMisses)
    print("False positives: %d" % self.falsePositives)
    print("False negatives: %d" % self.falseNegatives)
    print("Time: %d" % self.time)
    print("Run time: %f (seconds)" % self.runTime)


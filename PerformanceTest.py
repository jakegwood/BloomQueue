from BloomQueue import BloomQueue
from CountingFilter import CountingFilter
import inspect

# Even though I probably won't check this file in with pprint library
# used, I do use it a lot during development to dump matrices (i.e. lists
# of lists)
import pprint

def stringGenerator(name, actual, expected):
  return "%s is incorrect. Actual: %d, Expected: %d." % (name, actual, expected)

def initalizeWithTestData(filter):
  filter.request("data1", 10)
  filter.request("data2", 15)

def TEST_BQ_Insert():
  bq = BloomQueue(10, 10, 10)
  initalizeWithTestData(bq)

  bq.request("data2", 20)

  if len(bq.cache.keys()) != 2:
    return stringGenerator("Number of keys in cache", len(bq.cache.keys()), 2)

  if bq.cacheHits != 1:
    return stringGenerator("Cache hit", bq.cacheHits, 1)

  if bq.cacheMisses != 2:
    return stringGenerator("Cache miss", bq.cacheMisses, 2)

  if bq.falsePositives != 0:
    return stringGenerator("False positive", bq.falsePositives, 0)

  if bq.falseNegatives != 0:
    return stringGenerator("False negative", bq.falseNegatives, 0)

  return True

def TEST_CF_Insert():
  cf = CountingFilter(10, 10)
  initalizeWithTestData(cf)

  cf.request("data2", 20)

  if len(cf.cache.keys()) != 2:
    return stringGenerator("Number of keys in cache", len(cf.cache.keys()), 2)

  if cf.cacheHits != 1:
    return stringGenerator("Cache hit", cf.cacheHits, 1)

  if cf.cacheMisses != 2:
    return stringGenerator("Cache miss", cf.cacheMisses, 2)

  # There may be as many as 2 false positives depending on how the hashes land
  if cf.falsePositives > 2:
    return stringGenerator("False positive", cf.falsePositives, 0)

  if cf.falseNegatives != 0:
    return stringGenerator("False negative", cf.falseNegatives, 0)

  return True

def TEST_BQ_StepForwardExpire():
  bq = BloomQueue(10, 10, 10)
  initalizeWithTestData(bq)

  for x in range(0, 10):
    bq.stepForwardInTime()

  if bq.time != 10:
    return stringGenerator("Queue time", bq.time, 10)

  # We should have advanced to the next filter
  if bq.currentFilter != 1:
    return stringGenerator("Current filter", bq.currentFilter, 1)

  # There should be exactly slot in the filter equal to 1 at this point
  numItems = sum(bq.filters[bq.currentFilter]) 
  if numItems != 1:
    return stringGenerator("Items in current filter", numItems, 1)

  # All positions in the filter should be empty now.
  for x in range(0,10):
    bq.stepForwardInTime()

  # We should have advanced to the next filter
  if bq.currentFilter != 2:
    return stringGenerator("Current filter", bq.currentFilter, 2)

  numItems = sum(bq.filters[bq.currentFilter]) 
  if numItems != 0:
    return stringGenerator("Items in current filter", numItems, 0)

  # Make sure both items are indeed expired.
  if bq.cacheMisses != 2:
    return stringGenerator("Cache miss", bq.cacheMisses, 2)

  initalizeWithTestData(bq)

  if bq.cacheMisses != 4:
    return stringGenerator("Cache miss", bq.cacheMisses, 4)

  return True

def TEST_CF_StepForwardExpire():
  cf = CountingFilter(10, 10)
  initalizeWithTestData(cf)

  # There should be two items in the filter
  numItems = sum(cf.filter) 
  if numItems != 2:
    return stringGenerator("Items in current filter", numItems, 2)

  for x in range(0, 10):
    cf.stepForwardInTime()

  if cf.time != 10:
    return stringGenerator("Queue time", cf.time, 10)

  # There should be exactly 1 slot in the filter equal to 1 at this point
  numItems = sum(cf.filter) 
  if numItems != 1:
    return stringGenerator("Items in current filter", numItems, 1)

  for x in range(0,10):
    cf.stepForwardInTime()

  # All positions in the filter should be empty now.
  numItems = sum(cf.filter) 
  if numItems != 0:
    return stringGenerator("Items in current filter", numItems, 0)

  # Make sure both items are indeed expired by seeing if requesting
  # the same data again generates cache misses
  if cf.cacheMisses != 2:
    return stringGenerator("Cache miss", cf.cacheMisses, 2)

  initalizeWithTestData(cf)

  if cf.cacheMisses != 4:
    return stringGenerator("Cache miss", cf.cacheMisses, 4)

  return True

def TEST_BQ_StepForwardFalsePostive():
  bq = BloomQueue(10, 10, 10)
  initalizeWithTestData(bq)

  for x in range(0, 16):
    bq.stepForwardInTime()

  # data2 should be expired (expired at time), but still be in the current filter
  bq.request("data2", 10)

  # There may be more than one false positive depending on what the hash values are
  if bq.falsePositives > 1:
    return stringGenerator("False positive", bq.falsePositives, 1)

  return True

def TEST_CF_StepForwardFalsePostive():
  cf = CountingFilter(10, 10)
  initalizeWithTestData(cf)

  for x in range(0, 16):
    cf.stepForwardInTime()

  # data2 should be expired (expired at time), but still be in the current filter
  cf.request("data2", 10)

  # There may be more than one false positive depending on what the hash values are
  if cf.falsePositives > 1:
    return stringGenerator("False positive", cf.falsePositives, 1)

  return True

def TEST_CF_Saturate():
  bits = 3

  # 3 bits and width one so all objects hash to the same place
  cf = CountingFilter(bits, 1)
  
  for x in range(0, 2 ** bits - 1):
    cf.request(str(x), 5)

  if cf.cacheMisses != 1:
    return stringGenerator("Cache miss", cf.cacheMisses, 1)  

  if cf.falsePositives != 2 ** bits - 2:
    return stringGenerator("False positive", cf.falsePositives, 2 ** bits - 2) 

  # We should have saturated the filter
  if cf.filter[0] != 7:
    return stringGenerator("Count before stepping forward", cf.filter[0], 7)

  # Step forward enough in time that would normally expire the data
  for x in range(0, 10):
    cf.stepForwardInTime()

  # Confirm that we've saturated the filter (the data wasn't removed)
  if cf.filter[0] != 7:
    return stringGenerator("Count after stepping forward", cf.filter[0], 7)

  # Because of that, we should get all false positives now
  for x in range(0, 2 ** bits - 1):
    cf.request(str(x), 5)

  if cf.cacheMisses != 1:
    return stringGenerator("Cache miss", cf.cacheMisses, 1)

  if cf.falsePositives != 2 * (2 ** bits - 2) + 1:
    return stringGenerator("False positive", cf.falsePositives, 2 * (2 ** bits - 2) + 1)

  return True

# Run the tests
for key, value in locals().items():
    if callable(value) and (key[0:5] == 'TEST_') and (value.__module__ == __name__):
        result = value()
        if not result:
          print "FAILED: %s" % key
        elif isinstance(result, basestring):
          print "FAILED: %s, %s" % (key, result)
        else:
          print "PASSED: %s" % key
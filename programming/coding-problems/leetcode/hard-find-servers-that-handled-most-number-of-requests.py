"""
LC 1606 - Find Servers That Handled Most Number of Requests

Questions
    input
        are queue_time and processing_time guaranteed to be the same length and sorted?
        what are the expected ranges for m and n (number of indexers and documents)?
    semantics
        what should happen if all indexers are busy when a document arrives? (Drop the document)
    output
        ties for top k indexers be broken by indexer number?

Brute Force
    The brute-force approach checks each indexer in order for every document, starting from the preferred indexer (i % m) and wrapping around. 
    This is simple and works well for small m, with O(n*m) time complexity. If assignment could be to any available indexer (not in a specific order),
    then a heap (priority queue) would be useful to always pick the soonest-available indexer in O(log m) time per document. However, since assignment
    order matters (must check in increasing indexer number, wrapping), the heap approach is not helpful here and may even be less efficient.

    The main bottleneck is the assignment step, which can require up to m checks per document in the worst case. For finding the top k indexers,
    we can sort the counts or use a min-heap for efficiency if k is much smaller than m.

    O(n*k) where n is num of documents and k is number of doc processors

Optimized
    Can we do assignment step in logk? Yes with a heap and sortedset SortedList (search, add, delete are all logK time)
    If we cannot import 3p python package, then use segment tree or native bisect+list
        Avg/practical will perform faster but worst case we will have k linear to add/delete from the list so on update heavy it functions same as brute force
    
    O(nlogk) with sorted list here with optimal logk list updates

"""


# *********************************************************************************************************************************

## OPTIMIZED SORTEDSET and MIN HEAP

from sortedcontainers import SortedList
import heapq
import bisect


class SolutionOptimal:
    def busiestServers(self, k: int, arrival: List[int], load: List[int]) -> List[int]:
        
        processed = [0 for i in range(k)]
        busy = [] # minHeap (busy_until, indexer id)
        available = SortedList(range(k)) # sorted list of available indexer ids, at start, all k are available

        n = len(arrival)
        for i in range(n):
            doc_time = arrival[i]
            doc_duration = load[i]

            # check for any new available servers
            while busy and busy[0][0] <= doc_time:
                # move indexers to available
                _, idx = heapq.heappop(busy)
                # pos = bisect.bisect_left(available, idx)
                # available.insert(pos, idx) # manual insert here, O(k) time
                # with SortedList we can just add, will be handled under the hood in logk time
                available.add(idx)
            
            if not available:
                continue # drop the document

            # search for next index, logk with bisect_left
            preferred = i % k
            pos = available.bisect_left(preferred) ### bisect_left here is impl optimized for SortedList internals
            if pos == len(available):
                pos = 0 # key, wrap around to first avail here if did not find id > preferred
            # remove from avail, inc count, push back to heap
            idx = available.pop(pos) # with SortedList, pop is logk time
            processed[idx] += 1
            heapq.heappush(busy, (doc_time + doc_duration, idx))

        maxProcessed = max(processed)
        return [idx for idx in range(len(processed)) if processed[idx] == maxProcessed]

# *********************************************************************************************************************************

## FALLBACK with bisect and list

import bisect

class SolutionFallback:
    def busiestServers(self, k: int, arrival: List[int], load: List[int]) -> List[int]:
        
        processed = [0 for i in range(k)]
        busy = [] # minHeap (busy_until, indexer id)
        available = list(range(k)) # sorted list of available indexer ids, at start, all k are available

        n = len(arrival)
        for i in range(n):
            doc_time = arrival[i]
            doc_duration = load[i]

            # check for any new available servers
            while busy and busy[0][0] <= doc_time:
                # move indexers to available
                _, idx = heapq.heappop(busy)
                pos = bisect.bisect_left(available, idx)
                available.insert(pos, idx) # manual insert here, O(k) time
            
            if not available:
                continue # drop the document

            # search for next index, logk with bisect_left
            preferred = i % k
            pos = bisect.bisect_left(available, preferred)
            if pos == len(available):
                pos = 0 # key, wrap around to first avail here if did not find id > preferred
            
            # remove from avail, inc count, push back to heap
            idx = available.pop(pos) # O(k) time here
            processed[idx] += 1
            heapq.heappush(busy, (doc_time + doc_duration, idx))

        maxProcessed = max(processed)
        return [idx for idx in range(len(processed)) if processed[idx] == maxProcessed]


# *********************************************************************************************************************************

## BRUTE FORCE IMPL

"""
Questions
    input
        are queue_time and processing_time guaranteed to be the same length and sorted?
        what are the expected ranges for m and n (number of indexers and documents)?
    semantics
        what should happen if all indexers are busy when a document arrives? (Drop the document)
    output
        ties for top k indexers be broken by indexer number?

Brute Force
    The brute-force approach checks each indexer in order for every document, starting from the preferred indexer (i % m) and wrapping around. 
    This is simple and works well for small m, with O(n*m) time complexity. If assignment could be to any available indexer (not in a specific order),
    then a heap (priority queue) would be useful to always pick the soonest-available indexer in O(log m) time per document. However, since assignment
    order matters (must check in increasing indexer number, wrapping), the heap approach is not helpful here and may even be less efficient.

    The main bottleneck is the assignment step, which can require up to m checks per document in the worst case. For finding the top k indexers,
    we can sort the counts or use a min-heap for efficiency if k is much smaller than m.

    O(n*k) where n is num of documents and k is number of doc processors

Optimized
    Can we do assignment step in logk? Yes with a heap and sortedset SortedList (search, add, delete are all logK time)
    If we cannot import 3p python package, then use segment tree or native bisect+list
        Avg/practical will perform faster but worst case we will have k linear to add/delete from the list so on update heavy it functions same as brute force
    
    O(nlogk) with sorted list here with optimal logk list updates

"""

# from sortedcontainers import SortedList
# from heapq

class Indexer:
    def __init__(self, idx):
        self.index = idx
        self.busy_until = 0
        self.processed = 0

class Solution:
    def busiestServers(self, k: int, arrival: List[int], load: List[int]) -> List[int]:
        indexers = [Indexer(i) for i in range(k)]

        m = len(arrival)
        n = len(load)

        for i in range(m):
            doc_time = arrival[i]
            doc_duration = load[i]

            start = i % k
            for offset in range(k):
                # find next avail server - wrap around 
                idx = (start + offset) % k
                if indexers[idx].busy_until <= doc_time:
                    indexers[idx].busy_until = doc_time + doc_duration
                    indexers[idx].processed += 1
                    break
        
        # maxProcessed = float('-inf')
        # busiest = []
        # for indexer in indexers:
        #     if indexer.processed > maxProcessed:
        #         maxProcessed = indexer.processed
        #         busiest = [indexer.index]
        #     elif indexer.processed == maxProcessed:
        #         busiest.append(indexer.index)
        top = max(indexers, key=lambda x: x.processed)
        maxProcessed = top.processed
        return [indexer.index for indexer in indexers if indexer.processed == maxProcessed]

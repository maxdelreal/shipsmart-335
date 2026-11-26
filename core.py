"""
core.py - THE ALGORITHM ENGINE  (CPSC 335 Final Project)

This is the file you complete. Every project option (GridRestore, ShipSmart,
BloodLink) uses these SAME functions, so the app works as soon as they do.

    Part 1  build_index                      hash table + duplicate check
    Part 2  merge_sort, lower_bound          divide & conquer sort, binary search
    Part 3  MinHeap                          priority queue
    Part 4  greedy_select                    greedy algorithm
    Part 5  dp_select                        dynamic programming (0/1 knapsack)
    Part 6  bfs_reachable, dijkstra, mst_kruskal   graph algorithms
    Part 7  kmp_search                       string matching
    Part 8  tour_brute_force, tour_heuristic an NP-hard problem (TSP)

RULES (checked by check_project.py):
  * Write the algorithms yourself. Inside this file do NOT use:
    sorted(), .sort(), heapq, bisect, str.find(), str.index(), str.count(), re.
  * dict, set, list, collections.deque and itertools.permutations ARE allowed.
  * Do not change any function name or its inputs/outputs. The app and the
    tests depend on them.

Delete each `raise NotImplementedError(...)` line when you write that function.
Run  python check_project.py  to see which parts pass.
"""

from collections import deque
from itertools import permutations
import time


# =====================================================================
# PART 1 - Hash table lookup                              (Weeks 2, 11)
# =====================================================================
def build_index(records, key):
    index = {}
    duplicates = []
    for record in records:
        k = record[key]
        if k in index: 
            if k not in duplicates:
                duplicates.append(k)
        else:
            index[k] = record
    return index, duplicates


# =====================================================================
# PART 2 - Merge sort and binary search                        (Week 4)
# =====================================================================
def merge_sort(items, key=lambda x: x):
    #0 or 1 items already sorted so we have to return a copy not origninal
    if len(items) <= 1:
        return list(items)

    #split in half and sort each half
    mid = len(items) // 2
    left = merge_sort(items[:mid], key)
    right = merge_sort(items[mid:], key)

    #merge the two sorted halves
    result = []
    i = 0  #left position
    j = 0  #right position
    while i < len(left) and j < len(right):
        # <= so equal keys take from the left side first for stability
        if key(left[i]) <= key(right[j]):
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1

    #one half ran out, append the rest of the other half
    while i < len(left):
        result.append(left[i])
        i += 1
    while j < len(right):
        result.append(right[j])
        j += 1
    return result


def lower_bound(sorted_items, target, key=lambda x: x):
    low = 0
    high = len(sorted_items) 
    while low < high:
        mid = (low + high) // 2
        if key(sorted_items[mid]) < target:
            low = mid + 1 #the middle would be too small so we know the answer is to the right
        else:
            high = mid #the middle could be the answer so it should be kept in range
    return low


# =====================================================================
# PART 3 - Priority queue (binary min-heap)                    (Week 11)
# =====================================================================
class MinHeap:
    """A binary min-heap of (priority, item) pairs stored in a Python list.

    The SMALLEST priority comes out first. Priorities may be numbers or tuples.
    When two priorities are equal, the item pushed FIRST comes out first.
    Hint: store entries as (priority, counter, item) and compare (priority, counter).

    For index i: parent = (i - 1) // 2, children = 2*i + 1 and 2*i + 2.
    """

    def __init__(self):
        self._a = []          # the heap array
        self._count = 0       # insertion counter for tie-breaking

    def __len__(self):
        return len(self._a)

    def push(self, priority, item):
        #store (priority, counter, item) so we can break ties by insertion order
        entry = (priority, self._count, item)
        self._count += 1
        self._a.append(entry) 

        i = len(self._a) - 1
        while i > 0:
            parent = (i - 1) // 2
            if self._a[i] < self._a[parent]:
                self._a[i], self._a[parent] = self._a[parent], self._a[i]
                i = parent
            else:
                break

    def peek(self):
        if len(self._a) == 0:
            raise IndexError("peek from empty heap")
        priority, counter, item = self._a[0] #smallest is always at the top
        return (priority, item)

    def pop(self):
        if len(self._a) == 0:
            raise IndexError("pop from empty heap")
        top = self._a[0]
        last = self._a.pop() #remove the last entry
        if len(self._a) > 0:
            self._a[0] = last #move it to the top

            #bubble down: swap with the smaller child while a child is smaller
            i = 0
            n = len(self._a)
            while True:
                left = 2 * i + 1
                right = 2 * i + 2
                smallest = i
                if left < n and (self._a[left][0], self._a[left][1]) < (self._a[smallest][0], self._a[smallest][1]):
                    smallest = left
                if right < n and (self._a[right][0], self._a[right][1]) < (self._a[smallest][0], self._a[smallest][1]):
                    smallest = right
                if smallest == i:
                    break
                self._a[i], self._a[smallest] = self._a[smallest], self._a[i]
                i = smallest
        return (top[0], top[2])


# =====================================================================
# PART 4 - Greedy                                               (Week 5)
# =====================================================================
def greedy_select(items, capacity):
    #sort by value per weight, highest first
    #merge sort does smallest first so sort by a negative ratio
    ordered = merge_sort(items, key=lambda it: -(it["value"] / it["weight"]))

    #take every item that still fits
    chosen_ids = []
    total_value = 0
    total_weight = 0
    for it in ordered:
        if total_weight + it["weight"] <= capacity:
            chosen_ids.append(it["id"])
            total_value += it["value"]
            total_weight += it["weight"]
    return (chosen_ids, total_value, total_weight)


# =====================================================================
# PART 5 - Dynamic programming: 0/1 knapsack                (Weeks 6-7)
# =====================================================================
def dp_select(items, capacity):
    """Same input and output as greedy_select, but always the BEST total value.

    Table: best[i][c] = best value using only the first i items with capacity c
      best[0][c] = 0
      best[i][c] = best[i-1][c]                                  (skip item i)
                   or best[i-1][c - w] + v   if w <= c           (take item i)
    Then walk back from best[n][capacity] to find which items were taken.

    Return (chosen_ids, total_value, total_weight). chosen_ids in the same order
    as the items list. Target: O(n * capacity) time.
    """
    n = len(items)
    best = []
    for i in range(n + 1):
        best.append([0] * (capacity + 1))

    #fill the table one item(row) at a time
    for i in range(1, n + 1):
        w = items[i - 1]["weight"]   #row i is about item i-1 in the list
        v = items[i - 1]["value"]
        for c in range(capacity + 1):
            skip = best[i - 1][c]                #option 1: skip item i because we can't fit it or it's not worth it
            best[i][c] = skip
            if w <= c:
                take = best[i - 1][c - w] + v    #option 2: take item i because it fits and it's worth more than skipping it
                if take > skip:
                    best[i][c] = take

    #walk back from best[n][capacity] to find which items were taken
    chosen_ids = []
    total_weight = 0
    c = capacity
    for i in range(n, 0, -1):
        #if the value changed from the row above, item i was taken
        if best[i][c] != best[i - 1][c]:
            chosen_ids.append(items[i - 1]["id"])
            total_weight += items[i - 1]["weight"]
            c -= items[i - 1]["weight"]

    chosen_ids.reverse()   #we walked backwards, flip back to list order
    return chosen_ids, best[n][capacity], total_weight


# =====================================================================
# PART 6 - Graphs                                           (Weeks 9-10)
# graph format: dict  node -> list of (neighbor, weight), undirected
# =====================================================================
def bfs_reachable(graph, start, blocked_edge=None):
    """Breadth-first search from start.

    blocked_edge : None, or a pair (u, v) that may NOT be used in either
                   direction (for example a broken line or a closed road).

    Return a dict  node -> number of hops from start  for every reachable node
    (start itself has 0). Use collections.deque as the queue. Target: O(V + E).
    """
    hops = {start: 0}          
    queue = deque([start])
    while len(queue) > 0:
        node = queue.popleft()
        for neighbor, weight in graph.get(node, []):
            #skip the closed path, in either direction
            if blocked_edge is not None:
                a, b = blocked_edge
                if (node == a and neighbor == b) or (node == b and neighbor == a):
                    continue
            if neighbor not in hops:            #the fewest hops is obtained from the first time we reach it
                hops[neighbor] = hops[node] + 1
                queue.append(neighbor)
    return hops


def dijkstra(graph, start):
    """Shortest paths from start (all weights >= 0). Use YOUR MinHeap.

    Return (dist, prev)
      dist[node] : length of the shortest path from start
      prev[node] : the node just before it on that path (prev[start] = None)
    Only reachable nodes appear in dist and prev. Target: O((V + E) log V).
    """
    dist = {start: 0}
    prev = {start: None}
    heap = MinHeap()
    heap.push(0, start)

    while len(heap) > 0:
        current_dist, current_node = heap.pop()
        if current_dist > dist[current_node]:  #skip if we already found a shorter path
            continue
        for neighbor, weight in graph.get(current_node, []):
            new_dist = current_dist + weight
            if neighbor not in dist or new_dist < dist[neighbor]:
                dist[neighbor] = new_dist
                prev[neighbor] = current_node
                heap.push(new_dist, neighbor)

    return dist, prev


def path_to(prev, target):
    """GIVEN (do not change). Rebuild the path start -> target from prev."""
    if target not in prev:
        return []
    path = []
    while target is not None:
        path.append(target)
        target = prev[target]
    path.reverse()
    return path


def mst_kruskal(nodes, edges):
    """Minimum spanning tree with Kruskal's algorithm + union-find.

    nodes : list of node ids
    edges : list of (u, v, cost)

    Sort the edges by cost (YOUR merge_sort), then add each edge whose ends are
    in different components. Return (tree_edges, total_cost), tree_edges as
    (u, v, cost) in the order added. Target: O(E log E).
    """
    parent = {}
    for node in nodes:
        parent[node] = node  #each node is its own component

    def find(node):
        if parent[node] == node:
            return node
        parent[node] = find(parent[node])
        return parent[node]

    #sort edges by their cost, put the cheapest first using our merge sort
    sorted_edges = merge_sort(edges, key=lambda edge: edge[2])

    tree_edges = []
    total_cost = 0
    for u, v, cost in sorted_edges:
        root_u = find(u)
        root_v = find(v)
        if root_u != root_v:  #only add the edge if it connects two different components
            tree_edges.append((u, v, cost))
            total_cost += cost
            parent[root_v] = root_u  #union the two components
    return tree_edges, total_cost

# =====================================================================
# PART 7 - String matching                                     (Week 12)
# =====================================================================
def kmp_search(text, pattern):
    """Knuth-Morris-Pratt. Return a list of EVERY start index where pattern
    occurs in text, overlapping matches included. Empty pattern -> [].

    Example: kmp_search("aaaa", "aa") -> [0, 1, 2]
    1) build the failure table: fail[i] = length of the longest proper prefix of
       pattern[:i+1] that is also a suffix of it
    2) scan the text once, never moving backwards in the text
    Target: O(n + m).  Do not use str.find, str.index, `in` on strings, or re.
    """
    n = len(text)
    m = len(pattern)
    if m == 0:
        return []

    #failure table step
    fail = [0] * m
    j = 0  #length of the previous longest prefix suffix
    for i in range(1, m):
        while j > 0 and pattern[i] != pattern[j]:
            j = fail[j - 1]         #here we fall back to a shorter prefix that might still match
        if pattern[i] == pattern[j]:
            j += 1
        fail[i] = j

    #scan the text oncce and use the failure table to avoid backtracking
    matches = []
    j = 0  #how many pattern characters currently match the text
    for i in range(n):
        while j > 0 and text[i] != pattern[j]:
            j = fail[j - 1]         #fall back in the pattern
        if text[i] == pattern[j]:
            j += 1
        if j == m:                  #found a match
            matches.append(i - m + 1)
            j = fail[j - 1]         #look for the next match
    return matches


# =====================================================================
# PART 8 - An NP-hard problem: the shortest tour (TSP)          (Week 14)
# dist format: dist[a][b] = travel cost from place a to place b
# =====================================================================
def tour_cost(order, dist):
    """GIVEN (do not change). Cost of order[0] -> ... -> order[-1] -> order[0]."""
    return sum(dist[order[i]][order[(i + 1) % len(order)]] for i in range(len(order)))


def tour_brute_force(start, stops, dist):
    """EXACT answer: try every order of the stops (itertools.permutations).

    Each tour begins at start, visits every stop once, and returns to start.
    Return (order, cost) where order is a list beginning with start
    (do not repeat start at the end). If stops is empty return ([start], 0).
    Target: O(n!) - only for about 9 stops or fewer.
    """
    raise NotImplementedError("Part 8: tour_brute_force")


def tour_heuristic(start, stops, dist):
    """FAST answer: nearest neighbor, then 2-opt improvement.

    1) nearest neighbor: from start, always go to the closest unvisited stop
    2) 2-opt: try reversing every segment order[i..j] (i >= 1, so start stays
       first); keep a reversal if it makes the tour shorter; repeat until no
       reversal helps
    Return (order, cost) in the same format as tour_brute_force.
    """
    raise NotImplementedError("Part 8: tour_heuristic")


# =====================================================================
# GIVEN - timing helper for the speed report               (Weeks 3, 13)
# =====================================================================
def time_it(func, *args, repeat=3):
    """GIVEN (do not change). Best wall-clock time in seconds over `repeat` runs."""
    best = None
    for _ in range(repeat):
        t0 = time.perf_counter()
        func(*args)
        t = time.perf_counter() - t0
        best = t if best is None or t < best else best
    return best

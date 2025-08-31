import heapq

def rank_courses(courses, key="credits"):
    heap = []
    for c in courses:
        heapq.heappush(heap, (c[key], c["name"]))
    return [heapq.heappop(heap) for _ in range(len(heap))]

from collections import defaultdict, deque

class CourseGraph:
    def __init__(self):
        self.graph = defaultdict(list)

    def add_edge(self, prereq, course):
        self.graph[prereq].append(course)

    def bfs(self, start):
        visited, queue = set(), deque([start])
        order = []
        while queue:
            node = queue.popleft()
            if node not in visited:
                order.append(node)
                visited.add(node)
                for neighbor in self.graph[node]:
                    queue.append(neighbor)
        return order

    def topo_sort(self):
        indegree = defaultdict(int)
        for u in self.graph:
            for v in self.graph[u]:
                indegree[v] += 1
        queue = deque([u for u in self.graph if indegree[u] == 0])
        order = []
        while queue:
            node = queue.popleft()
            order.append(node)
            for v in self.graph[node]:
                indegree[v] -= 1
                if indegree[v] == 0:
                    queue.append(v)
        return order

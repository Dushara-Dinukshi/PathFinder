import sys
import os
import json
from modules.graph import CourseGraph
from modules.heap import rank_courses
from modules.sorting import sort_courses

# Ensure modules folder is recognized
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Debug: Show current directory
print("📂 Current working directory:", os.getcwd())

# Load course data
try:
    with open("data/courses.json") as f:
        courses = json.load(f)
except FileNotFoundError:
    print("❌ ERROR: courses.json not found. Make sure it is inside 'data' folder.")
    exit()

# Build graph of prerequisites
g = CourseGraph()
for c in courses:
    for p in c.get("prerequisites", []):  # safer access
        g.add_edge(p, c["id"])

# Run algorithms
topo_order = g.topo_sort()
ranked_courses = rank_courses(courses, key="credits")
sorted_courses = sort_courses(courses, key="credits")

# Display results
print("\n📌 Topological Order of Courses:")
print(" → ".join(topo_order) if topo_order else "No order available")

print("\n📌 Ranked Courses by Credits:")
for credits, name in ranked_courses:
    print(f"{name} ({credits} credits)")

print("\n📌 Sorted Courses by Credits:")
for c in sorted_courses:
    print(f"{c['name']} ({c['credits']} credits)")

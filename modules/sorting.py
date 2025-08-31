def sort_courses(courses, key="credits"):
    return sorted(courses, key=lambda x: x[key])

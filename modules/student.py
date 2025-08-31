class Student:
    def __init__(self, name, program, year, credit_limit):
        self.name = name
        self.program = program
        self.year = year
        self.credit_limit = credit_limit
        self.completed = []
        self.enrolled = []

    def add_completed(self, course_id):
        self.completed.append(course_id)

    def enroll(self, course_id, credits):
        if self.remaining_credits() >= credits:
            self.enrolled.append(course_id)
            return True
        return False

    def remaining_credits(self):
        return self.credit_limit - sum([c["credits"] for c in self.enrolled])

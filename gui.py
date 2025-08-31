import tkinter as tk
from tkinter import simpledialog, scrolledtext, ttk
from tkcalendar import DateEntry
import json
import os
from modules.graph import CourseGraph
from modules.heap import rank_courses
from modules.sorting import sort_courses

# Colors
WINDOW_BG = "#f0f0f0"
HEADER_BG = "#1f77b4"
HEADER_FG = "white"
BUTTON_BG = "#2ca02c"
BUTTON_FG = "white"
EXIT_BG = "#d62728"
POPUP_BG = "#fff8dc"
POPUP_FG = "#000000"

SCROLL_HEIGHT = 20
SCROLL_WIDTH = 70

TYPE_COLORS = {
    'required': 'red',
    'elective': 'green',
    'skill': 'blue'
}

STUDY_HOURS_FILE = "data/study_hours.json"

class PathFinderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("📘 PathFinder - Your Academic Assistant")
        self.root.geometry("900x750")
        self.root.configure(bg=WINDOW_BG)

        # Load course catalog
        try:
            with open("data/courses.json") as f:
                self.courses = json.load(f)
        except FileNotFoundError:
            self.show_popup("Error", "courses.json not found in data folder")
            self.root.destroy()
            return

        self.student = {}
        self.study_hours = self.load_study_hours()

        # Header
        tk.Label(root, text="PathFinder Dashboard", font=("Arial", 20, "bold"),
                 fg=HEADER_FG, bg=HEADER_BG, padx=10, pady=10).pack(pady=10, fill='x')

        # Student Profile Frame
        self.profile_frame = tk.LabelFrame(root, text="🧑 Student Profile", padx=10, pady=10, bg=WINDOW_BG)
        self.profile_frame.pack(fill='x', padx=20, pady=10)

        tk.Label(self.profile_frame, text="Name:", bg=WINDOW_BG).grid(row=0, column=0, sticky='w')
        self.name_entry = tk.Entry(self.profile_frame, width=30)
        self.name_entry.grid(row=0, column=1)
        self.name_entry.focus()

        tk.Label(self.profile_frame, text="Program:", bg=WINDOW_BG).grid(row=0, column=2, sticky='w')
        self.program_entry = tk.Entry(self.profile_frame, width=30)
        self.program_entry.grid(row=0, column=3)

        tk.Label(self.profile_frame, text="Year:", bg=WINDOW_BG).grid(row=1, column=0, sticky='w')
        self.year_entry = tk.Entry(self.profile_frame, width=10)
        self.year_entry.grid(row=1, column=1, sticky='w')

        tk.Label(self.profile_frame, text="Completed Courses (IDs, comma-separated):", bg=WINDOW_BG).grid(row=2, column=0, sticky='w')
        self.completed_entry = tk.Entry(self.profile_frame, width=50)
        self.completed_entry.grid(row=2, column=1, columnspan=3, sticky='w')

        tk.Label(self.profile_frame, text="Currently Enrolled (IDs, comma-separated):", bg=WINDOW_BG).grid(row=3, column=0, sticky='w')
        self.enrolled_entry = tk.Entry(self.profile_frame, width=50)
        self.enrolled_entry.grid(row=3, column=1, columnspan=3, sticky='w')

        tk.Label(self.profile_frame, text="Semester Credit Limit:", bg=WINDOW_BG).grid(row=4, column=0, sticky='w')
        self.credit_limit_entry = tk.Entry(self.profile_frame, width=10)
        self.credit_limit_entry.grid(row=4, column=1, sticky='w')

        save_profile_btn = tk.Button(self.profile_frame, text="Save Profile", bg=BUTTON_BG, fg=BUTTON_FG, command=self.save_profile)
        save_profile_btn.grid(row=4, column=3, sticky='e')
        self.add_hover_effect(save_profile_btn, BUTTON_BG)

        # Course Actions Frame
        self.action_frame = tk.LabelFrame(root, text="📚 Course Actions", padx=10, pady=10, bg=WINDOW_BG)
        self.action_frame.pack(fill='both', expand=True, padx=20, pady=10)

        buttons = [
            ("Show Dashboard Summary", self.show_dashboard),
            ("Show Topological Order", self.show_topo),
            ("Show Ranked Electives/Skill Courses", self.show_heap),
            ("Show Sorted Courses", self.show_sorted),
            ("Recommend Courses to Fill Credits", self.recommend_courses)
        ]
        for text, cmd in buttons:
            btn = tk.Button(self.action_frame, text=text, width=40, bg=BUTTON_BG, fg=BUTTON_FG, command=cmd)
            btn.pack(pady=5)
            self.add_hover_effect(btn, BUTTON_BG)

        # Study Hours Tracker Frame
        self.study_frame = tk.LabelFrame(root, text="📅 Study Hours Tracker", padx=10, pady=10, bg=WINDOW_BG, font=("Arial", 12, "bold"))
        self.study_frame.pack(fill='both', expand=True, padx=20, pady=10)

        tk.Label(self.study_frame, text="Select Date:", bg=WINDOW_BG).grid(row=0, column=0, sticky='w', padx=5, pady=3)
        self.date_entry = DateEntry(self.study_frame, width=12, background='darkblue', foreground='white', borderwidth=2)
        self.date_entry.grid(row=0, column=1, padx=5, pady=3)

        tk.Label(self.study_frame, text="Hours Studied:", bg=WINDOW_BG).grid(row=0, column=2, sticky='w', padx=5, pady=3)
        self.hours_entry = tk.Entry(self.study_frame, width=5)
        self.hours_entry.grid(row=0, column=3, padx=5, pady=3)

        add_hours_btn = tk.Button(self.study_frame, text="Add Study Hours", bg=BUTTON_BG, fg=BUTTON_FG, command=self.add_study_hours)
        add_hours_btn.grid(row=0, column=4, padx=5, pady=3)
        self.add_hover_effect(add_hours_btn, BUTTON_BG)

        # Treeview to display study hours
        columns = ("Date", "Hours")
        self.tree = ttk.Treeview(self.study_frame, columns=columns, show='headings', height=10)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor='center', stretch=True)
        self.tree.grid(row=1, column=0, columnspan=5, pady=10)

        tk.Label(self.study_frame, text="Total Study Hours:", bg=WINDOW_BG).grid(row=2, column=0, sticky='w', padx=5)
        self.total_hours_var = tk.StringVar(value="0")
        tk.Label(self.study_frame, textvariable=self.total_hours_var, bg=WINDOW_BG).grid(row=2, column=1, sticky='w', padx=5)

        self.study_hours.sort(key=lambda x: x['date'])
        self.populate_study_tree()  # Load existing hours

        # Exit Button
        exit_btn = tk.Button(root, text="Exit", width=50, bg=EXIT_BG, fg=BUTTON_FG, command=root.quit)
        exit_btn.pack(pady=10)
        self.add_hover_effect(exit_btn, EXIT_BG)

    # ------------------ Helper Methods ------------------ #
    def add_hover_effect(self, btn, bg_color, hover_color="#4CAF50"):
        btn.bind("<Enter>", lambda e: btn.config(bg=hover_color))
        btn.bind("<Leave>", lambda e: btn.config(bg=bg_color))

    def show_popup(self, title, text):
        popup = tk.Toplevel(self.root)
        popup.title(title)
        popup.configure(bg=POPUP_BG)
        popup.geometry("650x450")

        st = scrolledtext.ScrolledText(popup, width=SCROLL_WIDTH, height=SCROLL_HEIGHT, bg=POPUP_BG, fg=POPUP_FG, font=("Arial", 12))
        st.pack(padx=10, pady=10)
        st.insert(tk.END, text)
        st.configure(state="disabled")

        tk.Button(popup, text="Close", command=popup.destroy, bg=BUTTON_BG, fg=BUTTON_FG).pack(pady=10)

    # ------------------ Profile ------------------ #
    def save_profile(self):
        try:
            self.student = {
                "name": self.name_entry.get(),
                "program": self.program_entry.get(),
                "year": int(self.year_entry.get()),
                "completed": [c.strip() for c in self.completed_entry.get().split(",") if c.strip()],
                "enrolled": [c.strip() for c in self.enrolled_entry.get().split(",") if c.strip()],
                "credit_limit": int(self.credit_limit_entry.get())
            }
            self.show_popup("Profile Saved", f"Profile for {self.student['name']} saved successfully!")
        except Exception as e:
            self.show_popup("Error", f"Invalid input: {e}")

    # ------------------ Dashboard ------------------ #
    def show_dashboard(self):
        if not self.student:
            self.show_popup("Warning", "Please save the student profile first.")
            return
        completed_credits = sum(c['credits'] for c in self.courses if c['id'] in self.student['completed'] or c['id'] in self.student['enrolled'])
        remaining_credits = self.student['credit_limit'] - completed_credits
        required = [c['name'] for c in self.courses if c['type']=='required' and c['id'] not in self.student['completed']]
        info = (
            f"Student: {self.student['name']}\nProgram: {self.student['program']}, Year: {self.student['year']}\n"
            f"Completed Credits: {completed_credits}\nCredits Remaining: {remaining_credits}\nCredit Limit: {self.student['credit_limit']}\n"
            f"Pending Required Modules:\n- " + "\n- ".join(required)
        )
        self.show_popup("Dashboard Summary", info)

    # ------------------ Courses ------------------ #
    def show_topo(self):
        g = CourseGraph()
        for c in self.courses:
            for p in c.get("prerequisites", []):
                g.add_edge(p, c["id"])
        order = g.topo_sort()
        self.show_popup("Topological Order", " → ".join(order) if order else "No order available")

    def show_heap(self):
        electives = [c for c in self.courses if c['type'] in ['elective','skill']]
        ranked = rank_courses(electives, key="credits")
        ranked_str = "\n".join([f"{c[1]} ({c[0]} credits)" for c in ranked])
        self.show_popup("Ranked Electives/Skill Courses", ranked_str if ranked else "No data")

    def show_sorted(self):
        sorted_courses = sort_courses(self.courses, key="credits")
        sorted_str = "\n".join([f"{c['name']} ({c['credits']} credits)" for c in sorted_courses])
        self.show_popup("Sorted Courses", sorted_str if sorted_courses else "No data")

    def recommend_courses(self):
        if not self.student:
            self.show_popup("Warning", "Please save the student profile first.")
            return
        completed_set = set(self.student['completed'] + self.student['enrolled'])
        remaining_credits = self.student['credit_limit'] - sum(c['credits'] for c in self.courses if c['id'] in completed_set)
        if remaining_credits <= 0:
            self.show_popup("Recommendation", "No remaining credits to fill.")
            return

        eligible = [c for c in self.courses if c['id'] not in completed_set and c['type'] in ['elective','skill']
                    and all(pr in completed_set for pr in c.get('prerequisites', []))]
        recommended = []
        total = 0
        for course in sorted(eligible, key=lambda x:x['credits']):
            if total + course['credits'] <= remaining_credits:
                recommended.append(course)
                total += course['credits']

        if not recommended:
            self.show_popup("Recommendation", "No courses can be recommended to fill remaining credits.")
            return

        rec_str = "\n".join([f"{c['name']} ({c['credits']} credits, {c['type']})" for c in recommended])
        self.show_popup("Recommended Courses", f"Courses to fill remaining credits:\n\n{rec_str}")

    # ------------------ Study Hours ------------------ #
    def add_study_hours(self):
        date = self.date_entry.get_date().strftime("%Y-%m-%d")
        try:
            hours = float(self.hours_entry.get())
            if hours <= 0 or hours > 24:
                raise ValueError
        except:
            self.show_popup("Error", "Enter a valid number of hours (1-24).")
            return

        self.study_hours.append({"date": date, "hours": hours})
        self.study_hours.sort(key=lambda x: x['date'])
        self.save_study_hours()
        self.populate_study_tree()

    def populate_study_tree(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        total = 0
        for entry in self.study_hours:
            self.tree.insert("", tk.END, values=(entry["date"], entry["hours"]))
            total += entry["hours"]
        self.total_hours_var.set(str(total))

    def save_study_hours(self):
        os.makedirs("data", exist_ok=True)
        with open(STUDY_HOURS_FILE, "w") as f:
            json.dump(self.study_hours, f)

    def load_study_hours(self):
        if os.path.exists(STUDY_HOURS_FILE):
            with open(STUDY_HOURS_FILE) as f:
                return json.load(f)
        return []

if __name__ == "__main__":
    root = tk.Tk()
    app = PathFinderApp(root)
    root.mainloop()

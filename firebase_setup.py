# firebase_setup.py
import firebase_admin
from firebase_admin import credentials, firestore

# Use your downloaded Firebase service account JSON
SERVICE_ACCOUNT_PATH = "pathfinder-2f0cf-firebase-adminsdk-fbsvc-d9e8a6d064.json"

# Initialize Firebase app
cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
firebase_admin.initialize_app(cred)
db = firestore.client()

def save_student_profile(student):
    """Save or update student profile in Firestore"""
    try:
        if 'name' not in student:
            raise ValueError("Student must have a name")
        db.collection("students").document(student['name']).set(student)
    except Exception as e:
        print("Error saving profile:", e)

def load_student_profile(student_name=None):
    """Load student profile by name. If None, return empty dict"""
    try:
        if student_name:
            doc = db.collection("students").document(student_name).get()
            if doc.exists:
                return doc.to_dict()
            else:
                return {}
        else:
            # Load the first student in collection (optional)
            docs = db.collection("students").limit(1).stream()
            for doc in docs:
                return doc.to_dict()
            return {}
    except Exception as e:
        print("Error loading profile:", e)
        return {}

def save_study_hours(student_name, study_hours):
    """Save study hours for a student"""
    try:
        db.collection("students").document(student_name).update({"study_hours": study_hours})
    except Exception as e:
        print("Error saving study hours:", e)

def load_study_hours(student_name):
    """Load study hours for a student"""
    try:
        doc = db.collection("students").document(student_name).get()
        if doc.exists:
            return doc.to_dict().get("study_hours", [])
        return []
    except Exception as e:
        print("Error loading study hours:", e)
        return []

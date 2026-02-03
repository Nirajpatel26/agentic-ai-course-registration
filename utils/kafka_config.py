KAFKA_CONFIG = {
    'bootstrap_servers': ['localhost:9092'],
    'client_id': 'course_registration_system'
}

TOPICS = {
    'registration_requests': 'registration_requests',
    'capacity_updates': 'capacity_updates',
    'enrollment_confirmations': 'enrollment_confirmations',
    'waitlist_notifications': 'waitlist_notifications'
}

# Course database (in real system, this would be a database)
COURSES_DB = {
    "CS580": {"name": "Theory & Prac App AI Gen Model", "capacity": 30, "enrolled": 10, "waitlist": []},
    "CS501": {"name": "Algorithms", "capacity": 25, "enrolled": 9, "waitlist": []},
    "CS610": {"name": "Network Structure and Cloud Computing", "capacity": 20, "enrolled": 7, "waitlist": []},
    "CS550": {"name": "Data Management and Database Design", "capacity": 35, "enrolled": 20, "waitlist": []}
}

# Sample student pool
STUDENTS = [
    "S1001", "S1002", "S1003", "S1004", "S1005",
    "S1006", "S1007", "S1008", "S1009", "S1010",
    "S1011", "S1012", "S1013", "S1014", "S1015",
    "S1016", "S1017", "S1018", "S1019", "S1020"
]

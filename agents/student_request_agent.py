
from kafka import KafkaProducer
import json
import time
import random
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.kafka_config import KAFKA_CONFIG, TOPICS, STUDENTS, COURSES_DB

class StudentRequestAgent:
    def __init__(self):
        self.producer = KafkaProducer(
            bootstrap_servers=KAFKA_CONFIG['bootstrap_servers'],
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        self.students = STUDENTS.copy()
        self.courses = list(COURSES_DB.keys())
        print(" Student Request Agent initialized")
        print(f"   Available courses: {', '.join(self.courses)}")
        print(f"   Student pool: {len(self.students)} students")
    
    def generate_registration_request(self):
        student_id = random.choice(self.students)
        course_id = random.choice(self.courses)
        
        request = {
            "student_id": student_id,
            "course_id": course_id,
            "course_name": COURSES_DB[course_id]["name"],
            "timestamp": datetime.now().isoformat(),
            "request_id": f"REQ-{int(time.time()*1000)}"
        }
        
        return request
    
    def publish_request(self, request):
        """Publish registration request to Kafka"""
        try:
            self.producer.send(TOPICS['registration_requests'], value=request)
            self.producer.flush()
            print(f"\n Published Request:")
            print(f"   Student: {request['student_id']}")
            print(f"   Course: {request['course_id']} - {request['course_name']}")
            print(f"   Request ID: {request['request_id']}")
            return True
        except Exception as e:
            print(f" Error publishing request: {e}")
            return False
    
    def run(self, num_requests=15, delay=3):
        print(f"\nStarting to generate {num_requests} registration requests...")
        print(f" Delay between requests: {delay} seconds\n")
        
        for i in range(num_requests):
            request = self.generate_registration_request()
            self.publish_request(request)
            
            if i < num_requests - 1:
                time.sleep(delay)
        
        print(f"\n Completed generating {num_requests} requests!")
        self.producer.close()

if __name__ == "__main__":
    agent = StudentRequestAgent()
    
    agent.run(num_requests=15, delay=3)
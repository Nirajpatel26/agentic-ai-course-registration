
from kafka import KafkaConsumer, KafkaProducer
import json
import time
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.kafka_config import KAFKA_CONFIG, TOPICS, COURSES_DB

class CapacityMonitorAgent:
    def __init__(self):
        # Consumer setup
        self.consumer = KafkaConsumer(
            TOPICS['registration_requests'],
            bootstrap_servers=KAFKA_CONFIG['bootstrap_servers'],
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            auto_offset_reset='latest', 
            group_id='capacity_monitor_group'
        )
        
        # Producer setup
        self.producer = KafkaProducer(
            bootstrap_servers=KAFKA_CONFIG['bootstrap_servers'],
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        
        # Local course database (in-memory)
        self.courses = COURSES_DB.copy()
        
        print("Capacity Monitor Agent initialized")
        print("   Monitoring: registration_requests")
        print("   Publishing to: capacity_updates, enrollment_confirmations")
        self.print_current_capacity()
    
    def print_current_capacity(self):
        print("\nCurrent Course Capacity:")
        for course_id, course_info in self.courses.items():
            enrolled = course_info['enrolled']
            capacity = course_info['capacity']
            available = capacity - enrolled
            print(f"   {course_id}: {enrolled}/{capacity} (Available: {available})")
    
    def check_capacity(self, course_id):
        """Check if course has available capacity"""
        course = self.courses[course_id]
        return course['enrolled'] < course['capacity']
    
    def process_request(self, request):
        """Process a registration request"""
        student_id = request['student_id']
        course_id = request['course_id']
        course_name = request['course_name']
        
        print(f"\nProcessing Request:")
        print(f"   Student: {student_id}")
        print(f"   Course: {course_id} - {course_name}")
        
        # Check capacity
        has_space = self.check_capacity(course_id)
        
        if has_space:
            # Enroll student
            self.courses[course_id]['enrolled'] += 1
            
            # Publish confirmation
            confirmation = {
                "student_id": student_id,
                "course_id": course_id,
                "course_name": course_name,
                "status": "CONFIRMED",
                "timestamp": datetime.now().isoformat(),
                "message": f"Successfully enrolled in {course_name}"
            }
            
            self.producer.send(TOPICS['enrollment_confirmations'], value=confirmation)
            
            # Publish capacity update
            capacity_update = {
                "course_id": course_id,
                "course_name": course_name,
                "enrolled": self.courses[course_id]['enrolled'],
                "capacity": self.courses[course_id]['capacity'],
                "available": self.courses[course_id]['capacity'] - self.courses[course_id]['enrolled'],
                "timestamp": datetime.now().isoformat()
            }
            
            self.producer.send(TOPICS['capacity_updates'], value=capacity_update)
            self.producer.flush()
            
            print(f"   CONFIRMED - Enrolled successfully")
            print(f"   New capacity: {self.courses[course_id]['enrolled']}/{self.courses[course_id]['capacity']}")
        
        else:
            # Course is full - let waitlist manager handle
            print(f"   FULL - Course at capacity")
            print(f"   Capacity: {self.courses[course_id]['enrolled']}/{self.courses[course_id]['capacity']}")
            
            # Publish capacity update (course is full)
            capacity_update = {
                "course_id": course_id,
                "course_name": course_name,
                "enrolled": self.courses[course_id]['enrolled'],
                "capacity": self.courses[course_id]['capacity'],
                "available": 0,
                "status": "FULL",
                "timestamp": datetime.now().isoformat()
            }
            
            self.producer.send(TOPICS['capacity_updates'], value=capacity_update)
            self.producer.flush()
    
    def run(self):
        """Run the agent continuously"""
        print("\nCapacity Monitor Agent is now running...")
        print("   Waiting for registration requests...\n")
        
        try:
            for message in self.consumer:
                request = message.value
                self.process_request(request)
        except KeyboardInterrupt:
            print("\n\n Shutting down Capacity Monitor Agent...")
            self.consumer.close()
            self.producer.close()
            self.print_current_capacity()

if __name__ == "__main__":
    agent = CapacityMonitorAgent()
    agent.run()
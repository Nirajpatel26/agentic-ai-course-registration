
from kafka import KafkaConsumer, KafkaProducer
import json
from datetime import datetime
from collections import defaultdict
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.kafka_config import KAFKA_CONFIG, TOPICS, COURSES_DB

class WaitlistManagerAgent:
    def __init__(self):
        # Consumer setup - subscribe to multiple topics
        self.consumer = KafkaConsumer(
            TOPICS['registration_requests'],
            TOPICS['capacity_updates'],
            bootstrap_servers=KAFKA_CONFIG['bootstrap_servers'],
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            auto_offset_reset='latest',
            group_id='waitlist_manager_group'
        )
        
        # Producer setup
        self.producer = KafkaProducer(
            bootstrap_servers=KAFKA_CONFIG['bootstrap_servers'],
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        
        # Waitlist storage (in-memory)
        # Format: {course_id: [(student_id, timestamp), ...]}
        self.waitlists = defaultdict(list)
        
        # Track course status
        self.course_status = {course_id: info.copy() for course_id, info in COURSES_DB.items()}
        
        # Track processed requests to avoid duplicates
        self.processed_students = defaultdict(set)
        
        print(" Waitlist Manager Agent initialized")
        print("   Monitoring: registration_requests, capacity_updates")
        print("   Publishing to: waitlist_notifications, enrollment_confirmations")
    
    def add_to_waitlist(self, student_id, course_id, course_name):
        """Add student to course waitlist"""
        # Check if student already on waitlist
        if student_id in [s[0] for s in self.waitlists[course_id]]:
            print(f"Student {student_id} already on waitlist for {course_id}")
            return
        
        # Add to waitlist
        timestamp = datetime.now().isoformat()
        self.waitlists[course_id].append((student_id, timestamp))
        position = len(self.waitlists[course_id])
        
        # Publish waitlist notification
        notification = {
            "student_id": student_id,
            "course_id": course_id,
            "course_name": course_name,
            "status": "Waitlisted",
            "position": position,
            "timestamp": timestamp,
            "message": f"Added to waitlist for {course_name} (Position: {position})"
        }
        
        self.producer.send(TOPICS['waitlist_notifications'], value=notification)
        self.producer.flush()
        
        print(f"Waitlisted - Position {position}")
    
    def process_registration_request(self, request):
        """Process registration request to check if waitlist needed"""
        student_id = request['student_id']
        course_id = request['course_id']
        course_name = request['course_name']
        
        # Check if already processed this student for this course
        if student_id in self.processed_students[course_id]:
            return
        
        print(f"\n Waitlist Check:")
        print(f"   Student: {student_id}")
        print(f"   Course: {course_id} - {course_name}")
        
        # Check current course status
        course = self.course_status[course_id]
        if course['enrolled'] >= course['capacity']:
            self.add_to_waitlist(student_id, course_id, course_name)
            self.processed_students[course_id].add(student_id)
    
    def process_capacity_update(self, update):
        """Process capacity update - check if waitlist students can enroll"""
        course_id = update['course_id']
        course_name = update['course_name']
        available = update.get('available', 0)
        
        # Update local status
        self.course_status[course_id]['enrolled'] = update['enrolled']
        
        print(f"\n Capacity Update:")
        print(f"   Course: {course_id} - {course_name}")
        print(f"   Available: {available}")
        
        # Check if we can move waitlist students
        if available > 0 and self.waitlists[course_id]:
            # Get next student from waitlist
            student_id, _ = self.waitlists[course_id].pop(0)
            
            # Enroll from waitlist
            confirmation = {
                "student_id": student_id,
                "course_id": course_id,
                "course_name": course_name,
                "status": "CONFIRMED_FROM_Waitlist",
                "timestamp": datetime.now().isoformat(),
                "message": f"Enrolled from waitlist into {course_name}"
            }
            
            self.producer.send(TOPICS['enrollment_confirmations'], value=confirmation)
            
            # Update waitlist positions
            notification = {
                "student_id": student_id,
                "course_id": course_id,
                "course_name": course_name,
                "status": "ENROLLED_FROM_WAITLIST",
                "timestamp": datetime.now().isoformat(),
                "message": f"Moved from waitlist to enrolled in {course_name}"
            }
            
            self.producer.send(TOPICS['waitlist_notifications'], value=notification)
            self.producer.flush()
            
            print(f"   Enrolled {student_id} from waitlist")
            print(f"   Remaining on waitlist: {len(self.waitlists[course_id])}")
    
    def print_waitlist_status(self):
        """Print current waitlist status"""
        print("\n Current Waitlist Status:")
        for course_id, waitlist in self.waitlists.items():
            if waitlist:
                print(f"   {course_id}: {len(waitlist)} students waiting")
                for i, (student_id, _) in enumerate(waitlist, 1):
                    print(f"      {i}. {student_id}")
            else:
                print(f"   {course_id}: No waitlist")
    
    def run(self):
        """Run the agent continuously"""
        print("\n Waitlist Manager Agent is now running...")
        print("   Waiting for requests and capacity updates...\n")
        
        try:
            for message in self.consumer:
                data = message.value
                topic = message.topic
                
                if topic == TOPICS['registration_requests']:
                    self.process_registration_request(data)
                elif topic == TOPICS['capacity_updates']:
                    self.process_capacity_update(data)
        
        except KeyboardInterrupt:
            print("\n\n Shutting down Waitlist Manager Agent...")
            self.print_waitlist_status()
            self.consumer.close()
            self.producer.close()

if __name__ == "__main__":
    agent = WaitlistManagerAgent()
    agent.run()
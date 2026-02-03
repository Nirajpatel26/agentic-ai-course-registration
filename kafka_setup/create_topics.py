from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError
import time

def create_topics():
    
    # Wait a bit for Kafka to be fully ready
    print("Waiting for Kafka to be ready...")
    time.sleep(5)
    
    # Connect to Kafka
    admin_client = KafkaAdminClient(
        bootstrap_servers=['localhost:9092'],
        client_id='topic_creator'
    )
    
    # Define topics
    topics = [
        NewTopic(name='registration_requests', num_partitions=1, replication_factor=1),
        NewTopic(name='capacity_updates', num_partitions=1, replication_factor=1),
        NewTopic(name='enrollment_confirmations', num_partitions=1, replication_factor=1),
        NewTopic(name='waitlist_notifications', num_partitions=1, replication_factor=1)
    ]
    
    # Create topics
    try:
        admin_client.create_topics(new_topics=topics, validate_only=False)
        print(" Topics created successfully!")
        print("  - registration_requests")
        print("  - capacity_updates")
        print("  - enrollment_confirmations")
        print("  - waitlist_notifications")
    except TopicAlreadyExistsError:
        print("Topics already exist!")
    except Exception as e:
        print(f"Error creating topics: {e}")
    finally:
        admin_client.close()

if __name__ == "__main__":
    create_topics()

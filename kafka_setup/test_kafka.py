from kafka import KafkaProducer, KafkaConsumer
import json
import time
from threading import Thread

def test_producer():
    
    producer = KafkaProducer(
        bootstrap_servers=['localhost:9092'],
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    
    message = {
        "test": "Hello Kafka!",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    print(f"Sending test message: {message}")
    producer.send('registration_requests', value=message)
    producer.flush()
    print("Message sent successfully!")
    producer.close()

def test_consumer():

    consumer = KafkaConsumer(
        'registration_requests',
        bootstrap_servers=['localhost:9092'],
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        auto_offset_reset='earliest',
        consumer_timeout_ms=10000  
    )
    
    print("Listening for messages...")
    message_count = 0
    
    for message in consumer:
        print(f"Received: {message.value}")
        message_count += 1
    
    print(f"Total messages received: {message_count}")
    consumer.close()

if __name__ == "__main__":
    # First send a message
    test_producer()
    
    # Wait a moment
    time.sleep(2)
    
    # Then try to receive it
    test_consumer()

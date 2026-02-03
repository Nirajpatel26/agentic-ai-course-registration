# Agentic AI Course Registration System with Kafka Pub/Sub Architecture

A distributed multi-agent system demonstrating asynchronous communication using Apache Kafka pub/sub architecture for university course registration management.

## Overview

This project implements three intelligent agents that coordinate through Kafka topics to handle course registration requests, capacity management, and waitlist automation. The system demonstrates key principles of distributed systems including decoupling, scalability, and fault tolerance.

## Architecture

### System Components

- **Apache Kafka**: Message broker for asynchronous agent communication
- **Zookeeper**: Distributed coordination service for Kafka
- **Three Intelligent Agents**:
  - Student Request Agent (Producer)
  - Capacity Monitor Agent (Consumer + Producer)
  - Waitlist Manager Agent (Consumer + Producer)

### Communication Topics

1. **registration_requests**: Student course registration requests
2. **capacity_updates**: Real-time seat availability updates
3. **enrollment_confirmations**: Successful enrollment notifications
4. **waitlist_notifications**: Waitlist position and status updates

## Features

- Asynchronous message-based communication between agents
- Real-time course capacity monitoring
- Automatic waitlist management
- Concurrent agent execution
- Message persistence and replay capability
- Fault-tolerant architecture

## Technology Stack

- **Python 3.8+**
- **Apache Kafka 7.5.0**
- **Docker & Docker Compose**
- **kafka-python 2.0.2**
- **pandas** for data manipulation
- **matplotlib** for visualization
- **Jupyter Notebook** for interactive demonstration

## Prerequisites

- Docker Desktop installed and running
- Python 3.8 or higher
- Git installed

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/Nirajpatel26/agentic-ai-course-registration.git
cd agentic-ai-course-registration
```

### 2. Start Kafka and Zookeeper

```bash
docker-compose up -d
```

Wait 15-20 seconds for services to fully start.

### 3. Set up Python environment

```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On Mac/Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 4. Create Kafka topics

```bash
python kafka_setup/create_topics.py
```

## Usage

### Option 1: Run with Jupyter Notebook (Recommended)

```bash
jupyter notebook Course_Registration_Demo.ipynb
```

Run cells sequentially to see the complete system demonstration with visualizations.

### Option 2: Run agents separately

You need three terminal windows:

**Terminal 1 - Capacity Monitor Agent:**
```bash
python agents/capacity_monitor_agent.py
```

**Terminal 2 - Waitlist Manager Agent:**
```bash
python agents/waitlist_manager_agent.py
```

**Terminal 3 - Generate Registration Requests:**
```bash
python agents/student_request_agent.py
```

## Project Structure

```
course_registration_system/
├── agents/
│   ├── student_request_agent.py       # Publisher agent
│   ├── capacity_monitor_agent.py      # Capacity management agent
│   └── waitlist_manager_agent.py      # Waitlist management agent
├── kafka_setup/
│   ├── create_topics.py               # Topic creation script
│   └── test_kafka.py                  # Kafka connection test
├── utils/
│   └── kafka_config.py                # Shared configuration
├── data/
│   └── courses.json                   # Course catalog data
├── Course_Registration_Demo.ipynb     # Interactive demo notebook
├── docker-compose.yml                 # Docker services configuration
├── requirements.txt                   # Python dependencies
├── .gitignore                        # Git ignore rules
└── README.md                         # This file
```

## System Workflow

1. **Student Request Agent** generates and publishes registration requests to the `registration_requests` topic
2. **Capacity Monitor Agent** subscribes to requests, checks course capacity:
   - If seats available: confirms enrollment and publishes to `enrollment_confirmations`
   - If full: publishes course full status to `capacity_updates`
3. **Waitlist Manager Agent** monitors both topics:
   - Adds students to waitlist when courses are full
   - Automatically enrolls waitlisted students when capacity opens
   - Publishes notifications to `waitlist_notifications`

## Configuration

Course catalog and system settings can be modified in `utils/kafka_config.py`:

```python
COURSES_DB = {
    "CS580": {"name": "Neural Networks", "capacity": 30, ...},
    "CS501": {"name": "Algorithms", "capacity": 25, ...},
    ...
}
```

## Key Learnings

### Pub/Sub Architecture Benefits

- **Decoupling**: Agents only need to know topic names, not other agent details
- **Scalability**: Easy to add new agents without modifying existing code
- **Asynchronous Processing**: Agents work independently without blocking
- **Fault Tolerance**: System continues operating if individual agents fail
- **Message Persistence**: Kafka stores messages for reliability

### Real-World Applications

This architecture pattern is applicable to:
- University registration systems
- E-commerce order processing
- Healthcare patient monitoring
- Financial trading platforms
- IoT device coordination

## Testing

Test Kafka connection:
```bash
python kafka_setup/test_kafka.py
```

## Troubleshooting

### Kafka connection errors

```bash
# Check if containers are running
docker ps

# View Kafka logs
docker logs kafka

# Restart services
docker-compose down
docker-compose up -d
```

### Port conflicts

If port 9092 is already in use, modify `docker-compose.yml` to use a different port.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

Niraj Patel  
Northeastern University  
GenAI Course - Prof. Das

## Acknowledgments

- Apache Kafka documentation
- kafka-python library contributors
- Confluent Platform tutorials

## References

- [Apache Kafka Documentation](https://kafka.apache.org/documentation/)
- [Pub/Sub Pattern](https://www.geeksforgeeks.org/system-design/what-is-pub-sub/)
- [kafka-python Library](https://kafka-python.readthedocs.io/)

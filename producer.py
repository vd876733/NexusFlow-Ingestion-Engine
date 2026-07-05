import json
import os
import time
import uuid
from datetime import datetime, timezone
from random import choice, randint, random
from confluent_kafka import Producer

# CORRECTED: Mapped to the open external port on Windows
BOOTSTRAP_SERVERS = "localhost:9092"
TOPIC = "web-clickstream"
EVENT_TYPES = ["click", "view", "add_to_cart", "purchase"]

def delivery_report(err, msg):
    """ Callback called once message delivered or failed. """
    if err is not None:
        print(f"❌ Message delivery failed: {err}")
    else:
        print(f"✅ Delivered to {msg.topic()} [Partition: {msg.partition()}] at offset {msg.offset()}")

def generate_event(corrupt=False):
    """ Generates mock user data. Injects corrupted data if corrupt=True. """
    if corrupt:
        return {
            "event_id": str(uuid.uuid4()),
            "user_id": None,               # Malformed field
            "event_type": choice(EVENT_TYPES),
            "timestamp": "not-a-valid-timestamp", # Malformed timestamp
            "ip_address": "192.168.0.1",
        }

    return {
        "event_id": str(uuid.uuid4()),
        "user_id": randint(1, 100000),
        "event_type": choice(EVENT_TYPES),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "ip_address": f"192.168.{randint(0, 255)}.{randint(1, 254)}",
    }

def main():
    producer_conf = {
        "bootstrap.servers": BOOTSTRAP_SERVERS,
        "client.id": "nexusflow-producer"
    }
    
    # Initialize Kafka Producer
    producer = Producer(producer_conf)

    print(f"🚀 Starting NexusFlow Ingestion Engine Producer...")
    print(f"📡 Streaming real-time events to topic '{TOPIC}' on {BOOTSTRAP_SERVERS}...\n")

    try:
        while True:
            # 2% chance of injecting a corrupted payload
            corrupt = random() < 0.02
            event = generate_event(corrupt=corrupt)
            payload = json.dumps(event).encode("utf-8")

            # Produce message to Kafka asynchronously
            producer.produce(TOPIC, value=payload, callback=delivery_report)
            
            # Serve delivery callback queue events
            producer.poll(0)
            
            time.sleep(0.5)
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping producer pipeline gracefully...")
    finally:
        # Block until all outstanding messages are sent
        producer.flush()
        print("🏁 Producer stopped. All messages flushed.")

if __name__ == "__main__":
    main()
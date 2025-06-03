"""
Kafka Consumer for System Log Ingestion

This module implements a Kafka consumer that reads log lines from the
'system-logs' topic and forwards them to the Flask API for processing.
Will be implemented during Phase 1: Environment Setup & Data Ingestion.
"""

import json
import requests
from kafka import KafkaConsumer
from typing import Optional


class LogConsumer:
    """Kafka consumer for processing system logs."""
    
    def __init__(self, 
                 kafka_servers: str = "localhost:9092",
                 topic: str = "system-logs",
                 api_endpoint: str = "http://localhost:5000/api/ingest"):
        """
        Initialize the Kafka consumer.
        
        Args:
            kafka_servers: Kafka bootstrap servers
            topic: Kafka topic to consume from
            api_endpoint: Flask API endpoint for log ingestion
        """
        self.kafka_servers = kafka_servers
        self.topic = topic
        self.api_endpoint = api_endpoint
        self.consumer: Optional[KafkaConsumer] = None
        
    def connect(self):
        """
        Connect to Kafka cluster.
        
        TODO: Phase 1 implementation
        - Create KafkaConsumer instance
        - Configure auto_offset_reset, value_deserializer
        - Subscribe to topic
        """
        print(f"TODO: Connect to Kafka at {self.kafka_servers}")
        print(f"TODO: Subscribe to topic '{self.topic}'")
        
    def consume_logs(self):
        """
        Main consumer loop to process incoming log messages.
        
        TODO: Phase 1 implementation
        - Poll for messages from Kafka
        - Batch messages for efficiency
        - Forward to Flask API via HTTP POST
        - Handle errors and reconnection
        """
        print("TODO: Implement consume_logs() in Phase 1")
        print(f"TODO: Forward messages to {self.api_endpoint}")
        
    def forward_to_api(self, logs: list):
        """
        Forward log batch to Flask API.
        
        Args:
            logs: List of log message strings
            
        TODO: Phase 1 implementation
        - Format logs as JSON payload
        - Make HTTP POST request to API
        - Handle API errors and retries
        """
        payload = {"logs": logs}
        print(f"TODO: POST {len(logs)} logs to {self.api_endpoint}")
        print(f"Payload: {json.dumps(payload, indent=2)}")


def main():
    """Main entry point for the consumer service."""
    print("Starting Kafka Log Consumer...")
    
    consumer = LogConsumer()
    consumer.connect()
    
    try:
        consumer.consume_logs()
    except KeyboardInterrupt:
        print("\nShutting down consumer...")
    except Exception as e:
        print(f"Consumer error: {e}")


if __name__ == "__main__":
    main() 
import pika
import time
import os
import json

RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'rabbitmq')
QUEUE_NAME = 'judge_queue'

def connect_to_rabbitmq():
    while True:
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
            return connection
        except Exception as e:
            print(f"Waiting for RabbitMQ... Error: {e}")
            time.sleep(5)

def callback(ch, method, properties, body):
    print(f" [x] Received submission: {body}")
    # Simulate processing
    submission = json.loads(body)
    print(f"Processing submission for problem {submission.get('problem_id')}...")
    time.sleep(2) # Simulate work
    print(" [x] Done")
    ch.basic_ack(delivery_tag=method.delivery_tag)

def main():
    connection = connect_to_rabbitmq()
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME, durable=True)
    
    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback)
    channel.start_consuming()

if __name__ == '__main__':
    main()

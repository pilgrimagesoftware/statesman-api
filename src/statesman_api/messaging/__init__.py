__author__ = "Paul Schifferer <paul@schifferers.net>"
"""
- Messaging
"""

import logging, os, json, time
import pika
from statesman_api import constants
from threading import Thread


connection = pika.BlockingConnection(pika.ConnectionParameters(
            os.environ[constants.RABBITMQ_HOST],
            os.environ[constants.RABBITMQ_PORT],
            os.environ[constants.RABBITMQ_VHOST],
            pika.PlainCredentials(os.environ[constants.RABBITMQ_USER], os.environ[constants.RABBITMQ_PASSWORD]),
        ))
channel = connection.channel()


def send_amqp_response(msg, response_data:dict):
    """_summary_

    Args:
        msg (_type_): _description_
    """
    logging.debug("msg: %s", msg)

    body_data = {
        "sender": os.environ[constants.POD],
        "timestamp": time.time(),
        "response_data": response_data,
        "answer": msg,
    }
    body = json.dumps(body_data)
    logging.debug("body: %s", body)
    channel.basic_publish(exchange=os.environ[constants.RABBITMQ_EXCHANGE], routing_key=response_data['queue'], body=body)


class MessageConsumer(Thread):
    """_summary_

    Args:
        Thread (_type_): _description_
    """

    def message_callback(self, ch, method, properties, body):
        """_summary_

        Args:
            ch (_type_): _description_
            method (_type_): _description_
            properties (_type_): _description_
            body (_type_): _description_
        """
        logging.info("ch: %s, method: %s, properties: %s, body: %s", ch, method, properties, body)

        # extract info
        msg = json.loads(body)
        logging.debug("msg: %s", msg)
        sender = msg['sender']
        timestamp = msg['timestamp']
        response_data = msg['response_data']
        logging.debug("response_data: %s", response_data)
        user = msg['user']
        logging.debug("user: %s", user)
        command = msg['data']['command']
        logging.debug("command: %s", command)

        # TODO: process the command
        body_data = {}

        # send reponse
        send_amqp_response(body_data, response_data)


    def run(self):
        logging.info("Consumer thread started.")
        channel.basic_consume(queue=os.environ[constants.RABBITMQ_QUEUE], on_message_callback=self.message_callback, auto_ack=True)
        channel.start_consuming()


consumer_thread = MessageConsumer()
consumer_thread.setDaemon(True)
consumer_thread.start()

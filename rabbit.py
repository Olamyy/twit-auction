import pika
from user import UserTwitterModel


class RabbitMQ:
    def __init__(self, queue_name):
        self.queue_name = queue_name
        self._connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        self._channel = self._connection.channel()
        self._channel.queue_declare(queue=self.queue_name, durable=True)

    def producer(self, data):
        self._channel.publish(exchange="", routing_key=self.queue_name, body=data)

    def callback(self, ch, method, properties, body):
        user = UserTwitterModel()
        user.save()

    def consumer(self):
        self._channel.queue_declare(self.queue_name, durable=True)
        self._channel.basic_consume(self.callback, queue=self.queue_name, no_ack=True)
        print 'Consuming Data'
        self._channel.start_consuming()




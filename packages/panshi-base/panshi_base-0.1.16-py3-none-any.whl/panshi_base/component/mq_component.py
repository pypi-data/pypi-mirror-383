from typing import List, Dict

try:
    import pika
except ImportError:
    raise ValueError("pika is not installed. Please install it with `poetry add pika`")

from loguru import logger
from pydantic import BaseModel


class RabbitMqConf(BaseModel):
    host: str
    port: int
    virtual_host: str = "/"
    password: str
    username: str
    queue: List[str]
    durable: bool = True


class RabbitMqComponent:
    # rabbitmq配置
    conf: RabbitMqConf = None
    connection: pika.BlockingConnection = None
    channel = None

    def __init__(self, params: Dict):
        conf = RabbitMqConf.model_validate(params)
        self.conf = conf
        self.__init_connection__()
        self.__declare_queue__()

    def close(self):
        if self.channel:
            self.channel.close()
        if self.connection:
            self.connection.close()

    def __init_connection__(self):
        """
        连接到RabbitMQ服务器
        :return:
        """
        credentials = pika.PlainCredentials(username=self.conf.username, password=self.conf.password)
        parameters = pika.ConnectionParameters(
            host=self.conf.host,
            port=self.conf.port,
            virtual_host=self.conf.virtual_host,
            credentials=credentials
        )
        connection = pika.BlockingConnection(parameters)
        logger.info("rabbitmq创建连接成功")
        self.connection = connection
        self.channel = connection.channel()

    def __declare_queue__(self):
        for queue in self.conf.queue:
            self.channel.queue_declare(queue=queue, durable=self.conf.durable)
            logger.info(f"声明队列{queue}")

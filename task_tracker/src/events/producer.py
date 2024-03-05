from aiokafka import AIOKafkaProducer

BOOTSTRAP_SERVERS = 'kafka:9092'


async def send_event(topic: str, value: str, key: str | None = None):
    producer = AIOKafkaProducer(bootstrap_servers=BOOTSTRAP_SERVERS)

    await producer.start()
    try:
        result = await producer.send_and_wait(
            topic=topic,
            value=value.encode(),
            key=key.encode() if key else None,
        )
        print(f'{result=}')
    finally:
        await producer.stop()

from confluent_kafka import Consumer, KafkaException
import json

conf = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'news-consumer-group-test',  # 새 그룹으로 과거 메시지도 읽기
    'auto.offset.reset': 'earliest',
    'enable.auto.commit': True
}

consumer = Consumer(conf)
consumer.subscribe(['news'])

print("뉴스 수신 대기 중...")

try:
    while True:
        msg = consumer.poll(timeout=1.0)
        if msg is None:
            print("⏳ 메시지 없음... 대기 중")
            continue
        if msg.error():
            print(f"⚠️ Kafka Error: {msg.error()}")
            continue

        article = json.loads(msg.value().decode('utf-8'))
        print("\n📥 전체 데이터 수신:")
        print(json.dumps(article, indent=4, ensure_ascii=False))  # ✅ 전체 JSON 보기
except KeyboardInterrupt:
    print("소비자 종료")
finally:
    consumer.close()

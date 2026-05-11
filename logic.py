# logic.py (модифицированный для распределённой системы)
import paho.mqtt.client as mqtt

# Команды
CMD_LED_ON = "ON"
CMD_LED_OFF = "OFF"
CMD_BUZZER = "BUZZ"

MQTT_BROKER = 'localhost'

# Топики (ориентируемся на центральный хаб)
MQTT_TOPIC_RX = 'cluster/lora/rx/state'          # слушаем данные, пришедшие из Mesh
MQTT_TOPIC_TX = 'cluster/lora/tx/action'         # отправляем команды в Mesh (через bridge)
MQTT_TOPIC_ACTION = 'cluster/cmd/system/action'  # локальное управление (если есть устройство на хабе)

client = mqtt.Client()

def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode().strip()
    print(f"[logic] {topic} -> {payload}")

    # Обрабатываем сообщения пришедшие из LoRa-сети (канал приёма)
    if topic == MQTT_TOPIC_RX:
        # Здесь может быть "DARK" или "LIGHT" 
        if payload == "DARK":
            print("[logic] На датчике мало света -> включаем светодиод (Отправляем команду - ON в Mesh)")
            client.publish(MQTT_TOPIC_TX, CMD_LED_ON)   # команда уйдёт в LoRa, её принимают удалённые узлы.
            # Если нужно также управлять локальным устройством на центральном хабе:
            # client.publish(MQTT_TOPIC_ACTION, CMD_LED_ON)

        elif payload == "LIGHT":
            print("[logic] Светло → выключаем светодиод (отправляем команду - OFF в Mesh)")
            client.publish(MQTT_TOPIC_TX, CMD_LED_OFF)


client.on_message = on_message
client.connect(MQTT_BROKER, 1883, 60)
client.subscribe(MQTT_TOPIC_RX)  # подписываемся только на RX

print("[logic] logic.py запущен (слушает MQTT_TOPIC_RX=cluster/lora/rx/state)")
client.loop_forever()
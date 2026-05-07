#logic.py
import paho.mqtt.client as mqtt

# Команды
CMD_LED_ON = "Yes"
CMD_LED_OFF = "No"
CMD_BUZZER = "Bye"

MQTT_BROKER = 'localhost'
# Топики
MQTT_TOPIC_SENSOR = 'cluster/sensor/ambient_light/state'  # ← Слушаем датчик
MQTT_TOPIC_RX = 'cluster/lora/rx/state'                    # ← Слушаем из mesh
MQTT_TOPIC_TX = 'cluster/lora/tx/action'                   # ← Отправляем в mesh
MQTT_TOPIC_ACTION = 'cluster/cmd/system/action'            # ← Управляем устройством

client = mqtt.Client()

def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode()
    
    print(f"topic - {topic}, payload - {payload}")

    if topic == MQTT_TOPIC_RX:
        if payload == CMD_LED_ON:
            print("System - +LIGHT")
            client.publish(MQTT_TOPIC_ACTION,CMD_LED_ON)
        elif payload == CMD_LED_OFF:
            print("System - OFF")
            client.publish(MQTT_TOPIC_ACTION,CMD_LED_OFF)
        elif payload == CMD_BUZZER:
            print("System - +BUZZ")
            client.publish(MQTT_TOPIC_ACTION,CMD_BUZZER)
    
    elif topic == MQTT_TOPIC_SENSOR:
        # реагируем на изменение освещённости и передаем управляющую команду
        if payload == "DARK":
            print("Sensor DARK -> sending LED ON to Lora")
            client.publish(MQTT_TOPIC_TX, CMD_LED_ON)   # "Yes"
        elif payload == "LIGHT":
            print("Sensor LIGHT -> sending LED OFF to Lora")
            client.publish(MQTT_TOPIC_TX, CMD_LED_OFF)  # "No"

client.on_message = on_message
client.connect(MQTT_BROKER,1883,60)
client.subscribe(MQTT_TOPIC_SENSOR)
client.subscribe(MQTT_TOPIC_RX)



client.loop_forever()



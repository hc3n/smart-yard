#bridge.py
import paho.mqtt.client as mqtt
import meshtastic.serial_interface
from pubsub import pub

MQTT_BROKER = 'localhost'
# Топики
MQTT_TOPIC_SENSOR = 'cluster/sensor/ambient_light/state'  # ← Слушаем датчик
MQTT_TOPIC_RX = 'cluster/lora/rx/state'                    # ← Слушаем из mesh
MQTT_TOPIC_TX = 'cluster/lora/tx/action'                   # ← Отправляем в mesh
MQTT_TOPIC_ACTION = 'cluster/cmd/system/action'            # ← Управляем устройством

mqtt_client = mqtt.Client()

interface = meshtastic.serial_interface.SerialInterface()

def on_mqtt_message(client,userdata,msg):
    message = msg.payload.decode()
    print(f"[MQTT -> Lora]: {message}")

    interface.sendText(message)

def on_lora_message(packet,interface):
    message = packet.get("decoded", {}).get("text")
    if not message:
        return

    print(f"[LORA -> MQTT]: {message}")    
    
    mqtt_client.publish(MQTT_TOPIC_RX,message)
    
    

mqtt_client.on_message = on_mqtt_message
mqtt_client.connect(MQTT_BROKER,1883,60)
mqtt_client.subscribe(MQTT_TOPIC_TX)

mqtt_client.loop_start()

pub.subscribe(on_lora_message,"meshtastic.receive")

print("\n |BRIDGE STARTED| \n")
    

import time
while True:
    time.sleep(1)
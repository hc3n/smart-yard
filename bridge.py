# bridge.py (на центральном хабе)
# мост mqtt - lora, принимает сообщения о состоянии кластеров из lora сети и публикует их в топик состояния MQTT_TOPIC_ACTION. 
# Есть возможность автоматического управления через прослушивание топика MQTT_TOPIC_ACTION. 
# На данный момент является единственной точкой входа/выхода беспроводного трафика на хабе.


import paho.mqtt.client as mqtt
import meshtastic.serial_interface
from pubsub import pub

# MQTT брокер по умолчанию
MQTT_BROKER = 'localhost'

# Общий шаблон структуры топика брокера
# {cluster}/{category}/{device}/{action/state}
# cluster это любое помещение/комната/объект
# category - sensor/system/lora/cmd
# device - конкретное устройство


# MQTT_TOPIC_SENSOR = 'cluster/sensor/ambient_light/state'  - теперь датчик не слушаем, сейчас удалённый узел шле данные в LoRa, они приходят в топик приёма RX
MQTT_TOPIC_RX = 'cluster/lora/rx/state'                    # Слушаем из mesh
MQTT_TOPIC_TX = 'cluster/lora/tx/action'                   # Отправляем в mesh
MQTT_TOPIC_ACTION = 'cluster/cmd/system/action'            # Управляем устройством
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
mqtt_client.subscribe(MQTT_TOPIC_ACTION) # В случае если есть надобность автоматического управления. Работает при запущенном logic.py  

mqtt_client.loop_start()

pub.subscribe(on_lora_message,"meshtastic.receive")

print("\n |BRIDGE STARTED| \n")
    

import time
while True:
    time.sleep(1)
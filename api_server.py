from fastapi import FastAPI
from pydantic import BaseModel, Field
import paho.mqtt.client as mqtt

MQTT_TOPIC_SENSOR = 'cluster/sensor/ambient_light/state' # инфа от датчика света
MQTT_TOPIC_TX = 'cluster/lora/tx/action' # отправляем сообщение
MQTT_TOPIC_RX = 'cluster/lora/rx/state' # сообщаем о состоянии
MQTT_TOPIC_ACTION = 'cluster/cmd/system/action' # передаем команду

# создаем API
app = FastAPI(title="Lora Mesh Controller API",
    description="API для управления устройствами умного дома через MQTT и Lora Mesh сеть",
    version="0.1"
)

# подключение MQTT
MQTT_BROKER = "localhost"

client = mqtt.Client()
client.connect(MQTT_BROKER,1883,60)
client.loop_start()

# хранилище состояния
system_state = {
    "state": None, # 
    "action_to_device": None # Последняя отправленная команда устройству
}

# получение данных из MQTT
def on_message(client,userdata,msg):
    payload = msg.payload.decode()
    topic = msg.topic
    
    # обработка топиков mqtt -> system state
    if topic == MQTT_TOPIC_RX:
        system_state["state"] = payload

    elif topic == MQTT_TOPIC_ACTION:
        system_state["action_to_device"] = payload
    
    elif topic == MQTT_TOPIC_TX:
        system_state["state"] = payload


client.on_message = on_message
client.subscribe('#') # подписка на все топики (можно без TX)




# Получить состояние системы
@app.get("/status")
def get_status():
    return system_state


class Command(BaseModel):
    command: str
# Отправить команду устройству (HTTP -> MQTT_TOPIC_ACTION)
@app.post("/command")
def send_command(cmd: Command):
    client.publish(MQTT_TOPIC_ACTION,cmd.command)
    return {"status" : "ok", "sent": cmd.command}

class LoraMessage(BaseModel):
    message: str
    
# Отправить сообщение LORA (HTTP -> MQTT_TOPIC_TX (LORA)
@app.post("/lora")
def send_lora(msg: LoraMessage):
    client.publish(MQTT_TOPIC_TX, msg.message)
    return {"status" : "ok", "sent": msg.message}
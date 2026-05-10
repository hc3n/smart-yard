#device_node.py
import serial
import paho.mqtt.client as mqtt

# MQTT брокер по умолчанию
MQTT_BROKER = 'localhost'

# Общий шаблон структуры топика брокера
# {cluster}/{category}/{device}/{action/state}
# cluster это любое помещение/комната/объект
# category - sensor/system/lora/cmd
# device - конкретное устройство


MQTT_TOPIC_SENSOR = 'cluster/sensor/ambient_light/state'  # ← Слушаем датчик
MQTT_TOPIC_RX = 'cluster/lora/rx/state'                    # ← Слушаем из mesh
MQTT_TOPIC_TX = 'cluster/lora/tx/action'                   # ← Отправляем в mesh
MQTT_TOPIC_ACTION = 'cluster/cmd/system/action'            # ← Управляем устройством


# Конфигурация устройства
DEVICE_PORT = '/dev/cu.usbmodemFX2348N1' 
BAUDRATE = 9600 # скорость Serial, должна совпадать с Serial.begin() в Arduino
THRESHOLD = 800 # Пороговое значение яркости (светло/темно)

# инициализация Serial порта
ser = serial.Serial(DEVICE_PORT,BAUDRATE,timeout=1)

# Команды
CMD_LED_ON = "Yes"
CMD_LED_OFF = "No"
CMD_BUZZER = "Bye"

# MQTT блок
client = mqtt.Client() # пустой объект mqtt-клиента

# Обработка команд из MQTT и отправка на устройство (Arduino)
def on_message(client,userdata,msg):
    command = msg.payload.decode()
    print("[MQTT -> DEVICE]:", command)

    if command == CMD_LED_ON:
        ser.write("1\n".encode()) 
    elif command == CMD_LED_OFF:
        ser.write("0\n".encode())
    elif command == CMD_BUZZER:
        ser.write("buzz\n".encode())

client.on_message = on_message # ссылка на функцию при получении сообщения
client.connect(MQTT_BROKER,1883,60) # подключение к брокеру
client.subscribe(MQTT_TOPIC_ACTION) # подписка на топик 
client.loop_start() 


last_state = None 

# Считывание данных
while True:
    data = ser.readline().decode().strip()
    
    # получаем значение яркости и выводим его
    try:
        light_value = int(data)
        print(f"[Light sensor value] = {light_value}")
    except:
        continue

    # определение свето/темно по заданному порогу "THRESOLD"
    state = "DARK" if light_value < THRESHOLD else "LIGHT"
    if state != last_state:
        print(f"[STATE]: {state}")
        client.publish(MQTT_TOPIC_SENSOR,state) # публикуем в топик состояние датчика

        last_state = state




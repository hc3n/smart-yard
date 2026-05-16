# device_node_remote.py (на удалённом узле)
# Драйвер удалённого узла, обеспечивает автономность удалённого узла и связь с центальным хабом.
# Через Serial опрашивает контроллер (Arduino)
# Считывает количество света на датчике.
# При изменении состояния "DARK" или "LIGHT" - отправляет его в LoRa сеть. (можно изменить эту логику, например, отправлять значение света в некоторый промежуток времени, а в дальнейшем строить графики телеметрии).
# Одновременно прослушивает входящие из LoRa сети и ждет команды: "ON" - включить свет, "OFF" - выключить свет, "BUZZ" - короткий звуковой сигнал.
# не использует mqtt, напрямую работает с meshtastic модулем через pub/sub - meshtastic


import serial
import meshtastic.serial_interface
from pubsub import pub
import time

NODE_ID = "NODE_1" # ID или имя данного узла

# Подключаемся к Meshtastic устройству на удалённом узле 
MESHTASTIC_PORT = 'COM5'          # порт Meshtastic модуля
interface = meshtastic.serial_interface.SerialInterface(devPath=MESHTASTIC_PORT)

# Управление светодиодом по команде из LoRa (rx-channel)
def on_lora_command(packet, interface):
     text = packet.get("decoded", {}).get("text")
     if text == "ON":
         ser.write("1\n".encode())
     elif text == "OFF":
         ser.write("0\n".encode())
     elif text == "BUZZ":
        ser.write("buzz\n".encode())
pub.subscribe(on_lora_command, "meshtastic.receive")

# Конфигурация устройства (контроллер + датчик)
DEVICE_PORT = 'COM6' # Порт контроллера
BAUDRATE = 9600 # скорость Serial, должна совпадать с Serial.begin() в Arduino
THRESHOLD = 800 # Пороговое значение с датчика яркости (светло/темно)

# Открываем Serial к Arduino
ser = serial.Serial(DEVICE_PORT, BAUDRATE, timeout=1)

last_state = None

print("Remote sensor node started, sending data to Mesh...")
while True:
    data = ser.readline().decode().strip()
    try:
        light_value = int(data)
        state = "DARK" if light_value < THRESHOLD else "LIGHT"
        if state != last_state:
            print(f"Sensor: {light_value} -> {state}")
            interface.sendText(f"{NODE_ID}:{state}")    # отправка в LoRa сеть 
            last_state = state
    except:
        pass
    time.sleep(0.2)

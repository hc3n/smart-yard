from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import paho.mqtt.client as mqtt
import asyncio
import json

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

MQTT_BROKER = "localhost"
MQTT_TOPIC_ACTION = 'cluster/cmd/system/action'
MQTT_TOPIC_TX = 'cluster/lora/tx/action'
MQTT_TOPIC_RX = 'cluster/lora/rx/state'

client = mqtt.Client()
client.connect(MQTT_BROKER, 1883, 60)
client.loop_start()

# Состояние всех узлов: {"greenhouse1": "DARK", "node2": "LIGHT"}
nodes_state = {}
websocket_clients = set()
loop = asyncio.get_event_loop()

def on_message(client, userdata, msg):
    global nodes_state
    topic = msg.topic
    payload = msg.payload.decode().strip()

    if topic == MQTT_TOPIC_RX:
        # Ожидаем формат: "node_id:STATE" (например, "greenhouse1:DARK")
        if ':' in payload:
            node_id, state = payload.split(':', 1)
            nodes_state[node_id] = state
        else:
            # На случай сообщений без ID — используем "node0" 
            nodes_state["node0"] = payload

        # Рассылаем обновление всем WebSocket-клиентам
        data = json.dumps({"nodes": nodes_state})
        for ws in list(websocket_clients):
            asyncio.run_coroutine_threadsafe(ws.send_text(data), loop)

client.on_message = on_message
client.subscribe('#')

@app.get("/", response_class=HTMLResponse)
async def home():
    return HTMLResponse("""
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Smart-Yard Dashboard</title>
<style>
  :root {
    --bg: #1a1a2e;
    --card-bg: #16213e;
    --accent: #0f3460;
    --text: #e0e0e0;
    --success: #2ecc71;
    --danger: #e74c3c;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: 'Segoe UI', system-ui, sans-serif;
    background: var(--bg);
    color: var(--text);
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
    padding: 20px;
  }
  .dashboard {
    width: 100%;
    max-width: 800px;
    display: grid;
    gap: 20px;
  }
  h1 { text-align: center; font-weight: 600; }
  .nodes-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 15px;
  }
  .node-card {
    background: var(--card-bg);
    border-radius: 16px;
    padding: 20px;
    text-align: center;
    box-shadow: 0 8px 20px rgba(0,0,0,0.3);
    transition: transform 0.2s;
  }
  .node-card:hover { transform: translateY(-2px); }
  .node-name {
    font-size: 1em;
    color: #aaa;
    margin-bottom: 10px;
  }
  .node-state {
    font-size: 2em;
    font-weight: bold;
    padding: 15px;
    border-radius: 12px;
    color: white;
    margin: 10px 0;
  }
  .state-dark { background: var(--danger); }
  .state-light { background: var(--success); }
  .state-unknown { background: #555; }
  .controls {
    background: var(--card-bg);
    border-radius: 16px;
    padding: 24px;
    box-shadow: 0 8px 20px rgba(0,0,0,0.3);
  }
  .buttons {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    margin-bottom: 15px;
  }
  button {
    background: var(--accent);
    border: none;
    color: white;
    padding: 10px 20px;
    border-radius: 10px;
    font-size: 1em;
    cursor: pointer;
    font-weight: 600;
    transition: background 0.2s, transform 0.1s;
  }
  button:hover { background: #1a4b8c; }
  button:active { transform: scale(0.97); }
  .input-row {
    display: flex;
    gap: 10px;
  }
  input {
    flex: 1;
    padding: 10px;
    border-radius: 10px;
    border: none;
    background: #0a0a1a;
    color: white;
    font-size: 1em;
  }
  .status-bar {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    font-size: 0.9em;
    color: #aaa;
    margin-bottom: 10px;
  }
  .conn-dot {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    background: var(--danger);
  }
  .conn-dot.online { background: var(--success); }
</style>
</head>
<body>
<div class="dashboard">
  <h1>Smart-Yard Dashboard</h1>

  <div class="status-bar">
    <span class="conn-dot" id="connDot"></span>
    <span id="connText">Подключение...</span>
  </div>

  <div class="nodes-grid" id="nodesContainer">
    <div class="node-card">
      <div class="node-name">Нет данных</div>
      <div class="node-state state-unknown">---</div>
    </div>
  </div>

  <div class="controls">
    <div class="buttons">
      <button onclick="sendCommand('ON')">💡 Включить LED</button>
      <button onclick="sendCommand('OFF')">🌑 Выключить LED</button>
      <button onclick="sendCommand('BUZZ')">🔔 Зуммер</button>
    </div>
    <div class="input-row">
      <input type="text" id="loraMsg" placeholder="Сообщение в LoRa">
      <button onclick="sendLora()">Отправить</button>
    </div>
  </div>
</div>

<script>
let socket;

function connectWS() {
  socket = new WebSocket('ws://' + location.host + '/ws');
  socket.onopen = () => {
    document.getElementById('connDot').className = 'conn-dot online';
    document.getElementById('connText').textContent = 'Подключено (WebSocket)';
  };
  socket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    renderNodes(data.nodes || {});
  };
  socket.onclose = () => {
    document.getElementById('connDot').className = 'conn-dot';
    document.getElementById('connText').textContent = 'Переподключение...';
    setTimeout(connectWS, 3000);
  };
  socket.onerror = () => {
    document.getElementById('connDot').className = 'conn-dot';
    document.getElementById('connText').textContent = 'Ошибка';
  };
}

function renderNodes(nodes) {
  const container = document.getElementById('nodesContainer');
  const nodeIds = Object.keys(nodes);

  if (nodeIds.length === 0) {
    container.innerHTML = `<div class="node-card">
      <div class="node-name">Нет узлов</div>
      <div class="node-state state-unknown">---</div>
    </div>`;
    return;
  }

  container.innerHTML = nodeIds.map(id => {
    const state = nodes[id];
    let stateClass = 'state-unknown';
    if (state === 'DARK') stateClass = 'state-dark';
    else if (state === 'LIGHT') stateClass = 'state-light';

    return `<div class="node-card">
      <div class="node-name">${escapeHtml(id)}</div>
      <div class="node-state ${stateClass}">${escapeHtml(state)}</div>
    </div>`;
  }).join('');
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.appendChild(document.createTextNode(text));
  return div.innerHTML;
}

async function sendCommand(command) {
  await fetch('/command', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ command })
  });
}

async function sendLora() {
  const input = document.getElementById('loraMsg');
  const message = input.value.trim();
  if (!message) return;
  await fetch('/lora', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message })
  });
  input.value = '';
}

connectWS();
</script>
</body>
</html>""")

@app.get("/status")
def get_status():
    return {"nodes": nodes_state}

@app.post("/command")
def send_command(cmd: dict):
    client.publish(MQTT_TOPIC_ACTION, cmd.get("command", ""))
    return {"ok": True}

@app.post("/lora")
def send_lora(msg: dict):
    client.publish(MQTT_TOPIC_TX, msg.get("message", ""))
    return {"ok": True}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    websocket_clients.add(websocket)
    await websocket.send_text(json.dumps({"nodes": nodes_state}))
    try:
        while True:
            await websocket.receive_text()
    except:
        pass
    finally:
        websocket_clients.discard(websocket)
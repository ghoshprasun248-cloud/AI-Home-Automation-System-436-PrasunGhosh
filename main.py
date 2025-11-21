from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import asyncio, os
from .devices import DeviceManager
from .ai import SchedulerAI, load_model, DEFAULT_MODEL_PATH

app = FastAPI(title="AI Home Automation System")

templates = Jinja2Templates(directory="app/templates")
app.mount('/static', StaticFiles(directory='app/static'), name='static')

device_mgr = DeviceManager()
if os.path.exists(DEFAULT_MODEL_PATH):
    ai = load_model(DEFAULT_MODEL_PATH)
else:
    ai = SchedulerAI()

@app.get('/', response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse('index.html', {'request': request, 'devices': device_mgr.list_devices()})

@app.get('/api/devices')
async def list_devices():
    return device_mgr.list_devices()

@app.post('/api/devices/{device_id}/toggle')
async def toggle(device_id: str):
    state = device_mgr.toggle_device(device_id)
    return {'device_id': device_id, 'state': state}

class WS:
    clients = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.clients.append(ws)

    def disconnect(self, ws: WebSocket):
        if ws in self.clients:
            self.clients.remove(ws)

    async def broadcast(self, data):
        for c in list(self.clients):
            try:
                await c.send_json(data)
            except:
                pass

ws_mgr = WS()

@app.websocket('/ws')
async def websocket(ws: WebSocket):
    await ws_mgr.connect(ws)
    try:
        while True:
            data = await ws.receive_json()
            if data.get('cmd')=='list':
                await ws.send_json({'type':'list','devices': device_mgr.list_devices()})
            if data.get('cmd')=='toggle':
                did = data['device_id']
                state = device_mgr.toggle_device(did)
                await ws_mgr.broadcast({'type':'update','device_id':did,'state':state})
    except WebSocketDisconnect:
        ws_mgr.disconnect(ws)

async def ai_loop():
    while True:
        await asyncio.sleep(10)
        for did in device_mgr.list_devices():
            prob = ai.predict_now(did)
            if prob is not None:
                await ws_mgr.broadcast({
                    'type':'recommendation',
                    'device_id': did,
                    'prob': float(prob),
                    'suggest': 'ON' if prob>=0.5 else 'OFF'
                })

@app.on_event('startup')
async def start():
    asyncio.create_task(ai_loop())

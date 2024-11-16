from flask import Flask, render_template
from flask_sock import Sock
import json
import time
import threading
from simulation import SwarmSimulation

app = Flask(__name__)
sock = Sock(app)

# Initialize simulation
simulation = SwarmSimulation()
connected_clients = set()

def broadcast_state():
    """Broadcast simulation state to all connected clients"""
    while True:
        if connected_clients:
            state = {
                'type': 'state_update',
                'agents': simulation.get_agent_states(),
                'analytics': simulation.get_analytics()
            }
            message = json.dumps(state)
            
            # Broadcast to all clients
            disconnected = set()
            for ws in connected_clients:
                try:
                    ws.send(message)
                except Exception as e:
                    print(f"Failed to send to client: {e}")
                    disconnected.add(ws)
            
            # Remove disconnected clients
            connected_clients.difference_update(disconnected)
            
        time.sleep(1/30)  # 30 FPS update rate

# Start broadcast thread
broadcast_thread = threading.Thread(target=broadcast_state)
broadcast_thread.daemon = True
broadcast_thread.start()

@app.route('/')
def index():
    return render_template('index.html')

@sock.route('/ws')
def websocket(ws):
    """Handle WebSocket connections"""
    connected_clients.add(ws)
    print(f"Client connected. Total clients: {len(connected_clients)}")
    
    try:
        while True:
            message = ws.receive()
            data = json.loads(message)
            
            if data['type'] == 'command':
                if data['action'] == 'start':
                    simulation.start()
                elif data['action'] == 'stop':
                    simulation.stop()
                elif data['action'] == 'reset':
                    simulation.reset()
                elif data['action'] == 'start_recording':
                    simulation.start_recording()
                elif data['action'] == 'stop_recording':
                    simulation.stop_recording()
                elif data['action'] == 'start_playback':
                    if 'recording' in data:
                        simulation.load_recording(data['recording'])
                    simulation.start_playback()
                elif data['action'] == 'stop_playback':
                    simulation.stop_playback()
                    
            elif data['type'] == 'parameter':
                simulation.set_parameter(data['name'], data['value'])
                
            elif data['type'] == 'pattern':
                simulation.set_pattern(data['name'])
                
            elif data['type'] == 'custom_behavior':
                if data['action'] == 'save':
                    success, message = simulation.set_custom_behavior(data['code'])
                    if success:
                        simulation.set_pattern('custom')
                    ws.send(json.dumps({
                        'type': 'behavior_response',
                        'success': success,
                        'message': message
                    }))
                elif data['action'] == 'test':
                    success, message = simulation.validate_custom_behavior(data['code'])
                    ws.send(json.dumps({
                        'type': 'behavior_response',
                        'success': success,
                        'message': message
                    }))
                    
            elif data['type'] == 'get_recording':
                recording = simulation.save_recording()
                ws.send(json.dumps({
                    'type': 'recording_data',
                    'recording': recording
                }))
                
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        connected_clients.remove(ws)
        print(f"Client disconnected. Remaining clients: {len(connected_clients)}")
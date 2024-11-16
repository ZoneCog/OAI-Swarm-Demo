from flask import Flask, render_template
from flask_sock import Sock
import json
from simulation import SwarmSimulation

app = Flask(__name__)
sock = Sock(app)

# Initialize simulation
simulation = SwarmSimulation()

@app.route('/')
def index():
    return render_template('index.html')

@sock.route('/ws')
def websocket(ws):
    """Handle WebSocket connections"""
    while True:
        try:
            message = ws.receive()
            data = json.loads(message)
            
            if data['type'] == 'command':
                if data['action'] == 'start':
                    simulation.start()
                elif data['action'] == 'stop':
                    simulation.stop()
                elif data['action'] == 'reset':
                    simulation.reset()
                    
            elif data['type'] == 'parameter':
                simulation.set_parameter(data['name'], data['value'])
                
            elif data['type'] == 'pattern':
                simulation.set_pattern(data['name'])
            
            # Send current state back to client
            ws.send(json.dumps({
                'type': 'state_update',
                'agents': simulation.get_agent_states()
            }))
            
        except Exception as e:
            print(f"WebSocket error: {e}")
            break

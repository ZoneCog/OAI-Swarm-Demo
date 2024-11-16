class SwarmWebSocket {
    constructor() {
        this.connect();
        this.onUpdateCallbacks = [];
    }

    connect() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        this.ws = new WebSocket(`${protocol}//${window.location.host}/ws`);
        
        this.ws.onopen = () => {
            console.log('Connected to swarm server');
            document.querySelector('.status-indicator').style.color = '#0f0';
        };

        this.ws.onclose = () => {
            console.log('Disconnected from swarm server');
            document.querySelector('.status-indicator').style.color = '#f00';
            // Attempt to reconnect after 1 second
            setTimeout(() => this.connect(), 1000);
        };

        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            
            if (data.type === 'state_update') {
                // Update agent count
                document.getElementById('agentCount').textContent = 
                    data.agents.length;
                
                // Update renderer
                if (window.swarmRenderer) {
                    window.swarmRenderer.updateAgents(data.agents);
                }
                
                // Call all update callbacks
                this.onUpdateCallbacks.forEach(callback => callback(data));
            }
        };
    }

    send(message) {
        if (this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(message));
        }
    }

    onUpdate(callback) {
        this.onUpdateCallbacks.push(callback);
    }
}

// Initialize WebSocket connection
window.swarmWS = new SwarmWebSocket();

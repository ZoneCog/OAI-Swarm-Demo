class SwarmWebSocket {
    constructor() {
        this.connect();
        this.onUpdateCallbacks = [];
        this.lastUpdateTime = performance.now();
        this.updateCount = 0;
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
                const now = performance.now();
                this.updateCount++;
                
                // Log update statistics every 100 updates
                if (this.updateCount % 100 === 0) {
                    const timeDiff = now - this.lastUpdateTime;
                    const fps = 1000 / (timeDiff / 100);
                    console.log(`Receiving updates at ${fps.toFixed(1)} FPS`);
                    console.log(`Active agents: ${data.agents.length}`);
                    if (data.agents.length > 0) {
                        console.log(`Sample agent position:`, data.agents[0]);
                    }
                    this.lastUpdateTime = now;
                }
                
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
            console.log('Sending message:', message);
            this.ws.send(JSON.stringify(message));
        }
    }

    onUpdate(callback) {
        this.onUpdateCallbacks.push(callback);
    }
}

// Initialize WebSocket connection
window.swarmWS = new SwarmWebSocket();

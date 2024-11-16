class SwarmRenderer {
    constructor(canvas) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');
        this.agents = [];
        this.trailPoints = [];
        this.maxTrailLength = 50;
        this.resize();
        window.addEventListener('resize', () => this.resize());
    }

    resize() {
        this.canvas.width = this.canvas.offsetWidth;
        this.canvas.height = this.canvas.offsetHeight;
    }

    updateAgents(agents) {
        this.agents = agents;
        // Store trail points
        agents.forEach(agent => {
            this.trailPoints.push({
                x: agent.x,
                y: agent.y,
                age: 0,
                role: agent.role
            });
        });
        
        // Remove old trail points
        this.trailPoints = this.trailPoints
            .filter(point => point.age < this.maxTrailLength)
            .map(point => ({...point, age: point.age + 1}));
    }

    getAgentColor(role) {
        switch(role) {
            case 'predator':
                return '#ff3333';  // Red
            case 'prey':
                return '#33ff33';  // Green
            default:
                return '#0ff';     // Cyan
        }
    }

    getTrailColor(role, alpha) {
        switch(role) {
            case 'predator':
                return `rgba(255, 51, 51, ${alpha * 0.5})`;
            case 'prey':
                return `rgba(51, 255, 51, ${alpha * 0.5})`;
            default:
                return `rgba(0, 255, 255, ${alpha * 0.5})`;
        }
    }

    render() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Draw trails
        this.trailPoints.forEach(point => {
            const alpha = 1 - (point.age / this.maxTrailLength);
            this.ctx.beginPath();
            this.ctx.arc(point.x, point.y, 1, 0, Math.PI * 2);
            this.ctx.fillStyle = this.getTrailColor(point.role, alpha);
            this.ctx.fill();
        });

        // Draw agents
        this.agents.forEach(agent => {
            const agentColor = this.getAgentColor(agent.role);
            
            // Agent body
            this.ctx.beginPath();
            this.ctx.arc(agent.x, agent.y, agent.role === 'predator' ? 7 : 5, 0, Math.PI * 2);
            this.ctx.fillStyle = agentColor;
            this.ctx.fill();
            
            // Direction indicator
            this.ctx.beginPath();
            this.ctx.moveTo(agent.x, agent.y);
            this.ctx.lineTo(
                agent.x + Math.cos(agent.angle) * 10,
                agent.y + Math.sin(agent.angle) * 10
            );
            this.ctx.strokeStyle = agent.role === 'normal' ? '#f0f' : agentColor;
            this.ctx.stroke();
        });
    }
}

// Initialize renderer when document is loaded
document.addEventListener('DOMContentLoaded', () => {
    const canvas = document.getElementById('swarmCanvas');
    window.swarmRenderer = new SwarmRenderer(canvas);
    
    // Start animation loop
    let lastTime = 0;
    const animate = (timestamp) => {
        const deltaTime = timestamp - lastTime;
        lastTime = timestamp;
        
        // Update FPS counter
        document.getElementById('fps').textContent = 
            Math.round(1000 / deltaTime);
            
        window.swarmRenderer.render();
        requestAnimationFrame(animate);
    };
    requestAnimationFrame(animate);
});

class SwarmControls {
    constructor() {
        this.initializeControls();
    }

    initializeControls() {
        // Control buttons
        document.getElementById('startBtn').onclick = () => {
            window.swarmWS.send({ type: 'command', action: 'start' });
        };

        document.getElementById('stopBtn').onclick = () => {
            window.swarmWS.send({ type: 'command', action: 'stop' });
        };

        document.getElementById('resetBtn').onclick = () => {
            window.swarmWS.send({ type: 'command', action: 'reset' });
        };

        // Parameter sliders
        const parameters = ['agentSpeed', 'swarmCohesion', 'swarmAlignment'];
        parameters.forEach(param => {
            const slider = document.getElementById(param);
            slider.onchange = () => {
                window.swarmWS.send({
                    type: 'parameter',
                    name: param,
                    value: parseFloat(slider.value)
                });
            };
        });

        // Behavior pattern buttons
        document.querySelectorAll('.pattern-btn').forEach(btn => {
            btn.onclick = () => {
                window.swarmWS.send({
                    type: 'pattern',
                    name: btn.dataset.pattern
                });
            };
        });
    }
}

// Initialize controls when document is loaded
document.addEventListener('DOMContentLoaded', () => {
    new SwarmControls();
});

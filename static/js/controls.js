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
        const parameters = [
            {id: 'agentSpeed', valueId: 'speedValue'},
            {id: 'swarmCohesion', valueId: 'cohesionValue'},
            {id: 'swarmAlignment', valueId: 'alignmentValue'},
            {id: 'waveFrequency', valueId: 'waveFrequencyValue'},
            {id: 'waveAmplitude', valueId: 'waveAmplitudeValue'}
        ];
        
        parameters.forEach(param => {
            const slider = document.getElementById(param.id);
            const valueDisplay = document.getElementById(param.valueId);
            
            if (slider && valueDisplay) {
                // Update value display on input
                slider.oninput = () => {
                    valueDisplay.textContent = slider.value;
                };
                
                // Send value to server on change
                slider.onchange = () => {
                    window.swarmWS.send({
                        type: 'parameter',
                        name: param.id,
                        value: parseFloat(slider.value)
                    });
                };
            }
        });

        // Behavior pattern buttons
        document.querySelectorAll('.pattern-btn').forEach(btn => {
            btn.onclick = () => {
                // Remove active class from all buttons
                document.querySelectorAll('.pattern-btn').forEach(b => 
                    b.classList.remove('active'));
                // Add active class to clicked button
                btn.classList.add('active');
                
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

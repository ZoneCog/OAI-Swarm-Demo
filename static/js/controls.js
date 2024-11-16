class SwarmControls {
    constructor() {
        this.currentRecording = null;
        this.parameterUpdateTimeout = null;
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

        // Recording controls
        document.getElementById('startRecordingBtn').onclick = () => {
            window.swarmWS.send({ type: 'command', action: 'start_recording' });
        };

        document.getElementById('stopRecordingBtn').onclick = () => {
            window.swarmWS.send({ type: 'command', action: 'stop_recording' });
        };

        document.getElementById('saveRecordingBtn').onclick = () => {
            window.swarmWS.send({ type: 'get_recording' });
        };

        document.getElementById('loadRecordingBtn').onclick = () => {
            document.getElementById('recordingFileInput').click();
        };

        document.getElementById('recordingFileInput').onchange = (event) => {
            const file = event.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = (e) => {
                    try {
                        this.currentRecording = JSON.parse(e.target.result);
                        console.log('Recording loaded:', this.currentRecording.length, 'states');
                    } catch (error) {
                        console.error('Error parsing recording file:', error);
                    }
                };
                reader.readAsText(file);
            }
        };

        document.getElementById('startPlaybackBtn').onclick = () => {
            if (this.currentRecording) {
                window.swarmWS.send({
                    type: 'command',
                    action: 'start_playback',
                    recording: this.currentRecording
                });
            } else {
                console.log('No recording loaded');
            }
        };

        document.getElementById('stopPlaybackBtn').onclick = () => {
            window.swarmWS.send({ type: 'command', action: 'stop_playback' });
        };

        // Enhanced parameter sliders with detailed logging
        const parameters = [
            {
                id: 'agentCount',
                valueId: 'agentCountValue',
                min: 5,
                max: 50,
                step: 1,
                immediate: true,
                initialValue: 50  // Match simulation.py initial value
            },
            {id: 'agentSpeed', valueId: 'speedValue', min: 1, max: 10, step: 0.5},
            {id: 'swarmCohesion', valueId: 'cohesionValue', min: 1, max: 10, step: 1},
            {id: 'swarmAlignment', valueId: 'alignmentValue', min: 1, max: 10, step: 1},
            {id: 'waveFrequency', valueId: 'waveFrequencyValue', min: 0.1, max: 2, step: 0.1},
            {id: 'waveAmplitude', valueId: 'waveAmplitudeValue', min: 10, max: 100, step: 5}
        ];
        
        parameters.forEach(param => {
            const slider = document.getElementById(param.id);
            const valueDisplay = document.getElementById(param.valueId);
            
            if (slider && valueDisplay) {
                // Set slider attributes
                slider.min = param.min;
                slider.max = param.max;
                slider.step = param.step;
                
                // Set initial value if specified
                if (param.initialValue !== undefined) {
                    slider.value = param.initialValue;
                    valueDisplay.textContent = param.initialValue;
                    console.log(`Initialized ${param.id} slider with value: ${param.initialValue}`);
                }

                // Update display and handle parameter changes
                slider.oninput = () => {
                    try {
                        const value = parseFloat(slider.value);
                        console.log(`${param.id} slider value changed to: ${value}`);

                        // Validate value is within bounds
                        if (value < param.min || value > param.max) {
                            console.error(`Invalid ${param.id} value: ${value}. Must be between ${param.min} and ${param.max}`);
                            return;
                        }

                        // Update display
                        valueDisplay.textContent = value;

                        // Send parameter update
                        if (param.immediate) {
                            console.log(`Sending immediate parameter update for ${param.id}: ${value}`);
                            this.sendParameterUpdate(param.id, value);
                        } else {
                            // Debounce other parameter updates
                            if (this.parameterUpdateTimeout) {
                                clearTimeout(this.parameterUpdateTimeout);
                            }
                            this.parameterUpdateTimeout = setTimeout(() => {
                                console.log(`Sending debounced parameter update for ${param.id}: ${value}`);
                                this.sendParameterUpdate(param.id, value);
                            }, 100);
                        }
                    } catch (error) {
                        console.error(`Error handling slider change for ${param.id}:`, error);
                    }
                };

                // Trigger initial value update for agent count
                if (param.id === 'agentCount' && param.initialValue !== undefined) {
                    this.sendParameterUpdate(param.id, param.initialValue);
                }
            } else {
                console.error(`Could not find slider or value display elements for ${param.id}`);
            }
        });

        // Behavior pattern buttons
        document.querySelectorAll('.pattern-btn').forEach(btn => {
            btn.onclick = () => {
                document.querySelectorAll('.pattern-btn').forEach(b => 
                    b.classList.remove('active'));
                btn.classList.add('active');
                
                window.swarmWS.send({
                    type: 'pattern',
                    name: btn.dataset.pattern
                });
            };
        });

        // Add WebSocket message handler for recording data
        window.swarmWS.onMessage((data) => {
            if (data.type === 'recording_data') {
                this.downloadRecording(data.recording);
            }
        });
    }

    sendParameterUpdate(name, value) {
        try {
            const message = {
                type: 'parameter',
                name: name,
                value: value
            };
            console.log(`Sending parameter update - ${name}: ${value}`);
            window.swarmWS.send(message);
        } catch (error) {
            console.error(`Error sending parameter update for ${name}:`, error);
        }
    }

    downloadRecording(recording) {
        const blob = new Blob([JSON.stringify(recording)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'swarm-recording.json';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }
}

// Initialize controls when document is loaded
document.addEventListener('DOMContentLoaded', () => {
    new SwarmControls();
});
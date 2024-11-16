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

        // Parameter sliders
        const parameters = [
            {id: 'agentCount', valueId: 'agentCountValue', min: 5, max: 50},
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
                // Set min and max for agent count
                if (param.id === 'agentCount') {
                    slider.min = param.min;
                    slider.max = param.max;
                }

                // Update display and send parameter immediately for agent count
                slider.oninput = () => {
                    const value = parseFloat(slider.value);
                    valueDisplay.textContent = value;
                    console.log(`Slider ${param.id} value changed to:`, value);

                    if (param.id === 'agentCount') {
                        // Validate agent count range
                        if (value >= param.min && value <= param.max) {
                            console.log(`Sending immediate agent count update: ${value}`);
                            this.sendParameterUpdate(param.id, value);
                        } else {
                            console.warn(`Invalid agent count value: ${value}. Must be between ${param.min} and ${param.max}`);
                        }
                    } else {
                        // Debounce other parameter updates
                        if (this.parameterUpdateTimeout) {
                            clearTimeout(this.parameterUpdateTimeout);
                        }
                        this.parameterUpdateTimeout = setTimeout(() => {
                            this.sendParameterUpdate(param.id, value);
                        }, 100);
                    }
                };
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
            console.error(`Error updating parameter ${name}:`, error);
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

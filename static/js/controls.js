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
            }
        };

        document.getElementById('stopPlaybackBtn').onclick = () => {
            window.swarmWS.send({ type: 'command', action: 'stop_playback' });
        };

        // Parameter sliders with immediate updates
        const parameters = [
            {id: 'agentCount', valueId: 'agentCountValue', min: 5, max: 50, step: 1},
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
                slider.min = param.min;
                slider.max = param.max;
                slider.step = param.step;
                
                // Initialize slider with current simulation value
                if (param.id === 'agentCount') {
                    // The value will be updated by the WebSocket state updates
                    window.swarmWS.onUpdate((data) => {
                        if (data.agents) {
                            const currentCount = data.agents.length;
                            slider.value = currentCount;
                            valueDisplay.textContent = currentCount;
                            console.log('Updated agent count slider to:', currentCount);
                        }
                    });
                }
                
                slider.oninput = () => {
                    const value = parseFloat(slider.value);
                    valueDisplay.textContent = value;
                    console.log(`Parameter ${param.id} changed to:`, value);
                    
                    // Immediate update for agent count
                    if (param.id === 'agentCount') {
                        console.log('Sending immediate agent count update:', value);
                        this.sendParameterUpdate(param.id, value);
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
        console.log('Sending parameter update:', name, value);
        window.swarmWS.send({
            type: 'parameter',
            name: name,
            value: value
        });
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

document.addEventListener('DOMContentLoaded', () => {
    new SwarmControls();
});

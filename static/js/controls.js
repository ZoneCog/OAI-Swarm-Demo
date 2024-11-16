class SwarmControls {
    constructor() {
        this.currentRecording = null;
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

        // Parameter sliders with unified handling
        const parameters = [
            {id: 'agentCount', valueId: 'agentCountValue', min: 1, max: 200, step: 1},
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
                
                slider.oninput = () => {
                    const value = parseFloat(slider.value);
                    valueDisplay.textContent = value;
                    this.sendParameterUpdate(param.id, value);
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

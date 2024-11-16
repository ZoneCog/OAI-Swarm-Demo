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
                slider.oninput = () => {
                    valueDisplay.textContent = slider.value;
                };
                
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

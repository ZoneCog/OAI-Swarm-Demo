class BehaviorEditor {
    constructor() {
        this.editor = null;
        this.initializeEditor();
    }

    initializeEditor() {
        // Create behavior editor container
        const editorContainer = document.createElement('div');
        editorContainer.className = 'behavior-editor';
        editorContainer.innerHTML = `
            <div class="editor-header">
                <h3>Custom Behavior Editor</h3>
                <button id="saveBehaviorBtn" class="neon-btn">Save Behavior</button>
                <button id="testBehaviorBtn" class="neon-btn">Test Behavior</button>
            </div>
            <div id="behaviorCode" class="editor-content"></div>
            <div class="editor-footer">
                <div id="editorStatus"></div>
            </div>
        `;

        // Add after analytics panel
        const analyticsPanel = document.querySelector('.analytics-panel');
        analyticsPanel.parentNode.insertBefore(editorContainer, analyticsPanel.nextSibling);

        // Initialize CodeMirror editor
        this.editor = CodeMirror(document.getElementById('behaviorCode'), {
            mode: 'python',
            theme: 'monokai',
            lineNumbers: true,
            autofocus: true,
            value: this.getDefaultTemplate()
        });

        this.setupEventListeners();
    }

    getDefaultTemplate() {
        return `# Custom Swarm Behavior
# Available variables:
# - agents: List of agent objects with properties: x, y, angle, role
# - dt: Time delta
# - speed: Base movement speed
# - parameters: Dictionary of current parameter values

def update_agents(agents, dt, speed, parameters):
    """
    Update agent positions and behaviors
    Returns: List of updated agent positions
    """
    for agent in agents:
        # Add your custom behavior logic here
        agent.x += math.cos(agent.angle) * speed
        agent.y += math.sin(agent.angle) * speed
        agent.angle += random.uniform(-0.1, 0.1)
    
    return agents`;
    }

    setupEventListeners() {
        document.getElementById('saveBehaviorBtn').onclick = () => {
            const code = this.editor.getValue();
            window.swarmWS.send({
                type: 'custom_behavior',
                action: 'save',
                code: code
            });
        };

        document.getElementById('testBehaviorBtn').onclick = () => {
            const code = this.editor.getValue();
            window.swarmWS.send({
                type: 'custom_behavior',
                action: 'test',
                code: code
            });
        };

        // Add message handler for behavior validation responses
        window.swarmWS.onMessage((data) => {
            if (data.type === 'behavior_response') {
                const status = document.getElementById('editorStatus');
                status.textContent = data.message;
                status.className = data.success ? 'success' : 'error';
            }
        });
    }
}

// Initialize editor when document is loaded
document.addEventListener('DOMContentLoaded', () => {
    new BehaviorEditor();
});

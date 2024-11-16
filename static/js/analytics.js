class SwarmAnalytics {
    constructor() {
        // Initialize analytics display
        this.initializeAnalytics();
    }

    initializeAnalytics() {
        // Add WebSocket message handler for analytics updates
        window.swarmWS.onUpdate((data) => {
            if (data.analytics) {
                this.updateAnalytics(data.analytics);
            }
        });
    }

    updateAnalytics(analytics) {
        // Update role counts
        document.getElementById('normalCount').textContent = analytics.role_counts.normal;
        document.getElementById('predatorCount').textContent = analytics.role_counts.predator;
        document.getElementById('preyCount').textContent = analytics.role_counts.prey;

        // Update distances
        document.getElementById('avgDistance').textContent = analytics.avg_distance;
        document.getElementById('predatorPreyDistance').textContent = 
            analytics.predator_prey_distances.length > 0 
                ? analytics.predator_prey_distances[analytics.predator_prey_distances.length - 1]
                : 'N/A';

        // Update swarm metrics
        document.getElementById('cohesionScore').textContent = analytics.cohesion_score;
        document.getElementById('alignmentScore').textContent = analytics.alignment_score;

        // Update interaction zones
        document.getElementById('closeInteractions').textContent = analytics.interaction_zones.close;
        document.getElementById('mediumInteractions').textContent = analytics.interaction_zones.medium;
        document.getElementById('farInteractions').textContent = analytics.interaction_zones.far;
    }
}

// Initialize analytics when document is loaded
document.addEventListener('DOMContentLoaded', () => {
    new SwarmAnalytics();
});

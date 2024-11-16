import math
import time
import threading
import random
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class Agent:
    x: float
    y: float
    angle: float
    vx: float = 0
    vy: float = 0
    
    def to_dict(self):
        return {
            'x': self.x,
            'y': self.y,
            'angle': self.angle
        }

class SwarmSimulation:
    def __init__(self):
        self.agents: List[Agent] = []
        self.running = False
        self.parameters = {
            'agentSpeed': 5,
            'swarmCohesion': 5,
            'swarmAlignment': 5
        }
        self.current_pattern = 'flocking'
        self.reset()
        
        # Start simulation thread
        self.thread = threading.Thread(target=self._simulation_loop)
        self.thread.daemon = True
        self.thread.start()

    def reset(self):
        """Reset simulation with new agents"""
        self.agents = []
        for _ in range(20):
            self.agents.append(Agent(
                x=random.uniform(100, 700),
                y=random.uniform(100, 500),
                angle=random.uniform(0, 2 * math.pi)
            ))

    def start(self):
        """Start simulation"""
        self.running = True

    def stop(self):
        """Stop simulation"""
        self.running = False

    def set_parameter(self, name: str, value: float):
        """Update simulation parameter"""
        if name in self.parameters:
            self.parameters[name] = value

    def set_pattern(self, pattern: str):
        """Change swarm behavior pattern"""
        self.current_pattern = pattern

    def get_agent_states(self) -> List[Dict]:
        """Get current state of all agents"""
        return [agent.to_dict() for agent in self.agents]

    def _simulation_loop(self):
        """Main simulation loop"""
        while True:
            if self.running:
                self._update()
            time.sleep(1/30)  # 30 FPS

    def _update(self):
        """Update agent positions and behaviors"""
        # Parameters
        speed = self.parameters['agentSpeed'] * 0.5
        cohesion = self.parameters['swarmCohesion'] * 0.02
        alignment = self.parameters['swarmAlignment'] * 0.02

        for agent in self.agents:
            if self.current_pattern == 'flocking':
                # Calculate center of mass and average direction
                cx, cy = 0, 0
                avg_angle = 0
                
                for other in self.agents:
                    if other != agent:
                        cx += other.x
                        cy += other.y
                        avg_angle += other.angle
                
                cx /= len(self.agents) - 1
                cy /= len(self.agents) - 1
                avg_angle /= len(self.agents) - 1
                
                # Update angle based on cohesion and alignment
                target_angle = math.atan2(cy - agent.y, cx - agent.x)
                agent.angle += (
                    cohesion * math.sin(target_angle - agent.angle) +
                    alignment * math.sin(avg_angle - agent.angle)
                )

            elif self.current_pattern == 'circle':
                # Circular motion around center
                center_x, center_y = 400, 300
                target_angle = math.atan2(
                    center_y - agent.y,
                    center_x - agent.x
                ) + math.pi/2
                agent.angle += 0.1 * math.sin(target_angle - agent.angle)

            elif self.current_pattern == 'scatter':
                # Random walk
                agent.angle += random.uniform(-0.1, 0.1)

            # Update position
            agent.x += math.cos(agent.angle) * speed
            agent.y += math.sin(agent.angle) * speed
            
            # Wrap around edges
            agent.x = agent.x % 800
            agent.y = agent.y % 600

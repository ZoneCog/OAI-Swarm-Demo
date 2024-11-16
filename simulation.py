import math
import time
import threading
import random
import json
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class Agent:
    x: float
    y: float
    angle: float
    vx: float = 0
    vy: float = 0
    role: str = 'normal'  # Can be 'normal', 'predator', or 'prey'
    
    def to_dict(self):
        return {
            'x': self.x,
            'y': self.y,
            'angle': self.angle,
            'role': self.role
        }

class SwarmSimulation:
    def __init__(self):
        self.agents: List[Agent] = []
        self.running = False
        self.parameters = {
            'agentSpeed': 5,
            'swarmCohesion': 5,
            'swarmAlignment': 5,
            'waveFrequency': 0.5,
            'waveAmplitude': 50
        }
        self.current_pattern = 'flocking'
        self.time_accumulated = 0
        
        # Recording related attributes
        self.recording = False
        self.recorded_states = []
        self.playback_mode = False
        self.playback_index = 0
        self.playback_states = []
        
        self.reset()
        print("SwarmSimulation initialized with", len(self.agents), "agents")
        
        # Start simulation thread
        self.thread = threading.Thread(target=self._simulation_loop)
        self.thread.daemon = True
        self.thread.start()
        print("Simulation thread started")

    def reset(self):
        """Reset simulation with new agents"""
        self.agents = []
        for i in range(20):
            role = 'predator' if i < 2 else 'prey' if i < 5 else 'normal'
            self.agents.append(Agent(
                x=random.uniform(100, 700),
                y=random.uniform(100, 500),
                angle=random.uniform(0, 2 * math.pi),
                role=role
            ))
        self.time_accumulated = 0
        self.stop_recording()
        self.stop_playback()
        print("Simulation reset with", len(self.agents), "agents")

    def start(self):
        """Start simulation"""
        self.running = True
        print("Simulation started")

    def stop(self):
        """Stop simulation"""
        self.running = False
        print("Simulation stopped")

    def start_recording(self):
        """Start recording agent states"""
        if not self.playback_mode:
            self.recording = True
            self.recorded_states = []
            print("Recording started")

    def stop_recording(self):
        """Stop recording agent states"""
        self.recording = False
        print("Recording stopped")

    def save_recording(self) -> List[Dict]:
        """Return recorded states"""
        return self.recorded_states

    def load_recording(self, states: List[Dict]):
        """Load recorded states for playback"""
        self.playback_states = states
        print(f"Loaded {len(states)} recorded states")

    def start_playback(self):
        """Start playback mode"""
        if len(self.playback_states) > 0:
            self.playback_mode = True
            self.playback_index = 0
            self.running = True
            print("Playback started")

    def stop_playback(self):
        """Stop playback mode"""
        self.playback_mode = False
        self.playback_index = 0
        print("Playback stopped")

    def set_parameter(self, name: str, value: float):
        """Update simulation parameter"""
        if name in self.parameters:
            self.parameters[name] = float(value)
            print(f"Parameter {name} set to {value}")

    def set_pattern(self, pattern: str):
        """Change swarm behavior pattern"""
        self.current_pattern = pattern
        print(f"Pattern changed to {pattern}")

    def get_agent_states(self) -> List[Dict]:
        """Get current state of all agents"""
        return [agent.to_dict() for agent in self.agents]

    def _simulation_loop(self):
        """Main simulation loop"""
        last_update = time.time()
        updates_count = 0
        print("Simulation loop started")
        
        while True:
            if self.running:
                current_time = time.time()
                dt = current_time - last_update
                last_update = current_time
                
                if self.playback_mode:
                    if self.playback_index < len(self.playback_states):
                        # Load agent states from recording
                        state = self.playback_states[self.playback_index]
                        self.agents = [
                            Agent(x=a['x'], y=a['y'], angle=a['angle'], role=a['role'])
                            for a in state
                        ]
                        self.playback_index += 1
                    else:
                        self.stop_playback()
                        self.stop()
                else:
                    self.time_accumulated += dt
                    self._update(dt)
                    
                    # Record state if recording is enabled
                    if self.recording:
                        self.recorded_states.append(self.get_agent_states())
                
                updates_count += 1
                if updates_count % 100 == 0:
                    print(f"Simulation running: {updates_count} updates completed")
                    if self.agents:
                        agent = self.agents[0]
                        print(f"Sample agent position: x={agent.x:.2f}, y={agent.y:.2f}, angle={agent.angle:.2f}")
                        
            time.sleep(1/60)  # 60 FPS target

    def _update(self, dt: float):
        """Update agent positions and behaviors"""
        base_speed = max(self.parameters['agentSpeed'], 2)
        speed = base_speed * 4.0 * dt
        cohesion = self.parameters['swarmCohesion'] * 0.02
        alignment = self.parameters['swarmAlignment'] * 0.02

        if self.current_pattern == 'predator_prey':
            self._update_predator_prey(speed, dt)
        elif self.current_pattern == 'vortex':
            self._update_vortex(speed, dt)
        elif self.current_pattern == 'split_merge':
            self._update_split_merge(speed, dt)
        elif self.current_pattern == 'wave':
            self._update_wave(speed, dt)
        elif self.current_pattern == 'flocking':
            self._update_flocking(speed, cohesion, alignment)
        elif self.current_pattern == 'circle':
            self._update_circle(speed)
        elif self.current_pattern == 'scatter':
            self._update_scatter(speed)

        # Apply position updates and wrapping
        for agent in self.agents:
            agent.x = agent.x % 800
            agent.y = agent.y % 600

    def _update_predator_prey(self, speed: float, dt: float):
        """Predator-prey behavior pattern"""
        for agent in self.agents:
            if agent.role == 'predator':
                # Predators chase closest prey
                closest_prey = None
                min_dist = float('inf')
                for other in self.agents:
                    if other.role == 'prey':
                        dist = math.sqrt((agent.x - other.x)**2 + (agent.y - other.y)**2)
                        if dist < min_dist:
                            min_dist = dist
                            closest_prey = other
                
                if closest_prey:
                    target_angle = math.atan2(closest_prey.y - agent.y, closest_prey.x - agent.x)
                    agent.angle += 0.1 * math.sin(target_angle - agent.angle)
                    agent.x += math.cos(agent.angle) * speed * 1.2  # Predators are faster
                    agent.y += math.sin(agent.angle) * speed * 1.2
            
            elif agent.role == 'prey':
                # Prey flee from closest predator
                closest_predator = None
                min_dist = float('inf')
                for other in self.agents:
                    if other.role == 'predator':
                        dist = math.sqrt((agent.x - other.x)**2 + (agent.y - other.y)**2)
                        if dist < min_dist:
                            min_dist = dist
                            closest_predator = other
                
                if closest_predator and min_dist < 200:  # Only flee if predator is close
                    flee_angle = math.atan2(agent.y - closest_predator.y, agent.x - closest_predator.x)
                    agent.angle += 0.1 * math.sin(flee_angle - agent.angle)
                    agent.x += math.cos(agent.angle) * speed * 1.1  # Prey slightly faster than normal
                    agent.y += math.sin(agent.angle) * speed * 1.1
                else:
                    # Normal movement if no predator nearby
                    agent.x += math.cos(agent.angle) * speed
                    agent.y += math.sin(agent.angle) * speed
            
            else:  # Normal agents
                agent.x += math.cos(agent.angle) * speed
                agent.y += math.sin(agent.angle) * speed
                agent.angle += random.uniform(-0.1, 0.1)

    def _update_vortex(self, speed: float, dt: float):
        """Vortex pattern - spiral formation"""
        center_x, center_y = 400, 300
        for agent in self.agents:
            # Calculate distance from center
            dx = agent.x - center_x
            dy = agent.y - center_y
            distance = math.sqrt(dx*dx + dy*dy)
            
            # Calculate tangential and radial components
            current_angle = math.atan2(dy, dx)
            spiral_factor = 0.1  # Controls how tight the spiral is
            
            # Adjust angle based on distance (closer = faster rotation)
            rotation_speed = 2.0 / (distance + 50)  # Prevent division by zero
            target_angle = current_angle + math.pi/2 + spiral_factor
            
            # Smoothly adjust to target angle
            agent.angle += 0.1 * math.sin(target_angle - agent.angle)
            
            # Move agent
            agent.x += math.cos(agent.angle) * speed
            agent.y += math.sin(agent.angle) * speed

    def _update_split_merge(self, speed: float, dt: float):
        """Split-merge pattern - swarm splits and merges periodically"""
        # Use accumulated time to create periodic behavior
        split_period = 5.0  # Complete cycle every 5 seconds
        split_phase = (math.sin(self.time_accumulated * 2 * math.pi / split_period) + 1) / 2
        
        # Two attraction points that move with time
        center1_x = 400 + math.cos(self.time_accumulated) * 200 * split_phase
        center1_y = 300 + math.sin(self.time_accumulated) * 200 * split_phase
        center2_x = 400 - math.cos(self.time_accumulated) * 200 * split_phase
        center2_y = 300 - math.sin(self.time_accumulated) * 200 * split_phase
        
        for i, agent in enumerate(self.agents):
            # Alternate agents between centers
            target_x = center1_x if i % 2 == 0 else center2_x
            target_y = center1_y if i % 2 == 0 else center2_y
            
            # Calculate direction to target
            dx = target_x - agent.x
            dy = target_y - agent.y
            target_angle = math.atan2(dy, dx)
            
            # Smoothly adjust angle
            angle_diff = (target_angle - agent.angle + math.pi) % (2 * math.pi) - math.pi
            agent.angle += 0.1 * angle_diff
            
            # Move agent
            agent.x += math.cos(agent.angle) * speed
            agent.y += math.sin(agent.angle) * speed

    def _update_wave(self, speed: float, dt: float):
        """Wave pattern - sine wave formation"""
        frequency = self.parameters['waveFrequency']
        amplitude = self.parameters['waveAmplitude']
        
        for i, agent in enumerate(self.agents):
            # Calculate base position along a line
            base_x = (i * 40 + self.time_accumulated * speed * 50) % 800
            base_y = 300  # Center of screen
            
            # Add sine wave offset
            wave_offset = amplitude * math.sin(frequency * (base_x / 100 + self.time_accumulated))
            target_y = base_y + wave_offset
            
            # Calculate direction to target
            dx = base_x - agent.x
            dy = target_y - agent.y
            target_angle = math.atan2(dy, dx)
            
            # Smoothly adjust angle
            angle_diff = (target_angle - agent.angle + math.pi) % (2 * math.pi) - math.pi
            agent.angle += 0.1 * angle_diff
            
            # Move agent
            agent.x += math.cos(agent.angle) * speed
            agent.y += math.sin(agent.angle) * speed

    def _update_flocking(self, speed: float, cohesion: float, alignment: float):
        """Original flocking behavior"""
        for agent in self.agents:
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
            
            target_angle = math.atan2(cy - agent.y, cx - agent.x)
            agent.angle += (
                cohesion * math.sin(target_angle - agent.angle) +
                alignment * math.sin(avg_angle - agent.angle)
            )
            
            agent.x += math.cos(agent.angle) * speed
            agent.y += math.sin(agent.angle) * speed

    def _update_circle(self, speed: float):
        """Original circular pattern"""
        center_x, center_y = 400, 300
        for agent in self.agents:
            target_angle = math.atan2(
                center_y - agent.y,
                center_x - agent.x
            ) + math.pi/2
            agent.angle += 0.1 * math.sin(target_angle - agent.angle)
            
            agent.x += math.cos(agent.angle) * speed
            agent.y += math.sin(agent.angle) * speed

    def _update_scatter(self, speed: float):
        """Original scatter pattern"""
        for agent in self.agents:
            agent.angle += random.uniform(-0.1, 0.1)
            agent.x += math.cos(agent.angle) * speed
            agent.y += math.sin(agent.angle) * speed
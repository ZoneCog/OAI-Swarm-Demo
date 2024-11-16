import math
import time
import threading
import random
import json
import logging
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple

# Configure logging
logging.basicConfig(level=logging.DEBUG,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class Agent:
    x: float
    y: float
    angle: float
    vx: float = 0
    vy: float = 0
    role: str = 'normal'  # Can be 'normal', 'predator', or 'prey'
    state: str = 'normal'  # Added state field for tracking organization status
    
    def to_dict(self):
        return {
            'x': self.x,
            'y': self.y,
            'angle': self.angle,
            'role': self.role,
            'state': self.state
        }

    def distance_to(self, other: 'Agent') -> float:
        dx = other.x - self.x
        dy = other.y - self.y
        return math.sqrt(dx * dx + dy * dy)

class SwarmAnalytics:
    def __init__(self):
        self.reset_metrics()

    def reset_metrics(self):
        self.avg_distance: float = 0.0
        self.predator_prey_distances: List[float] = []
        self.role_counts: Dict[str, int] = {'normal': 0, 'predator': 0, 'prey': 0}
        self.pattern_durations: Dict[str, float] = {}
        self.pattern_switches: int = 0
        self.cohesion_score: float = 0.0
        self.alignment_score: float = 0.0
        self.interaction_zones: Dict[str, int] = {
            'close': 0,  # < 50 units
            'medium': 0, # 50-150 units
            'far': 0     # > 150 units
        }

    def to_dict(self):
        return {
            'avg_distance': round(self.avg_distance, 2),
            'predator_prey_distances': [round(d, 2) for d in self.predator_prey_distances[-5:]],
            'role_counts': self.role_counts,
            'pattern_switches': self.pattern_switches,
            'cohesion_score': round(self.cohesion_score, 2),
            'alignment_score': round(self.alignment_score, 2),
            'interaction_zones': self.interaction_zones
        }

class SwarmSimulation:
    MIN_AGENTS = 5
    MAX_AGENTS = 50
    
    def __init__(self):
        self.agents: List[Agent] = []
        self.running = False
        self.parameters = {
            'agentCount': self.MIN_AGENTS,
            'agentSpeed': 5,
            'swarmCohesion': 5,
            'swarmAlignment': 5,
            'waveFrequency': 0.5,
            'waveAmplitude': 50
        }
        self.current_pattern = 'flocking'
        self._initialize_simulation()

    def _initialize_simulation(self):
        """Initialize simulation components"""
        self.time_accumulated = 0
        self.last_pattern_change = time.time()
        self.analytics = SwarmAnalytics()
        self.recording = False
        self.recorded_states = []
        self.playback_mode = False
        self.playback_index = 0
        self.playback_states = []
        
        self.reset()
        logger.info("SwarmSimulation initialized with %d agents", len(self.agents))
        
        # Start simulation thread
        self.thread = threading.Thread(target=self._simulation_loop)
        self.thread.daemon = True
        self.thread.start()
        logger.info("Simulation thread started")

    def _validate_agent_count(self, count: int) -> int:
        """Simple validation to ensure count is between MIN_AGENTS and MAX_AGENTS"""
        return max(min(int(count), self.MAX_AGENTS), self.MIN_AGENTS)

    def set_parameter(self, name: str, value: float) -> bool:
        """Update simulation parameter with validation"""
        try:
            if name not in self.parameters:
                return False

            if name == 'agentCount':
                logger.info(f"Received agent count update request: {value}")
                count = self._validate_agent_count(int(value))
                logger.info(f"Validated agent count: {count}")
                self.parameters[name] = count
                self.reset()
                return True
            
            self.parameters[name] = float(value)
            return True
            
        except (ValueError, TypeError) as e:
            logger.error(f"Error setting parameter {name}: {e}")
            return False

    def reset(self):
        """Reset simulation with current parameter value"""
        self.agents = []
        agent_count = self.parameters['agentCount']
        logger.info(f"Resetting simulation with {agent_count} agents")
        
        predator_count = max(2, int(agent_count * 0.1))
        prey_count = max(3, int(agent_count * 0.15))
        normal_count = agent_count - (predator_count + prey_count)
        
        # Create predators
        for _ in range(predator_count):
            self.agents.append(Agent(
                x=random.uniform(100, 700),
                y=random.uniform(100, 500),
                angle=random.uniform(0, 2 * math.pi),
                role='predator'
            ))
            
        # Create prey
        for _ in range(prey_count):
            self.agents.append(Agent(
                x=random.uniform(100, 700),
                y=random.uniform(100, 500),
                angle=random.uniform(0, 2 * math.pi),
                role='prey'
            ))
            
        # Create normal agents
        for _ in range(normal_count):
            self.agents.append(Agent(
                x=random.uniform(100, 700),
                y=random.uniform(100, 500),
                angle=random.uniform(0, 2 * math.pi),
                role='normal'
            ))

        self.time_accumulated = 0
        self.stop_recording()
        self.stop_playback()
        self.analytics.reset_metrics()
        logger.info(f"Reset complete. Total agents: {len(self.agents)}")

    def start(self):
        """Start simulation"""
        self.running = True
        logger.info("Simulation started")

    def stop(self):
        """Stop simulation"""
        self.running = False
        logger.info("Simulation stopped")

    def start_recording(self):
        """Start recording agent states"""
        if not self.playback_mode:
            self.recording = True
            self.recorded_states = []
            logger.info("Recording started")

    def stop_recording(self):
        """Stop recording agent states"""
        self.recording = False
        logger.info("Recording stopped")

    def save_recording(self) -> List[Dict]:
        """Return recorded states"""
        return self.recorded_states

    def load_recording(self, states: List[Dict]):
        """Load recorded states for playback"""
        self.playback_states = states
        logger.info(f"Loaded {len(states)} recorded states")

    def start_playback(self):
        """Start playback mode"""
        if len(self.playback_states) > 0:
            self.playback_mode = True
            self.playback_index = 0
            self.running = True
            logger.info("Playback started")

    def stop_playback(self):
        """Stop playback mode"""
        self.playback_mode = False
        self.playback_index = 0
        logger.info("Playback stopped")

    def set_pattern(self, pattern: str):
        """Change swarm behavior pattern"""
        if pattern != self.current_pattern:
            self.analytics.pattern_switches += 1
            current_time = time.time()
            duration = current_time - self.last_pattern_change
            self.analytics.pattern_durations[self.current_pattern] = \
                self.analytics.pattern_durations.get(self.current_pattern, 0) + duration
            self.last_pattern_change = current_time
            
        self.current_pattern = pattern
        logger.info(f"Pattern changed to {pattern}")

    def get_analytics(self) -> Dict:
        """Get current analytics data"""
        return self.analytics.to_dict()

    def get_agent_states(self) -> List[Dict]:
        """Get current state of all agents"""
        return [agent.to_dict() for agent in self.agents]

    def _simulation_loop(self):
        """Main simulation loop"""
        last_update = time.time()
        updates_count = 0
        logger.info("Simulation loop started")
        
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
                    self._update_analytics()
                    
                    # Record state if recording is enabled
                    if self.recording:
                        self.recorded_states.append(self.get_agent_states())
                
                updates_count += 1
                if updates_count % 100 == 0:
                    logger.debug(f"Simulation running: {updates_count} updates completed")
                    if self.agents:
                        agent = self.agents[0]
                        logger.debug(f"Sample agent position: x={agent.x:.2f}, y={agent.y:.2f}, angle={agent.angle:.2f}")
                        
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
        elif self.current_pattern == 'custom':
            self._update_custom(speed, dt)
        elif self.current_pattern == 'collective_action':
            self._update_collective_action(speed, dt)
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

    def _update_collective_action(self, speed: float, dt: float):
        """Enhanced collective action behavior where prey organize to chase predators"""
        # Count prey agents and check organization threshold
        prey_agents = [agent for agent in self.agents if agent.role == 'prey']
        num_prey = len(prey_agents)
        organize_threshold = int(len(self.agents) * self.ORGANIZATION_THRESHOLD)
        
        logger.debug(f"Collective action update - Prey count: {num_prey}, Threshold: {organize_threshold}")

        # Update organization state
        is_organized = num_prey >= organize_threshold
        for agent in prey_agents:
            agent.state = 'organized' if is_organized else 'normal'
            
        if is_organized:
            logger.debug("Prey agents are organized - forming collective")
            # Find center of predators
            predator_agents = [a for a in self.agents if a.role == 'predator']
            if predator_agents:
                target_x = sum(a.x for a in predator_agents) / len(predator_agents)
                target_y = sum(a.y for a in predator_agents) / len(predator_agents)
            else:
                target_x, target_y = 400, 300

            # Move formation center towards predators
            dx = target_x - self.formation_center['x']
            dy = target_y - self.formation_center['y']
            dist = math.sqrt(dx*dx + dy*dy)
            
            if dist > 0:
                self.formation_center['x'] += int((dx/dist) * speed * 0.5)
                self.formation_center['y'] += int((dy/dist) * speed * 0.5)

            # Arrange prey in arrow formation
            formation_radius = 30 + num_prey * 2
            for idx, agent in enumerate(prey_agents):
                angle = (2 * math.pi * idx) / num_prey
                # Create arrow shape
                if abs(angle - math.pi) < math.pi/3:
                    radius = formation_radius * 0.7  # Front of arrow
                else:
                    radius = formation_radius  # Wings
                
                desired_x = self.formation_center['x'] + radius * math.cos(angle)
                desired_y = self.formation_center['y'] + radius * math.sin(angle)
                
                dx = desired_x - agent.x
                dy = desired_y - agent.y
                target_angle = math.atan2(dy, dx)
                
                # Smooth angle adjustment
                angle_diff = (target_angle - agent.angle + math.pi) % (2 * math.pi) - math.pi
                agent.angle += angle_diff * 0.1
                
                # Move agent
                agent.x += math.cos(agent.angle) * speed * 1.2
                agent.y += math.sin(agent.angle) * speed * 1.2

            # Convert nearby normal agents to prey
            conversions = 0
            for agent in prey_agents:
                for other in self.agents:
                    if other.role == 'normal':
                        dist = agent.distance_to(other)
                        if dist < self.CONVERSION_RADIUS:
                            other.role = 'prey'
                            other.state = 'organized' if is_organized else 'normal'
                            conversions += 1
            
            if conversions > 0:
                logger.debug(f"Converted {conversions} normal agents to prey")

            # Update predators - they now flee from organized prey
            for agent in [a for a in self.agents if a.role == 'predator']:
                dx = agent.x - self.formation_center['x']
                dy = agent.y - self.formation_center['y']
                dist = math.sqrt(dx*dx + dy*dy)
                
                if dist < self.FLEE_DISTANCE:
                    flee_angle = math.atan2(dy, dx)
                    agent.angle = flee_angle
                    agent.x += math.cos(agent.angle) * speed * 1.5
                    agent.y += math.sin(agent.angle) * speed * 1.5
                else:
                    # Random movement when not fleeing
                    agent.angle += random.uniform(-0.1, 0.1)
                    agent.x += math.cos(agent.angle) * speed
                    agent.y += math.sin(agent.angle) * speed
        else:
            logger.debug("Prey agents not organized - standard behavior")
            # Standard behavior for unorganized prey
            for agent in prey_agents:
                agent.angle += random.uniform(-0.1, 0.1)
                agent.x += math.cos(agent.angle) * speed
                agent.y += math.sin(agent.angle) * speed

            # Normal predator behavior
            for agent in [a for a in self.agents if a.role == 'predator']:
                agent.angle += random.uniform(-0.1, 0.1)
                agent.x += math.cos(agent.angle) * speed * 1.2
                agent.y += math.sin(agent.angle) * speed * 1.2

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
            
            # Add wave motion
            wave_y = math.sin(2 * math.pi * frequency * (base_x / 800 + self.time_accumulated)) * amplitude
            target_y = base_y + wave_y
            
            # Move towards target position
            dx = base_x - agent.x
            dy = target_y - agent.y
            target_angle = math.atan2(dy, dx)
            
            # Smoothly adjust angle
            angle_diff = (target_angle - agent.angle + math.pi) % (2 * math.pi) - math.pi
            agent.angle += 0.1 * angle_diff
            
            # Move agent
            agent.x += math.cos(agent.angle) * speed
            agent.y += math.sin(agent.angle) * speed

    def _update_custom(self, speed: float, dt: float):
        """Execute custom behavior pattern"""
        if hasattr(self, 'custom_behavior') and self.custom_behavior:
            try:
                # Create a safe namespace for custom code execution
                namespace = {
                    'math': math,
                    'random': random,
                    'agents': self.agents,
                    'dt': dt,
                    'speed': speed,
                    'parameters': self.parameters
                }
                
                # Execute custom behavior
                exec(self.custom_behavior, namespace)
                
                # Call the update_agents function from custom code
                if 'update_agents' in namespace:
                    updated_agents = namespace['update_agents'](
                        self.agents, dt, speed, self.parameters
                    )
                    if isinstance(updated_agents, list):
                        self.agents = updated_agents
            except Exception as e:
                print(f"Error in custom behavior: {str(e)}")

    def validate_custom_behavior(self, code: str) -> tuple[bool, str]:
        """Validate custom behavior code"""
        try:
            # Check for unsafe imports
            if any(keyword in code for keyword in ['import', 'exec', 'eval', '__']):
                return False, "Unsafe code detected"
            
            # Try to compile the code
            compile(code, '<string>', 'exec')
            
            # Basic structure validation
            if 'def update_agents' not in code:
                return False, "Missing update_agents function"
            
            return True, "Behavior code validated successfully"
        except Exception as e:
            return False, f"Validation error: {str(e)}"

    def set_custom_behavior(self, code: str) -> tuple[bool, str]:
        """Set custom behavior code after validation"""
        is_valid, message = self.validate_custom_behavior(code)
        if is_valid:
            self.custom_behavior = code
        return is_valid, message

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

    def _update_analytics(self):
        """Update analytics metrics"""
        if len(self.agents) < 2:
            return

        # Calculate average distance between all agents
        total_distance = 0
        distance_count = 0
        self.analytics.predator_prey_distances = []
        
        # Reset interaction zones
        self.analytics.interaction_zones = {'close': 0, 'medium': 0, 'far': 0}
        
        # Reset role counts
        self.analytics.role_counts = {'normal': 0, 'predator': 0, 'prey': 0}
        
        # Calculate cohesion and alignment scores
        center_x = sum(agent.x for agent in self.agents) / len(self.agents)
        center_y = sum(agent.y for agent in self.agents) / len(self.agents)
        avg_angle = sum(agent.angle for agent in self.agents) / len(self.agents)
        
        cohesion_total = 0
        alignment_total = 0

        for i, agent1 in enumerate(self.agents):
            self.analytics.role_counts[agent1.role] += 1
            
            for j, agent2 in enumerate(self.agents[i+1:], i+1):
                dx = agent1.x - agent2.x
                dy = agent1.y - agent2.y
                distance = math.sqrt(dx*dx + dy*dy)
                
                # Update interaction zones
                if distance < 50:
                    self.analytics.interaction_zones['close'] += 1
                elif distance < 150:
                    self.analytics.interaction_zones['medium'] += 1
                else:
                    self.analytics.interaction_zones['far'] += 1
                
                total_distance += distance
                distance_count += 1
                
                # Track predator-prey interactions
                if (agent1.role == 'predator' and agent2.role == 'prey') or \
                   (agent1.role == 'prey' and agent2.role == 'predator'):
                    self.analytics.predator_prey_distances.append(distance)
            
            # Calculate individual agent's contribution to cohesion and alignment
            agent_dist = math.sqrt((agent1.x - center_x)**2 + (agent1.y - center_y)**2)
            cohesion_total += agent_dist
            angle_diff = abs(math.sin(agent1.angle - avg_angle))
            alignment_total += angle_diff

        self.analytics.avg_distance = total_distance / max(1, distance_count)
        self.analytics.cohesion_score = 100 * (1 - cohesion_total / (len(self.agents) * 400))  # 400 is max expected distance
        self.analytics.alignment_score = 100 * (1 - alignment_total / len(self.agents))
import random
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.template import Template
from spade.message import Message
from environment import Environment

class ObserverAgent(Agent):
    class PollutionNotificationBehaviour(CyclicBehaviour):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.q_table = {}
            self.learning_rate = 0.8
            self.discount_factor = 0.9
            self.epsilon = 0.2
            self.start_pos = (0, 0)
        
        def get_possible_actions(self, position):
            x, y = position
            actions = []
            if x > 0: actions.append((x-1, y))  # Left
            if x < Environment.SIZE-1: actions.append((x+1, y))  # Right
            if y > 0: actions.append((x, y-1))  # Down
            if y < Environment.SIZE-1: actions.append((x, y+1))  # Up
            return actions
        
        def initialize_q_table(self):
            
            all_positions = [(x, y) for x in range(Environment.SIZE) 
                           for y in range(Environment.SIZE)]
            for pos in all_positions:
                for action in self.get_possible_actions(pos):
                    self.q_table[(pos, action)] = 0
        
        def find_optimal_directions(self, polluted_cells):
            if not polluted_cells:
                return []
            
            self.q_table = {}
            episodes = 1000
            best_path = None
            best_steps = float('inf')
            
            polluted_cells_set = set(polluted_cells)
            
            for _ in range(episodes):
                current_pos = self.start_pos
                remaining_cells = polluted_cells_set.copy()
                path = []
                visited = set()
                
                while remaining_cells:
                    state = (current_pos, frozenset(remaining_cells))
                    
                    possible_actions = self.get_possible_actions(current_pos)
                    if not possible_actions:
                        break  # no moves possible
                    
                    # ε-greedy action selection
                    if random.random() < self.epsilon:
                        action = random.choice(possible_actions)
                    else:
                        action = max(possible_actions,
                                    key=lambda a: self.q_table.get((state, a), 0))
                    
                    dx = action[0] - current_pos[0]
                    dy = action[1] - current_pos[1]
                    if dx == 1:
                        direction = "right"
                    elif dx == -1:
                        direction = "left"
                    elif dy == 1:
                        direction = "up"
                    else:
                        direction = "down"
                    
                    path.append(direction)
                    next_pos = action
                    
                    reward = -1
                    if next_pos in remaining_cells:
                        reward = 100
                        remaining_cells.remove(next_pos)
                    
                    next_state = (next_pos, frozenset(remaining_cells))
                    max_next_q = max([self.q_table.get((next_state, a), 0)
                                    for a in self.get_possible_actions(next_pos)], default=0)
                    current_q = self.q_table.get((state, action), 0)
                    
                    new_q = current_q + self.learning_rate * (reward + self.discount_factor * max_next_q - current_q)
                    self.q_table[(state, action)] = new_q
                    
                    current_pos = next_pos
                
                if not remaining_cells and len(path) < best_steps:
                    best_path = path
                    best_steps = len(path)
            
            return best_path if best_path else []


        async def run(self):
            msg = await self.receive(timeout=10)
            if msg:
                print("\n" + "="*50)
                print("Observer received new pollution report:")
                print(f"From: {msg.sender}")
                print(f"Body: {msg.body}")
                print("="*50 + "\n")
                
                # Parse polluted cells
                polluted_cells = [tuple(map(int, coord.split(","))) 
                                for coord in msg.body.split(";")]
                
                Environment.display_grid()
                
                # Find optimal movement directions
                directions = self.find_optimal_directions(polluted_cells)
                
                if directions:
                    # Verify all polluted cells are covered
                    current_pos = self.start_pos
                    visited_cells = set()
                    
                    for direction in directions:
                        x, y = current_pos
                        if direction == "left": x -= 1
                        elif direction == "right": x += 1
                        elif direction == "up": y += 1
                        elif direction == "down": y -= 1
                        current_pos = (x, y)
                        
                        if current_pos in polluted_cells:
                            visited_cells.add(current_pos)
                    
                    coverage = len(visited_cells) == len(polluted_cells)
                    print(f"Path covers all cells: {coverage}")
                    print(f"Optimal directions ({len(directions)} moves):")
                    print(", ".join(directions))
                    
                    # Send to CleanerAgent
                    path_str = ",".join(directions)
                    cleaner_msg = Message(
                        to="cleaner1234@xmpp.jp",
                        body=path_str,
                        metadata={
                            "performative": "request",
                            "ontology": "cleaning-path",
                            "action": "execute-cleaning"
                        }
                    )
                    await self.send(cleaner_msg)
                    print("Sent directions to CleanerAgent")
                else:
                    print("Error: Failed to generate valid path")

    async def setup(self):
        print("ObserverAgent started")
        template = Template()
        template.metadata = {
            "performative": "inform",
            "ontology": "pollution-report"
        }
        self.add_behaviour(self.PollutionNotificationBehaviour(), template)
import random
import asyncio
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.template import Template
from spade.message import Message
from environment import Environment
import numpy as np

class ObserverAgent(Agent):
    class PollutionNotificationBehaviour(CyclicBehaviour):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.q_table = {}
            self.learning_rate = 0.8
            self.discount_factor = 0.9
            self.epsilon = 0.2
            self.start_pos = (0, 0)
            self.best_path_history = []  # Track best path lengths over time

        def get_possible_actions(self, position):
            x, y = position
            actions = []
            if x > 0: actions.append((x-1, y))
            if x < Environment.SIZE-1: actions.append((x+1, y))
            if y > 0: actions.append((x, y-1))
            if y < Environment.SIZE-1: actions.append((x, y+1))
            return actions

        def visualize_path(self, directions, polluted_cells, is_best=False):
            x, y = self.start_pos
            grid = np.zeros_like(Environment.grid)

            # Mark polluted cells (green)
            for px, py in polluted_cells:
                grid[px, py] = 1

            # Mark the path
            path_color = 3 if is_best else 2  # Different colors for best vs current
            for direction in directions:
                if direction == "left": x -= 1
                elif direction == "right": x += 1
                elif direction == "up": y += 1
                elif direction == "down": y -= 1
                if 0 <= x < Environment.SIZE and 0 <= y < Environment.SIZE:
                    grid[x, y] = path_color

            # Mark start position (red)
            sx, sy = self.start_pos
            grid[sx, sy] = 4

            Environment.learning_grid = grid
            Environment.update_plot()

        def find_optimal_directions(self, polluted_cells):
            if not polluted_cells:
                return []

            self.q_table = {}
            episodes = 1000
            polluted_cells_set = set(polluted_cells)
            best_path = None
            best_steps = float('inf')
            self.best_path_history = []

            for ep in range(episodes):
                current_pos = self.start_pos
                remaining_cells = polluted_cells_set.copy()
                path = []

                while remaining_cells:
                    state = (current_pos, frozenset(remaining_cells))
                    actions = self.get_possible_actions(current_pos)
                    if not actions:
                        break

                    # ε-greedy action selection
                    if random.random() < self.epsilon:
                        action = random.choice(actions)
                    else:
                        action = max(actions, key=lambda a: self.q_table.get((state, a), 0))

                    next_pos = action
                    reward = 100 if next_pos in remaining_cells else -1
                    if next_pos in remaining_cells:
                        remaining_cells.remove(next_pos)

                    # Q-learning update
                    next_state = (next_pos, frozenset(remaining_cells))
                    max_q = max([self.q_table.get((next_state, a), 0) for a in self.get_possible_actions(next_pos)], default=0)
                    curr_q = self.q_table.get((state, action), 0)
                    self.q_table[(state, action)] = curr_q + self.learning_rate * (reward + self.discount_factor * max_q - curr_q)

                    # Convert action to direction
                    dx = next_pos[0] - current_pos[0]
                    dy = next_pos[1] - current_pos[1]
                    if dx == 1: path.append("right")
                    elif dx == -1: path.append("left")
                    elif dy == 1: path.append("up")
                    else: path.append("down")
                    current_pos = next_pos

                # Update best path if current path is better
                if not remaining_cells and len(path) < best_steps:
                    best_path = path
                    best_steps = len(path)
                    self.best_path_history.append(best_steps)
                    print(f"New best path found at episode {ep}: length {best_steps}")

                # Visualize every 50 episodes (showing CURRENT path)
                if ep % 50 == 0:
                    self.visualize_path(path, polluted_cells_set)
                    asyncio.sleep(0.4)

            # After all episodes, show FINAL BEST PATH
            if best_path:
                print("\n=== TRAINING COMPLETE ===")
                print(f"Optimal path length: {len(best_path)} steps")
                print(f"Path directions: {best_path}")
                
                # Visualize final path with different style
                self.visualize_path(best_path, polluted_cells_set)
                asyncio.sleep(2)  # Longer pause for final path
                
                # Verify coverage
                covered = set()
                x, y = self.start_pos
                for direction in best_path:
                    if direction == "left": x -= 1
                    elif direction == "right": x += 1
                    elif direction == "up": y += 1
                    elif direction == "down": y -= 1
                    if (x,y) in polluted_cells_set:
                        covered.add((x,y))
                
                print(f"Covered {len(covered)}/{len(polluted_cells_set)} polluted cells")
                if covered != polluted_cells_set:
                    print("WARNING: Path doesn't cover all cells!")
                    print(f"Missing cells: {polluted_cells_set - covered}")

            return best_path if best_path else []

        async def run(self):
            msg = await self.receive(timeout=10)
            if msg:
                print("\n" + "="*50)
                print("Observer received new pollution report:")
                print(f"From: {msg.sender}")
                print(f"Body: {msg.body}")
                print("="*50 + "\n")

                polluted_cells = [tuple(map(int, coord.split(","))) for coord in msg.body.split(";")]
                Environment.display_grid()

                directions = self.find_optimal_directions(polluted_cells)

                if directions:
                    path_str = ",".join(directions)
                    cleaner_msg = Message(
                        to="cleaner99@jabber.sk",
                        body=path_str,
                        metadata={
                            "performative": "request",
                            "ontology": "cleaning-path",
                            "action": "execute-cleaning",
                            "message_type": "chat"
                        }
                    )
                    await self.send(cleaner_msg)
                    
                    #? debugging message
                    cleaner_msg = Message(
                        to="bot99@jabber.sk",
                        body=path_str,
                        metadata={
                            "performative": "request",
                            "ontology": "cleaning-path",
                            "action": "execute-cleaning",
                            "message_type": "chat"
                        }
                    )
                    await self.send(cleaner_msg)

                    print(f"\nSent optimal path to CleanerAgent (length: {len(directions)})")
                    print(f"Path: {path_str}")
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
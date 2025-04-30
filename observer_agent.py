import random
import time
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

        def get_possible_actions(self, position):
            x, y = position
            actions = []
            if x > 0: actions.append((x-1, y))
            if x < Environment.SIZE-1: actions.append((x+1, y))
            if y > 0: actions.append((x, y-1))
            if y < Environment.SIZE-1: actions.append((x, y+1))
            return actions

        def visualize_path(self, directions, polluted_cells):
            x, y = self.start_pos
            grid = np.zeros_like(Environment.grid)

            for px, py in polluted_cells:
                grid[px, py] = 1  # green for polluted

            for direction in directions:
                if direction == "left": x -= 1
                elif direction == "right": x += 1
                elif direction == "up": y += 1
                elif direction == "down": y -= 1
                if 0 <= x < Environment.SIZE and 0 <= y < Environment.SIZE:
                    grid[x, y] = 2  # blue for current path

            Environment.learning_grid = grid
            Environment.update_plot()

        def find_optimal_directions(self, polluted_cells):
            if not polluted_cells:
                return []

            self.q_table = {}
            episodes = 100
            polluted_cells_set = set(polluted_cells)
            best_path = None
            best_steps = float('inf')

            total_visual_time = 10  # seconds
            delay = total_visual_time / episodes

            for ep in range(episodes):
                current_pos = self.start_pos
                remaining_cells = polluted_cells_set.copy()
                path = []

                while remaining_cells:
                    state = (current_pos, frozenset(remaining_cells))
                    actions = self.get_possible_actions(current_pos)
                    if not actions:
                        break

                    if random.random() < self.epsilon:
                        action = random.choice(actions)
                    else:
                        action = max(actions, key=lambda a: self.q_table.get((state, a), 0))

                    next_pos = action
                    reward = 100 if next_pos in remaining_cells else -1
                    if next_pos in remaining_cells:
                        remaining_cells.remove(next_pos)

                    next_state = (next_pos, frozenset(remaining_cells))
                    max_q = max([self.q_table.get((next_state, a), 0) for a in self.get_possible_actions(next_pos)], default=0)
                    curr_q = self.q_table.get((state, action), 0)
                    self.q_table[(state, action)] = curr_q + self.learning_rate * (reward + self.discount_factor * max_q - curr_q)

                    dx = next_pos[0] - current_pos[0]
                    dy = next_pos[1] - current_pos[1]
                    if dx == 1: path.append("right")
                    elif dx == -1: path.append("left")
                    elif dy == 1: path.append("up")
                    else: path.append("down")
                    current_pos = next_pos

                self.visualize_path(path, polluted_cells_set)
                time.sleep(delay)

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

                polluted_cells = [tuple(map(int, coord.split(","))) for coord in msg.body.split(";")]
                Environment.display_grid()

                directions = self.find_optimal_directions(polluted_cells)

                if directions:
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

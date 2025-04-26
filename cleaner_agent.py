import asyncio
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.template import Template
from environment import Environment

class CleanerAgent(Agent):
    class CleaningBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=10)
            if msg and msg.metadata.get("ontology") == "cleaning-path":
                print("\n" + "="*50)
                print(f"CleanerAgent received cleaning path from {msg.sender}:")
                print(msg.body)
                print("="*50 + "\n")
                
                # Parse directions
                directions = msg.body.split(",")
                current_pos = (0, 0)  # Starting position
                
                print("Beginning cleaning process...")
                for i, direction in enumerate(directions, 1):
                    # Move cleaner
                    x, y = current_pos
                    if direction == "left": x -= 1
                    elif direction == "right": x += 1
                    elif direction == "up": y += 1
                    elif direction == "down": y -= 1
                    current_pos = (x, y)
                    
                    # Clean if cell is polluted
                    if Environment.grid[x][y] == 1:
                        Environment.grid[x][y] = 0
                        print(f"Step {i}: Cleaned ({x}, {y})")
                    else:
                        print(f"Step {i}: Moved to ({x}, {y}) [already clean]")
                    
                    # Display updated environment
                    Environment.display_grid()
                    await asyncio.sleep(1)  # Pause between steps
                
                print("Cleaning completed !!")

    async def setup(self):
        print("CleanerAgent initialized and ready")
        template = Template()
        template.metadata = {
            "ontology": "cleaning-path"
        }
        self.add_behaviour(self.CleaningBehaviour(), template)
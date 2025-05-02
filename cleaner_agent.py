import asyncio
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.template import Template
from environment import Environment
from spade.message import Message

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

                    # Save original value and mark cleaner position
                    prev_value = Environment.grid[x][y]
                    Environment.grid[x][y] = 2  # Mark cleaner location
                    Environment.display_grid()
                    await asyncio.sleep(0.4)

                    # Clean if cell is polluted
                    if prev_value == 1:
                        print(f"Step {i}: Cleaned ({x}, {y})")
                        Environment.grid[x][y] = 0
                    else:
                        print(f"Step {i}: Moved to ({x}, {y}) [already clean]")
                        Environment.grid[x][y] = 0 if prev_value == 0 else prev_value

                    Environment.display_grid()
                    await asyncio.sleep(0.4)

                print("Cleaning completed !!")

                               
                polluter_msg = Message(
                    to="polluter99@jabber.sk",
                    body="Cleaning completed !!",
                    metadata={
                        "performative": "request",
                        "ontology": "pollution-request",
                        "action": "pollute-now",
                        "message_type": "chat"
                    }
                )
                await self.send(polluter_msg)
                
                #? debugging message :
                polluter_msg = Message(
                    to="bot99@jabber.sk",
                    body="Cleaning completed !!",
                    metadata={
                        "performative": "request",
                        "ontology": "pollution-request",
                        "action": "pollute-now",
                        "message_type": "chat"
                    }
                )
                await self.send(polluter_msg)
        


    async def setup(self):
        print("CleanerAgent started")
        template = Template()
        template.metadata = {
            "ontology": "cleaning-path"
        }
        self.add_behaviour(self.CleaningBehaviour())

import random
import asyncio
from spade.agent import Agent
from spade.behaviour import PeriodicBehaviour
from spade.message import Message
from environment import Environment  # Import at module level

class PolluterAgent(Agent):
    SIZE = Environment.SIZE  # Get size from Environment
    
    class PolluteBehaviour(PeriodicBehaviour):
        async def run(self):
            polluted_cells = []

            print("\n" + "="*50)
            print("Polluter - Polluting the environment...")

            # Pollute 10 random unique cells
            while len(polluted_cells) < 10:
                x, y = random.randint(0, Environment.SIZE - 1), random.randint(0, Environment.SIZE - 1)
                if (x, y) not in polluted_cells and Environment.grid[x][y] == 0:
                    Environment.grid[x][y] = 1
                    polluted_cells.append((x, y))

            # Convert coordinates to string format "x1,y1;x2,y2;..."
            polluted_str = ";".join([f"{x},{y}" for x, y in polluted_cells])
            
            # Notify Observer agent
            observer_msg = Message(
                to="observator1234@xmpp.jp",
                body=polluted_str,
                metadata={
                    "performative": "inform",
                    "ontology": "pollution-report",
                    "action": "new-pollution"
                }
            )
            await self.send(observer_msg)
            print(f"Polluter - Notified Observer about the pollution of the {len(polluted_cells)} follwing cells : {polluted_str}")
            print("="*50 + "\n")

    async def setup(self):
        print("PolluterAgent started")
        # Add polluting behavior (every 5 seconds)
        self.add_behaviour(self.PolluteBehaviour(period=60.0))
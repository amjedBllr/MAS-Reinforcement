from environment import Environment
from polluter_agent import PolluterAgent
from observer_agent import ObserverAgent
from cleaner_agent import CleanerAgent 
from spade import run
import asyncio

async def main():
    # Initialize environment
    print("\nInitializing environment :")

    Environment.initialize_plot()
    Environment.display_grid()
    
    # Start agents
    polluter = PolluterAgent("polluter1234@xmpp.jp", "password")
    observer = ObserverAgent("observator1234@xmpp.jp", "password")
    cleaner = CleanerAgent("cleaner1234@xmpp.jp", "password")

    await cleaner.start()
    await observer.start()
    await polluter.start()

    # Keep running
    while True:
        await asyncio.sleep(1)

if __name__ == "__main__":
    try:
        run(main())
    except KeyboardInterrupt:
        print("Shutting down...")
from environment import Environment
from polluter_agent import PolluterAgent
from observer_agent import ObserverAgent
from cleaner_agent import CleanerAgent 
import asyncio

async def main():
    print("\nInitializing environment :")

    Environment.initialize_plot()
    Environment.display_grid()

    observer = ObserverAgent("observer99@jabber.sk", "password")
    await observer.start()

    cleaner = CleanerAgent("cleaner99@jabber.sk","password")
    await cleaner.start()

    polluter = PolluterAgent("polluter99@jabber.sk", "password")
    await polluter.start()

    
    # Keep running
    while True:
        await asyncio.sleep(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Shutting down...")
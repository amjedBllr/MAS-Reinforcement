import numpy as np
import asyncio
from spade import run
from spade.container import Container
import matplotlib.pyplot as plt

class Environment:
    SIZE = 10
    grid = np.zeros((SIZE, SIZE), dtype=int)

    fig = None
    ax = None
    img = None

    @classmethod
    def initialize_plot(cls):
        plt.ion() 
        cls.fig, cls.ax = plt.subplots()
        cls.img = cls.ax.imshow(cls.grid, cmap="Blues", vmin=0, vmax=1)
        cls.ax.set_title("Environment Grid")
        plt.show(block=False) 

    @classmethod
    def update_plot(cls):
        if cls.img is not None:
            cls.img.set_data(cls.grid)
            cls.fig.canvas.draw_idle()
            cls.fig.canvas.flush_events()

    @classmethod
    def display_grid(cls):
        print("\n" + "="*50)
        print("Current Environment Grid:")
        for row in cls.grid:
            print(" ".join(str(cell) for cell in row))
        print("="*50 + "\n")
        cls.update_plot()

async def main():
    
    container = Container()
    await container.start()

    while True:
        await asyncio.sleep(1)

if __name__ == "__main__":
    try:
        run(main())
    except KeyboardInterrupt:
        print("Environment shutting down...")

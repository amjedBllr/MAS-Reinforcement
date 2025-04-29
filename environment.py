import numpy as np
import asyncio
from spade import run
from spade.container import Container
import matplotlib.pyplot as plt
from matplotlib import colors

class Environment:
    SIZE = 10
    grid = np.zeros((SIZE, SIZE), dtype=int)

    fig = None
    ax = None
    img = None
    text_labels = []

    @classmethod
    def initialize_plot(cls):
        plt.ion()
        cls.fig, cls.ax = plt.subplots()

        # Improved colormap
        cmap = colors.ListedColormap(["#e0e0e0", "#4CAF50", "#2196F3"])
        bounds = [-0.5, 0.5, 1.5, 2.5]
        norm = colors.BoundaryNorm(bounds, cmap.N)

        cls.img = cls.ax.imshow(cls.grid, cmap=cmap, norm=norm)

        cls.ax.set_title("Environment Grid", fontsize=14, fontweight='bold')

        # Add axis ticks and labels
        cls.ax.set_xticks(np.arange(cls.SIZE))
        cls.ax.set_yticks(np.arange(cls.SIZE))
        cls.ax.set_xticklabels([str(i) for i in range(cls.SIZE)])
        cls.ax.set_yticklabels([str(i) for i in range(cls.SIZE)])

        cls.ax.tick_params(top=True, bottom=False,
                           labeltop=True, labelbottom=False)

        # Minor gridlines
        cls.ax.set_xticks(np.arange(-.5, cls.SIZE, 1), minor=True)
        cls.ax.set_yticks(np.arange(-.5, cls.SIZE, 1), minor=True)
        cls.ax.grid(which="minor", color="black", linestyle='-', linewidth=0.5)

        cls.ax.set_aspect('equal')
        plt.tight_layout()
        plt.show(block=False)

    @classmethod
    def update_plot(cls):
        if cls.img is not None:
            cls.img.set_data(cls.grid)

            # Clear previous text labels
            for text in cls.text_labels:
                text.remove()
            cls.text_labels.clear()

            # Add text labels to each cell
            for i in range(cls.SIZE):
                for j in range(cls.SIZE):
                    value = cls.grid[i, j]
                    text_color = 'black' if value != 2 else 'white'
                    label = cls.ax.text(j, i, str(value),
                                        ha='center', va='center',
                                        fontsize=10, weight='bold',
                                        color=text_color)
                    cls.text_labels.append(label)

            cls.fig.canvas.draw_idle()
            cls.fig.canvas.flush_events()

    @classmethod
    def display_grid(cls):
        print("\n" + "=" * 50)
        print("Current Environment Grid:")
        for row in cls.grid:
            print(" ".join(str(cell) for cell in row))
        print("=" * 50 + "\n")
        cls.update_plot()

async def main():
    Environment.initialize_plot()
    
    container = Container()
    await container.start()

    # Simulate some activity on the grid
    for i in range(10):
        await asyncio.sleep(1)
        x, y = np.random.randint(0, Environment.SIZE, size=2)
        Environment.grid[x, y] = 1 if Environment.grid[x, y] == 0 else 0
        Environment.display_grid()

if __name__ == "__main__":
    try:
        run(main())
    except KeyboardInterrupt:
        print("Environment shutting down...")

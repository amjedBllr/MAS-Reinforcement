import numpy as np
import asyncio
from spade import run
from spade.container import Container
import matplotlib.pyplot as plt
from matplotlib import colors

class Environment:
    SIZE = 10
    grid = np.zeros((SIZE, SIZE), dtype=int)
    learning_grid = np.zeros((SIZE, SIZE), dtype=int)

    fig = None
    axes = None
    imgs = [None, None]
    text_labels = [[], []]  # Separate label sets for each subplot

    @classmethod
    def initialize_plot(cls):
        plt.ion()
        plt.rcParams['font.family'] = 'Montserrat'

        cls.fig, cls.axes = plt.subplots(1, 2, figsize=(10, 5))

        cmap = colors.ListedColormap(["#f7ede2", "#e6ccb2", "#99d98c"])
        bounds = [-0.5, 0.5, 1.5, 2.5]
        norm = colors.BoundaryNorm(bounds, cmap.N)

        cls.imgs[0] = cls.axes[0].imshow(cls.grid, cmap=cmap, norm=norm)
        cls.imgs[1] = cls.axes[1].imshow(cls.learning_grid, cmap=cmap, norm=norm)

        for ax in cls.axes:
            ax.set_xticks(np.arange(cls.SIZE))
            ax.set_yticks(np.arange(cls.SIZE))
            ax.set_xticklabels([str(i) for i in range(cls.SIZE)])
            ax.set_yticklabels([str(i) for i in range(cls.SIZE)])
            ax.tick_params(top=True, bottom=False, labeltop=True, labelbottom=False)
            ax.set_xticks(np.arange(-.5, cls.SIZE, 1), minor=True)
            ax.set_yticks(np.arange(-.5, cls.SIZE, 1), minor=True)
            ax.grid(which="minor", color="black", linestyle='-', linewidth=0.5)
            ax.set_aspect('equal')

        # Move titles below the plots manually
        cls.axes[0].set_title("Static Environment", fontsize=11, weight='semibold', y=-0.12)
        cls.axes[1].set_title("Learning Progress", fontsize=11, weight='semibold', y=-0.12)

        plt.tight_layout()
        plt.show(block=False)


    @classmethod
    def update_plot(cls):
        # Update both plots (left: static, right: dynamic learning)
        for i, data in enumerate([cls.grid, cls.learning_grid]):
            if cls.imgs[i] is not None:
                cls.imgs[i].set_data(data)

                # Clear previous text
                for label in cls.text_labels[i]:
                    label.remove()
                cls.text_labels[i].clear()

                # Add text to cells
                for r in range(cls.SIZE):
                    for c in range(cls.SIZE):
                        value = data[r, c]
                        if value == 0:
                            text_color = '#555'
                        elif value == 1:
                            text_color = 'white'
                        else:
                            text_color = 'black'

                        label = cls.axes[i].text(
                            c, r, str(value),
                            ha='center', va='center',
                            fontsize=9,
                            weight='normal',  # <- no bold
                            color=text_color
                        )
                        cls.text_labels[i].append(label)

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

# Optional grid update simulation for testing
async def main():
    Environment.initialize_plot()
    container = Container()
    await container.start()

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

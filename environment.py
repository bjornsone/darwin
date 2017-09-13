import logging
import matplotlib.pyplot as plt
import numpy as np
import plant


class Environment(object):
    """
    Tracks each location in a 2D environment and defines the parameters of the environment.
    """

    given_energy_per_cycle = 40
    taken_energy_per_cycle = 20
    energy_per_cell = 8
    energy_per_seed = 50
    energy_in_new_plant = 40
    seed_spread = 20
    cell_life_span = 100
    include_diagonal_neighbors = True

    def __init__(self, width, height):
        self.plant_manager = plant.PlantManager(self)
        self.width = width
        self.height = height
        self.time = 0
        self.cells = [[None] * height for y in range(width)]

    def __str__(self):
        return "Environment %d by %d with %d plants" % (self.width, self.height, self.plant_manager.living_count())

    def valid_coords(self, x, y):
        """ Returns whether or not the coordinates are valid within the the bounds of the rectangular environment. """

        return x >= 0 and y >= 0 and x < self.width and y < self.height

    def is_space_available(self, x, y):
        """ Returns whether or not the coordinates are a valid location to grow a new cell. """

        if not self.valid_coords(x, y):
            return False
        return self.cells[x][y] is None

    def complete_death(self):
        """Returns boolean of whether all plants in the environment are dead. """

        return self.plant_manager.living_count() == 0

    def step_time(self):
        """ Takes all actions which are part of taking one step in time

        A step in time gives energy, takes energy, grows new cells, kills old cells, and kills plants with no remaining
        cells.

        :return: None
        """

        if self.time % 500 == 0:
            logging.info("Cycle %d living count: %d" % (self.time, self.plant_manager.living_count()))
        self._give_energy()
        self._take_energy()
        self._enforce_life_span()
        self.plant_manager.grow_all_plants()
        self._kill_disconnected_cells()
        self.plant_manager.prune_plants()
        self.time += 1

    def _give_energy(self):
        """ Gives energy to the topmost cell in each column. """

        for x in range(self.width):
            for y in reversed(range(self.height)):
                cell = self.cells[x][y]
                if cell is not None:
                    cell.plant.increment_energy(Environment.given_energy_per_cycle)
                    break

    def _take_energy(self):
        """ Takes energy from each plant for each cell that the plan has which is alive. """

        for x in range(self.width):
            for y in reversed(range(self.height)):
                cell = self.cells[x][y]
                if cell is not None:
                    cell.plant.increment_energy(-Environment.taken_energy_per_cycle)

    def _enforce_life_span(self):
        """ Kills all cells that have exceeded the lifespan as defined by cell_life_span"""

        for x in range(self.width):
            for y in reversed(range(self.height)):
                cell = self.cells[x][y]
                if cell is not None:
                    if self.time - cell.creation_time > Environment.cell_life_span:
                        cell.set_living(False)

    def _kill_disconnected_cells(self):
        """
        Uses a depth first search to determine which cells are not connected to the ground (y=0), and then kills any cells
        that are not connected.  A neighbor is defined as any of the four cells that are left, right, above, or below.
        """

        if Environment.include_diagonal_neighbors:
            neighbor_list = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]  # 8 neighbors
        else:
            neighbor_list = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        pending_exploration = []
        # Mark all cells on ground level as connected and add them to pending queue
        for x in range(self.width):
            cell = self.cells[x][0]
            if cell is not None:
                pending_exploration.append((x, 0))
                cell.connected_time = self.time
        # Keep exploring neighbors until the queue is empty
        while pending_exploration:
            x, y = pending_exploration.pop()
            cell = self.cells[x][y]
            for dx, dy in neighbor_list:
                neighbor_x = x + dx
                neighbor_y = y + dy
                if not self.valid_coords(neighbor_x, neighbor_y):
                    continue
                neighbor_cell = self.cells[neighbor_x][neighbor_y]
                if neighbor_cell is None:
                    continue
                if neighbor_cell.plant is cell.plant and neighbor_cell.connected_time is not self.time:
                    neighbor_cell.connected_time = self.time
                    pending_exploration.append((neighbor_x, neighbor_y))
        # Kill any cells that were not marked with the most recent time
        for x in range(self.width):
            for y in range(self.height):
                cell = self.cells[x][y]
                if cell is None:
                    continue
                if cell.connected_time is not self.time:
                    logging.debug("Killing disconnected Cell (%d, %d) time: %d" % (x, y, cell.creation_time))
                    cell.set_living(False)

    def connected(self, x, y, plant):
        """ returns boolean indicating whether the specified location in the environment is adjacent (i.e. connected) to
        the specified plant.
        """

        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            neighbor_x = x + dx
            neighbor_y = y + dy
            if not self.valid_coords(neighbor_x, neighbor_y):
                continue
            neighbor_cell = self.cells[neighbor_x][neighbor_y]
            if neighbor_cell is None:
                continue
            if neighbor_cell.plant is plant:
                return True
        return False

    def draw_pyplot(self):
        """ Displays a pyplot of the current state of the environment.  Each plan is given a semi-random color when it is
        created."""

        env_rgb = np.zeros((self.width, self.height, 3), dtype=np.uint8)
        for x in range(self.width):
            for y in range(self.height):
                cell = self.cells[x][self.height - 1 - y]
                if cell is not None:
                    logging.debug("Adding colored cell")
                    env_rgb[x, y, 0] = cell.plant.r
                    env_rgb[x, y, 1] = cell.plant.g
                    env_rgb[x, y, 2] = cell.plant.b

        plt.imshow(env_rgb.transpose((1, 0, 2)))
        plt.show()

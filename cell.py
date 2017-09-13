import logging


class CellState(object):
    """ Enumeration of the three possible states for a cell. """
    PENDING, ALIVE, DEAD = range(3)


class Cell(object):
    """ A single cell that may be in any CellState and is a component of one plant
    Each cell has a location relative to the root cell of a plant.  A cell can either be a normal cell or a seed cell.
    """

    def __init__(self, plant, dx, dy, seed=False):
        self.plant = plant
        self.dx = dx
        self.dy = dy
        self.seed = seed
        self._state = CellState.PENDING
        self.connected_time = -1  # latest time it was verified as being connected
        self.birth_time = plant.env.time
        return

    def state(self):
        """ Returns a CellState indicating whether the cell is PENDING, ALIVE, or DEAD.  """
        return self._state

    def age(self):
        """ Returns the current age of the cell relative to when this cell came to life. """
        return self.plant.env.time - self.birth_time

    def is_space_available(self):
        """ Returns boolean indicate whether the space where this cell would grow is unoccupied. """
        x = self.plant.root_x + self.dx
        y = self.plant.root_y + self.dy
        env = self.plant.env
        return env.is_space_available(x, y)

    def set_living(self, alive):
        """ Changes this cell's state to the be alive or dead.

        Function ignores the request if the requested state matches the current state.
        Updates the environment by adding/removing the cell that grew/died.
        """

        env = self.plant.env
        if alive:
            if self._state is CellState.ALIVE:
                return
            if self._state is CellState.DEAD:
                raise Exception("Cannot make a dead cell living")
            self.creation_time = env.time
            if self.seed:
                self._state = CellState.DEAD
                logging.debug("Seed cell is now dead root: (%d, %d) delta: (%d, %d)" %
                              (self.plant.root_x, self.plant.root_y, self.dx, self.dy))
            else:
                self._state = CellState.ALIVE
                env.cells[self.plant.root_x + self.dx][self.plant.root_y + self.dy] = self
                self.plant.living_cell_count += 1
                logging.debug("Cell is now alive. root: (%d, %d) delta: (%d, %d) plant age: %d" %
                              (self.plant.root_x, self.plant.root_y, self.dx, self.dy, self.plant.age()))
        else:
            if self._state is CellState.DEAD:
                return
            if self._state is CellState.PENDING:
                raise Exception("Cannot kill a pending cell")
            self._state = CellState.DEAD
            env.cells[self.plant.root_x + self.dx][self.plant.root_y + self.dy] = None
            self.plant.living_cell_count -= 1
            logging.debug("Cell is now dead. root: (%d, %d) delta: (%d, %d) cell age: %d  plant age: %d" %
                          (self.plant.root_x, self.plant.root_y, self.dx, self.dy, self.age(), self.plant.age()))

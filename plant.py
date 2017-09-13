import random
import logging
import environment as e
import cell as c


class PlantManager(object):
    """ Class that keeps track of all living plants.

    Class tracks all living plants and statistics regarding the current state of the plants.
    """

    def __init__(self, environment):
        self.env = environment
        self.birth_count = 0
        self.death_count = 0
        self.plants = []
        self._new_plants = []
        self._dead_plants = []

    def grow_all_plants(self):
        """ Performs growth ofor each living plant that is able to grow.

        :return: None
        """
        for plant in self.env.plant_manager.plants:
            plant.grow()
        self.plants.extend(self._new_plants)
        del self._new_plants[:]

    def add_new_plant(self, new_plant):
        """ Adds the specified plan so that it is properly tracked. """
        self._new_plants.append(new_plant)

    def prune_plants(self):
        """ Fully removes any plant that has no living cells. """

        for plant in self.plants:
            if plant.living_cell_count == 0:
                logging.debug("Killing plant with no living cells")
                plant.set_living(False)
                self._dead_plants.append(plant)
        self.plants = [p for p in self.plants if p not in self._dead_plants]
        del self._dead_plants[:]

    def living_count(self):
        """ Returns number of plants that are currently alive. """
        return self.birth_count - self.death_count

    def basic_plant(self, environment, energy, root_x, width=1, height=1):
        """ Creates a simple plant as the starting point of all other plants.

        energy: the initial amount of energy
        root_x: the position in the environment where its root cell grows
        width: the size that the top of the plant grows to the right and left
        height: the height that the plant grows vertically before growing horizontally.
        """

        root_y = 0
        new_plant = Plant(environment, root_x, root_y)
        new_plant.append_cells_up(0, 0, height + 1)
        new_plant.append_cells_wide(0, height, width)
        new_plant.append_cells_wide(0, height + 1, width, seed=True)
        new_plant.set_living(True)
        return new_plant


class Plant(object):
    """ A plant that contains a list of cells, an amount of energy, and a color (for drawing).

    This class manages the state of the plant and how the plant grows.
    """

    def __init__(self, environment, root_x, root_y):
        self.env = environment
        self.energy = environment.energy_in_new_plant
        self._alive = False
        self.creation_time = environment.time

        self.root_x = root_x
        self.root_y = root_y

        index = id(self)
        self.r = ((index * 5) % 7) * (255 // 6)
        self.g = ((index * 5) % 11) * (255 // 10)
        self.b = 255 - (self.r + self.g) // 2

        self.living_cell_count = 0
        self.cells = []
        self.env.plant_manager.add_new_plant(self)
        logging.debug("Created Plant id=%d  color=(%d, %d, %d)" % (id(self), self.r, self.g, self.b))

    def increment_energy(self, energy_delta):
        self.energy += energy_delta
        if self.energy < 0:
            logging.debug("Killing whole plant due to low energy")
            self.set_living(False)
        return

    def is_alive(self):
        """ Returns boolean on whether the plant is currently alive. """
        return self._alive

    def age(self):
        """ Returns integer of the current age of the plant. """
        return self.env.time - self.creation_time

    def set_living(self, alive):
        """ Updates the state of the plant to the specified state. """

        if self._alive == alive:
            return

        self._alive = alive
        if alive:
            # life of plant starts with one living cell
            self.cells[0].set_living(True)
            self.env.plant_manager.birth_count += 1
            logging.debug("Plant is now alive")
        else:
            # death of plan kills all cells
            for cell in self.cells:
                logging.debug("Killing whole plant")
                if cell.state() is c.CellState.ALIVE:
                    cell.set_living(False)
            self.env.plant_manager.death_count += 1
            logging.debug("Plant is now dead")

    def grow(self):
        """ Grows any cells within the plant for which the plant has sufficient energy and whose locations are not
        already occupied.
        """

        if self.energy < e.Environment.energy_per_cell:
            return
        for cell in self.cells:
            if cell.state() is c.CellState.PENDING and cell.is_space_available() and \
                    self.env.connected(self.root_x + cell.dx, self.root_y + cell.dy, self):
                if cell.seed:
                    if self.energy >= e.Environment.energy_per_seed:
                        cell.set_living(True)
                        self.energy -= e.Environment.energy_per_seed
                        self._reproduce(cell.dx)
                        break
                else:
                    if self.energy >= e.Environment.energy_per_cell:
                        cell.set_living(True)
                        self.energy -= e.Environment.energy_per_cell
                        break

    def _reproduce(self, dx):
        """ Creates a copy of this plant with possible mutations.

        dx: the location where the copy of the plant will attempt to start growing.
        """

        # TODO: Move constants to a general area for configuration parameters
        mutation_probability = .1
        mutation_addition_probability = .5
        mutation_max_cell_additions = 5
        mutation_max_cell_removals = 5

        x = self.root_x + dx + random.randint(-e.Environment.seed_spread, e.Environment.seed_spread)
        y = self.root_y
        if not self.env.is_space_available(x, y):
            return
        baby = Plant(self.env, x, y)
        for cell in self.cells:
            baby.append_cell(cell.dx, cell.dy, cell.seed)
        baby.set_living(True)

        mutate = random.random() < mutation_probability
        if mutate:
            do_addition = random.random() < mutation_addition_probability
            if do_addition:
                add_count = random.randint(1, mutation_max_cell_additions)
                for _ in range(add_count):
                    self._mutate_add()
            else:
                remove_count = random.randint(1, mutation_max_cell_removals)
                for _ in range(remove_count):
                    self._mutate_remove()
        logging.debug("Created baby Plant")

    def _mutate_remove(self):
        """ Mutates the current list of cells by removing a random subset of the cells. """

        # if there is only one cell left, we can't remove any more
        if len(self.cells) <= 1:
            return
        # removes a random cell other than the root cell
        removal_index = random.randint(1, len(self.cells) - 1)
        del self.cells[removal_index]

    def _mutate_add(self):
        """ Mutates the current list of cells by adding a random number of cells. """

        # TODO: Move constants to a general area for configuration parameters
        mutation_seed_probability = .1

        parent_index = random.randint(0, len(self.cells) - 1)
        dx = self.cells[parent_index].dx
        dy = self.cells[parent_index].dy
        delta = random.randint(0, 1) * 2 - 1  # Randomly selects direction of new cell to be +1 or -1
        if random.randint(0, 1) == 0:  # randomly selects direction of shift to be horizontal or vertical
            dx += delta
        else:
            dy += delta
        seed = random.random() < mutation_seed_probability
        self.cells.insert(parent_index + 1, c.Cell(self, dx, dy, seed))

    def append_cell(self, dx, dy, seed=False):
        """ Adds on another cell that is in a state of PENDING at the specified location. """

        self.cells.append(c.Cell(self, dx, dy, seed))

    def append_cells_up(self, dx, dy, count, seed=False):
        """ Adds multiple cells above the specified location.

        dx: x location to start adding cells
        dy: y location to start adding cells
        count: number of cells to add
        seed: type of cell to add (normal or seed)
        """

        for i in range(count):
            self.cells.append(c.Cell(self, dx, dy + i, seed))

    def append_cells_wide(self, dx, dy, count, seed=False):
        """ Adds multiple cells to either side of the specified location.

        dx: x location to start adding cells
        dy: y location to start adding cells
        count: number of cells to add to each side
        seed: type of cell to add (normal or seed)
        """

        for i in range(1, count + 1):
            self.cells.append(c.Cell(self, dx + i, dy, seed))
            self.cells.append(c.Cell(self, dx - i, dy, seed))

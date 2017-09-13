## Darwin Plant Growth Simulation
This is a learning exercise in Python in which plants can grow, mutate, and compete for surival in a two-dimensional environment.

![Example Plant Life](darwin2017-09-12_1.png)

* The environment is a 2D grid in which each discete location can be occupied by only one cell
* Each Plant has a list of cells that try to grow
* Each cell at the highest point in each column receives energy from light
* Each cell consumes energy to survive each cycle and requires additional energy to grow new cells
* Each Plant survives until the plant runs out of energy or all of its cells die due to a fixed life span
* A cell is also killed if there is no path within the same plant that connects it to the soil (y=0)
* Each new cell can either be a normal cell of the structure or a seed that prouduces a new plant
* When a new plant is created, there is a probability that it mutates which either randomly adds or removes from its list of cells that try to grow
* The environment starts with just a few identical plants

Have fun playing with parameters and seeing how it affects the simulated growth and evolution of the plants.

The only algorithmic part of this is program how disconnected cells are found. Such cells are found and pruned based on a depth-first search that starts with all cells that are connected to the soil.  After the depth-first search completes, any cell that is not marked as having been visited is then killed.

import environment
import logging


def main():
    """
    Runs example environment where plants grow, mutate, and compete for survival.

    :return: None
    """
    logging.basicConfig(level=logging.INFO)

    environment_width = 300
    environment_height = 20
    time_to_draw_initial_state = 100
    total_cycle_count = 10 * 1000
    initial_energy = 100
    initial_plant_count = 10

    # Create the one and only environment in which all plants will grow
    env = environment.Environment(environment_width, environment_height)

    # Create a few initial plants which are spread evenly in the environment
    for x in range(initial_plant_count):
        env.plant_manager.basic_plant(env, initial_energy, (x + 1) *
                                      environment_width // (initial_plant_count + 1), 2, 1)

    for cycle_time in range(total_cycle_count):
        env.step_time()
        if env.complete_death():
            print("Complete death of all plants! cycle_time: %d" % cycle_time)
            break
        # show an initial state
        if cycle_time == time_to_draw_initial_state:
            env.draw_pyplot()
    # draw the final state
    env.draw_pyplot()

if __name__ == '__main__':
    main()

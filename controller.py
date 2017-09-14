import environment
import logging
import argparse

def main():
    """
    Runs example environment where plants grow, mutate, and compete for survival.

    :return: None
    """
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser()

    parser.add_argument("-dx", "--width", dest="width", type=int, default="300", help="Width of environment")
    parser.add_argument("-dy", "--height", dest="height", type=int, default="20", help="Height of environment")
    parser.add_argument("-pc", "--plant_count", dest="plant_count", type=int, default="10",
                        help="Number of initial plants")
    parser.add_argument("-c", "--cycle_count", dest="cycle_count", type=int, default="10000",
                        help="Number of cycles to execute")
    parser.add_argument("-dt", "--display_time", dest="display_time", type=int, default="100",
                        help="Time at which to display the initial state")

    args = parser.parse_args()

    environment_width = args.width
    environment_height = args.height

    print("Environment: width: %d height: %d" % (environment_width, environment_height))
    initial_plant_count = args.plant_count

    # Create the one and only environment in which all plants will grow
    env = environment.Environment(environment_width, environment_height)

    # Create a few initial plants which are spread evenly in the environment
    for x in range(initial_plant_count):
        env.plant_manager.basic_plant(env, env.energy_in_new_plant, (x + 1) *
                                      environment_width // (initial_plant_count + 1), 2, 1)

    for cycle_time in range(args.cycle_count):
        env.step_time()
        if env.complete_death():
            print("Complete death of all plants! cycle_time: %d" % cycle_time)
            break
        # show an initial state
        if cycle_time == args.display_time:
            env.draw_pyplot()
    # draw the final state
    env.draw_pyplot()

if __name__ == '__main__':
    main()

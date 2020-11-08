"""usage: 
-h, -help                                 shows this help message
-s, -simulation out_file1 out_file2        runs algorithm and stores solutions with calculated fitness function in <out_file2> and best solution in <out_file2>
-v_s, -visualize_solution in_file          visualizes single solution instance red from <in_file>
-v_c, -visualize_chart in_file             visualizes fitness function charts red from <in_file>
"""
from visualization import *
from algorithm import *
import simulation
import random
import threading
import numpy as np
import matplotlib.pyplot as plt
from time import sleep
import json

mode = None
try:
    for index, arg in enumerate(sys.argv):
        if arg.startswith('-') and mode is not None:
            print("cannot use with multiple flags")
            print(__doc__)
            sys.exit()
        elif arg.startswith('-'):
            if arg == "-h":
                print(__doc__)
                sys.exit()
            elif arg == "-s":
                mode = ["-s", sys.argv[index+1], sys.argv[index+2]]
            elif arg == "-v_s":
                mode = ["-v_s", sys.argv[index+1]]
            elif arg == "-v_c":
                mode = ["-v_c", sys.argv[index+1]]
except:
    print(__doc__)
    sys.exit()
if mode is None:
    print(__doc__)
    sys.exit()


if mode[0] == "-s":
    algorithm = GeneticAlgorithm()
    print("calculating ...")
    populations = algorithm.compute_populations()
    print("done calculating.")
    try:
        with open(mode[1],'w') as file:
            x = [i for i in range(len(populations))]
            y = [sum([s.fitness_function for s in pop]) / len(pop) for pop in populations]
            for i in range(len(populations)):
                file.write(str(x[i]) + ' ' + str(y[i]) + '\n')
        print("population written to " + str(mode[1]))
        with open(mode[2],'w') as file:
            file.write(json.dumps((populations[-1][-1]).__dict__))
        print("best solution written to " + str(mode[2]))
    except Exception as e:
        print(e)
        print('something went wrong with saving to file ... exiting')
        sys.exit()
elif mode[0] == "-v_s":
    try:
        with open(mode[1]) as file:
            solution_as_dict = json.loads(file.read())
            solution = SolutionInstance(solution_as_dict['launch_time'], solution_as_dict['latitude'], solution_as_dict['launch_speed'])
        algorithm = GeneticAlgorithm()
        time_begin, time_end, planets ,rocket = algorithm.prepare_solution_to_visualize(solution, nr_of_frames = 8000)
        visualization = Visualization(time_begin, time_end, planets ,rocket, 4)
        visualization.show()
    except Exception as e:
        print("something went wrong with reading from file " + str(mode[1]) + " ... exiting")
        sys.exit()
elif mode[0] == "-v_c":
    try:
        x = []
        y = []
        with open(mode[1]) as file:
            for line in file:
                xx, yy = line.split(' ')
                x.append(int(xx))
                y.append(float(yy))
        print("done reading from file")
        width = 0.35       # the width of the bars
        fig, ax = plt.subplots()
        ax.set_ylabel('Fitness function')
        rect = ax.bar(x, y, width, color='r')
        for r in rect:
            height = r.get_height()
            ax.text(r.get_x() + r.get_width()/2., 1.05*height,'', ha='center', va='bottom')
        plt.show()
    except:
        print("something went wrong with reading from file " + str(mode[1]) + " ... exiting")
        sys.exit()
else:
    print("can not understand")
    print(__doc__)

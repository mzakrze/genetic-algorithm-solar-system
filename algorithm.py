import time as t
import math
import random
import copy
import json
import sys

current_time = 	int(round(t.time()))
current_time_str = t.strftime('%Y-%m-%d %H:%M:%S', t.localtime(current_time))

with open("constants.json") as file:
    constants = json.loads(file.read())



class Planet:
	def __init__(self, radius, period, mass, name, angle_at_epoch_begin):
		self.radius = float(radius * 1000) # in m
		self.period = float(period * 24 * 60 * 60) # in s
		self.mass = float(mass * 10e21) # in kg
		self.name = name
		self.angle_at_epoch_begin = float(angle_at_epoch_begin) # in radians, at 'right' from Sun its 0 radians, on 'top' is PI/2


	def location_at(self, time):
		if self.period == 0:
			return (0,0) # Sun
		time = time % self.period
		angle = 2 * math.pi * (time / self.period) + self.angle_at_epoch_begin
		x = self.radius * math.cos(angle)
		y = self.radius * math.sin(angle)
		return (x, y)


class ProblemInstance:
	def __init__(self, rocket_mass, dest_planet):
		self.rocket_mass = rocket_mass
		self.dest_planet = dest_planet


class SolutionInstance(json.JSONEncoder):
	def __init__(self, launch_time, latitude, launch_speed):
		self.launch_time = launch_time
		self.latitude = latitude
		self.launch_speed = launch_speed

	def __str__(self):
		return "launch_time:" + t.strftime('%Y-%m-%d %H:%M:%S', t.localtime(self.launch_time)) + \
			", landing_time:" + t.strftime('%Y-%m-%d %H:%M:%S', t.localtime(self.landing_time)) + \
			", latitude:" + str(self.latitude) + \
			", launch_speed:" + str(self.launch_speed) + \
			", fitness_fun:" + str(self.fitness_function) + \
			", closes_dist:" + str(self.closes_dist_to_destination)


class GeneticAlgorithm:
	def __init__(self):
		try:
			self.earth = [p for p in planets if p.name=="Earth"][0]
		except IndexError:
			print("Planet Earth not specified in constants.json. Exiting ...")
			sys.exit()
		self.problem_instance = ProblemInstance(constants['problem_instance']['rocket_mass'],constants['problem_instance']['target_planet'])
		self.destination = planets[constants['problem_instance']['target_planet']]
		self.population_size = constants['algorithm_properties']['population_size']
		self.population_subset_size = self.population_size / 2
		self.randomize_coord = 0.1
		self.latitude_range = (0.00001, 2 * math.pi)
		self.launch_speed_range = (12000, 20000) # m / s
		self.launch_time_range = (current_time, current_time + 20 * 365 * 24 * 60 * 60)
		self.gravitational_constant = 6.67408 * 10e-13 # m^3 / kgs^2
		# coordinates to calculate fitness function
		self.fuel_coord = constants['algorithm_properties']['fuel_coord']
		self.waiting_time_coord = constants['algorithm_properties']['waiting_time_coord']
		self.vicinity_coord = constants['algorithm_properties']['vicinity_coord']

	def compute_populations(self):
		nr_of_populations = constants['algorithm_properties']['populations']
		populations = []
		self.population = self.generate_random_population()
		start_time = int(round(t.time()))
		print("population #0")
		for solution in self.population:
			self.run_launch_simulation(solution)
		populations.append(self.population)
		for i in range(nr_of_populations - 1):
			average_time = ((int(round(t.time()))-start_time)*1.0)/(i+1)
			print(" ---------------------- population #" + str(i + 1)
				  + " ETC: " + str(average_time*(nr_of_populations-i)) + "s")
			self.perform_selection()
			self.perform_crossovers()
			for solution in self.population:
				self.adjust_launch_speed(solution)
			for solution in self.population:
				self.run_launch_simulation(solution)
			populations.append(copy.deepcopy(self.population))
		return populations

	def adjust_launch_speed(self, solution):
		while solution.launch_speed > self.launch_speed_range[1]:
			solution.launch_speed -= (self.launch_speed_range[1]-self.launch_speed_range[0]) * random.random()
		while solution.launch_speed < self.launch_speed_range[0]:
			solution.launch_speed += (self.launch_speed_range[1]-self.launch_speed_range[0]) * random.random()

	def perform_crossovers(self):
		new_population = []
		random.shuffle(self.population)
		for i in range(self.population_size):
			s = len(self.population) / 2 - 1
			first_mate = self.population[random.randint(0, s)]
			sec_mate = self.population[random.randint(0, s)]
			new_population.append(self.mutate_agent(self.perform_crossover(first_mate, sec_mate)))
		self.population = new_population

	def mutate_agent(self, agent_genome):
		agent_genome.launch_time *= (1 + self.randomize_coord * (random.random()-0.5))
		agent_genome.latitude *= (1 + self.randomize_coord * (random.random()-0.5))
		agent_genome.launch_speed *= (1 + self.randomize_coord * (random.random()-0.5))
		return agent_genome

	def perform_crossover(self, a, b):
		return SolutionInstance(\
			launch_time = (a.launch_time + b.launch_time) / 2.0, \
			latitude = (a.latitude + b.latitude) / 2.0, \
			launch_speed = (a.launch_speed + b.launch_speed) / 2.0)

	def perform_selection(self):
		self.population.sort(key=lambda x: int(x.fitness_function/10000))
		self.population = self.population[:self.population_subset_size]

	def run_launch_simulation(self, solution, nr_of_frames = None):
		planets_coords = [[] for p in planets]
		rocket_coords = []
		closes_dist_to_destination = None
		landing_time = None
		continue_cond = True
		time = solution.launch_time
		pos_x, pos_y = self.earth.location_at(time)
		speed_orbital = self.earth.radius / self.earth.period
		speed_rotation = (6371 * 1000) / (1 * 24 * 60 * 60)
		if pos_x >= 0:
			orbital_angle = math.atan(pos_y / pos_x)
		else:
			orbital_angle = math.atan(pos_y / pos_x) + 3.14
		rotation_angle = solution.latitude
		speed_x = 0
		speed_y = 0
		speed_x += 6.28 * -1.0 * speed_orbital * math.sin(orbital_angle)
		speed_y += 6.28 * speed_orbital * math.cos(orbital_angle)
		speed_x += 6.28 * (-1.0) * speed_rotation * math.sin(rotation_angle)
		speed_y += 6.28 * speed_rotation * math.cos(rotation_angle)
		speed_x += solution.launch_speed * -math.sin(rotation_angle - 3.14 / 2.0) 
		speed_y += solution.launch_speed * math.cos(rotation_angle - 3.14 / 2.0)
		iterations = 0
		time_diff = 60 * 60 * 24 # a day

		simulation_duration_in_years = 20
		init_distance = math.sqrt((self.earth.location_at(time)[0] - self.destination.location_at(time)[0])**2 + (self.earth.location_at(time)[1] - self.destination.location_at(time)[1])**2)
		while continue_cond:
			iterations += 1
			force_x = 0
			force_y = 0
			time += time_diff
			for index, planet in enumerate(planets):
				planet_x, planet_y = planet.location_at(time)
				if nr_of_frames is not None:
					planets_coords[index].append((planet_x, planet_y))
				distance = math.sqrt((planet_x - pos_x)**2 + (planet_y - pos_y)**2)
				if distance < 10000000: # for small distances a day precision isn't enough
					continue
				force = self.gravitational_constant * planet.mass  / (distance**2)
				diff_x = pos_x - planet_x
				diff_y = pos_y - planet_y
				planet_to_rocket_angle = math.atan(diff_y / diff_x)
				if diff_x < 0:
					force_x += force * math.cos(math.atan(diff_y / diff_x))
				else:
					force_x -= force * math.cos(math.atan(diff_y / diff_x))
				if diff_y < 0:
					force_y += force * math.cos(math.atan(diff_x / diff_y))
				else:
					force_y -= force * math.cos(math.atan(diff_x / diff_y))

			speed_x += force_x * time_diff
			speed_y += force_y * time_diff
			pos_x += speed_x * time_diff
			pos_y += speed_y * time_diff
			dest_planet_location = self.destination.location_at(time)
			distance_to_dest = math.sqrt((dest_planet_location[0] - pos_x)**2 + (dest_planet_location[1] - pos_y)**2)
			if init_distance > distance_to_dest and (closes_dist_to_destination is None or distance_to_dest < closes_dist_to_destination):
				closes_dist_to_destination = distance_to_dest
				landing_time = time
			if nr_of_frames is not None:
				rocket_coords.append((pos_x, pos_y))
			continue_cond = iterations <= (simulation_duration_in_years * 365 * 24 * 60 * 60) / time_diff

		if landing_time is None:
			solution.fitness_function = sys.maxint# rocket never was closer to target than when it launched
			return (None, None, None, None)
		solution.landing_time = landing_time
		solution.closes_dist_to_destination = closes_dist_to_destination
		solution.fitness_function = self.compute_fitness(solution)
		travel_duration_frames = int((solution.landing_time - solution.launch_time) / time_diff)
		rocket_coords = rocket_coords[:travel_duration_frames]
		planets_coords = [planet_coord[:travel_duration_frames] for planet_coord in planets_coords]
		if nr_of_frames is not None:
			return (solution.launch_time, solution.landing_time, planets_coords, rocket_coords)


	def compute_fitness(self, solution):
		return self.fuel_coord * self.problem_instance.rocket_mass * solution.launch_speed + \
			self.waiting_time_coord * (solution.launch_time - current_time/1000/60/60) + \
			self.vicinity_coord * solution.closes_dist_to_destination


	def generate_random_population(self):
		random_population = []
		for i in range(self.population_size):
			random_population.append(SolutionInstance(\
				launch_time = random.random() * (self.launch_time_range[1] - self.launch_time_range[0]) + self.launch_time_range[0], \
				latitude = random.random() * (self.latitude_range[1] - self.latitude_range[0]) + self.latitude_range[0],\
				launch_speed = (self.launch_speed_range[1] - self.launch_speed_range[0]) * random.random() + self.launch_speed_range[0]))
		return random_population


	def prepare_solution_to_visualize(self, solution, nr_of_frames):
		return self.run_launch_simulation(solution, nr_of_frames)

# TODO - change angle_at_epoch_begin to accurate(http://www.fourmilab.ch/cgi-bin/Solar)
# all planets revolve counter-clock wise(looking from above at Sun's north polar)
planets = [
	Planet(radius=planet['radius'], period=planet['period'], mass=planet['mass'],name=planet['name'], angle_at_epoch_begin=planet['angle_at_epoch_begin']) 
	for planet in constants['solar_system']]

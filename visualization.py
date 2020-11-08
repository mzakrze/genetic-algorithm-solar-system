from Tkinter import *
from algorithm import *
import sys
import threading


# TODO - generator of x,y of planets, and only rocket in memory
# TODO - change scale to logarythmic etc

class Visualization:
	def __init__(self, time_begin, time_end, planets, rocket, dest_planet_index):
		self.canvas_width = 800
		self.canvas_height = 600
		self.time_begin = time_begin
		self.time_end = time_end
		self.planets = planets
		self.rocket = rocket
		self.dest_planet_index = dest_planet_index

	def show(self):
		maxx = []
		for planet in self.planets:
			maxx.append((
				max(map(lambda item: abs(item[0]), planet)), 
				max(map(lambda item: abs(item[1]), planet))
				))
		
		max_x = max(map(lambda item: item[0], maxx))
		max_y = max(map(lambda item: item[1], maxx))

		self.planets = [[(
					(x_y[0] + max_x) / (2 * max_x) * self.canvas_height
					, (1.0 - ((x_y[1] + max_y) / (2 * max_y))) * self.canvas_height
				) for x_y in planet] for planet in self.planets]

		self.rocket = [((x_y[0] + max_x) / (2 * max_x) * self.canvas_height, (1.0 - ((x_y[1] + max_y) / (2 * max_y))) * self.canvas_height) for x_y in self.rocket]

		nr_of_frames = len(self.rocket)

		master = Tk()
		master.title("Solar system visualization")

		self.canvas = Canvas(master, width = self.canvas_width, height = self.canvas_height)
		self.canvas.pack(expand = YES)

		self.slidebar = Scale(master, from_ = 0, to = nr_of_frames - 1, orient = HORIZONTAL,command = self.on_slidebar_change)
		self.slidebar.pack(expand = YES, fill = BOTH)

		self.message = Label(master, text = "Drag to change time")
		self.message.pack(expand = YES, side = BOTTOM)
			
		mainloop()

	def on_slidebar_change(self, val):
		val = int(val)
		self.canvas.delete(ALL)
		for count, planet in enumerate(self.planets):
			if count == self.dest_planet_index:
				self.canvas.create_rectangle(planet[val][0],planet[val][1], planet[val][0] + 10, planet[val][1] + 10, fill = "yellow")
			else:
				self.canvas.create_rectangle(planet[val][0],planet[val][1], planet[val][0] + 10, planet[val][1] + 10, fill = "blue")
		self.canvas.create_rectangle(self.rocket[val][0],self.rocket[val][1], self.rocket[val][0] + 10, self.rocket[val][1] + 10, fill = "red")
		for i in range(val):
			self.canvas.create_rectangle(self.rocket[i][0],self.rocket[i][1], self.rocket[i][0] + 1, self.rocket[i][1] + 1, fill = "red")

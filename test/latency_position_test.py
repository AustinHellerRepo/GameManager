from __future__ import annotations
import unittest
import time
import matplotlib.pyplot as plt
import numpy as np
from typing import List, Tuple, Dict, Set, Callable, Type


class Dot():

	def __init__(self, position: Tuple[float, float], velocity: Tuple[float, float], acceleration: Tuple[float, float]):

		self.__position = position
		self.__velocity = velocity
		self.__acceleration = acceleration
		self.__time_index_offset = 0

		self.__acceleration_delta = None  # type: Tuple[float, float]
		self.__acceleration_delta_end_time_index = None  # type: float
		self.__acceleration_delta_end_time_index_acceleration = None  # type: Tuple[float, float]

	def set_positiion(self, *, position: Tuple[float, float]):
		self.__position = position

	def set_velocity(self, *, velocity: Tuple[float, float]):
		self.__velocity = velocity

	def set_acceleration(self, *, acceleration: Tuple[float, float]):
		self.__acceleration = acceleration

	def get_position(self, *, time_index: float) -> Tuple[float, float]:
		calculated_time_index = time_index + self.__time_index_offset
		position = list(self.__position)
		for dimension_index in range(len(position)):
			position[dimension_index] += self.__velocity[dimension_index] * calculated_time_index
			if self.__acceleration_delta_end_time_index is None:
				position[dimension_index] += (self.__acceleration[dimension_index] * calculated_time_index ** 2) / 2.0
			else:
				if calculated_time_index < self.__acceleration_delta_end_time_index:
					position[dimension_index] += (self.__acceleration[dimension_index] * calculated_time_index ** 2) / 2.0
					position[dimension_index] += (self.__acceleration_delta[dimension_index] * calculated_time_index ** 3) / 6.0
				else:
					position[dimension_index] += (self.__acceleration[dimension_index] * self.__acceleration_delta_end_time_index ** 2) / 2.0
					position[dimension_index] += (self.__acceleration_delta_end_time_index_acceleration[dimension_index] * (calculated_time_index - self.__acceleration_delta_end_time_index) ** 2) / 2.0
					position[dimension_index] += (self.__acceleration_delta[dimension_index] * self.__acceleration_delta_end_time_index ** 3) / 6.0
		return tuple(position)

	def get_velocity(self, *, time_index: float) -> Tuple[float, float]:
		calculated_time_index = time_index + self.__time_index_offset
		velocity = list(self.__velocity)
		for dimension_index in range(len(velocity)):
			if self.__acceleration_delta_end_time_index is None:
				velocity[dimension_index] += self.__acceleration[dimension_index] * calculated_time_index
			else:
				if calculated_time_index < self.__acceleration_delta_end_time_index:
					velocity[dimension_index] += self.__acceleration[dimension_index] * calculated_time_index
					velocity[dimension_index] += (self.__acceleration_delta[dimension_index] * calculated_time_index**2) / 2.0
				else:
					velocity[dimension_index] += self.__acceleration[dimension_index] * self.__acceleration_delta_end_time_index
					velocity[dimension_index] += self.__acceleration_delta_end_time_index_acceleration[dimension_index] * (calculated_time_index - self.__acceleration_delta_end_time_index)
					velocity[dimension_index] += (self.__acceleration_delta[dimension_index] * self.__acceleration_delta_end_time_index**2) / 2.0
		return tuple(velocity)

	def get_acceleration(self, *, time_index: float) -> Tuple[float, float]:
		calculated_time_index = time_index + self.__time_index_offset
		acceleration = [0] * len(self.__position)
		for dimension_index in range(len(acceleration)):
			if self.__acceleration_delta_end_time_index is None:
				acceleration[dimension_index] += self.__acceleration[dimension_index]
			else:
				if calculated_time_index < self.__acceleration_delta_end_time_index:
					acceleration[dimension_index] += self.__acceleration[dimension_index]
					acceleration[dimension_index] += (self.__acceleration_delta[dimension_index] * calculated_time_index)
				else:
					acceleration[dimension_index] += self.__acceleration_delta_end_time_index_acceleration[dimension_index]
					acceleration[dimension_index] += (self.__acceleration_delta[dimension_index] * self.__acceleration_delta_end_time_index)
		return tuple(self.__acceleration)

	def bounce(self, *, time_index: float):
		bounce_position = self.get_position(
			time_index=time_index
		)
		bounce_velocity = self.get_velocity(
			time_index=time_index
		)
		bounce_acceleration = self.get_acceleration(
			time_index=time_index
		)
		self.__position = bounce_position
		self.__velocity = (bounce_velocity[0], -bounce_velocity[1])
		self.__acceleration = bounce_acceleration
		calculated_time_index = time_index + self.__time_index_offset
		if self.__acceleration_delta_end_time_index is not None:
			self.__acceleration_delta_end_time_index -= calculated_time_index
			if self.__acceleration_delta_end_time_index <= 0:
				self.__acceleration_delta = None
				self.__acceleration_delta_end_time_index = None
				self.__acceleration_delta_end_time_index_acceleration = None
		self.__time_index_offset = -time_index

	def reflect(self, *, time_index: float):
		reflect_position = self.get_position(
			time_index=time_index
		)
		reflect_velocity = self.get_velocity(
			time_index=time_index
		)
		reflect_acceleration = self.get_acceleration(
			time_index=time_index
		)
		self.__position = reflect_position
		self.__velocity = (-reflect_velocity[0], reflect_velocity[1])
		self.__acceleration = reflect_acceleration
		calculated_time_index = time_index + self.__time_index_offset
		if self.__acceleration_delta_end_time_index is not None:
			self.__acceleration_delta_end_time_index -= calculated_time_index
			if self.__acceleration_delta_end_time_index <= 0:
				self.__acceleration_delta = None
				self.__acceleration_delta_end_time_index = None
				self.__acceleration_delta_end_time_index_acceleration = None
		self.__time_index_offset = -time_index

	def set_state(self, *, position: Tuple[float, float], velocity: Tuple[float, float], acceleration: Tuple[float, float], time_index: float):
		self.__position = position
		self.__velocity = velocity
		self.__acceleration = acceleration
		calculated_time_index = time_index + self.__time_index_offset
		if self.__acceleration_delta_end_time_index is not None:
			self.__acceleration_delta_end_time_index -= calculated_time_index
			if self.__acceleration_delta_end_time_index <= 0:
				self.__acceleration_delta = None
				self.__acceleration_delta_end_time_index = None
				self.__acceleration_delta_end_time_index_acceleration = None
		self.__time_index_offset = -time_index

	def set_acceleration_delta(self, *, time_index: float, acceleration_delta: Tuple[float, float], end_time_index: float):
		time_index_position = self.get_position(
			time_index=time_index
		)
		time_index_velocity = self.get_velocity(
			time_index=time_index
		)
		time_index_acceleration = self.get_acceleration(
			time_index=time_index
		)
		self.__position = time_index_position
		self.__velocity = time_index_velocity
		self.__acceleration = time_index_acceleration
		self.__time_index_offset = -time_index
		self.__acceleration_delta = acceleration_delta
		self.__acceleration_delta_end_time_index = end_time_index
		self.__acceleration_delta_end_time_index_acceleration = time_index_acceleration

	def merge(self, *, dot: Dot, current_time_index: float, merge_time_index_offset: float):
		self_position = self.get_position(
			time_index=current_time_index
		)
		self_velocity = self.get_velocity(
			time_index=current_time_index
		)
		destination_position = dot.get_position(
			time_index=current_time_index + merge_time_index_offset
		)
		destination_velocity = dot.get_velocity(
			time_index=current_time_index + merge_time_index_offset
		)
		destination_acceleration = dot.get_acceleration(
			time_index=current_time_index + merge_time_index_offset
		)

		acceleration_delta = []
		acceleration = []
		for dimension_index in range(len(self.__position)):
			temp_acceleration_delta = (-12 * destination_position[dimension_index] + 6 * destination_velocity[dimension_index] * merge_time_index_offset + 12 * self_position[dimension_index] + 6 * self_velocity[dimension_index] * merge_time_index_offset) / (merge_time_index_offset**3)
			temp_acceleration = (destination_velocity[dimension_index] - self_velocity[dimension_index]) / merge_time_index_offset - 0.5 * temp_acceleration_delta * merge_time_index_offset
			acceleration_delta.append(temp_acceleration_delta)
			acceleration.append(temp_acceleration)

		self.__position = self_position
		self.__velocity = self_velocity
		self.__acceleration = tuple(acceleration)
		self.__acceleration_delta = tuple(acceleration_delta)
		self.__acceleration_delta_end_time_index = merge_time_index_offset
		self.__acceleration_delta_end_time_index_acceleration = destination_acceleration
		self.__time_index_offset = -current_time_index


class DotPlotter():

	def __init__(self, minimum_position: Tuple[float, float], maximum_position: Tuple[float, float]):

		self.__minimum_position = minimum_position
		self.__maximum_position = maximum_position

		self.__dots = []  # type: List[Dot]

		self.__x = []
		self.__y = []
		self.__figure = None
		self.__scatter = None

	def add_dot(self, *, dot: Dot):
		self.__dots.append(dot)

	def __get_scatter(self, *, time_index: float) -> Tuple[List[float], List[float]]:
		scatter = ([], [])
		for dot in self.__dots:
			position = dot.get_position(
				time_index=time_index
			)

			if position[1] < self.__minimum_position[1]:
				dot.bounce(
					time_index=time_index
				)
			if position[0] < self.__minimum_position[0] or position[0] > self.__maximum_position[0]:
				dot.reflect(
					time_index=time_index
				)

			scatter[0].append(position[0])
			scatter[1].append(position[1])

			print(f"position: {position}")

		return scatter

	def show(self):
		plt.ion()
		self.__figure, ax = plt.subplots()
		self.__scatter = ax.scatter(self.__x, self.__y, facecolors="none", edgecolors=["black", "red"], s=10)
		plt.xlim(self.__minimum_position[0], self.__maximum_position[0])
		plt.ylim(self.__minimum_position[1], self.__maximum_position[1])
		plt.draw()

	def refresh(self, *, time_index: float):
		x, y = self.__get_scatter(
			time_index=time_index
		)
		self.__x.clear()
		self.__x.extend(x)
		self.__y.clear()
		self.__y.extend(y)
		self.__scatter.set_offsets(np.c_[self.__x, self.__y])
		self.__figure.canvas.draw_idle()
		plt.pause(0.01)


class LatencyPositionTest(unittest.TestCase):

	def test_initialize(self):

		dot_plotter = DotPlotter(
			minimum_position=(0, 0),
			maximum_position=(10, 10)
		)

		self.assertIsNotNone(dot_plotter)

	def test_move_dot_along_path(self):

		dot_plotter = DotPlotter(
			minimum_position=(0, 0),
			maximum_position=(10, 10)
		)

		dot = Dot(
			position=(1, 9),
			velocity=(1, 0),
			acceleration=(0, -1)
		)

		dot_plotter.add_dot(
			dot=dot
		)

		dot_plotter.show()

		print(f"refreshing")

		time_index = 0.0
		time_index_delta = 0.05
		while time_index < 20.0:
			dot_plotter.refresh(
				time_index=time_index
			)
			time_index += time_index_delta

		plt.waitforbuttonpress()

	def test_move_dot_along_path_in_separate_windows(self):

		dot_plotters_total = 2
		dot_plotters = []

		for dot_plotter_index in range(dot_plotters_total):
			dot_plotter = DotPlotter(
				minimum_position=(0, 0),
				maximum_position=(10, 10)
			)

			dot = Dot(
				position=(1, 9),
				velocity=(1, 0),
				acceleration=(0, -1)
			)

			dot_plotter.add_dot(
				dot=dot
			)

			dot_plotter.show()

			dot_plotters.append(dot_plotter)

		print(f"refreshing")

		time_index = 0.0
		time_index_delta = 0.05
		while time_index < 10.0:
			for dot_plotter in dot_plotters:
				dot_plotter.refresh(
					time_index=time_index
				)
			time_index += time_index_delta

		plt.waitforbuttonpress()

	def test_move_dot_along_path_then_alter_state(self):

		dot_plotter = DotPlotter(
			minimum_position=(0, 0),
			maximum_position=(10, 10)
		)

		dot = Dot(
			position=(1, 9),
			velocity=(1, 0),
			acceleration=(0, -1)
		)

		def alter_dot(*, time_index: float):
			nonlocal dot
			dot.set_state(
				position=dot.get_position(
					time_index=time_index
				),
				velocity=(-1, 1),
				acceleration=(0, -1),
				time_index=time_index
			)

		dot_plotter.add_dot(
			dot=dot
		)

		dot_plotter.show()

		print(f"refreshing")

		time_index = 0.0
		time_index_delta = 0.05
		maximum_time_index = 20.0
		is_altered = False
		while time_index < maximum_time_index:
			dot_plotter.refresh(
				time_index=time_index
			)
			time_index += time_index_delta

			if not is_altered and time_index > maximum_time_index / 2.0:
				alter_dot(
					time_index=time_index
				)
				is_altered = True

		plt.waitforbuttonpress()

	def test_move_dot_along_path_then_set_acceleration_delta(self):

		dot_plotter = DotPlotter(
			minimum_position=(0, 0),
			maximum_position=(10, 10)
		)

		dot = Dot(
			position=(1, 9),
			velocity=(1, 0),
			acceleration=(0, -1)
		)

		def alter_dot(*, time_index: float):
			nonlocal dot
			dot.set_acceleration_delta(
				time_index=time_index,
				acceleration_delta=(0, 0.5),
				end_time_index=5.0
			)

		dot_plotter.add_dot(
			dot=dot
		)

		dot_plotter.show()

		print(f"refreshing")

		time_index = 0.0
		time_index_delta = 0.05
		maximum_time_index = 30.0
		alter_time_index = 10.0
		is_altered = False
		while time_index < maximum_time_index:
			dot_plotter.refresh(
				time_index=time_index
			)
			time_index += time_index_delta

			if not is_altered and time_index > alter_time_index:
				alter_dot(
					time_index=time_index
				)
				is_altered = True

		plt.waitforbuttonpress()

	def test_move_two_dots_along_path_in_same_windows(self):

		dots_total = 2
		dots = []

		dot_plotter = DotPlotter(
			minimum_position=(0, 0),
			maximum_position=(10, 10)
		)

		for dot_index in range(dots_total):

			dot = Dot(
				position=(1, 9),
				velocity=(dot_index + 1, 0),
				acceleration=(0, -1)
			)

			dot_plotter.add_dot(
				dot=dot
			)

			dots.append(dot)

		dot_plotter.show()

		print(f"refreshing")

		time_index = 0.0
		time_index_delta = 0.05
		maximum_time_index = 20.0
		while time_index < maximum_time_index:
			dot_plotter.refresh(
				time_index=time_index
			)
			time_index += time_index_delta

		plt.waitforbuttonpress()

	def test_move_two_dots_along_path_in_same_windows_but_first_gets_acceleration_delta(self):

		dots_total = 2
		dots = []

		dot_plotter = DotPlotter(
			minimum_position=(0, 0),
			maximum_position=(10, 10)
		)

		for dot_index in range(dots_total):

			dot = Dot(
				position=(1, 9),
				velocity=(1, 0),
				acceleration=(0, -1)
			)

			dot_plotter.add_dot(
				dot=dot
			)

			dots.append(dot)

		dot_plotter.show()

		def alter_dot(*, time_index: float):
			nonlocal dots
			dots[0].set_acceleration_delta(
				time_index=time_index,
				acceleration_delta=(0, 0.5),
				end_time_index=5.0
			)

		print(f"refreshing")

		time_index = 0.0
		time_index_delta = 0.05
		maximum_time_index = 30.0
		alter_time_index = 10.0
		is_altered = False
		while time_index < maximum_time_index:
			dot_plotter.refresh(
				time_index=time_index
			)
			time_index += time_index_delta

			if not is_altered and time_index > alter_time_index:
				alter_dot(
					time_index=time_index
				)
				is_altered = True

		plt.waitforbuttonpress()

	def test_move_two_dots_along_path_in_same_windows_second_merges_specific_time_index_after_first_altered(self):

		dots_total = 2
		dots = []

		dot_plotter = DotPlotter(
			minimum_position=(0, 0),
			maximum_position=(10, 10)
		)

		for dot_index in range(dots_total):
			dot = Dot(
				position=(1, 9),
				velocity=(1, 0),
				acceleration=(0, -1)
			)

			dot_plotter.add_dot(
				dot=dot
			)

			dots.append(dot)

		dot_plotter.show()
		def alter_dot(*, time_index: float):
			nonlocal dots
			if False:
				dots[0].set_acceleration_delta(
					time_index=time_index,
					acceleration_delta=(0, 0.5),
					end_time_index=1.0
				)
			else:
				dots[0].set_velocity(
					velocity=(-1, 1)
				)

		def merge_dot(*, time_index: float):
			nonlocal dots
			dots[1].merge(
				dot=dots[0],
				current_time_index=time_index,
				merge_time_index_offset=1.0
			)

		print(f"refreshing")

		time_index = 0.0
		time_index_delta = 0.01
		maximum_time_index = 30.0
		alter_time_index = 10.0
		merge_time_index = 11.0
		is_altered = False
		is_merged = False
		while time_index < maximum_time_index:
			dot_plotter.refresh(
				time_index=time_index
			)
			time_index += time_index_delta

			if not is_altered and time_index > alter_time_index:
				alter_dot(
					time_index=time_index
				)
				is_altered = True
			if not is_merged and time_index > merge_time_index:
				merge_dot(
					time_index=time_index
				)
				is_merged = True

		plt.waitforbuttonpress()

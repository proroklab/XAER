# -*- coding: utf-8 -*-
import gym
import numpy as np
import copy
from matplotlib import use as matplotlib_use, patches

matplotlib_use('Agg',force=True) # no display
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.patches import Circle, Rectangle
from matplotlib.collections import PatchCollection
from matplotlib.lines import Line2D

from environments.car_controller.grid_drive.lib.road_grid import RoadGrid
from environments.car_controller.grid_drive.lib.road_cultures import HardRoadCulture

class GridDriveHard(gym.Env):
	CULTURE 					= HardRoadCulture
	GRID_DIMENSION				= 15
	MAX_SPEED 					= 120
	SPEED_GAP					= 10
	MAX_GAPPED_SPEED			= MAX_SPEED//SPEED_GAP
	MAX_STEP					= 2**5
	DIRECTIONS					= 4 # N,S,W,E
	VISITED_CELL_GRID_IDX		= -2
	AGENT_CELL_GRID_IDX			= -1

	def get_state(self):
		fc_dict = {
			"neighbours": self.grid.neighbour_features(), 
		}
		if self.obs_car_features > 0:
			fc_dict["agent"] = self.grid.agent.binary_features()
		return {
			"cnn": {
				"grid": self.grid_view,
			},
			"fc": fc_dict,
		}

	def get_reward(self, following_regulation, explanation_list):
		explanation_list_with_label = lambda l: list(map(lambda x:(l,x), explanation_list))
		x, y = self.grid.agent_position
		if not following_regulation:
			return (
				-(self.speed+1)/self.MAX_SPEED, # in [-1,0)
				True, # terminal state
				# explanation_list
				explanation_list_with_label('not_following_regulation'),
			)
		visiting_old_cell = self.grid_view[x][y][self.VISITED_CELL_GRID_IDX] > 0
		if visiting_old_cell: # already visited cell
			return (
				0,
				False, # non-terminal state
				'not_visiting_new_cells',
				# explanation_list_with_label('not_visiting_new_cells'),
			)
		return (
			(self.speed+1)/self.MAX_SPEED, # in (0,1]
			False, # non-terminal state
			# 'moving_forward',
			explanation_list_with_label('moving_forward'),
		)
	
	def __init__(self):
		self.culture = self.CULTURE(road_options={
			'motorway': 1/2,
			'stop_sign': 1/2,
			'school': 1/2,
			'single_lane': 1/2,
			'town_road': 1/2,
			'roadworks': 1/8,
			'accident': 1/8,
			'heavy_rain': 1/2,
			'congestion_charge': 1/8,
		}, agent_options={
			'emergency_vehicle': 1/5,
			'heavy_vehicle': 1/4,
			'worker_vehicle': 1/3,
			'tasked': 1/2,
			'paid_charge': 1/2,
			'speed': self.MAX_SPEED,
		})
		self.obs_road_features = len(self.culture.properties)  # Number of binary ROAD features in Hard Culture
		self.obs_car_features = len(self.culture.agent_properties)-1  # Number of binary CAR features in Hard Culture (excluded speed)

		# Direction (N, S, W, E) + Speed [0-MAX_SPEED]
		# self.action_space	   = gym.spaces.MultiDiscrete([self.DIRECTIONS, self.MAX_GAPPED_SPEED])
		self.action_space	   = gym.spaces.Discrete(self.DIRECTIONS*self.MAX_GAPPED_SPEED)
		fc_dict = {
			"neighbours": gym.spaces.MultiBinary(self.obs_road_features * self.DIRECTIONS), # Neighbourhood view
		}
		if self.obs_car_features > 0:
			fc_dict["agent"] = gym.spaces.MultiBinary(self.obs_car_features) # Car features
		self.observation_space = gym.spaces.Dict({
			"cnn": gym.spaces.Dict({
				"grid": gym.spaces.MultiBinary([self.GRID_DIMENSION, self.GRID_DIMENSION, self.obs_road_features+2]), # Features representing the grid + visited cells + current position
			}),
			"fc": gym.spaces.Dict(fc_dict),
		})
		self.step_counter = 0

	def reset(self):
		self.viewer = None
		# if self.step_counter%self.MAX_STEP == 0:
		self.grid = RoadGrid(self.GRID_DIMENSION, self.GRID_DIMENSION, self.culture)
		self.grid_features = np.array(self.grid.get_features(), ndmin=3, dtype=np.int8)
		self.step_counter = 0
		self.grid_view = np.concatenate([
			self.grid_features,
			np.zeros((self.GRID_DIMENSION, self.GRID_DIMENSION, 2), dtype=np.int8), # current position + visited cells
		], -1)
		self.grid.set_random_position()
		x,y = self.grid.agent_position
		self.grid_view[x][y][self.AGENT_CELL_GRID_IDX] = 1 # set new position
		self.grid_view[x][y][self.VISITED_CELL_GRID_IDX] = 1 # set current cell as visited
		return self.get_state()

	def step(self, action_vector):
		self.step_counter += 1
		self.direction = action_vector//self.MAX_GAPPED_SPEED
		self.speed = (action_vector%self.MAX_GAPPED_SPEED)*self.SPEED_GAP
		# direction, gapped_speed = action_vector
		old_x, old_y = self.grid.agent_position # get this before moving the agent
		reward, terminal, explanatory_labels = self.get_reward(*self.grid.move_agent(self.direction, self.speed))
		new_x, new_y = self.grid.agent_position # get this after moving the agent
		# do the following aftwer moving the agent and checking positions with get_reward
		self.grid_view[old_x][old_y][self.AGENT_CELL_GRID_IDX] = 0 # remove old position
		self.grid_view[new_x][new_y][self.AGENT_CELL_GRID_IDX] = 1 # set new position
		self.grid_view[new_x][new_y][self.VISITED_CELL_GRID_IDX] = 1 # set current cell as visited
		return [
			self.get_state(), # observation
			reward, 
			terminal or self.step_counter >= self.MAX_STEP, # terminal
			{'explanation': explanatory_labels} # info_dict
		]

	def get_screen(self):  # RGB array
		# First set up the figure and the axis
		# fig, ax = matplotlib.pyplot.subplots(nrows=1, ncols=1, sharey=False, sharex=False, figsize=(10,10)) # this method causes memory leaks
		figure = Figure(figsize=(10, 10), tight_layout=True)
		canvas = FigureCanvas(figure)
		ax = figure.add_subplot(111)  # nrows=1, ncols=1, index=1

		cell_side = 20

		# Compute speed limits for all cells.
		road_limits = {}
		columns = self.grid.width
		rows = self.grid.height
		temp_agent = copy.deepcopy(self.grid.agent)
		for x in range(columns):
			for y in range(rows):
				road = self.grid.cells[x][y]
				min_speed = None
				max_speed = None
				for speed in range(0, 121, 10):
					temp_agent.assign_property_value("Speed", speed)
					can_move, _ = self.grid.run_dialogue(road, temp_agent, explanation_type="compact")
					if can_move:
						if min_speed is None or speed < min_speed:
							min_speed = speed
						if max_speed is None or speed > max_speed:
							max_speed = speed
				road_limits[road] = (min_speed, max_speed)  # (None,None) if road is unfeasible

		# Draw cells
		shapes = []
		for x in range(columns):
			for y in range(rows):
				road = self.grid.cells[x][y]
				# Draw rectangle
				left = x * cell_side
				right = left + cell_side
				bottom = y * cell_side
				top = bottom + cell_side
				if self.grid_view[x][y][self.VISITED_CELL_GRID_IDX] > 0:  # Already visited cell
					cell_handle = Rectangle((left, bottom), cell_side, cell_side, color='gray', alpha=0.25)
				elif road_limits[road] == (None, None):  # Unfeasible road
					cell_handle = Rectangle((left, bottom), cell_side, cell_side, color='red', alpha=0.25)
				else: # new road with possible speed limits
					cell_handle = Rectangle((left, bottom), cell_side, cell_side, fill=False)
				shapes.append(cell_handle)

				# Do not add label if agent is on top of cell.
				if (x, y) == self.grid.agent_position:
					continue
				# Add speed limit label
				min_speed, max_speed = road_limits[road]
				label = f'{min_speed}-{max_speed}' if min_speed is not None else 'N/A'
				ax.text(0.5*(left + right), 0.5*(bottom + top), label,
							horizontalalignment='center', verticalalignment='center', size=18)



		# Draw agent and agent label
		agent_x, agent_y = self.grid.agent_position
		left = agent_x * cell_side
		right = left + cell_side
		bottom = agent_y * cell_side
		top = agent_y * cell_side
		agent_circle = Circle((left + (cell_side/2), bottom + (cell_side/2)), cell_side/2, color='b', alpha=0.5)
		shapes.append(agent_circle)

		patch_collection = PatchCollection(shapes, match_original=True)
		ax.add_collection(patch_collection)

		# Adjust view around agent
		zoom_factor = 3
		left_view = agent_x - zoom_factor
		right_view = agent_x + zoom_factor
		bottom_view = agent_y - zoom_factor
		top_view = agent_y + zoom_factor
		if agent_x > (columns - zoom_factor):  # Too far right
			left_view -= (agent_x + zoom_factor) - columns
		elif agent_x < zoom_factor:  		   # Too far left
			right_view += (zoom_factor - agent_x)
		if agent_y > (rows - zoom_factor):     # Too far up
			bottom_view -= (agent_y + zoom_factor) - rows
		elif agent_y < zoom_factor: 		   # Too far down
			top_view += (zoom_factor - agent_y)
		ax.set_xlim([max(0, left_view * cell_side),
					 min(columns * cell_side, right_view * cell_side)])
		ax.set_ylim([max(0, bottom_view * cell_side),
					 min(rows * cell_side, top_view * cell_side)])
		# ax.set_ylim([0, rows * cell_side])

		# Draw agent commanded speed on top of circle
		label = str(self.grid.agent["Speed"])
		ax.text(left + (cell_side/2), bottom + (cell_side/2), label,
					horizontalalignment='center', verticalalignment='center', size=18)

		# # Adjust ax limits in order to get the same scale factor on both x and y
		# a, b = ax.get_xlim()
		# c, d = ax.get_ylim()
		# max_length = max(d - c, b - a)
		# ax.set_xlim([a, a + max_length])
		# ax.set_ylim([c, c + max_length])

		# figure.tight_layout()
		canvas.draw()
		# Save plot into RGB array
		data = np.fromstring(figure.canvas.tostring_rgb(), dtype=np.uint8, sep='')
		data = data.reshape(figure.canvas.get_width_height()[::-1] + (3,))
		figure.clear()
		return data  # RGB array

	def render(self, mode='human'):
		img = self.get_screen()
		if mode == 'rgb_array':
			return img
		elif mode == 'human':
			from gym.envs.classic_control import rendering
			if self.viewer is None:
				self.viewer = rendering.SimpleImageViewer()
			self.viewer.imshow(img)
			return self.viewer.isopen

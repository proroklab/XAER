from gym.envs.atari.atari_env import AtariEnv
import numpy as np

class SpecialAtariEnv(AtariEnv):

	def reset(self):
		obs = super().reset()
		self.lives = self.ale.lives()
		return obs
	
	def step(self, a):
		old_lives = self.lives
		old_ram = self._get_ram()
		state, reward, terminal, info_dict = super().step(a)
		new_ram = self._get_ram()
		new_lives = self.ale.lives()

		lost_lives = old_lives-new_lives
		if reward != 0:
			explanation_list = ['reward']
		if lost_lives != 0:
			explanation_list = ['lost_lives']
		else:
			explanation_list = []
		explanation_list.append(new_ram-old_ram if explanation_list else 'no_reward')

		info_dict['explanation'] = [tuple(explanation_list)]
		self.lives = new_lives
		# print(reward, terminal, delta)

		return state, reward, terminal, info_dict
# Read this guide for how to use this script: https://medium.com/distributed-computing-with-ray/intro-to-rllib-example-environments-3a113f532c70
import os
os.environ["TUNE_RESULT_DIR"] = 'tmp/ray_results'
import multiprocessing
import json
import shutil
import ray
import time

from ray.rllib.agents.ddpg.td3 import TD3Trainer, TD3_DEFAULT_CONFIG
from environments import *
from ray.rllib.models import ModelCatalog
from xarl.models.ddpg import TFAdaptiveMultiHeadDDPG
ModelCatalog.register_custom_model("adaptive_multihead_network", TFAdaptiveMultiHeadDDPG)

# SELECT_ENV = "CescoDrive-V1"
SELECT_ENV = "GraphDrive-Hard"

CONFIG = TD3_DEFAULT_CONFIG.copy()
CONFIG.update({
	# "model": {
	# 	"custom_model": "adaptive_multihead_network",
	# },
	"rollout_fragment_length": 2**6, # Divide episodes into fragments of this many steps each during rollouts.
	"replay_sequence_length": 1, # The number of contiguous environment steps to replay at once. This may be set to greater than 1 to support recurrent models.
	"train_batch_size": 2**8, # Number of transitions per train-batch
	"batch_mode": "truncate_episodes", # For some clustering schemes (e.g. extrinsic_reward, moving_best_extrinsic_reward, etc..) it has to be equal to 'complete_episodes', otherwise it can also be 'truncate_episodes'.
	###########################
	"prioritized_replay": True, # Whether to replay batches with the highest priority/importance/relevance for the agent.
	'buffer_size': 2**14, # Size of the experience buffer. Default 50000
	"prioritized_replay_alpha": 0.6,
	"prioritized_replay_beta": 0.4, # The smaller, the stronger is over-sampling
	"prioritized_replay_eps": 1e-6,
	###########################
	"grad_clip": 40, # This prevents giant gradients and so improves robustness
	"l2_reg": 1e-6, # This mitigates over-fitting
	"tau": 1e-3, # The smaller, the lower the value over-estimation, the higher the bias
})

####################################################################################
####################################################################################

ray.shutdown()
ray.init(ignore_reinit_error=True)

# Configure RLlib to train a policy using the “Taxi-v3” environment and a PPO optimizer
agent = TD3Trainer(CONFIG, env=SELECT_ENV)

# Inspect the trained policy and model, to see the results of training in detail
# policy = agent.get_policy()
# model = policy.model
# print(model.base_model.summary())

# Train a policy. The following code runs 30 iterations and that’s generally enough to begin to see improvements in the “Taxi-v3” problem
# results = []
# episode_data = []
# episode_json = []
n = 0
while True:
	n += 1
	last_time = time.time()
	result = agent.train()
	# print(result)
	# results.append(result)
	episode = {
		'n': n, 
		'episode_reward_min': result['episode_reward_min'], 
		'episode_reward_mean': result['episode_reward_mean'], 
		'episode_reward_max': result['episode_reward_max'],  
		'episode_len_mean': result['episode_len_mean']
	}
	# episode_data.append(episode)
	# episode_json.append(json.dumps(episode))
	# file_name = agent.save(checkpoint_root)
	print(f'{n+1:3d}: Min/Mean/Max reward: {result["episode_reward_min"]:8.4f}/{result["episode_reward_mean"]:8.4f}/{result["episode_reward_max"]:8.4f}, len mean: {result["episode_len_mean"]:8.4f}, steps: {result["info"]["num_steps_trained"]:8.4f}, train ratio: {(result["info"]["num_steps_trained"]/result["info"]["num_steps_sampled"]):8.4f}, seconds: {time.time()-last_time}')
	# print(f'Checkpoint saved to {file_name}')


from ray.tune.registry import register_env
######### Add new environment below #########

from environments.custom_metrics import CustomEnvironmentCallbacks

from environments.gym_env_example import Example_v0
register_env("ToyExample-V0", lambda config: Example_v0(config))

### CescoDrive
from environments.car_controller.cesco_drive.cesco_drive_v0 import CescoDriveV0
register_env("CescoDrive-V0", lambda config: CescoDriveV0(config))

from environments.car_controller.cesco_drive.cesco_drive_v1 import CescoDriveV1
register_env("CescoDrive-V1", lambda config: CescoDriveV1(config))

### GraphDrive
from environments.car_controller.graph_drive.graph_drive import GraphDrive
## V1
register_env("GraphDrive-Easy-V1", lambda config: GraphDrive({"reward_fn": 'frequent_reward_v1', "culture_level": "Easy"}))
register_env("GraphDrive-Medium-V1", lambda config: GraphDrive({"reward_fn": 'frequent_reward_v1', "culture_level": "Medium"}))
register_env("GraphDrive-Hard-V1", lambda config: GraphDrive({"reward_fn": 'frequent_reward_v1', "culture_level": "Hard"}))
## V2
register_env("GraphDrive-Easy-V2", lambda config: GraphDrive({"reward_fn": 'frequent_reward_v2', "culture_level": "Easy"}))
register_env("GraphDrive-Medium-V2", lambda config: GraphDrive({"reward_fn": 'frequent_reward_v2', "culture_level": "Medium"}))
register_env("GraphDrive-Hard-V2", lambda config: GraphDrive({"reward_fn": 'frequent_reward_v2', "culture_level": "Hard"}))
## V3
register_env("GraphDrive-Easy-V3", lambda config: GraphDrive({"reward_fn": 'frequent_reward_v3', "culture_level": "Easy"}))
register_env("GraphDrive-Medium-V3", lambda config: GraphDrive({"reward_fn": 'frequent_reward_v3', "culture_level": "Medium"}))
register_env("GraphDrive-Hard-V3", lambda config: GraphDrive({"reward_fn": 'frequent_reward_v3', "culture_level": "Hard"}))
## V1
register_env("GraphDrive-Easy-Sparse-V1", lambda config: GraphDrive({"reward_fn": 'sparse_reward_v1', "culture_level": "Easy"}))
register_env("GraphDrive-Medium-Sparse-V1", lambda config: GraphDrive({"reward_fn": 'sparse_reward_v1', "culture_level": "Medium"}))
register_env("GraphDrive-Hard-Sparse-V1", lambda config: GraphDrive({"reward_fn": 'sparse_reward_v1', "culture_level": "Hard"}))
## V2
register_env("GraphDrive-Easy-Sparse-V2", lambda config: GraphDrive({"reward_fn": 'sparse_reward_v2', "culture_level": "Easy"}))
register_env("GraphDrive-Medium-Sparse-V2", lambda config: GraphDrive({"reward_fn": 'sparse_reward_v2', "culture_level": "Medium"}))
register_env("GraphDrive-Hard-Sparse-V2", lambda config: GraphDrive({"reward_fn": 'sparse_reward_v2', "culture_level": "Hard"}))
## V3
register_env("GraphDrive-Easy-Sparse-V3", lambda config: GraphDrive({"reward_fn": 'sparse_reward_v3', "culture_level": "Easy"}))
register_env("GraphDrive-Medium-Sparse-V3", lambda config: GraphDrive({"reward_fn": 'sparse_reward_v3', "culture_level": "Medium"}))
register_env("GraphDrive-Hard-Sparse-V3", lambda config: GraphDrive({"reward_fn": 'sparse_reward_v3', "culture_level": "Hard"}))
## V4
register_env("GraphDrive-Easy-Sparse-V4", lambda config: GraphDrive({"reward_fn": 'sparse_reward_v4', "culture_level": "Easy"}))
register_env("GraphDrive-Medium-Sparse-V4", lambda config: GraphDrive({"reward_fn": 'sparse_reward_v4', "culture_level": "Medium"}))
register_env("GraphDrive-Hard-Sparse-V4", lambda config: GraphDrive({"reward_fn": 'sparse_reward_v4', "culture_level": "Hard"}))

### GridDrive
from environments.car_controller.grid_drive.grid_drive import GridDrive
## V1
register_env("GridDrive-Easy-V1", lambda config: GridDrive({"reward_fn": 'frequent_reward_v1', "culture_level": "Easy"}))
register_env("GridDrive-Medium-V1", lambda config: GridDrive({"reward_fn": 'frequent_reward_v1', "culture_level": "Medium"}))
register_env("GridDrive-Hard-V1", lambda config: GridDrive({"reward_fn": 'frequent_reward_v1', "culture_level": "Hard"}))
## V2
register_env("GridDrive-Easy-V2", lambda config: GridDrive({"reward_fn": 'frequent_reward_v2', "culture_level": "Easy"}))
register_env("GridDrive-Medium-V2", lambda config: GridDrive({"reward_fn": 'frequent_reward_v2', "culture_level": "Medium"}))
register_env("GridDrive-Hard-V2", lambda config: GridDrive({"reward_fn": 'frequent_reward_v2', "culture_level": "Hard"}))
## V3
register_env("GridDrive-Easy-V3", lambda config: GridDrive({"reward_fn": 'frequent_reward_v3', "culture_level": "Easy"}))
register_env("GridDrive-Medium-V3", lambda config: GridDrive({"reward_fn": 'frequent_reward_v3', "culture_level": "Medium"}))
register_env("GridDrive-Hard-V3", lambda config: GridDrive({"reward_fn": 'frequent_reward_v3', "culture_level": "Hard"}))

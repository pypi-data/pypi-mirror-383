from collectivecrossing import CollectiveCrossingEnv
from collectivecrossing.configs import CollectiveCrossingConfig
from collectivecrossing.reward_configs import DefaultRewardConfig
from collectivecrossing.terminated_configs import IndividualAtDestinationTerminatedConfig
from collectivecrossing.truncated_configs import MaxStepsTruncatedConfig
from collectivecrossing.observation_configs import DefaultObservationConfig

# Create environment with configurable systems
reward_config = DefaultRewardConfig(
    boarding_destination_reward=15.0,
    tram_door_reward=10.0,
    tram_area_reward=5.0,
    distance_penalty_factor=0.1
)

terminated_config = IndividualAtDestinationTerminatedConfig()
truncated_config = MaxStepsTruncatedConfig(max_steps=100)
observation_config = DefaultObservationConfig()

config = CollectiveCrossingConfig(
    width=12, 
    height=8, 
    division_y=4,
    tram_door_left=5, 
    tram_door_right=7, 
    tram_length=9,
    num_boarding_agents=5, 
    num_exiting_agents=3,
    exiting_destination_area_y=0, 
    boarding_destination_area_y=8,
    render_mode="rgb_array",
    reward_config=reward_config,
    terminated_config=terminated_config,
    truncated_config=truncated_config,
    observation_config=observation_config
)

env = CollectiveCrossingEnv(config=config)
observations, infos = env.reset(seed=42)

# Take actions for all agents
actions = {
    "boarding_0": 0,  # Move right
    "boarding_1": 1,  # Move up
    "boarding_2": 2,  # Move left
    "boarding_3": 3,  # Move down
    "boarding_4": 4,  # Wait
    "exiting_0": 0,   # Move right
    "exiting_1": 1,   # Move up
    "exiting_2": 2,   # Move left
}

# Step the environment
observations, rewards, terminated, truncated, infos = env.step(actions)

# Render the environment
rgb_array = env.render()
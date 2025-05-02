from gymnasium.envs.registration import register

register(
    id="BackgammonHumanEnv-v0",
    entry_point="envs:BackgammonHumanEnv",
)
register(
    id="BackgammonPolicyEnv-v0",
    entry_point="envs:BackgammonPolicyEnv",
)
register(
    id="BackgammonRandomEnv-v0",
    entry_point="envs:BackgammonRandomEnv",
)
register(
    id="BackgammonRandomContinuousEnv-v0",
    entry_point="envs:BackgammonRandomContinuousEnv",
)

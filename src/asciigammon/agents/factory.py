from gymnasium import spaces

from asciigammon.agents import RandomAgent, HumanAgent, BaseAgent  # Example


def create_agent(agent_type: str, player_type, game) -> BaseAgent:
    action_space = spaces.Discrete(len(game.actions))
    action_list = game.actions

    if agent_type == "human":
        return HumanAgent(player_type, game)
    elif agent_type == "random":
        return RandomAgent(action_space, action_list)
    else:
        raise ValueError(f"Unknown agent type: {agent_type}")

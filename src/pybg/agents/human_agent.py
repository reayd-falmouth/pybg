from pybg.agents import BaseAgent


class HumanAgent(BaseAgent):
    def __init__(self, player_type, game):
        self.player_type = player_type
        self.game = game

    def make_decision(self, observation=None, action_mask=None, legal_plays=None):
        # No-op: actual input comes from CLI
        return None

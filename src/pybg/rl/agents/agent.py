from abc import abstractmethod


class Agent:

    @abstractmethod
    def make_decision(self, observation=None, action_mask=None):
        pass

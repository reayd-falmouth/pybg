from abc import abstractmethod


class BaseAgent:

    @abstractmethod
    def make_decision(self, observation=None, action_mask=None):
        pass

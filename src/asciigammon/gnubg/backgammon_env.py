import gymnasium as gym
import numpy as np
import random
from gymnasium import spaces


from asciigammon.core.board import Board
from asciigammon.core.match import GameState

# from asciigammon.neuralnet.gnubg_nn import GnubgEvaluator
from asciigammon.neuralnet.helpers import encode_board_by_size


class BackgammonEnv(gym.Env):
    """
    A Gym Environment for Backgammon based on your existing Stones+Dice code.

    Observation:
      A 250-dimensional vector (float32) encoding the board position using a
      GNUBG-compatible feature encoder.

    Actions:
      An integer in Discrete(N) representing the selected legal play.
      (Legal plays are generated dynamically from the board state.)

    Rewards:
      For now, a reward is given at the end of the game:
        - 1.0 for a win (player 0 winning, adjust as desired)
        - 0.0 for a loss.
      Intermediate moves provide a zero reward.

    Note:
      The legal moves available in a given state are returned in the info dict.
      In the step() function if the provided action index is out of bounds,
      a random legal move will be taken.
    """

    metadata = {"render.modes": ["human"]}

    def __init__(self):

        # Define the observation space: 250-dimensional vector with values [0,1]
        self.observation_space = spaces.Box(
            low=-1.0, high=1.0, shape=(250,), dtype=np.float32
        )

        # Define a discrete action space (we choose an upper bound; legal moves can vary)
        self.action_space: spaces.Discrete = spaces.Discrete(1157)

        # Initialize the board
        self.board = Board()
        self.board.first_roll()  # Perform the first dice roll if necessary

        # Populate state and legal moves
        self.state = self._get_state()
        self.legal_moves = self.board.generate_plays()
        self.done = False

    def _get_state(self):
        """Encode the board position as a 250-dimensional feature vector."""
        return encode_board_by_size(self.board.position, 250)

    def reset(self, *, seed=None, options=None):
        """Reset the game environment to its initial state."""
        super().reset(seed=seed)
        self.board = Board()
        # self.board._evaluator = GnubgEvaluator()
        self.board.first_roll()
        self.done = False
        self.state = self._get_state()
        self.legal_moves = self.board.generate_plays()
        return self.state, {"action_mask": self._get_action_mask()}

    def step(self, action):
        """
        Apply the chosen action (indexed into the legal moves).
        Returns:
          observation (250-dim vector), reward, done flags, and info dict.
        """
        print(f"Turn switch: now it's player {self.board.match.player}")

        # 🎲 Roll dice if we're on roll and dice haven't been rolled yet
        if self.board.match.game_state == GameState.ON_ROLL:
            self.board.roll()
            # print(self.board)
            # print(f"🎲 Rolled: {self.board.match.dice}")
            self.legal_moves = self.board.generate_plays()

        # ⏩ If no legal moves, just end the turn
        if not self.legal_moves:
            self.board.end_turn()
            self.legal_moves = self.board.generate_plays()
            self.state = self._get_state()
            return (
                self.state,
                0.0,
                False,
                False,
                {
                    "legal_moves": self.legal_moves,
                    "action_mask": self._get_action_mask(),  # ← Add this
                },
            )

        # ✅ Select and apply legal move
        if action >= len(self.legal_moves):
            print(
                f"⚠️ Invalid action {action}, falling back to a legal random move during env check"
            )
            action = random.randint(0, len(self.legal_moves) - 1)

        chosen_play = self.legal_moves[action]

        move_tuple = tuple((m.source, m.destination) for m in chosen_play.moves)
        try:
            self.board.play(move_tuple)
        except Exception as e:
            print("🚨 Invalid move attempted:", move_tuple)
            print("Board state:", self.board)
            raise e

        # 🏁 Check for game over
        if self.board.match.game_state == GameState.GAME_OVER:
            self.done = True
            reward = (
                1.0
                if self.board.match.player_0_score >= self.board.match.length
                else 0.0
            )
        else:
            reward = 0.0

        # 🔁 Update observation and legal moves
        self.state = self._get_state()
        self.legal_moves = self.board.generate_plays()
        return (
            self.state,
            reward,
            self.done,
            False,
            {
                "legal_moves": self.legal_moves,
                "action_mask": self._get_action_mask(),
            },
        )

    def render(self, mode="human"):
        """Render the current board state."""
        print(self.board)
        return

    def close(self):
        """Any necessary cleanup."""
        pass

    def _play_key(self, play):
        return tuple((m.source, m.destination) for m in play.moves)

    def _get_action_mask(self):
        mask = np.zeros(self.action_space.n, dtype=bool)
        for play in self.legal_moves:
            key = self._play_key(play)
            index = self.play_to_index.get(key)
            if index is not None:
                mask[index] = True
            else:
                print(f"⚠️ Missing index for legal play: {key}")
        return mask


if __name__ == "__main__":
    # Run a simple test of the environment
    env = BackgammonEnv()
    state = env.reset()
    print("Initial state (first 20 features):", state[:20])
    done = False
    steps = 0

    while not done and steps < 10:
        # List legal moves info for debugging
        print("Legal moves count:", len(env.legal_moves))
        # Choose a random legal move index
        action = env.action_space.sample()
        state, reward, done, info = env.step(action)
        print(f"Step: {steps} Reward: {reward} Done: {done}")
        steps += 1

    env.render()

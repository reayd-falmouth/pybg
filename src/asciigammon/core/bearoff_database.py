# bearoff_database.py
import math

import json
import numpy as np
import os
import struct

from .board import Board
from .logger import logger
from .position import Position, PositionClass
from ..constants import ASSETS_DIR

CACHE_FILE = f"{ASSETS_DIR}/bearoff_cache.json"
OS_PATH = f"{ASSETS_DIR}/gnubg/gnubg_os0.bd"
TS_PATH = f"{ASSETS_DIR}/gnubg/gnubg_ts0.bd"


class _BearoffReader:
    POSITION_CACHE = {}
    MAX_PLY_DEPTH = 2  # default depth for n-ply evaluation
    DICE_ROLLS = [(i, j) for i in range(1, 7) for j in range(i, 7)]  # 21 unique rolls
    GAMMON_WEIGHT = 1.0
    LOSE_GAMMON_WEIGHT = 1.0

    def __init__(self, filename: str, cache: dict):
        self.filename = filename
        self.cache = cache
        self.loaded = False
        self.points = 0
        self.chequers = 0
        self.two_sided = False
        self.data = None
        self.load_database()

    def load_database(self):
        with open(self.filename, "rb") as f:
            header = f.read(40)
            self.parse_header(header)
            f.seek(0, os.SEEK_END)
            size = f.tell()
            f.seek(0)
            self.data = f.read(size)
            self.loaded = True

    def parse_header(self, header: bytes):
        header_str = header.decode("ascii", errors="ignore").strip("\x00")
        if not header_str.startswith("gnubg-"):
            raise ValueError("Invalid bearoff file: missing 'gnubg-' prefix")

        parts = header_str.split("-")
        if parts[1] == "TS":
            self.two_sided = True
        elif parts[1] == "OS":
            self.two_sided = False
        else:
            raise ValueError(f"Unknown bearoff type: {parts[1]}")

        self.points = int(parts[2])
        self.chequers = int(parts[3])

    def get_position_id(self, board: list):
        fBits = 0
        j = len(board) - 1
        for i in range(len(board)):
            j += board[i]
        fBits = 1 << j
        for i in range(len(board) - 1):
            j -= board[i] + 1
            fBits |= 1 << j
        return self.position_f(fBits, 15 + len(board), len(board))

    def position_f(self, fBits, n, r):
        if n == r:
            return 0
        if (fBits >> (n - 1)) & 1:
            return self.combination(n - 1, r) + self.position_f(fBits, n - 1, r - 1)
        else:
            return self.position_f(fBits, n - 1, r)

    def combination(self, n, r):
        if n < r or r < 0:
            return 0
        return math.comb(n, r)

    def read_distribution(self, pos_id: int):
        if self.two_sided:
            raise NotImplementedError(
                "Two-sided bearoff DB support not yet implemented."
            )

        n_pos = self.combination(self.points + self.chequers, self.points)
        offset_area = 40 + n_pos * 8

        entry = self.data[40 + pos_id * 8 : 40 + (pos_id + 1) * 8]
        offset, nz, ioff, nzg, ioffg = struct.unpack("<IBBBB", entry)

        data_offset = offset_area + 2 * offset
        n_bytes = 2 * (nz + nzg)

        values = self.data[data_offset : data_offset + n_bytes]
        dist = np.zeros(64, dtype=np.uint16)

        for i in range(nz):
            dist[ioff + i] = values[2 * i] | (values[2 * i + 1] << 8)

        for i in range(nzg):
            idx = 32 + ioffg + i
            dist[idx] = values[2 * (nz + i)] | (values[2 * (nz + i) + 1] << 8)

        return dist

    def evaluate_position(self, position: Position) -> dict:
        pos_id = position.encode()
        if pos_id in self.cache:
            logger.debug(f"Cache hit for position {pos_id}")
            return self.cache[pos_id]

        board_opp, board_player = position.to_board_array()

        pos_id_player = self.get_position_id(board_player[: self.points])
        pos_id_opp = self.get_position_id(board_opp[: self.points])

        dist_player = self.read_distribution(pos_id_player)
        dist_opp = self.read_distribution(pos_id_opp)

        probs_player = dist_player[:32] / 65535.0
        probs_opp = dist_opp[:32] / 65535.0

        win_chance = 0.0
        for i in range(32):
            for j in range(i, 32):
                win_chance += probs_player[i] * probs_opp[j]

        expected_rolls = sum(i * probs_player[i] for i in range(32))

        result = {
            "expected_rolls": expected_rolls,
            "win_prob": float(min(max(win_chance, 0), 1)),
            "gammon_prob": 0.0,
            "lose_gammon_prob": 0.0,
        }

        self.cache[pos_id] = result
        return result

    def calculate_equity(self, win_prob, gammon_prob, lose_gammon_prob):
        """Approximate GNUBG 0-ply equity calculation."""
        return (
            (2 * win_prob - 1)
            + self.GAMMON_WEIGHT * gammon_prob
            - self.LOSE_GAMMON_WEIGHT * lose_gammon_prob
        )

    def opponent_best_response(self, board):
        plays = board.generate_plays(partial=False)
        if not plays:
            # No legal moves, opponent passes
            return self.evaluate_position(board.position)

        worst_equity = None
        worst_eval = None

        for play in plays:
            new_position = play.position
            eval_result = self.evaluate_position(new_position)
            equity = self.calculate_equity(
                eval_result["win_prob"],
                eval_result["gammon_prob"],
                eval_result["lose_gammon_prob"],
            )

            if worst_equity is None or equity < worst_equity:
                worst_equity = equity
                worst_eval = eval_result

        return worst_eval

    def average_opponent_response(self, position):
        """Average opponent responses across all 21 dice rolls."""
        total_win = 0.0
        total_gammon = 0.0
        total_lose_gammon = 0.0
        num_rolls = 0

        for d0, d1 in self.DICE_ROLLS:
            new_board = Board(position_id=position.encode())
            new_board.match.dice = (d0, d1)
            worst_eval = self.opponent_best_response(new_board)

            total_win += worst_eval["win_prob"]  # ✅ No flipping
            total_gammon += worst_eval["gammon_prob"]
            total_lose_gammon += worst_eval["lose_gammon_prob"]

            num_rolls += 1 if d0 == d1 else 2

        avg_win = total_win / num_rolls
        avg_gammon = total_gammon / num_rolls
        avg_lose_gammon = total_lose_gammon / num_rolls

        return {
            "win_prob": avg_win,
            "gammon_prob": avg_gammon,
            "lose_gammon_prob": avg_lose_gammon,
        }

    def complete_eval(self, board: Board) -> list:
        plays = board.generate_plays(partial=False)

        if not plays:
            logger.warn("No legal plays.")
            return []

        evaluations = []

        for play in plays:
            new_position = play.position

            avg_eval = self.average_opponent_response(new_position)

            equity = self.calculate_equity(
                avg_eval["win_prob"],
                avg_eval["gammon_prob"],
                avg_eval["lose_gammon_prob"],
            )

            evaluations.append((play, avg_eval, equity))

        evaluations.sort(key=lambda x: x[2], reverse=True)

        return evaluations


class BearoffDatabase:
    def __init__(self, os_path: str = OS_PATH, ts_path: str = TS_PATH):
        self._cache = self.load_cache()
        self.os_reader: _BearoffReader = _BearoffReader(os_path, self._cache)
        self.ts_reader: _BearoffReader = _BearoffReader(ts_path, self._cache)

    def evaluate(self, board: Board, position_class: PositionClass) -> list:
        if position_class == PositionClass.BEAROFF1:
            if not self.os_reader:
                raise RuntimeError("One-sided bearoff database not loaded.")
            return self.os_reader.complete_eval(board)
        elif position_class == PositionClass.BEAROFF2:
            if not self.ts_reader:
                raise RuntimeError("Two-sided bearoff database not loaded.")
            return self.ts_reader.complete_eval(board)
        else:
            raise ValueError(f"Unsupported position class: {position_class}")

    def save(self):
        self.save_cache(self._cache)

    def clear_cache(self):
        self._cache.clear()
        self.save()

    def get_cached_eval(self, position: Position):
        return self._cache.get(position.encode())

    @staticmethod
    def load_cache():
        if os.path.exists(CACHE_FILE):
            try:
                with open(CACHE_FILE, "r") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                logger.warn("Cache file is corrupted. Starting empty cache.")
        return {}

    @staticmethod
    def save_cache(cache):
        with open(CACHE_FILE, "w") as f:
            json.dump(cache, f)

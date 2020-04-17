# -*- coding: utf-8 -*-

import random
import string
from datetime import datetime
import re


class Boggle:
    def __init__(self, bg_dict, game_id, duration, size=4):
        self.game_id = game_id
        self.size = size
        self._board = [[" "] * self.size for _ in range(self.size)]
        self.adjacency = self._build_adjacency()
        self.score = 0
        self.bg_dict = bg_dict
        self.words = None
        self.init_time = datetime.now()
        self.duration = duration
        self.token = self._random_char(32)

    def _random_char(self, y):
        return "".join(
            random.choice(string.ascii_lowercase + string.digits) for x in range(y)
        )

    def _random_board(self):
        y = self.size * self.size
        return ",".join(random.choice(string.ascii_uppercase) for x in range(y))

    def __repr__(self):
        return "\n".join([" ".join(row) for row in self._board])

    def _count_adjacent(self, pos):
        """
        Finds all adjacent positions for a given position on the board
        """
        row, col = pos
        adj = []
        for i in [-1, 0, 1]:
            for j in [-1, 0, 1]:
                new_row = row + i
                new_col = col + j
                if (
                    0 <= new_row < self.size
                    and 0 <= new_col < self.size
                    and not (i == j == 0)
                ):
                    adj.append((new_row, new_col))
        return adj

    def _build_adjacency(self):
        """
        Builds the adjacency lookup for each position on the board
        """
        adjacency = dict()
        for row in range(0, self.size):
            for col in range(0, self.size):
                adjacency[(row, col)] = self._count_adjacent((row, col))

        return adjacency

    def _get_letter(self, pos):
        return self._board[pos[0]][pos[1]]

    def set_board(self, random=True, letters=None):
        if random:
            letters = self._random_board()

        if random == False and letters is None:
            with open("./test_board.txt", "r") as f:
                letters = f.readlines()[0].rstrip().replace(" ", "")

        letters = letters.replace(" ", "").split(",")
        for row in range(self.size):
            index = row * self.size
            row_letters = letters[index : index + self.size]
            for col, letter in enumerate(row_letters):
                self._board[row][col] = letter

        self.words = self._find_words()

        return {
            "id": self.game_id,
            "token": self.token,
            "duration": self.duration,
            "board": self.get_board(),
        }

    def _find_words(self):
        """
        Finds all words on the board
        """
        words = set()
        for row in range(self.size):
            for col in range(self.size):
                words |= self._find_words_pos((row, col))
        return words

    def _find_words_pos(self, pos):
        """
        Finds words starting at a given position on the board
        """
        stack = [(n, [pos], self._get_letter(pos)) for n in self.adjacency[pos]]
        words = set()
        while len(stack) > 0:
            curr, path, chars = stack.pop()
            curr_char = self._get_letter(curr)
            curr_chars = chars + curr_char

            search_chars = curr_chars.replace("*", "[A-Z]").lower()

            p = re.compile(search_chars)
            l = len(curr_chars)

            if l > 1 and (str(l) in self.bg_dict):
                words.update(p.findall(self.bg_dict[str(l)]))

            if l < 3:
                search_key = f"prefix:{l}"
            else:
                search_key = str(l)

            if (search_key in self.bg_dict) and p.search(self.bg_dict[search_key]):
                curr_adj = self.adjacency[curr]
                stack.extend(
                    [(n, path + [curr], curr_chars) for n in curr_adj if n not in path]
                )

        return words

    def get_board(self):
        return ", ".join([y for x in self._board for y in x])

    def get_words(self):
        return self.words

    def timeout_check(self):
        return self.check_left_time() > 0

    def check_left_time(self):
        delta = datetime.now() - self.init_time
        result = 0

        if delta.total_seconds() < self.duration:
            result = self.duration - int(round(delta.total_seconds()))

        return result

    def play(self, word):
        if self.check_left_time() is 0:
            return self.show_game()

        word = word.lower()
        check_result = word in self.words

        if check_result:
            self.score += len(word)

        return check_result, self.show_game()

    def show_game(self):
        return {
            "id": self.game_id,
            "token": self.token,
            "duration": self.duration,
            "board": self.get_board(),
            "time_left": self.check_left_time(),
            "points": self.score,
        }

    def get_token(self):
        return self.token

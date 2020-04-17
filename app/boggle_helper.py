# -*- coding: utf-8 -*-

import re


class Board_helper:
    def __init__(self, redis_cli=None):
        return None

    def load_dictionary(self, file):
        result = {}

        prefix1 = set()
        prefix2 = set()
        with open(file, "r") as f:
            next(f)
            for line in f:
                word = line.rstrip()
                word_len = len(word)
                dict_key = str(word_len)

                if word_len > 1:
                    prefix1.add(word[0])

                if word_len > 2:
                    prefix2.add(word[:2])

                if dict_key not in result:
                    result.update({dict_key: ""})

                result[dict_key] += f",{word}"

            result.update(
                {"prefix:1": ",".join(prefix1), "prefix:2": ",".join(prefix2)}
            )

        return result

    def _randomString(self, stringLength=10):
        import random
        import string

        """Generate a random string of fixed length """
        letters = string.ascii_lowercase
        return "".join(random.choice(letters) for i in range(stringLength))

    def word_check(self, word):
        p = re.compile(r"^[A-Za-z]+$")
        return p.match(word)

    def board_check(self, board):
        p = re.compile(r"^[A-Z\*\, ]+$")
        if not p.match(board):
            return False

        b = board.split(",")
        if len(b) != 16:
            return False

        if "" in b:
            return False

        return True

    def board_trans(self, board):
        return board.rstrip().split(",")

    def duration_check(self, duration):
        p = re.compile(r"[0-9]+$")
        return p.match(str(duration))

    def start_game_check(self, content):
        if content is None:
            return False, "No content"

        if ("duration" not in content) or ("random" not in content):
            return False, "wrong parameteres"

        if not self.duration_check(content["duration"]):
            return False, "Duration chould onlu contain numbers"

        return True, ""

    def play_game_check(self, content):
        if content is None:
            return False, "No content", 400

        if ("token" not in content) or ("word" not in content):
            return False, "wrong parameteres", 400

        if not self.word_check(content["word"]):
            return False, "word should only contain characters", 400

        return True, "", 200

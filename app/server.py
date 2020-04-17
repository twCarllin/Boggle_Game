# -*- coding: utf-8 -*-

import os
import sys
import json
from flask import Flask, jsonify, request, abort
from app.boggle import Boggle
from app.boggle_helper import Board_helper


def create_app():
    app = Flask(__name__)

    bg_helper = Board_helper()
    boggle_dict = bg_helper.load_dictionary("./dictionary.txt")
    boards = {}

    def err_msg(message):
        return jsonify({"message": message})

    @app.route("/games", methods=["POST"])
    def start_game():
        content = request.get_json()
        game_id = str(len(boards) + 1)

        start_game_check, msg = bg_helper.start_game_check(content)
        if not start_game_check:
            return err_msg(msg), 400

        if content["random"]:
            b = Boggle(boggle_dict, game_id, content["duration"])
            result = b.set_board()

        elif not content["random"] and ("board" in content):
            if not bg_helper.board_check(content["board"]):
                return err_msg("bord should only inclufind [A-Z] and *"), 400

            b = Boggle(boggle_dict, game_id, content["duration"])
            result = b.set_board(random=False, letters=content["board"])

        else:
            b = Boggle(boggle_dict, game_id, content["duration"])
            result = b.set_board(random=False)

        boards.update({game_id: b})
        return jsonify(result), 201

    @app.route("/games/<game_id>", methods=["PUT"])
    def play_game(game_id):
        content = request.get_json()

        play_game_check, msg, status = bg_helper.play_game_check(content)
        if not play_game_check:
            return err_msg(msg), status

        if content["token"] != boards[game_id].get_token():
            return err_msg("auth fail"), 401

        if game_id not in boards:
            return err_msg("game not exist"), 404

        if not boards[game_id].timeout_check():
            return err_msg("outdated game"), 400

        bool_find, result = boards[game_id].play(content["word"])

        if bool_find:
            return jsonify(result), 200

        return err_msg("word not in board"), 400

    @app.route("/games/<game_id>", methods=["GET"])
    def show_game(game_id):
        if game_id not in boards:
            return err_msg("game not exist"), 404

        result = boards[game_id].show_game()

        return jsonify(result), 200

    @app.errorhandler(404)
    def bad_request(*args):
        response = jsonify({"message": "path not exist"})
        response.status_code = 404
        return response

    return app

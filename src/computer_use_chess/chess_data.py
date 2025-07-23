import chess
import chess.svg
import random
import os
import json

def random_move(board: chess.Board) -> chess.Move:
    return random.choice(list(board.legal_moves))

def square_to_coords(square: int) -> str:
    file = chess.square_file(square)
    rank = chess.square_rank(square)
    return f"{chr(file + ord('a'))}{rank + 1}"

def play_and_save_images(dataset_dir: str, moves_per_game: int, game_idx: int):
    game_dir = os.path.join(dataset_dir, f"game_{game_idx}")
    os.makedirs(game_dir, exist_ok=True)
    board = chess.Board()
    move_data = []
    for m in range(moves_per_game):
        if board.is_game_over():
            break
        move = random_move(board)
        board.push(move)
        img_name = f"move_{m}.svg"
        svg = chess.svg.board(board)
        with open(os.path.join(game_dir, img_name), "w") as f:
            f.write(svg)
        move_record = {
            "move_number": m,
            "uci": move.uci(),
            "from": square_to_coords(move.from_square),
            "to": square_to_coords(move.to_square),
            "image": img_name
        }
        move_data.append(move_record)
    with open(os.path.join(game_dir, "moves.json"), "w") as f:
        json.dump(move_data, f, indent=2)

# Usage
play_and_save_images(dataset_dir="/Users/sashanktirumala/projects/data/test_dataset", moves_per_game=40, game_idx=0)

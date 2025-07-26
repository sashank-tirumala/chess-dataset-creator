import chess
import chess.svg
import random
import os
import json
from PIL import Image
import cairosvg
import io
import numpy as np

def get_vm_background_image_dict(img_path:str):
    lichess_img = Image.open(img_path)
    lichess_img_array = np.array(lichess_img)
    pts= [(200, 190), (720, 190), (720, 710), (200, 710)]
    min_x = min([pts[0][0], pts[1][0], pts[2][0], pts[3][0]])
    max_x = max([pts[0][0], pts[1][0], pts[2][0], pts[3][0]])
    min_y = min([pts[0][1], pts[1][1], pts[2][1], pts[3][1]])
    max_y = max([pts[0][1], pts[1][1], pts[2][1], pts[3][1]])
    dist1 = ((pts[0][0] - pts[1][0])**2 +  (pts[0][1] - pts[1][1])**2)**0.5
    dist2 = ((pts[1][0] - pts[2][0])**2 +  (pts[1][1] - pts[2][1])**2)**0.5
    dist3 = ((pts[2][0] - pts[3][0])**2 +  (pts[2][1] - pts[3][1])**2)**0.5
    dist4 = ((pts[3][0] - pts[0][0])**2 +  (pts[3][1] - pts[0][1])**2)**0.5
    assert dist1 == dist2 ==dist3 == dist4
    return {
        "image": lichess_img_array,
        "min_x": min_x,
        "max_x": max_x,
        "min_y": min_y,
        "max_y": max_y,
        "dist": dist1
    }

def random_move(board: chess.Board) -> chess.Move:
    return random.choice(list(board.legal_moves))

def square_to_coords(square: int) -> str:
    file = chess.square_file(square)
    rank = chess.square_rank(square)
    return f"{chr(file + ord('a'))}{rank + 1}"

def convert_svg_to_png_array(svg_img_path: str, size: int):
    board_png_bytes = cairosvg.svg2png(
    url=svg_img_path,
    output_width=size,
    output_height= size
    )
    board_img = Image.open(io.BytesIO(board_png_bytes))
    board_img_array = np.array(board_img)
    return board_img_array

def overlay_board_on_background(board_img_array: np.ndarray, background_img_array: np.ndarray, min_x: int, max_x: int, min_y: int, max_y: int) -> np.ndarray:
    overlay_img = background_img_array.copy()
    overlay_img[min_y:max_y, min_x:max_x] = board_img_array
    return overlay_img

def get_coord_from_square(square: str, board_size:int) -> int:
    multiples = np.array([1,3,5,7,9,11,13,15])
    square_size = board_size / 8
    coord_dict = {"a":0,"b":1,'c':2,'d':3,'e':4,'f':5,'g':6,'h':7}
    letter = square[0]
    num = 8 - int(square[1])
    coordinate = np.array((square_size*multiples[coord_dict[letter]]/2, square_size*multiples[num]/2)).astype(int)
    return coordinate

def play_and_save_images(dataset_dir: str, moves_per_game: int, game_idx: int, normalize: bool = False):
    game_dir = os.path.join(dataset_dir, f"game_{game_idx}")
    os.makedirs(game_dir, exist_ok=True)
    board = chess.Board()
    move_data = []
    background_img_dict = get_vm_background_image_dict("/Users/sashanktirumala/Desktop/chess_vm.png")
    for m in range(moves_per_game):
        if board.is_game_over():
            break
        move = random_move(board)
        board.push(move)
        img_svg_name = f"move_{m}.svg"
        svg = chess.svg.board(board, colors={'square light': '#f0d9b5', 'square dark': '#b58863'}, coordinates=False)
        with open(os.path.join(game_dir, img_svg_name), "w") as f:
            f.write(svg)
        board_img_array = convert_svg_to_png_array(os.path.join(game_dir, img_svg_name), background_img_dict["dist"])
        overlaid_img = overlay_board_on_background(
            board_img_array,
            background_img_dict["image"],
            background_img_dict["min_x"],
            background_img_dict["max_x"],
            background_img_dict["min_y"],
            background_img_dict["max_y"]
        )
        height, width, _ = overlaid_img.shape
        img_png_name = f"move_{m}.png"
        with open(os.path.join(game_dir, img_png_name), "wb") as f:
            Image.fromarray(overlaid_img).save(f, format='PNG')
        os.remove(os.path.join(game_dir, img_svg_name))
        from_square = square_to_coords(move.from_square)
        to_square = square_to_coords(move.to_square)
        from_coords = get_coord_from_square(from_square, background_img_dict["dist"]) + np.array([background_img_dict["min_x"], background_img_dict["min_y"]])
        to_coords = get_coord_from_square(to_square, background_img_dict["dist"]) + np.array([background_img_dict["min_x"], background_img_dict["min_y"]])
        if normalize:
            from_coords = np.array([from_coords[0]*1000 / height, from_coords[1]*1000 / width]).astype(int)
            to_coords = np.array([to_coords[0]*1000 / height, to_coords[1]*1000 / width]).astype(int)
        move_record = {
            "move_number": m,
            "uci": move.uci(),
            "from_square": square_to_coords(move.from_square),
            "to_square": square_to_coords(move.to_square),
            "from_coords": from_coords.tolist(),
            "to_coords": to_coords.tolist(),
            "image": img_png_name
        }
        move_data.append(move_record)
    with open(os.path.join(game_dir, "moves.json"), "w") as f:
        json.dump(move_data, f, indent=2)

# Usage
play_and_save_images(dataset_dir="/Users/sashanktirumala/projects/data/test_dataset3", moves_per_game=40, game_idx=0, normalize=True)

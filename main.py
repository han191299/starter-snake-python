# Welcome to
# __________         __    __  .__                               __
# \______   \_____ _/  |__/  |_|  |   ____   ______ ____ _____  |  | __ ____
#  |    |  _/\__  \\   __\   __\  | _/ __ \ /  ___//    \\__  \ |  |/ // __ \
#  |    |   \ / __ \|  |  |  | |  |_\  ___/ \___ \|   |  \/ __ \|    <\  ___/
#  |________/(______/__|  |__| |____/\_____>______>___|__(______/__|__\\_____>
#
# This file can be a nice home for your Battlesnake logic and helper functions.
#
# To get you started we've included code to prevent your Battlesnake from moving backwards.
# For more info see docs.battlesnake.com

import random
import typing
import sys
from operator import itemgetter
import copy


# info is called when you create your Battlesnake on play.battlesnake.com
# and controls your Battlesnake's appearance
# TIP: If you open your Battlesnake URL in a browser you should see this data
def info() -> typing.Dict:
  print("INFO")

  return {
    "apiversion": "1",
    "author": "Mega Five",  # TODO: Your Battlesnake Username
    "color": "#00ff66",  # TODO: Choose color
    "head": "bonhomme",  # TODO: Choose head
    "tail": "coffee",  # TODO: Choose tail
  }


# start is called when your Battlesnake begins a game
def start(game_state: typing.Dict):
  print("GAME START")


# end is called when your Battlesnake finishes a game
def end(game_state: typing.Dict):
  print("GAME OVER\n")


def get_manhattan_dist(obj1, obj2):
  diff_x = abs(obj1["x"] - obj2["x"])
  diff_y = abs(obj1["y"] - obj2["y"])
  manhattan_dist = diff_x + diff_y
  return manhattan_dist


#VVVVV get_safe_moves is used in move(). also might be useful to use in get_heuristic_value once minimax is complete VVVVV
def get_safe_moves(game_state, snake):
  is_move_safe = {"up": True, "down": True, "left": True, "right": True}

  body = snake["body"]  # array of body
  head = body[0]  # Coordinates of head
  health = snake["health"]  # health of snake
  #VVV other important coordinates in relation to head VVV
  right_of_head = {"x": head["x"] + 1, "y": head["y"]}
  left_of_head = {"x": head["x"] - 1, "y": head["y"]}
  above_head = {"x": head["x"], "y": head["y"] + 1}
  below_head = {"x": head["x"], "y": head["y"] - 1}

  # TODO: Step 1 - Prevent your Battlesnake from moving out of bounds
  board_width = game_state['board']['width']
  board_height = game_state['board']['height']
  if head["x"] == 0:
    is_move_safe["left"] = False
  if head["x"] == board_width - 1:
    is_move_safe["right"] = False
  if head["y"] == board_height - 1:
    is_move_safe["up"] = False
  if head["y"] == 0:
    is_move_safe["down"] = False

  # TODO: Step 2 - Prevent your Battlesnake from colliding with itself
  # TODO: Step 3 - Prevent your Battlesnake from colliding with other Battlesnakes
  opponents = game_state['board']['snakes']
  for opponent in opponents:
    if left_of_head in opponent["body"][:-1]:
      is_move_safe["left"] = False
    if right_of_head in opponent["body"][:-1]:
      is_move_safe["right"] = False
    if above_head in opponent["body"][:-1]:
      is_move_safe["up"] = False
    if below_head in opponent["body"][:-1]:
      is_move_safe["down"] = False

  #if health is 1, any move will result in death if there is no food on the square

  food = game_state["board"]["food"]
  if health == 1:
    if left_of_head not in food:
      is_move_safe["left"] = False
    if right_of_head not in food:
      is_move_safe["right"] = False
    if above_head not in food:
      is_move_safe["up"] = False
    if below_head not in food:
      is_move_safe["down"] = False

  # Are there any safe moves left?
  safe_moves = []
  for move, isSafe in is_move_safe.items():
    if isSafe:
      safe_moves.append(move)
  return safe_moves


#VVVV 2 things required to complete minimax VVVV
def is_snake_index_you(game_state, snake_index):
  snakes = game_state["board"]["snakes"]
  if snakes[snake_index]["id"] == game_state["you"]["id"]:
    return True
  return False


#VVVVV get_heuristic_value is not complete. will fine tune once minimax is done VVVVV
def get_your_snake_index(game_state):
  for x in range(len(game_state["board"]["snakes"])):
    if is_snake_index_you(game_state, x):
      return x


def get_enemy_snake_index(game_state):
  for x in range(len(game_state["board"]["snakes"])):
    if not is_snake_index_you(game_state, x):
      return x


def get_heuristic(game_state):

  you = game_state["you"]
  enemy = game_state["board"]["snakes"][get_enemy_snake_index(game_state)]
  health = you["health"]
  length = you["length"]

  dist_from_enemy = get_manhattan_dist(you["head"], enemy["head"])

  safety_val = 0
  if dist_from_enemy <= 5:
    if length < enemy["length"]:
      safety_val = -1
    elif length > enemy["length"]:
      safety_val = 1

  closest_food = None
  closest_food_dist = 9999
  if len(game_state["board"]["food"]) > 0:
    for piece_food in game_state["board"]["food"]:
      distance = get_manhattan_dist(you["head"], piece_food)
      if distance < closest_food_dist:
        closest_food = piece_food
        closest_food_dist = distance


  food_dist_weight = -2
  health_weight = 4
  length_weight = 1
  safety_weight = 20

  heuristic_value = health_weight * health + length_weight * length + safety_weight * safety_val + food_dist_weight * closest_food_dist

  return heuristic_value


def updateFood(food, eaten_food):
  food.remove(eaten_food)
  return food


def updateSnake(snake, food, move):
  move_index_x = {"up": 0, "down": 0, "left": -1, "right": 1}
  move_index_y = {"up": 1, "down": -1, "left": 0, "right": 0}
  future_head = {
    "x": snake["head"]["x"] + move_index_x[move],
    "y": snake["head"]["y"] + move_index_y[move]
  }
  if future_head in food:
    snake["health"] = 100
    snake["length"] = snake["length"] + 1
    food = updateFood(food, future_head)
  else:
    snake["health"] = snake["health"] - 1

  snake["body"].insert(0, future_head)
  snake["head"] = future_head
  if len(snake["body"]) == snake["length"]:
    snake["body"].pop()

  return snake, food


def updateBoard(game_state, move, maximizingPlayer):
  board = game_state["board"]
  snakes = board["snakes"]
  food = board["food"]
  snake_index = None
  #determine which snake is moving
  if maximizingPlayer:
    snake_index = get_your_snake_index(game_state)
  else:
    snake_index = get_enemy_snake_index(game_state)

  snakes[snake_index], food = updateSnake(snakes[snake_index], food, move)
  board["snakes"] = snakes
  board["food"] = food

  return board


def simulateGameState(game_state, move, maximizingPlayer):
  #change the board given move
  game_state["board"] = updateBoard(game_state, move, maximizingPlayer)
  #change "you"
  snake_index = get_your_snake_index(game_state)
  game_state["you"] = game_state["board"]["snakes"][snake_index]
  return game_state


def minimax(game_state, depth, maximizingPlayer):

  safe_moves = []
  snake_index = None
  #check if depth is maxed
  if depth == 0:
    return get_heuristic(
      game_state)  #NEED TO DO heuristic still needs to be implemented

  if maximizingPlayer:
    #get safe moves for max player (you)
    safe_moves = get_safe_moves(game_state, game_state["you"])
    #check if game_state is terminal (snake dies due to no safe moves) -infinity
    if len(safe_moves) == 0:
      #print(depth*"  ", "max terminating node")
      return -9999999
    print("  " * depth, "max's safe moves:", safe_moves)

    value = -sys.maxsize - 1
    bestMove = None
    for move_choice in safe_moves:
      #set newState to an updated version of game_state based on maximizingPlayer move
      #print("  " * depth, snake_index, "before max player moves", move_choice, "|", game_state["board"]["snakes"][snake_index]["body"])
      newState = copy.deepcopy(game_state)
      newState = simulateGameState(newState, move_choice, True)
      #print("  " * depth, snake_index, "after max player moves", move_choice, "|", newState["board"]["snakes"][snake_index]["body"])
      possibleTuple = minimax(newState, depth - 1, False)
      if type(possibleTuple) is tuple:
        value, bestMove = max([(value, bestMove), (possibleTuple[0], move_choice)], key=itemgetter(0))
      else:
        value, bestMove = max([(value, bestMove), (possibleTuple, move_choice)], key=itemgetter(0))
    print("  " * depth, "max move out of", safe_moves, "is", bestMove, "with value", value)
    return (value, bestMove)
  else:
    #get enemy snake index
    snake_index = get_enemy_snake_index(game_state)
    #get_safe_moves for min player (enemy)
    if snake_index != None:
      safe_moves = get_safe_moves(game_state, game_state["board"]["snakes"][snake_index])
    #check if game_state is terminal (snake dies due to no safe moves) return infinity
    if len(safe_moves) == 0:
      #print(depth* "  ", "min terminating node")
      return 9999999
    print("  " * depth, "min's safe moves:", safe_moves)

    value = sys.maxsize
    bestMove = None
    for move_choice in safe_moves:
      #set newState to an updated version of game_state based on minimizingPlayer move
      #print("  " * depth, snake_index, "before min player moves", move_choice, "|", game_state["board"]["snakes"][snake_index]["body"])
      newState = copy.deepcopy(game_state)
      newState = simulateGameState(newState, move_choice, False)
      #print("  " * depth, snake_index, "after min player moves", move_choice, "|", newState["board"]["snakes"][snake_index]["body"])
      possibleTuple = minimax(newState, depth - 1, True)
      if type(possibleTuple) is tuple:
        value, bestMove = min([(value, bestMove),
                               (possibleTuple[0], move_choice)],
                              key=itemgetter(0))
      else:
        value, bestMove = min([(value, bestMove),
                               (possibleTuple, move_choice)],
                              key=itemgetter(0))
    print("  " * depth, "min move out of", safe_moves, "is", bestMove, "with value", value)
    return (value, bestMove)


# move is called on every turn and returns your next move
# Valid moves are "up", "down", "left", or "right"
# See https://docs.battlesnake.com/api/example-move for available data
def move(game_state: typing.Dict) -> typing.Dict:
  heuristic_value, next_move = minimax(game_state, 5, True)
  print(f"MOVE {game_state['turn']}: {next_move}")
  return {"move": next_move}


# Start server when `python main.py` is run
if __name__ == "__main__":
  from server import run_server
  port = "8000"
  for i in range(len(sys.argv) - 1):
    if sys.argv[i] == '--port':
      port = sys.argv[i + 1]

  run_server({
    "info": info,
    "start": start,
    "move": move,
    "end": end,
    "port": port
  })

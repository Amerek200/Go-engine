#Go engine, should be able to:
#place stones on the board
#only allow legal moves
#remove captured stones 
#keep track of point/captured stones
#Logging / histroy of the different moves
#maybe support different board sizes
#Groundwork to use for GUI / pygame / CLI
#maybe work with @property decorator
#https://www.freecodecamp.org/news/python-property-decorator/

#notation: corrdinates from (1, 1) to (19, 19) where (column, row) starting 
#with top left being (1, 1)

#Classes: 
#Board, 
#attribute board = 19x19grid
#method state returning current board and points
#method history returning list of tuples corresponding to the moves -> allows method like go_back or go_to_move
#method place(color, position)

#Stone?
#each stone is a seperate object name = move number 
#attibute: black/white
#maybe stone attributes = id/move , position_tuple, color.
#maybe give each stone a board group to remember / add other stones faster?
#this would also greatly increase the space needed compared to storing groups 
#in the board object.  

#Engine
#iterate between turn black and turn white
#https://nedbatchelder.com/blog/201112/keep_data_out_of_your_variable_names.html
#do not name the objects by name but instead make a list of of moves and append a stone object for every move,
#still letting me access every move via move[nr]
#stop iteratring when both players pass   

import os
from itertools import product
import pytest


class Engine():
  def __init__(self, board_size):
    #moves = list of stone objects
    self.moves = []
    self.board = [[None for x in range(board_size)] for x in range(board_size)]
    self.board_size = board_size
    #19x19 list of None, filled with stone objects/move reference to object

  def play(self):
    i = 0 #start moves at 0
    while not (moves[-1].passed and moves[-2].passed):
      try: 
        color = next(moves[i-1])  
      except IndexError: #if i-1 does not exist (start of the game) set color to black/true
        color = True 
      moves[i] = Stone(color, i)
      
      while moves[i].coords == ():
        pos = input(f"Move Nr.: {i + 1}, enter as x,y (without space)")
        x, y = pos
        try: 
          moves[i].coords = ((x, y), self.board)
          self.board[x][y] = i
        except placementException:
          print("Already a stone in place")
        
      #now solve placement, check for each neighbor if same color or not,
      #update group if same, check liberties if not.
      solve_placement(moves[i])


      i += 1 
      

  def solve_placement(self, stone):
    """
    Iterates over neighbors of given stone and either updates group attribute or checks if group is dead.
    """
    neighbors = stone.get_neighbors(self.board_size)
    color = stone.black
    for n in neighbors:
      n_id = self.board[n[0]][n[1]]
      #could you if (if None oder if isstance) or try-except to 
      if n_id == None:
        continue
      n_obj = self.moves[n_id]
      if n_obj.black == color:
        self.update_group(stone, n_obj)
      else: #must me opposite color
         if self.check_liberties(n_obj) == False:
           self.delete(n_obj)

  def check_liberties(self, stone):
    #get list of possible liberties, then check if at least one is emtpy.
    to_check = self.get_group_borders(stone)
    for coords in to_check:
      x, y = coords
      if self.board[x][y] == None:
        #emtpy point found
        return True
    #no emtpy neighboring point found -> return False
    return False

  def update_group(self, new_stone, old_stone):
    #unite sets = adds new stone to group without creating dublicates
    new_stone.group.update(old_stone.group)
    for s_id in new_stone.group:
      self.moves[s_id].group.update(new_stone.group)

  def delete(self, stone):
    """
    sets captured = True for every stone in the group and clears them from .board.
    """
    for s_id in stone.group:
      s_obj = self.moves[s_id]
      s_obj.captured = True
      x, y = s_obj.coords
      self.board[x][y] = None 

  def check_placement(self):
    pass

  def print_board(self):
    pass

  #due to calling get_neighbor of different stones this has to be a method of Engine() and not Stone()
  def get_group_borders(self, stone): 
    """
    Returns set containing possible liberties (coords) of the group.
    """
    #set does automaically ignore the addition of dublicates, yay
    border = set()
    
    for s_id in stone.group:
      s_obj = self.moves[s_id]
      x, y = s_obj.coords
      neighbors = s_obj.get_neighbors(self.board_size)
      border.update(neighbors)

    return border

class placementException(Exception):
  pass
       

class Stone():
  def __init__(self, color, id):
    #black = Flase == white
    self.black = color
    #id = move number
    self.id = id
    #set of id's belonging to a group, set makes update easier
    self.group = {id, }
    self.captured = False
    #decorate coords with @property for getter and setter?
    self._coords = tuple()
    self.passed = False

  def get_neighbors(self, board_size):
    """
    Returns neighboring coordinates.
    """
    x, y = self.coords
    #for generating neighor coords product (like I used for the chess think) doest not make sense, can't think of a better way then hard-coding it.
    adja = [(x-1, y), (x+1, y), (x, y-1), (x, y+1)]
    #maybe I can use all() instead of the double comparison?
    return [pos for pos in adja if (0 <= pos[0] < board_size) and (0 <= pos[1] < board_size)]
    

  @property # this is the getter
  def coords(self):
    return self._coords

  #setters can only accepts one argument arg_tuple = (coord_tuple, board)
  @coords.setter 
  def coords(self, arg_tuple): 
    """
    Tests if a stone can be placed, return exception if not.
    
    """
    coord, board = arg_tuple
    x, y = coord
    try:
      if board[x][y] != None:
        raise placementException
      else:
        self._coords = (x, y)
        return True
    except IndexError: #x or y is out of board range -> coord does not exist
      raise placementException

  #makes object iterable, allowing me to use next(stone) to get T/F for next stone
  def __next__(self):
    if self.black:
      return False
    else:
      return True




  #def check_liberty(self): #does not work as method of Stone since I need to get the other Stone objects.
  #  """
  #  Gets called when checking the neighbors of a just placed stone in when neighbor = #opponent.
  #  Checks for the group the stone belongs to if there is at least one liberty.
  #  Returns true as soon as liberty if found.
  #  """
  
#class Board():
#  def __init__(self, size):
#    self.board = [[None for x in range(size)] for x in range(size)]
#
#  def check_liberty(self, coords):
#    """
#    Checks for given coords if the stone / group has at least one liberty left.
#    Returns True/False.
#    """
#    for stone_id in self.group:
#    
#      adjacent = stone_id.get_neighbors()
#      for neighbor in adjacent:
#        x, y = neighbor
#        if self.board[x][y] == None:
#        #emtpy field = liberty found!
#          return True
#    #no emtpy adjacent point found while iterating over groups neighbors
#    return False#
#
#    pass
  

#e = Engine()
#how to iterate over game:
#beginning color = black
#color = True
#for i in range(5):
#  e.moves.append(Stone(color, i, e.board))
#  color = next(e.moves[i])
#  print(e.moves[i].black)
#  print(e.moves[i].id)
#  pos = input(f"Move Nr.: {i}, enter as x,y (without space)")
#  pos = pos.split(",")

#  try:
#    e.moves[i].coords = (int(pos[0]), int(pos[1]))
#    e.board[int(pos[0])][int(pos[1])] = i
#  except placementException:
#    print("it worked")
#    break
    
  

  #print(type(e.moves[i].coords))

if __name__ == "__main__":
  os.system("pytest")
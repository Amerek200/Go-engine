#TODO: end game, let user input coords of dead stones -> remove group
#TODO: counting after dead stones are removed
#TODO: implements inputs in a way that allows/recognizes different players
#TODO: (maybe) clean up play() method -> source things out. goutils = input check, get neighbors etc.
#DONE: fix while at the beginning, IndexError
#DONE: add input checker that only accepts coord tuple & pass

import os
import pytest
from helpers import *

class Engine():
    def __init__(self, board_size):

        #moves = list of stone objects
        self.moves = []
        self.board = [[None for x in range(board_size)] for x in range(board_size)]
        self.board_size = board_size

    def both_passed(self, current):


        """
        Returns true if last two moves are "pass". Does not raise exception for first two moves. (ValueError)
        """
        if current <= 1:
            return False
        else:
            return self.moves[current-1].passed and self.moves[current-2].passed


    def play(self):


        i = 0 #start moves at 0
        while not self.both_passed(i):

            if i > 0:
                color = next(self.moves[i-1])
            else:
               #if i-1 is out of range (start of the game) set color to black/true
                color = True

            #tried using self.moves[i] = Stone(color, i) returns IndexError as it does not exist.
            self.moves.append(Stone(color, i))
            while self.moves[i].coords == ():
                pos = input(f"Move Nr.: {i + 1}, enter as x,y (without space) or pass. ")
                pos = process_input(pos) #returns either False or correct formated tuple or "pass" -> problem with pass & validate_scope
                if not pos or not validate_scope(pos, self.board_size):
                    print("wrong input")
                    continue

                try:
                    self.moves[i].coords = (pos, self.board)
                    if not self.moves[i].passed:
                        x, y = pos
                        self.board[x][y] = i
                except placementException:
                    print("Already a stone in place")
                    continue
            self.solve_placement(self.moves[i])
            i += 1
            self.print_board()

        #both players passed, counting and removing
        remove = None
        remove_ls = []
        while remove != "pass":
            remove = input("Select dead groups by entering a single coordinate per group. \n Enter pass if you want to continue to counting. ")
            remove = process_input(remove)
            if not remove or not validate_scope(pos, self.board_size):
                print("wrong input")
                continue
            remove_ls.append(remove)

        #trigger delete (requires stone object as argument)
        for coord in remove_ls:
            if coord == "pass":
                continue
            x, y = coord
            rm_id = self.board[x][y]
            self.delete(self.moves[rm_id])



    def solve_placement(self, stone):
        """
        Iterates over neighbors of given stone and either updates group attribute or checks if group is dead.
        """
        if stone.passed:
            return

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

    def print_board(self):
        for i in range(self.board_size):
            self.print_row(i)
            if i < self.board_size - 1:
                print(" |   " * self.board_size)


    def print_row(self, i):
        """
        prints row i
        """
        row = [column[i] for column in self.board]
        for i in range(len(row)):
            if row[i] != None:
                row[i] = self.moves[row[i]].black
        row = [convert_for_printing(x) for x in row]
        print("--".join(row))

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

    def count(self):
        """
        Counts territory for each players after all dead stones are removed.
        """
        #plan: create Stone of color None, update group, get group borders, if every stone in border is of the same color its points.
        pass

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
        return [pos for pos in adja if validate_scope(pos, board_size)]

    @property
    def coords(self):
        return self._coords

    #setters can only accepts one argument arg_tuple = (coord_tuple, board)
    @coords.setter
    def coords(self, arg_tuple):
        """
        Tests if a stone can be placed, return exception if not.
        Accepts either coord tuple or "pass".
        """
        coord, board = arg_tuple
        #even when passed coords have to be set to escape "input while" loop
        if coord == "pass":
            self._coords = (None, None)
            self.passed = True
            return True
        x, y = coord

        if board[x][y] != None:
            raise placementException
        else:
            self._coords = (x, y)
            return True


  #makes object iterable, allowing me to use next(stone) to get T/F for next stone
    def __next__(self):
        if self.black:
            return False
        else:
            return True





e = Engine(4)
e.play()
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

  #print(type(e.moves[i].coords))

#if __name__ == "__main__":
#  os.system("pytest")

#Board representation in command line:
#   -- B --  --   --   --   --   --
# |    |    |   |    |    |    |    |
# W -- B --  --   --   --   --   --
# |    |    |    |    |    |    |   |
# etc.
#use:
# '{:^30}'.format('centered')
#'           centered           ' ? from: https://docs.python.org/2/library/string.html

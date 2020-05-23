#TODO: (maybe) create something like a field class to further seperate code and maybe
#fixes having to go from coodinate tuples to board[x][y] to moves[id] in three steps
#TODO: Fix remove, should get own method and work with confirming of both player and removing -> display -> query again.
#TODO: implements inputs in a way that allows/recognizes different players
#TODO: clean up play() method ->
#source things out. helpers = input check, print board moved

#DONE: get_group_borders() returns coords or stones of the group, not just borders!!! (breaks counting, could just ignone None but,,,)
#DONE: fix while at the beginning, IndexError
#DONE: add input checker that only accepts coord tuple & pass
#DONE: end game, let user input coords of dead stones -> remove group
#DONE: counting after dead stones are removed

import os
import pytest
from helpers import *

class Engine():
    def __init__(self, board_size):

        #moves = list of stone objects
        self.moves = []
        self.board = [[None for x in range(board_size)] for x in range(board_size)]
        self.board_size = board_size
        self.points = {"black": 0, "white": 0}

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
            self.moves.append(Stone(color, i))
            while self.moves[i].coords == ():
                self.place_stone(i, color)
            self.solve_placement(self.moves[i])
            i += 1
            print_board(self.board_size, self.board, self.moves)
        #both players passed, counting and removing, move to seperate method some time
        remove = None
        remove_ls = []
        while remove != "pass":
            remove = input("Select dead groups by entering a single coordinate per group. \n Enter pass if you want to continue to counting. ")
            remove = process_input(remove)
            if not remove or not validate_scope(remove, self.board_size):
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

        self.count()
        print("Final Score:")
        for co, points in self.points.items():
            print(f"{co}: {points}")

    def place_stone(self, i, color):
        if color:
            player = "Black"
        else:
            player = "White"
        pos = input(f"Move Nr.: {i + 1}, enter x,y (without space) or pass. {player}: ")
        pos = process_input(pos) #returns either False or correct formated tuple or "pass" -> problem with pass & validate_scope
        if not pos or not validate_scope(pos, self.board_size):
            print("wrong input")
            return
        try:
            self.moves[i].coords = (pos, self.board)
            if not self.moves[i].passed:
                x, y = pos
                self.board[x][y] = i
        except placementException:
            print("Already a stone in place")
            return

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
            if n_id == None:
                continue
            n_obj = self.moves[n_id]
            if n_obj.black == color:
                self.update_group(stone, n_obj)
            #allows me to use solve_placement() in count because deletion of groups/liberty check wont occur
            elif color == None:
                continue
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

      #due to calling get_neighbor of different stones this has to be a method of Engine() and not Stone()
    def get_group_borders(self, stone):
        """
        Returns set containing possible liberties (coords) of the group.
        """
        #set does automaically ignore the addition of dublicates, yay
        border = set()
        #add set of the coords OF THE group to remove /not add to border set. (would break counting)
        group_coords = set()
        for s_id in stone.group:
          s_obj = self.moves[s_id]
          x, y = s_obj.coords
          group_coords.add((x, y))
          neighbors = s_obj.get_neighbors(self.board_size)
          border.update(neighbors)
        #return border - group_coords
        #difference_update =  Remove the items that exist in both sets
        border.difference_update(group_coords)
        return border

    def count(self):
        """
        Counts territory for each players after all dead stones are removed.
        """
        #plan: create Stone of color None & update group
        self.fill_points()
        #get a list of all None color groups on the board
        groups = self.get_none_groups()
        #check for each group if every stone in border is of the same color => points.
        self.evaluate_none_groups(groups)
        self.count_captures()

    def fill_points(self):
        """
        Fills every emtpy point with a Stone object of black = None. (updates group without liberty check)
        """
        i = len(self.moves)

        #populate emtpy points on the board with Stones of color = None
        for x in range(self.board_size):
            for y in range(self.board_size):
                if self.board[x][y] == None:
                    self.moves.append(Stone(None, i))
                    self.moves[i].coords = ((x,y), self.board)
                    self.board[x][y] = i
                    self.solve_placement(self.moves[i])
                    i += 1

    def get_none_groups(self):
        """
        Returns list of None-colored group sets for counting.
        """
        #to create a set of sets the inner set must be set to frozenset() -> immutable
        groups = []
        for x in range(self.board_size):
            for y in range(self.board_size):
                id = self.board[x][y]
                obj = self.moves[id]
                if obj.black == None and obj.group not in groups:
                    groups.append(obj.group)
        return groups

    def evaluate_none_groups(self, groups):
        """
        Checks for each group if it is completely surrounded by just one color.
        Adds points if thats the case.
        """
        for group in groups:
            #set does not support indexing -> cast into list would be wastefull I think,
            #creating an iterator and getting the first it is. (or itertools, islice() (stackowerflow))
            id = next(iter(group))
            border = self.get_group_borders(self.moves[id])
            border_color = []
            for coord in border:
                x, y = coord
                id = self.board[x][y]
                border_color.append(self.moves[id].black)
            #check if every border stone is of the same color:
            if border_color.count(border_color[0]) == len(border_color):
                #color that gets the points:
                color = border_color[0]
                if color:
                    self.points["black"] += len(group)
                else:
                    self.points["white"] += len(group)

    def count_captures(self):
        for move in self.moves:
            if move.captured == True:
                if move.black == True:
                    self.points["white"] += 1
                else:
                    self.points["black"] += 1


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
        #better way then hard coding? Couldnt think of one rn.
        adja = [(x-1, y), (x+1, y), (x, y-1), (x, y+1)]
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

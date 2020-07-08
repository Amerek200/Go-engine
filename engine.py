#TODO TLDR: Clean a lot of stuff up, move to helpers etc.
#TODO: (maybe) move app or command line version to subclass.
#TODO: Clean up the multiple moves lists I work with within app and engine.app_updater. basically one should be all that's needed.
#TODO: remove next? len(moves) is used anyways for len(moves) < 1/2
#DONE: ko-checker
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
        self.changes = []
        self.current_player = True
        self.prev_board_state = [[None for x in range(board_size)] for x in range(board_size)]
        self.curr_board_state = [[None for x in range(board_size)] for x in range(board_size)]
        #flags used for communicating game state to js.
        self.removing = False
        self.end = False

    def both_passed(self):
        """
        Returns true if last two moves are "pass". Does not raise exception for first two moves. (ValueError)
        """
        if len(self.moves) <= 1:
            return False
        else:
            return self.moves[-1].passed and self.moves[-2].passed

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
        #possible dead groups of the opponent are removed, group updated.
        #Now we still need to check if the new stone/group is alive at all^^
        if color != None and not self.check_liberties(stone):
            self.delete(stone)

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
        #difference_update = Remove the items that exist in both sets, -> coords of the stones in this case.
        border.difference_update(group_coords)
        return border

    def count(self):
        """
        Counts territory for each players after all dead stones are removed.
        """
        #plan: create Stone of color None & None colored groups accordingly.
        self.fill_points()
        #get a list of all None color groups on the board
        groups = self.get_none_groups()
        #check for each group if every stone in border is of the same color => points.
        self.evaluate_none_groups(groups)
        return True

    def fill_points(self):
        """
        Fills every emtpy point with a Stone object of black = None. (updates group without liberty check)
        """
        i = len(self.moves)
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

    def app_updater(self, moves, new_move):
        """
        Gets called from flask with past moves and a proposed move.
        Returns False if move is invalid, True if move is valid.
        Changes to make on the board are saved in self.changes. (last 3 changes actually)
        """
        #use copy or full slice, otherwise temp_moves was also just a reference.. dumb me.
        # -> prevents addition of an invalid move to session[moves].
        temp_moves = moves.copy()
        temp_moves.append(new_move)

        if not self.app_read_moves(temp_moves):
            #move not valid, blocked or KO
            return False
        else:
            #move is valid, can be added to moves and therefore session["moves"] from the App.
            moves.append(new_move)
            self.count_captures()
            #why not use next(self.moves[-1]) ?
            self.current_player = len(self.moves) % 2 == 0
            return True

    def app_read_moves(self, moves):
        """
        Reads lists of coords into the engine, returns false if an error or Ko arises.
        Also sets board_state and changes for the app to use.
        """
        i = 0
        for move in moves:
            #"cuts" length of self.changes down to two, adding this one makes three, all we need for Ko-check.
            #can be made bigger to add "rewind" function.
            clean_changes(self.changes, 2)
            self.prev_board_state = self.convert_board()
            if i > 0:
                color = next(self.moves[-1])
            else: # i = 0, blacks turn
                color = True
            self.moves.append(Stone(color, i))

            try:
                self.moves[i].coords = (moves[i], self.board)
            except placementException:
                return False

            if self.both_passed():
                self.removing = True
                rest = moves[i+1:] #emtpy array if pass is current move.
                return self.app_remove(rest)

            if not self.moves[i].passed:
                x, y = moves[i]
                self.board[x][y] = i

            self.solve_placement(self.moves[i])
            #get / convert chages for Ko-check and frontend to use/update.
            self.curr_board_state = self.convert_board()
            self.changes.append(get_board_differences(self.prev_board_state, self.curr_board_state))
            if self.ko_check(color):
                return False
            i += 1
        return True


    def app_remove(self, rm_moves):
        """
        As part of app_read_moves, handles the input of dead groups after both players have passed.
        Removes entire group for the stone selected and creates new board state.
        """
        for coord in rm_moves:
            if coord == "pass":
                #set flag for .js / flask.
                self.end = True
                #SOLVE PLACEMENT IS DELETING MY NONE GROUPS CAUSE THEY RUN OUT OF LIBERTIES, dumbo.
                self.count()
                return True

            x, y = coord
            rm_id = self.board[x][y]
            if rm_id == None:
                #no stone at given/clicked coords, return false, no changes.
                return False
            else:
                self.delete(self.moves[rm_id])
        #create now board state after deleting stones.
        self.curr_board_state = self.convert_board()
        self.changes.append(get_board_differences(self.prev_board_state, self.curr_board_state))
        return True

    #feels like there is a smarter way, comparing board state from two rounds ago with currently proposed state is
    #a possibility but appears to me a bit more "wastefull" because I have to store three entire board states compared
    #with a list of changes from the last three moves
    def ko_check(self, color):
        """
        Checks if a played move recreates the last board position -> KO.
        Returns true if KO / move is invalid.
        """
        if len(self.changes) <= 2:
            #not enough moves into the game
            return False
        #if you desperatly want to avoid writing len(self.changes[1/2] == 2) two times: ^^
        elif all([len(self.changes[i]) == 2 for i in range(1,3)]):
            #check the rest of KO exists
            for change in self.changes[2]:
                x, y, c = change
                if c != None:
                    if change not in self.changes[0]:
                        #the placed stone is the same position/color as two moves before.
                        return False
                    elif (x, y, None) not in self.changes[1]:
                        #stone must have been removed in between move 0 and 2, just a sanity check I guess and not that needed.
                        return False
                else:
                    #c == None, check if placed at previous change
                    if (x, y, not color) not in self.changes[1]:
                        return False
            return True
        else:
            return False


    def convert_board(self):
        """
        Converts engine board list (filled with move ID's) to list of T/F/None.
        """
        board = [[None for x in range(self.board_size)] for x in range(self.board_size)]
        for x in range(self.board_size):
            for y in range(self.board_size):
                if self.board[x][y] == None:
                    continue
                else:
                    stone_id = self.board[x][y]
                    stone_obj = self.moves[stone_id]
                    color = stone_obj.black
                    board[x][y] = color
        return board

#used for Stone.coord setting, just because I want to have a custom exception.
class placementException(Exception):
  pass

class Stone():

    def __init__(self, color, id):
        #Black = True, white = False
        self.black = color
        #id = move number
        self.id = id
        #set of id's belonging to a group, set makes update easier
        self.group = {id, }
        self.captured = False
        self._coords = tuple()
        self.passed = False


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

    def get_neighbors(self, board_size):
        """
        Returns neighboring coordinates.
        """
        x, y = self.coords
        #better way then hard coding? Couldnt think of one rn.
        adja = [(x-1, y), (x+1, y), (x, y-1), (x, y+1)]
        return [pos for pos in adja if validate_scope(pos, board_size)]

    #makes object iterable, allowing me to use next(stone) to get T/F for next stone
    def __next__(self):
        if self.black:
            return False
        else:
            return True

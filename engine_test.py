import pytest
from main import *

e = Engine(9)

#creates first 10 stones, (indicies 0-9 incl, 0=black, 1=white)
for i in range(0, 20, 2):
  e.moves.append(Stone(True, i))
  e.moves.append(Stone(False, i+1))

#setting up some stones
e.moves[0].coords = ((0, 0), e.board)
e.board[0][0] = 0 #black
e.solve_placement(e.moves[0])
e.moves[1].coords = ((1, 0), e.board)
e.board[1][0] = 1 #white
e.solve_placement(e.moves[1])
e.moves[2].coords = ((1, 1), e.board)
e.board[1][1] = 2 #black
e.solve_placement(e.moves[2])
e.moves[3].coords = ((1, 5), e.board)
e.board[1][5] = 3 #white
e.solve_placement(e.moves[3])
e.moves[4].coords = ((0, 2), e.board)
e.board[0][2] = 4 #black
e.solve_placement(e.moves[4])
e.moves[5].coords = ((0, 1), e.board)
e.board[0][1] = 5 #white
e.solve_placement(e.moves[5])
e.moves[6].coords = ((0, 5), e.board)
e.board[0][5] = 6 #black
e.solve_placement(e.moves[6])
e.moves[7].coords = ((2, 5), e.board)
e.board[2][5] = 7 #white
e.solve_placement(e.moves[7]) 
e.moves[8].coords = ((1, 4), e.board)
e.board[1][4] = 8 #black
e.solve_placement(e.moves[8])
e.moves[9].coords = ((2, 6), e.board)
e.board[2][6] = 9 #white
e.solve_placement(e.moves[9]) 
e.moves[10].coords = ((1, 6), e.board)
e.board[1][6] = 10 #black
e.solve_placement(e.moves[10])
e.moves[11].coords = ((6, 2), e.board)
e.board[6][2] = 11 #white
e.solve_placement(e.moves[11])
e.moves[12].coords = ((0, 6), e.board)
e.board[0][6] = 12 #black
e.solve_placement(e.moves[12])
e.moves[13].coords = ((3, 5), e.board)
e.board[3][5] = 13 #white
e.solve_placement(e.moves[13]) 
e.moves[14].coords = ((0, 3), e.board)
e.board[0][3] = 14 #black
e.solve_placement(e.moves[14])
e.moves[15].coords = ((4, 6), e.board)
e.board[4][6] = 15 #white
e.solve_placement(e.moves[15])
e.moves[16].coords = ((0, 4), e.board)
e.board[0][4] = 16 #black
e.solve_placement(e.moves[16])


def test_stone():
  assert e.moves[1].group == {1}
  
def test_placement():
  with pytest.raises(placementException): #already a stone there
    e.moves[2].coords = (((1, 0), e.board))
  with pytest.raises(placementException): #coord does not exist
    e.moves[3].coords = ((200, -4), e.board)

def test_liberty_check():
  assert e.check_liberties(e.moves[1]) == True
  assert e.check_liberties(e.moves[5]) == True
  assert e.check_liberties(e.moves[0]) == False
  assert e.check_liberties(e.moves[3]) == True

def test_update_group():
  assert len(e.moves[3].group) == 4
  #check if groups are combined (connection between two groups is done in moves[16])
  for i in range(4, 17, 2):
    assert e.moves[i].group == {4, 6, 8, 10, 12, 14, 16}

def test_delete():
  assert e.moves[0].captured == True
  assert e.board[0][0] == None



#def test_placement():
#  with pytest.raises(placementException):
#    e.moves[3].coords = (0, 0)

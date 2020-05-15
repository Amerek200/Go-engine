import pytest
from main import *

e = Engine(9)
for i in range(5):
  e.moves.append(Stone(True, i, e.board))
  e.moves.append(Stone(False, i+5, e.board))

e.moves[0].coords = (0, 0)
e.moves[1].coords = (1, 0)

def test_placement():
  with pytest.raises(placementException):
    e.moves[3].coords = (0, 0)

def test_liberty_check():
  assert e.moves[0].check_liberty() == True
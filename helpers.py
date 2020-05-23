def process_input(inp):
    """
    Validates, casts and returns input as coord tuple or "pass"
    Returns false if input is != x,y or "pass".
    """
    if inp == "pass":
        return "pass"
    else:
        #try converting str into desired x,y tuple, there should be a smarter way right?
        inp = tuple(inp.split(","))
        if len(inp) == 2 and all([x.isdigit() for x in inp]):
            return tuple(map(int, inp))
    #seems like inp is something else.
    return False

def validate_scope(coords, board_size):
    """
    Input: x,y coordinate tuple.
    Returns false if coords are out of board scope.
    """
    if coords == "pass":
        return True
    x, y = coords
    return (0 <= x < board_size) and (0 <= y < board_size)

def convert_for_printing(x):
    """
    Converts True/False into a string three spaces containing B/W centered.
    """
    #check: https://docs.python.org/2/library/string.html#formatstrings
    #'{:^3}'.format("B") gets me a centered B
    if x == None:
        return "   "
    elif x == True:
        return "{:^3}".format("B")
    else:
        return "{:^3}".format("W")

def print_board(board_size, board, moves):
    for i in range(board_size):
        print_row(i, board, moves)
        if i < board_size - 1:
            print(" |   " * board_size)

def print_row(i, board, moves):
    """
    prints row i
    """
    row = [column[i] for column in board]
    for i in range(len(row)):
        if row[i] != None:
            row[i] = moves[row[i]].black
    row = [convert_for_printing(x) for x in row]
    print("--".join(row))

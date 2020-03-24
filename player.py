def play(board_ln, board_col ,numbers, ownership, player, mode):
    import random
    if mode == 0:
        ln=random.randrange(board_ln)
        col=random.randrange(board_col*2)
        i=0
        while ownership[ln][col]!=player or numbers[ln][col] and i < 200:
            ln=random.randrange(board_ln)
            col=random.randrange(board_col*2)
            i+=1
        return [ln,col]
    else:
        return random.randrange(4)
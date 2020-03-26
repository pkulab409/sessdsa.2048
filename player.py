class Player:
    def __init__(self):
        pass

    def play(self, board_ln, board_col, numbers, ownership, self_place, player, mode):
        if mode == 0:
            if random.randrange(2):
                ln = random.randrange(board_ln)
                col = random.randrange(board_col * 2)
                i = 0
                while [ln, col] == self_place[player ^ 1] or ownership[ln][col] == player or numbers[ln][col] and i < 200:
                    ln = random.randrange(board_ln)
                    col = random.randrange(board_col * 2)
                    i += 1
                return [ln, col]
            else:
                return self_place[player]
        else:
            return random.randrange(4)

import sys
import time
import math

#  defining class with its params


class Tile():

    # Goal constants
    T_NONE = 0
    T_WHITE = 1
    T_BLACK = 2

    # Piece constants
    P_NONE = 0
    P_WHITE = 1
    P_BLACK = 2

    # Outline constants
    O_NONE = 0
    O_SELECT = 1
    O_MOVED = 2

    def __init__(self, tile=0, piece=0, outline=0, row=0, col=0, fromPath=[]):
        self.tile = tile
        self.piece = piece
        self.outline = outline
        self.fromPath = fromPath
        self.row = row
        self.col = col
        self.loc = (row, col)

#   main function


class Halma():
    def initiateBoard(self):
        for row in range(16):
            for col in range(16):
                if row + col < 6 and row < 5 and col < 5:
                    elm = Tile(2, 2, 0, row, col)
                elif row + col > 24:
                    if row+col == 25 and (row == 10 and col == 15) or(row == 15 and col == 10):
                        elm = Tile(0, 0, 0, row, col)
                    else:
                        elm = Tile(1, 1, 0, row, col)
                else:
                    elm = Tile(0, 0, 0, row, col)
                self.board[row][col] = elm             

    def readBoard(self):
        for x in range(3, 19):
            target_xy = (self.lineObj[x].rstrip())
            for y, content in enumerate(target_xy):
                if content == 'B':
                    self.board[y][x-3].piece = 2
                elif content == 'W':
                    self.board[y][x-3].piece = 1
                elif content == '.':
                    self.board[y][x-3].piece = 0
            #     print(self.board[y][x-3].piece,end=" ")
            # print('\n')

    def __init__(self):
        # to get input from file
        self.filePath_in = 'input.txt'
        self.filePath_out = 'output.txt'
        #  SIZE OF THE BOARD
        self.b_size = 16
        with open(self.filePath_in, 'r') as fp:
            # start = time.time()
            self.lineObj = fp.readlines()
            # print(self.lineObj)
            #  SINGLE OR GAME
        self.game_type = self.lineObj[0].rstrip()
        #  BLACK OR WHITE
        self.player = self.lineObj[1].rstrip()
        # Remaining time or initial time
        self.remainingTime = float(self.lineObj[2].rstrip())
        self.board = [[None] * 16 for _ in range(16)]
        # self.int_board = [[None] * 16 for _ in range(16)]

        self.initiateBoard()
        #  read board pattern
        self.readBoard()
        self.c_player = Tile.P_WHITE if self.player == 'WHITE' else Tile.P_BLACK
        self.current_player = self.c_player
        # print(self.c_player)


        # DEFINING CONFIGURATION
        self.ply_depth = 3
        self.ab_enabled = True
        self.b_goals = [t for row in self.board
                        for t in row if t.tile == Tile.T_BLACK]
        self.w_goals = [t for row in self.board
                        for t in row if t.tile == Tile.T_WHITE]       

        self.execute_computer_move()

    def execute_computer_move(self):
        max_time = time.time() + self.remainingTime
        _, move, _, _ = self.minimax(self.ply_depth, self.c_player, max_time)
        # Move the resulting piece
        move_from = self.board[move[0][0]][move[0][1]]
        move_to = self.board[move[1][0]][move[1][1]]
        self.move_piece(move_from, move_to)

    def minimax(self, depth, player_to_max, max_time, a=float("-inf"),
                b=float("inf"), maxing=True, prunes=0, boards=0):

        # Bottomed out base case
        if depth == 0 or self.find_winner() or time.time() > max_time:
            return self.utility_distance(player_to_max), None, prunes, boards

        # Setup initial variables and find moves
        best_move = None
        if maxing:
            best_val = float("-inf")
            moves = self.get_next_moves(player_to_max)
        else:
            best_val = float("inf")
            moves = self.get_next_moves((Tile.P_BLACK
                                         if player_to_max == Tile.P_WHITE else Tile.P_WHITE))

        # For each move
        for move in moves:
            for to in move["to"]:

                # Bail out when we're out of time
                if time.time() > max_time:
                    return best_val, best_move, prunes, boards

                # Move piece to the move outlined
                piece = move["from"].piece
                move["from"].piece = Tile.P_NONE
                to.piece = piece
                boards += 1

                # Recursively call self
                val, _, new_prunes, new_boards = self.minimax(depth - 1,
                                                              player_to_max, max_time, a, b, not maxing, prunes, boards)
                prunes = new_prunes
                boards = new_boards

                # Move the piece back
                to.piece = Tile.P_NONE
                move["from"].piece = piece

                if maxing and val > best_val:
                    best_val = val
                    best_move = (move["from"].loc, to.loc)
                    a = max(a, val)

                if not maxing and val < best_val:
                    best_val = val
                    best_move = (move["from"].loc, to.loc)
                    b = min(b, val)

                if self.ab_enabled and b <= a:
                    return best_val, best_move, prunes + 1, boards

        return best_val, best_move, prunes, boards

    def get_next_moves(self, player=1):

        moves = []  # All possible moves
        basemoves =[]
        look_out = True
        if(self.c_player==1):
            basemoves =self.w_goals
        else:
            basemoves =  self.b_goals
        filtered_moves= []
        for x in filter(lambda x: x.piece == self.c_player and x.tile == self.c_player,basemoves):
            filtered_moves.append(x)
        if(len(filtered_moves)>=1):
            
            for node in filtered_moves:
                curr_tile = node
                if(player == curr_tile.piece):
                    next_tiles =self.get_moves_at_tile(curr_tile, player)
                    if(len(next_tiles)):
                        look_out=False
                    move = {
                                "from": curr_tile,
                                "to": next_tiles
                            }
                    # if len(move["to"]):
                    moves.append(move)
                    # print(moves)
        if(look_out):

            for col in range(self.b_size):
                for row in range(self.b_size):
                    curr_tile = self.board[row][col]
                    # Skip board elements that are not the current player
                    if curr_tile.piece != player:
                        continue               
                    move = {
                        "from": curr_tile,
                        "to": self.get_moves_at_tile(curr_tile, player)
                    }
                    moves.append(move)
            

        return moves

    def get_moves_at_tile(self, tile, player, moves=None, adj=True):

        if moves is None:
            moves = []

        row = tile.loc[0]
        col = tile.loc[1]

        # List of valid tile types to move to
        valid_tiles = [Tile.T_NONE, Tile.T_WHITE, Tile.T_BLACK]
        if tile.tile != player:
            valid_tiles.remove(player)  # Moving back into your own goal
        if tile.tile != Tile.T_NONE and tile.tile != player:
            valid_tiles.remove(Tile.T_NONE)  # Moving out of the enemy's goal

        # Find and save immediately adjacent moves
        for col_delta in range(-1, 2):
            for row_delta in range(-1, 2):

                # Check adjacent tiles

                new_row = row + row_delta
                new_col = col + col_delta

                # Skip checking degenerate values
                if ((new_row == row and new_col == col) or
                    new_row < 0 or new_col < 0 or
                        new_row >= self.b_size or new_col >= self.b_size):
                    continue


                if(tile.tile==player):
                    if(tile.tile==2 and (new_row<row or new_col<col)):
                        continue
                    if(tile.tile ==1 and (new_row>row or new_col > col)):
                        continue

                # Handle moves out of/in to goals
                new_tile = self.board[new_row][new_col]
                if new_tile.tile not in valid_tiles:
                    continue

                if new_tile.piece == Tile.P_NONE:
                    if adj:  # Don't consider adjacent on subsequent calls
                        moves.append(new_tile)
                    continue
                

                # Check jump tiles

                new_row = new_row + row_delta
                new_col = new_col + col_delta

                # Skip checking degenerate values
                if (new_row < 0 or new_col < 0 or
                        new_row >= self.b_size or new_col >= self.b_size):
                    continue

                # Handle returning moves and moves out of/in to goals
                new_tile = self.board[new_row][new_col]
                if new_tile in moves or (new_tile.tile not in valid_tiles):
                    continue

                if new_tile.piece == Tile.P_NONE:
                    # if(row==4 and col ==3):
                    #      print(new_tile.loc)
                    new_tile.fromPath = [row, col]
                    moves.insert(0, new_tile)  # Prioritize jumps
                    self.get_moves_at_tile(new_tile, player, moves, False)

        return moves

    def get_moves_at_tile_withoutJumps(self, tile, player, moves=None, adj=True):

        if moves is None:
            moves = []

        row = tile.loc[0]
        col = tile.loc[1]

        # List of valid tile types to move to
        valid_tiles = [Tile.T_NONE, Tile.T_WHITE, Tile.T_BLACK]
        if tile.tile != player:
            valid_tiles.remove(player)  # Moving back into your own goal
        if tile.tile != Tile.T_NONE and tile.tile != player:
            valid_tiles.remove(Tile.T_NONE)  # Moving out of the enemy's goal

        # Find and save immediately adjacent moves
        for col_delta in range(-1, 2):
            for row_delta in range(-1, 2):

                # Check adjacent tiles

                new_row = row + row_delta
                new_col = col + col_delta

                # Skip checking degenerate values
                if ((new_row == row and new_col == col) or
                    new_row < 0 or new_col < 0 or
                        new_row >= self.b_size or new_col >= self.b_size):
                    continue

                # Handle moves out of/in to goals
                new_tile = self.board[new_row][new_col]
                if new_tile.tile not in valid_tiles:
                    continue

                if new_tile.piece == Tile.P_NONE:
                    # if adj:  # Don't consider adjacent on subsequent calls
                        # moves.append(new_tile)
                    continue

                # Check jump tiles

                new_row = new_row + row_delta
                new_col = new_col + col_delta

                # Skip checking degenerate values
                if (new_row < 0 or new_col < 0 or
                        new_row >= self.b_size or new_col >= self.b_size):
                    continue

                # Handle returning moves and moves out of/in to goals
                new_tile = self.board[new_row][new_col]
                if new_tile in moves or (new_tile.tile not in valid_tiles):
                    continue

                if new_tile.piece == Tile.P_NONE:
                    # if(row==4 and col ==3):
                    #      print(new_tile.loc)
                    new_tile.fromPath = [row, col]
                    moves.insert(0, new_tile)  # Prioritize jumps

        return moves

    def move_piece(self, from_tile, to_tile):

        # Handle trying to move a non-existant piece and moving into a piece
        if from_tile.piece == Tile.P_NONE or to_tile.piece != Tile.P_NONE:
            return

        if(abs(from_tile.loc[0]-to_tile.loc[0]) < 2 and abs(from_tile.loc[1] - to_tile.loc[1]) < 2):
            path = [to_tile.loc, from_tile.loc]
            self.printOutput_File('E', path)

        else:
            path = self.findPath(from_tile, to_tile)
            self.printOutput_File('J', path)

    # to find winner
    def find_winner(self):

        if all(g.piece == Tile.P_WHITE for g in self.b_goals):
            return Tile.P_WHITE
        elif all(g.piece == Tile.P_BLACK for g in self.w_goals):
            return Tile.P_BLACK
        else:
            return None

    def utility_distance(self, player):

        def point_distance(p0, p1):
            return math.sqrt((p1[0] - p0[0])**2 + (p1[1] - p0[1])**2)
        value = 0
        for col in range(self.b_size):
            for row in range(self.b_size):

                tile = self.board[row][col]

                if tile.piece == Tile.P_WHITE:
                    distances = [point_distance(tile.loc, g.loc) for g in
                                 self.b_goals if g.piece != Tile.P_WHITE]
                    value -= max(distances) if len(distances) else -50

                elif tile.piece == Tile.P_BLACK:
                    distances = [point_distance(tile.loc, g.loc) for g in
                                 self.w_goals if g.piece != Tile.P_BLACK]
                    value += max(distances) if len(distances) else -50
        if player == Tile.P_BLACK:
            value *= -1

        return value

    def findPath(self, from_tile, to_tile):

        path = self.bfsSearch(from_tile, to_tile)
        path_loc = []
        for p in path:
            path_loc.append(p.loc)
        path_loc.reverse()
        return path_loc

    def bfsSearch(self, from_tile, to_tile):
        explored = []
        queue = [[from_tile]]
        goal = to_tile
        while queue:
            path = queue.pop()
            node = path[-1]
            if node not in explored:
                neighbours = self.get_moves_at_tile_withoutJumps(
                    node, self.c_player)
                for neighbour in neighbours:
                    new_path = list(path)
                    new_path.append(neighbour)
                    queue.append(new_path)
                    if neighbour == goal:
                        return new_path
                explored.append(node)
        return queue

    def printOutput_File(self, move_type, moves):
        temp = ''
        moves.reverse()
        for i, x in enumerate(moves):
            if i == 0:
                continue
            temp_a = ''
            temp_a += move_type+' ' + \
                str(moves[i-1][0])+','+str(moves[i-1][1]) + \
                ' '+str(x[0])+','+str(x[1])
            temp += temp_a.lstrip()+'\n'
        temp = temp.rstrip()
        print(temp)
        with open(self.filePath_out, 'w+') as fp:
            fp.write(temp)


if __name__ == "__main__":

    halma = Halma()

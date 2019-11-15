import sys
import time
import math
class BOX():
    T_NONE = 0
    T_WHITE = 1
    T_BLACK = 2
    P_NONE = 0
    P_WHITE = 1
    P_BLACK = 2
    def __init__(self, tile=0, men=0,  row=0, col=0, fromPath=[]):
        self.tile = tile
        self.men = men
        self.fromPath = fromPath
        self.row = row
        self.col = col
        self.xy_loc = (row, col)
class HalmaAIAgent():
    def initiateBoard(self):
        for row in range(16):
            for col in range(16):
                if row + col < 6 and row < 5 and col < 5:
                    elm = BOX(2, 2, row, col)
                elif row + col > 24:
                    if row+col == 25 and (row == 10 and col == 15) or(row == 15 and col == 10):
                        elm = BOX(0, 0,  row, col)
                    else:
                        elm = BOX(1, 1,  row, col)
                else:
                    elm = BOX(0, 0,  row, col)
                self.board[row][col] = elm             
    def readBoard(self):
        for x in range(3, 19):
            target_xy = (self.lineObj[x].rstrip())
            for y, content in enumerate(target_xy):
                if content == 'B':
                    self.board[y][x-3].men = 2
                    if(self.board[y][x-3].men == self.board[y][x-3].tile):
                        self.blackInBlack+=1
                    if(self.board[y][x-3].tile == BOX.P_WHITE):
                        self.blackInWhite+=1
                    if(self.board[y][x-3].tile == BOX.P_NONE):
                        self.blackInOpen+=1                    
                elif content == 'W':
                    self.board[y][x-3].men = 1
                    if(self.board[y][x-3].men == self.board[y][x-3].tile):
                        self.whiteInWhite+=1
                    if(self.board[y][x-3].tile == BOX.P_WHITE):
                        self.whiteInBlack+=1
                    if(self.board[y][x-3].tile == BOX.P_NONE):
                         self.whiteInOpen+=1   
                elif content == '.':
                    self.board[y][x-3].men = 0

    def __init__(self):
        self.blackInBlack=0
        self.blackInWhite=0
        self.blackInOpen=0
        self.whiteInOpen=0                   
        self.whiteInWhite=0
        self.whiteInBlack=0
        self.filePath_in = 'input.txt'
        self.filePath_out = 'output.txt'
        self.b_size = 16
        with open(self.filePath_in, 'r') as fp:
            self.lineObj = fp.readlines()
        self.game_type = self.lineObj[0].rstrip()
        self.player = self.lineObj[1].rstrip()
        self.remainingTime = float(self.lineObj[2].rstrip())
        self.maxMoveTime= time.time() + min(self.remainingTime*0.175,15)
        # self.remainingTime=self.remainingTime/2
        self.board = [[None] * 16 for _ in range(16)]
        self.initiateBoard()
        self.readBoard()

        self.c_player = BOX.P_WHITE if self.player == 'WHITE' else BOX.P_BLACK
        self.current_player = self.c_player
        
        if(self.current_player==BOX.P_BLACK):
            if(self.remainingTime<20):
                self.ply_depth=1
            elif(self.remainingTime<60):
                self.ply_depth=2         
            elif(self.blackInWhite>10):
                self.ply_depth=3
            elif(self.blackInOpen+self.whiteInOpen>30):
                self.ply_depth=1
            elif(self.whiteInBlack>17):
                self.ply_depth=1
            else:
                self.ply_depth=2
        else:
            if(self.remainingTime<20):
                self.ply_depth=1
            elif(self.remainingTime<60):
                self.ply_depth=2               
            elif(self.whiteInBlack>7):
                self.ply_depth=3
            elif(self.blackInOpen+self.whiteInOpen>30):
                self.ply_depth=1
            elif(self.blackInWhite>17):
                self.ply_depth=1
            else:
                self.ply_depth=2


        
        # if(self.remainingTime<37 or self.remainingTime>270):
        #     self.ply_depth = 1
        # elif(self.remainingTime<75 or self.remainingTime>175):
        #     self.ply_depth =3
        # else:
        #     self.ply_depth=2
        self.ab_enabled = True
        self.b_goals = [t for row in self.board
                        for t in row if t.tile == BOX.T_BLACK]
        self.w_goals = [t for row in self.board
                        for t in row if t.tile == BOX.T_WHITE]       
        self.play()
    def play(self):
        max_time = time.time() + self.remainingTime
        _, move, _, _ = self.minimax(self.ply_depth, self.c_player, max_time)
        move_from = self.board[move[0][0]][move[0][1]]
        move_to = self.board[move[1][0]][move[1][1]]
        self.move_piece(move_from, move_to)
    def minimax(self, depth, player_to_max, max_time, a=float("-inf"),
                b=float("inf"), maxing=True, prunes=0, boards=0):
        if depth == 0 or self.isWinner() or time.time() > max_time or time.time() > self.maxMoveTime:
            return self.evaluating_function(player_to_max), None, prunes, boards
        best_move = None
        if maxing:
            best_val = float("-inf")
            moves = self.find_moves(player_to_max)
            if len(moves)<1:
                print('as')
                moves = self.find_moves(player_to_max,force_look_out=True)


            # for idx,fro in enumerate(moves):
            #     print('From \n', fro['from'].xy_loc)
            #     for idx,to in enumerate(fro['to']):
            #         print('\n To:', to.xy_loc)
        else:
            best_val = float("inf")
            moves = self.find_moves((BOX.P_BLACK
                                         if player_to_max == BOX.P_WHITE else BOX.P_WHITE))
        
        for move in moves:
            for to in move["to"]:
                if time.time() > max_time:
                    return best_val, best_move, prunes, boards
                men = move["from"].men
                move["from"].men = BOX.P_NONE
                to.men = men
                boards += 1
                val, _, new_prunes, new_boards = self.minimax(depth - 1,
                                                              player_to_max, max_time, a, b, not maxing, prunes, boards)
                prunes = new_prunes
                boards = new_boards
                to.men = BOX.P_NONE
                move["from"].men = men
                if maxing and val > best_val:
                    best_val = val
                    best_move = (move["from"].xy_loc, to.xy_loc)
                    a = max(a, val)
                if not maxing and val < best_val:
                    best_val = val
                    best_move = (move["from"].xy_loc, to.xy_loc)
                    b = min(b, val)
                if self.ab_enabled and b <= a:
                    return best_val, best_move, prunes + 1, boards
        return best_val, best_move, prunes, boards
    def find_moves(self, player=1, force_look_out=False):
        moves = [] 
        basemoves =[]
        look_out = True
        outMove=False
        if(self.c_player==1):
            basemoves =self.w_goals
        else:
            basemoves =  self.b_goals
        filtered_moves= []
        for x in filter(lambda x: x.men == self.c_player and x.tile == self.c_player,basemoves):
            filtered_moves.append(x)
        if(len(filtered_moves)>=1):
            
            for node in filtered_moves:
                curr_tile = node
                filtered_to=[]
                if(player == curr_tile.men):
                    row = curr_tile.xy_loc[0]
                    col = curr_tile.xy_loc[1]
                    # if(row==3 and col ==2):
                        # print('a')
                    next_tiles =self.get_moves_at_tile(curr_tile, player)
                    if(len(next_tiles)>=1):
                        look_out=False
                    for x in filter(lambda x: x not in basemoves ,next_tiles):
                        if(x.tile==player):
                            # if(x.xy_loc[1]==3 and x.xy_loc[0]==2):
                                # print('ab')
                            if(curr_tile.tile==2 and (x.xy_loc[0]<curr_tile.xy_loc[0] or x.xy_loc[1]<curr_tile.xy_loc[1])):
                                continue
                            if(curr_tile.tile ==1 and (x.xy_loc[0]>curr_tile.xy_loc[0] or x.xy_loc[1]>curr_tile.xy_loc[1])):
                                continue
                        filtered_to.append(x)
                        if(len(filtered_to)>=1):
                            outMove=True 
                    if(len(filtered_to)>=1):
                        move = {
                                "from": curr_tile,
                                "to": filtered_to
                            }
                        moves.append(move)

                    elif not outMove:
                        for x in filter(lambda x: x  in basemoves ,next_tiles): 
                            if(x.tile==player):
                                # if(x.xy_loc[1]==3 and x.xy_loc[0]==2):
                                    # print('ab')
                                if(curr_tile.tile==2 and (x.xy_loc[0]<curr_tile.xy_loc[0] or x.xy_loc[1]<curr_tile.xy_loc[1])):
                                    next_tiles.remove(x)
                                    continue
                                if(curr_tile.tile ==1 and (x.xy_loc[0]>curr_tile.xy_loc[0] or x.xy_loc[1]>curr_tile.xy_loc[1])):
                                    next_tiles.remove(x)
                                    continue                                                
                        
                        if(len(next_tiles)>=1):
                            move = {
                                    "from": curr_tile,
                                    "to": next_tiles
                                }
                            moves.append(move)     
                        # else:
                            # look_out=True
                                                


        if(look_out or force_look_out):
            for col in range(self.b_size):
                for row in range(self.b_size):
                    curr_tile = self.board[row][col]
                    if curr_tile.men != player:
                        continue  
                    next_tiles =self.get_moves_at_tile(curr_tile, player)                   
                    if(len(next_tiles)>=1):
                        move = {
                                "from": curr_tile,
                                "to": next_tiles
                            }
                        moves.append(move)


                                # if(look_out or force_look_out):
        #     for col in range(self.b_size):
        #         for row in range(self.b_size):
        #             curr_tile = self.board[row][col]
        #             if curr_tile.men != player:
        #                 continue  
        #             next_tiles =self.get_moves_at_tile(curr_tile, player)
        #             for x in filter(lambda x: x  in basemoves ,next_tiles):
        #                 if(x.xy_loc[0]<curr_tile.xy_loc[0] or x.xy_loc[1]<curr_tile.xy_loc[1]):
        #                     next_tiles.remove(x)
        #                     continue
        #                 if(x.xy_loc[0]>curr_tile.xy_loc[0] or x.xy_loc[1]>curr_tile.xy_loc[1]):
        #                     next_tiles.remove(x)
        #                     continue 
        #             if(len(next_tiles)>=1):
        #                 move = {
        #                         "from": curr_tile,
        #                         "to": next_tiles
        #                     }
        #                 moves.append(move)





            
                    # move = {
                    #     "from": curr_tile,
                    #     "to": self.get_moves_at_tile(curr_tile, player)
                    # }
                    # moves.append(move)
            
        return moves
    def get_moves_at_tile(self, tile, player, moves=None, adj=True):
        if moves is None:
            moves = []
        # if priority_moves is None:
        #     priority_moves=[]
        row = tile.xy_loc[0]
        col = tile.xy_loc[1]

        valid_tiles = [BOX.T_NONE, BOX.T_WHITE, BOX.T_BLACK]
        # basemoves =[]
        # if(self.c_player==1):
        #     basemoves =self.w_goals
        # else:
        #     basemoves =  self.b_goals
        if tile.tile != player:
            valid_tiles.remove(player) 
        if tile.tile != BOX.T_NONE and tile.tile != player:
            valid_tiles.remove(BOX.T_NONE) 
        for col_delta in range(-1, 2):
            for row_delta in range(-1, 2):
                new_row = row + row_delta
                new_col = col + col_delta
                # if(new_row==3 and new_col ==2 and col ==3 and row ==2):
                #  print('a')
                if ((new_row == row and new_col == col) or
                    new_row < 0 or new_col < 0 or
                        new_row >= self.b_size or new_col >= self.b_size):
                    continue
                # if(tile.tile==player):
                #     if(tile.tile==2 and (new_row<row or new_col<col)):
                #         continue
                #     if(tile.tile ==1 and (new_row>row or new_col > col)):
                #         continue
                new_tile = self.board[new_row][new_col]
                if new_tile.tile not in valid_tiles:
                    continue
                if new_tile.men == BOX.P_NONE:
                    if adj:
                        moves.append(new_tile)
                        # if new_tile in basemoves:
                        #     moves.append(new_tile)
                        # else:
                        #     priority_moves.append(new_tile)
                    continue
                
                new_row = new_row + row_delta
                new_col = new_col + col_delta
                # if(new_row==4 and new_col ==1 and col ==3 and row ==2):
                #     print('a')
                if (new_row < 0 or new_col < 0 or
                        new_row >= self.b_size or new_col >= self.b_size):
                    continue
                new_tile = self.board[new_row][new_col]
                if new_tile in moves or new_tile.tile not in valid_tiles :                  
                    continue
                    # if(tile.tile !=player):
                    #     continue
                # if new_tile in priority_moves or (new_tile.tile not in valid_tiles):
                #     continue                
                if new_tile.men == BOX.P_NONE:
                    new_tile.fromPath = [row, col]
                    moves.insert(0,new_tile)
                    # if new_tile in basemoves:s
                    #     moves.insert(0,new_tile)
                    # else:
                    #     priority_moves.insert(0,new_tile)
                    self.get_moves_at_tile(new_tile, player, moves, False)

        # if(len(priority_moves)):
        #     return priority_moves            
        # else: 
        return moves
    def get_moves_at_tile_withoutJumps(self, tile, player, moves=None, adj=True):
        if moves is None:
            moves = []
        row = tile.xy_loc[0]
        col = tile.xy_loc[1]
        valid_tiles = [BOX.T_NONE, BOX.T_WHITE, BOX.T_BLACK]
        if tile.tile != player:
            valid_tiles.remove(player) 
        if tile.tile != BOX.T_NONE and tile.tile != player:
            valid_tiles.remove(BOX.T_NONE) 
        for col_delta in range(-1, 2):
            for row_delta in range(-1, 2):
                new_row = row + row_delta
                new_col = col + col_delta
                if ((new_row == row and new_col == col) or
                    new_row < 0 or new_col < 0 or
                        new_row >= self.b_size or new_col >= self.b_size):
                    continue
                new_tile = self.board[new_row][new_col]
                # if(tile.tile==player and new_tile.tile==player):
                    # if(tile.tile==2 and (new_row<row or new_col<col)):
                    #     continue
                    # if(tile.tile ==1 and (new_row>row or new_col > col)):
                    #     continue
                if new_tile.tile not in valid_tiles:
                    continue
                if new_tile.men == BOX.P_NONE:
                    continue
                new_row = new_row + row_delta
                new_col = new_col + col_delta
                if (new_row < 0 or new_col < 0 or
                        new_row >= self.b_size or new_col >= self.b_size):
                    continue                 
                new_tile = self.board[new_row][new_col]
                if new_tile in moves or (new_tile.tile not in valid_tiles):
                    continue
                if new_tile.men == BOX.P_NONE:
                    new_tile.fromPath = [row, col]
                    moves.insert(0, new_tile)
        return moves
    def move_piece(self, from_tile, to_tile):
        if from_tile.men == BOX.P_NONE or to_tile.men != BOX.P_NONE:
            return
        if(abs(from_tile.xy_loc[0]-to_tile.xy_loc[0]) < 2 and abs(from_tile.xy_loc[1] - to_tile.xy_loc[1]) < 2):
            path = [to_tile.xy_loc, from_tile.xy_loc]
            self.printOutput_File('E', path)
        else:
            path = self.findPath(from_tile, to_tile)
            self.printOutput_File('J', path)
    # to find winner
    def isWinner(self):
        if all(g.men == BOX.P_WHITE for g in self.b_goals):
            return BOX.P_WHITE
        elif all(g.men == BOX.P_BLACK for g in self.w_goals):
            return BOX.P_BLACK
        else:
            return None
    def evaluating_function(self, player):
        def point_distance(p0, p1):
            return math.sqrt((p1[0] - p0[0])**2 + (p1[1] - p0[1])**2)
        value = 0
        for col in range(self.b_size):
            for row in range(self.b_size):
                tile = self.board[row][col]
                if tile.men == BOX.P_WHITE:
                    distances = [point_distance(tile.xy_loc, g.xy_loc) for g in
                                 self.b_goals if g.men != BOX.P_WHITE]
                    value -= max(distances) if len(distances) else -300
                elif tile.men == BOX.P_BLACK:
                    distances = [point_distance(tile.xy_loc, g.xy_loc) for g in
                                 self.w_goals if g.men != BOX.P_BLACK]
                    value += max(distances) if len(distances) else -300
        if player == BOX.P_BLACK:
            value *= -1
        return value
    def findPath(self, from_tile, to_tile):
        path = self.bfsSearch(from_tile, to_tile)
        path_loc = []
        for p in path:
            path_loc.append(p.xy_loc)
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
        # print(temp)
        with open(self.filePath_out, 'w+') as fp:
            fp.write(temp)
if __name__ == "__main__":
    halma_ai = HalmaAIAgent()

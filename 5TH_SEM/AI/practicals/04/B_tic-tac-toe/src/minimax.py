from src.game import * 
import numpy as np

def minimax(minimax_board , depth , is_maximizing): 
    if check_win(2, minimax_board): 
        return float("inf")
    elif check_win(1, minimax_board): 
        return float("-inf")
    elif is_board_full(minimax_board): 
        return 0 
    
    if is_maximizing: 
        best_score = -1000
        for row in range(board_rows): 
            for col in range(board_cols): 
                if minimax_board[row][col] == 0 : 
                    minimax_board[row][col] = 2
                    score = minimax(minimax_board, depth +1 , False)
                    minimax_board[row][col] = 0 
                    best_score = max(score ,best_score)
        return best_score 
    
    else : 
        best_score = 1000
        for row in range(board_rows): 
            for col in range(board_cols): 
                if minimax_board[row][col] == 0 : 
                    minimax_board[row][col] = 1
                    score = minimax(minimax_board, depth +1 , True)
                    minimax_board[row][col] = 0 
                    best_score = min(score ,best_score)
        return best_score 


def best_move(): 
    best_score = -1000
    move = (-1 , -1)
    for row in range(board_rows): 
        for col in range(board_cols): 
            if board[row][col] == 0 : 
                board[row][col] = 2
                score = minimax(board.copy(), 0 , False)
                board[row][col] = 0 
                if score > best_score:
                    best_score = score 
                    move = (row,col) 
    if move != (-1 , -1): 
        mark_square(move[0],move[1],player=2)
        return True
    
    return False 


def restart_game(): 
    screen.fill(black)
    draw_lines()
    for row in range(board_rows): 
        for col in range(board_cols): 
            board[row][col] = 0

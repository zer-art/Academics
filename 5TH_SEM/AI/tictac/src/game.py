import sys 
import pygame 
import numpy as np 

pygame.init()

## GAME CONSTANTS 

# Game colors
white = (255,255,255)
grey = (180,180,180)
red = (255,0,0)
green = (0,255,0)
black = (0,0,0)

# Proportions and Sizes 

width = 300 
height = 300
line_width = 5 
board_rows = 3 
board_cols = 3 
square_size = width//board_cols
circle_radius = square_size//3
circle_width = 15 
cross_width = 25 


screen = pygame.display.set_mode((width,height))
pygame.display.set_caption("TIC TAC TOE AI")
screen.fill(black)

board = np.zeros((board_rows,board_cols))

def draw_lines(color = white): 
    for i in range(1,board_rows): 
        pygame.draw.line(screen, color, (0, square_size*i), (width, square_size*i), line_width)
        pygame.draw.line(screen, color, (square_size*i, 0), (square_size*i, height), line_width)

def draw_figures(color= white): 
    for row in range(board_rows): 
        for col in range(board_cols): 
            if board[row][col] == 1: 
                pygame.draw.circle(screen, color, (int(col*square_size+square_size//2), int(row*square_size+square_size//2)), circle_radius, circle_width)
            elif board[row][col] == 2: 
                pygame.draw.line(screen, color, (int(col*square_size+square_size//4), int(row*square_size+square_size//4)), (int(col*square_size+3*square_size//4), int(row*square_size+3*square_size//4)), cross_width)
                pygame.draw.line(screen, color, (int(col*square_size+square_size//4), int(row*square_size+3*square_size//4)), (int(col*square_size+3*square_size//4), int(row*square_size+square_size//4)), cross_width)
        
def mark_square(row, col, player): 
    board[row][col] = player

def available_square(row, col): 
    return board[row][col] == 0 

def is_board_full(check_board = board): 
    for row in range(board_rows): 
        for col in range(board_cols): 
            if check_board[row][col] == 0: 
                return False
    return True

def check_win(player, check_board=board): 
    for col in range(board_cols): 
        if check_board[0][col] == player and check_board[1][col] == player and check_board[2][col] == player: 
            return True
        
    for row in range(board_rows): 
        if check_board[row][0] == player and check_board[row][1] == player and check_board[row][2] == player: 
            return True

    if check_board[0][0] == player and check_board[1][1] == player and check_board[2][2] == player: 
        return True 
    
    if check_board[0][2] == player and check_board[1][1] == player and check_board[2][0] == player: 
        return True     
    
    return False

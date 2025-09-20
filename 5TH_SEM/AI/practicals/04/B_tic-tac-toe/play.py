from src.game import * 
from src.minimax import * 
import pygame 
import sys

draw_lines()

player = 1
game_over = False 
result_shown = False

while True : 
    for event in pygame.event.get(): 
        if event.type == pygame.QUIT: 
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN and not game_over : 
            mousex = event.pos[0]//square_size
            mousey = event.pos[1]//square_size

            if available_square(mousey,mousex): 
                mark_square(mousey,mousex,player)
                if check_win(player): 
                    game_over = True 
                player = player%2+1 

                if not game_over and not is_board_full(): 
                    if best_move():
                        if check_win(2): 
                            game_over = True
                        player = player%2+1 

                if not game_over and is_board_full(): 
                    game_over = True
                                
        if event.type == pygame.KEYDOWN :  
            if event.key == pygame.K_r : 
                restart_game()
                game_over = False 
                player = 1 
                result_shown = False

    draw_figures()

    if game_over and not result_shown: 
        if check_win(1): 
            print("You Win!")           
            draw_figures(green)
            draw_lines(green)
        elif check_win(2): 
            print("You Lose!")          
            draw_figures(red)
            draw_lines(red)
        else : 
            print("It's a Tie!")        
            draw_figures(grey)
            draw_lines(grey)
        result_shown = True

    pygame.display.update()

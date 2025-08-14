import random

player =[]
ai = []

board= list(range(1,10))
print(board)

player = input("select O or X")
if player.lower() == 'o' :
    ai = 'X'
elif player.lower() =="x": 
    ai = 'O'
else : 
    print("invalid input")

def game(board): 
    moves = []
    ai_moves = []
    human_move = []
    ai_move = random.choice(board)
    moves = moves.append(ai_move)
    ai_moves = ai_moves.append(ai_move)

    while True :
        human_move = input('')
        if human_move not in [moves]:
            moves = moves.append(human_move)
            human_move = human_move.append(human_move)
        else :
            print("space is not empty")
        ai_move = minmax()
        

        






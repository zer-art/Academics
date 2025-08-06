'''THIS IS FIRST REPOSATORY OF VSD '''
import random
# lucky draw 
dice_nums = [1,2,3,4,5,6]
# lucky draw number 
lucky_draw = (random.choice(dice_nums))
# user choice 
choice = input("guess any number of dice : ")
try: 
    choice = int(choice)
except ValueError : 
    print(f"{choice} is not a integer .")
else: 
     if (choice) > 6:
        print("do you have any mental issue")
     elif (choice) < 1 :
         print("seriously")  
     elif (choice)== lucky_draw: 
         print("you win")
     else :
         print("better luck next time ")  
           

user_input = int(input("enter num : "))
binary_num = ""
while user_input!=0:
    binary_num = str(user_input%2)+binary_num
    user_input = int(user_input/2)
print(binary_num)  


user_list =[]
no_of_inputs = int(input("enter number of inputs : "))
for i in range (no_of_inputs):
    user_list.append(int(input("enter ammount : ")))

user_list.insert(len(user_list),int(input("add new value : ")))


user_ask = int(input("enter serial no : ")) 
print(user_list[user_ask-1])

user_list.remove(len(user_list)-1)    

twodim = [[1,2,3],
          [4,5,6]]

print(twodim[0][2])
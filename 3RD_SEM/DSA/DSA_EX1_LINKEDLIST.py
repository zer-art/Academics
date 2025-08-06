'''
Let us say your expense for every month are listed below,
January - 2200
February - 2350
March - 2600
April - 2130
May - 2190
'''

expense = [
    {"jan":2200,
    "feb":2350,
    "mar":2600,
    "apr":2130,
    "may":2190 }  
]

print(expense[0]['jan'])

'''
1. In Feb, how many dollars you spent extra compare to January?
2. Find out your total expense in first quarter (first three months) of the year.
3. Find out if you spent exactly 2000 dollars in any month
4. June month just finished and your expense is 1980 dollar. Add this item to 
our monthly expense list
5. You returned an item that you bought in a month of April and
got a refund of 200$. Make a correction to your monthly expense list
based on this'''

a1 = str(input("Enter first month : ")).replace(" ","").lower()
b1 = str(input("Enter second month : ")).replace(" ","").lower()

def comaparison(a1,b1):
    a = expense[0][a1]
    b = expense[0][b1]
    print(a-b)

comaparison(a1,b1)


def total():
    no_of_months = int(input("enter no of months : "))
    net = 0 
    i=0
    while i<no_of_months:
        month_name = str(input(f"Enter {i+1} month : ")).replace(" ","").lower()
        net = net + expense[0][month_name]
        i= i+1
    print(net)

total()

def find(spent):
    for key, value in expense[0].items():
        if value == spent:
            print(key)
        else:
            print("None of the month have exact same spent amount")   
            break 


find(int(input("enter num : "))) 

def add_item(month_name):
    expense[0][month_name] = int(input("enter amount : "))

add_item(str(input("month name : ")).replace(" ","").lower())


expense[0]['apr'] = expense[0]['apr'] - 200

print(expense[0]['apr'])

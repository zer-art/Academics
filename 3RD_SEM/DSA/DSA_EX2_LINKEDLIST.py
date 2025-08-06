class Node : 
    def __init__(self,data=None,next=None,prev=None):
        self.data = data
        self.next = next 
        self.prev = prev

class linkedlist :
    def __init__(self):
        self.head = None

    def insert_at_begining(self,data) : 
        node = Node(data,self.head)
        self.head = node

    def print(self):
        itr = self.head 
        llstr = ''
        while itr :
            suffix = ''
            if itr.next :
                suffix = '--->'
            llstr += str(itr.data) + suffix
            itr = itr.next
        print(llstr)

    def get_len (self): 
        itr = self.head
        count = 0 
        while itr : 
            count += 1
            itr = itr.next
        return count    
        print(count)
        
    def insert_at(self,index,data):
        if index <0 or index > self.get_len():
            raise Exception("Invalid Index")
        if index==0:
            self.insert_at_begining(data)
            return
        if index == self.get_len():
            self.insert_at_end(data)
            return
         
        itr = self.head
        count = 0 
        while itr : 
            if count == index -1:
                node = Node(data,itr.next)
                itr.next = node 
                break
            itr = itr.next
            count += 1
        
    def insert_at_end(self,data):
        if self.head is None:
            self.head = Node(data,None)
            return
        
        itr = self.head
        while itr.next:
            itr = itr.next

        itr.next = Node(data,None)

    def remove_at(self,index):
        if index <0 or index > self.get_len():
            raise Exception("Invalid Index")
        if index==0:
            self.head = self.head.next
            return
        count = 0 
        itr = self.head 
        while itr :
            if count == index -1:
                itr.next = itr.next.next
                break
            itr = itr.next
            count += 1
    '''
def insert_after_value(self, data_after, data_to_insert):
    # Search for first occurance of data_after value in linked list
    # Now insert data_to_insert after data_after node

def remove_by_value(self, data):
    # Remove first node that contains data 
    '''

    def insert_datalist(self,datalist):
        self.head = None
        for data in datalist:
            self.insert_at_end(data)
        return
    
    def insert_after_value(self,data_after, data_to_insert):
        if not self.head:
            raise Exception("Linked List is empty")
        while self.head :
            if self.head.data == data_after:
                self.head.next=Node(data_to_insert,self.head.next)
                break
            self.head = self.head.next

    def remove_by_value(self,data):
        if not self.head:
            raise Exception("Linked List is empty")
        if self.head.data == data:
                 self.head = self.head.next  
                 return
        itr  = self.head            
        while itr.next:
            if itr.next.data == data:
                itr.next = itr.next.next
                return
            itr = itr.next
        raise ValueError(f"Value {data} not found in the list")   
    '''
def print_forward(self):
    # This method prints list in forward direction. Use node.next

def print_backward(self):
    # Print linked list in reverse direction. Use node.prev for this.
    '''
    def get_last_node(self):
        itr = self.head
        while itr.next:
            itr = itr.next
        return itr
        
    def backward_print(self):
        if not self.head:
            raise Exception("Linked List is empty") 
        dllstr = ''
        itr = self.get_last_node()
        while itr :
            suffix = ''
            if itr.prev :
                suffix = '--->'
            dllstr += str(itr.data) + suffix
            itr = itr.prev
        print(dllstr)
    
if __name__ == '__main__':
    root = linkedlist()
    root.insert_at_begining(5)
    root.insert_at_begining(10)
    root.print()
    root.get_len()
    root.insert_at_end(20)
    root.print()
    root.insert_at(2,30)
    root.print()
    root.remove_at(2)
    root.print()


if __name__ == '__main__':
    ll = linkedlist()
    ll.insert_datalist(["banana","mango","grapes","orange"])
    ll.insert_at(1,"blueberry")
    ll.remove_at(2)
    ll.print()

    #ll.insert_datalist([45,7,12,567,99])
    #ll.insert_at_end(67)
    #ll.print()
    ll.insert_after_value("banana","apple")
    ll.print()
    ll.remove_by_value("banana")
    ll.print()
    ll.backward_print()




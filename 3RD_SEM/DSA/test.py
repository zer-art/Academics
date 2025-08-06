class Node:
    def __init__(self, data=None):
        self.data = data
        self.next = None

class LinkedList:
    def __init__(self):
        self.head = None

    def remove_by_value(self, data):
        if not self.head:
            raise Exception("Linked List is empty")
        
        # Special case if the node to be removed is the head
        if self.head.data == data:
            self.head = self.head.next
            return
        
        itr = self.head
        while itr.next:
            if itr.next.data == data:
                itr.next = itr.next.next
                return
            itr = itr.next
        
        raise ValueError(f"Value {data} not found in the list")

    def insert_at_end(self, data):
        if self.head is None:
            self.head = Node(data)
            return

        itr = self.head
        while itr.next:
            itr = itr.next

        itr.next = Node(data)

    def print_list(self):
        if not self.head:
            print("Linked List is empty")
            return
        
        itr = self.head
        llstr = ''
        while itr:
            llstr += str(itr.data) + ' -> '
            itr = itr.next
        print(llstr + 'None')

# Example usage
ll = LinkedList()
ll.insert_at_end("banana")
ll.insert_at_end("apple")
ll.insert_at_end("blueberry")
ll.insert_at_end("grapes")
ll.insert_at_end("orange")

print("Original List:")
ll.print_list()

ll.remove_by_value("banana")

print("List after removing 'banana':")
ll.print_list()

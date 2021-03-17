class CircularQueue(object):

    def __init__(self, size):
        self.size = size
        self.max_size = size + 1
        self.queue = [None] * self.max_size
        self.front = self.rear = 0

    def enqueue(self, data):
        if self.isFull():
            self.front = (self.front + 1) % self.max_size

        self.queue[self.rear] = data
        self.rear = (self.rear + 1) % self.max_size

        return True

    def dequeue(self):
        if self.isEmpty():  # codition for empty queue
            return None
        else:
            temp = self.queue[self.front]
            self.front = (self.front + 1) % self.max_size
            return temp

    def Front(self):
        if self.isEmpty():  # codition for empty queue
            return None
        else:
            temp = self.queue[self.front]
            return temp

    def Rear(self):
        """
        Get the last item from the queue.
        :rtype: int
        """
        if self.isEmpty():
            return None

        return self.queue[(self.rear + self.max_size - 1) % self.max_size]

    def isEmpty(self):
        """
        Checks whether the circular queue is empty or not.
        :rtype: bool
        """
        return self.rear == self.front

    def isFull(self):
        """
        Checks whether the circular queue is full or not.
        :rtype: bool
        """
        return (self.rear + 1) % self.max_size == self.front

    def cur_len(self):
        len = self.rear - self.front
        if len < 0:
            len += self.max_size
        return len

    def __getitem__(self, i):
        if i <= self.cur_len():
            return self.queue[(self.front + i) % self.max_size]
        else:
            return None

    def get_index(self, i):
        return (self.front + i) % self.max_size

    def show(self):
        print("Elements in the circular queue are:", end=" ")
        for i in range(self.cur_len()):
            print(self[i], end=" ")
        print()

    def remove(self, len):
        l = min(self.cur_len(), len)
        self.front = (self.front + l) % self.max_size

    def showhex(self, show=True):
        queue = []
        for i in range(self.cur_len()):
            queue.append(self[i])
        s = (''.join(['%02X ' % b for b in queue]))
        if show:
            print("queue: {}".format(s))
        return s


if __name__ == "__main__":
    cq = CircularQueue(5)
    cq.enqueue("a")
    cq.enqueue("b")
    cq.enqueue("c")
    cq.enqueue("d")

    cq.enqueue("e")
    cq.show()
    cq.enqueue("f")
    cq.show()
    cq.enqueue("f")
    cq.show()

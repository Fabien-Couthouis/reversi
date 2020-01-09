import copy
class Test:
    def __init__(self):
        self.test = 1

test = Test()
test.test = 0

test2 = copy.deepcopy(test)  
print(test2.test)
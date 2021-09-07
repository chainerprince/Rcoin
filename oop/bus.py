
from vehicle import Vehicle

class Bus(Vehicle):
    def __init__(self,):
        super().__init__(initial_speed=100)
        # self.speed = 100
        # self.__warnings = []
        self.passengers = []

    def brag(self):
        print("These are the brag that we are making")
    

bus1 = Bus()
bus1.passengers = ["Jack","Dorsey"]
# bus1.add_warning("The warning that we make")

# print(bus1.get_warnings())

bus1.drive()

print(bus1)

print(bus1.passengers)
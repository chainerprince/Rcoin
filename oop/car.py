
from vehicle import Vehicle

class Car(Vehicle):
    # def __init__(self,initial_speed=100):
    #     self.speed = 100
    #     self.__warnings = []

    def brag(self):
        print("These are the brag that we are making")
    

car1 = Car()
# print(car1.__warnings)
car1.add_warning("The warning that we make")
print(car1.get_warnings())
car1.drive()
print(car1)

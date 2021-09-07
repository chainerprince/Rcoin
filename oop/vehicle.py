class Vehicle:
    def __init__(self,initial_speed=100):
        self.speed = 100
        self.__warnings = []


    def __repr__(self):
         return f"{self.__warnings} and {self.speed}"
           

    def add_warning(self,warning_text):
        if len(warning_text):
            self.__warnings.append(warning_text)
     
    def get_warnings(self):
        return self.__warnings


    def drive(self):
        print(f"I am driving at a {self.speed} km per hour")



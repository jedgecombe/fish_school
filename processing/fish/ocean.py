
class Ocean:
    def __init__(self):
        self.land_colour = 255
        self.sea_colour = '#006994'
        self.population = []
        # self.create_ocean()
        
        
    def create_ocean(self):
        background(self.sea_colour)
   
        
    def swim(self):
        for fsh in self.population:
            fsh.move()
            fsh.display()
    


class Ocean:
    def __init__(self):
        self.population = []
        
    def swim(self):
        for fsh in self.population:
            fsh.move()
            fsh.display()
    

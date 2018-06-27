import random

from spatial_utils import SpatialUtils


class Fish:
    def __init__(self, colour, ocean, repel_distance, x=None, y=None,
                     velocity=1):
        self.colour = colour
        self.x = x if x is not None else random.choice(range(width))
        self.y = y if y is not None else random.choice(range(height))
        # TODO include speed somehow
        # self.speed = random.choice(range(3))
        self.repel_distance = 10
        self.velocity = velocity
        ocean.population.append(self)
        self.environment = ocean
                
    def move(self):
        self.repel_vector()
        x_change = random.choice(range(-2, 2, 1))
        y_change = random.choice(range(-2, 2, 1))
        self.x += x_change
        self.y += y_change
        self.x = 0 if self.x > width else self.x
        self.y = 0 if self.y > height else self.y
    
    def repel_vector(self):
        # NEXT continue here
        for other_fish in self.environment.population:
            distance = SpatialUtils.calc_distance([self.x, self.y], [other_fish.x, other_fish.y])
            repel_fish = []
            if 0 < distance < self.repel_distance:
                repel_fish.append(other_fish)
            if len(repel_fish) > 0:
                dirs = []
                for repeller in repel_fish:
                    dir_to_fish = SpatialUtils.calc_angle([self.x, self.y], [other_fish.x, other_fish.y])
                    dirs.append(dir_to_fish)
                avg_dir = mean(dirs)
                desired_move = avg_dir - 180
                
    def assess_enviromment(self):
        
        # TODO think about clasifying environment or perhaps create a series of weights of motivations
        pass
    
    def display(self):
        fill(self.colour)
        rect(self.x, self.y, 30, 10)

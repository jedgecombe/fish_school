import math
import random

from spatial_utils import SpatialUtils


class Fish:
    def __init__(self, colour, ocean, separation_distance, x=None, y=None,
                     velocity=1, separation_weighting=2, radius=5,
                         cohesion_weighting=1.5, alignment_weighting=1):
        self.colour = colour
        self.radius = radius
        self.x = x if x is not None else random.choice(range(width))
        self.y = y if y is not None else random.choice(range(height))
        self.separation_distance = separation_distance
        self.velocity = velocity
        ocean.population.append(self)
        self.environment = ocean
        self.rotation = 0
        
        self.separation_weighting = separation_weighting
        self.cohesion_weighting = cohesion_weighting
        self.alignment_weighting = alignment_weighting
        # self.create_shape()
        
    # def create_shape(self):
    #     s = createShape()
    #     # shapeMode(CENTER)
    #     s.beginShape(TRIANGLE_STRIP)
    #     s.vertex(30, 75)
    #     s.vertex(40, 20)
    #     s.vertex(50, 75)
    #     s.vertex(60, 20)
    #     s.vertex(70, 75)
    #     s.vertex(80, 20)
    #     s.vertex(90, 75)
    #     s.endShape()
                
    def move(self):
        chosen_dir = self.assess_enviromment()
        if chosen_dir != 0:
            new_x, new_y = SpatialUtils.new_position_angle_length(chosen_dir, self.velocity, [self.x, self.y])
        else:
            new_x, new_y = self.x, self.y
            x_change = random.choice(range(-self.velocity, self.velocity + 1, 1))
            y_change = random.choice(range(-self.velocity, self.velocity + 1, 1))
            new_x += x_change
            new_y += y_change
        self.x, self.y = new_x, new_y
        self.rotation = chosen_dir
        
        self.x = 0 if self.x > width else self.x
        self.y = 0 if self.y > height else self.y
    
    def separation(self):
        dirs = []
        weighted_dists = []
        for other_fish in self.environment.population:
            distance = SpatialUtils.calc_distance([self.x, self.y], [other_fish.x, other_fish.y])
            if 0 < distance < self.separation_distance:
                # create weights for distances such that closer fish are proportionately more influential on decision
                distance_weighted = 1 / distance
                weighted_dists.append(distance_weighted)
                dir_to_fish = SpatialUtils.calc_angle([self.x, self.y], [other_fish.x, other_fish.y])
                dir_away_from_fish = dir_to_fish - 180
                dirs.append(dir_away_from_fish)
        weighted_dirs = []
        for dir, distance in zip(dirs, weighted_dists):
            weight_adj = distance / sum(weighted_dists)
            weighted_dirs.append(weight_adj * dir)
        desired_dir = sum(weighted_dirs)
        return desired_dir
    
    def cohesion(self):
        return 0
    
    def alignment(self):
        return 0 
    
    def obstacle_avoidance(self):
        return 0
        
    def seek(self):
        return 0
        
                
    def assess_enviromment(self):
        sep_angle = self.separation()
        coh_angle = self.cohesion()
        align_angle = self.alignment()
        # TODO add self.random move()
        
        # calculated weighted average of desired angle
        # only consider weight if it has a non-zero effect
        adj_weights_angles = [[x, y] for x, y in zip([sep_angle, coh_angle, align_angle], [self.separation_weighting, self.cohesion_weighting, self.alignment_weighting]) if x != 0]
        weighted_angles = []
        for angle, weight in adj_weights_angles:
            weight_adj = weight / sum(j for i, j in adj_weights_angles)
            weighted_angles.append(weight_adj * angle)
        chosen_dir = sum(weighted_angles)
        return chosen_dir
            
    
    def create_creature_shape(self):
        x1, y1 = self.x - self.radius / 2, self.y - self.radius
        x2, y2 = self.x, self.y + self.radius
        x3, y3 = self.x + self.radius / 2, self.y - self.radius
        # x1, y1 = self.x - self.radius / 2, self.y - self.radius
        # x2, y2 = self.x - self.radius * 2 , self.y - self.radius * 2
        # x3, y3 = self.x + self.radius / 2, self.y - self.radius
        return x1, y1, x2, y2, x3, y3
    
    def display(self):
        fill(self.colour)
        # self.create_shape()
        # stroke(255)
        # pushMatrix()
        # translate(self.x, self.y)
        # rotate(self.rotation)
        # beginShape(TRIANGLES)
        # vertex(0, -self.radius*2)
        # vertex(-self.radius, -self.radius*2)
        # vertex(self.radius, self.radius*2)
        # endShape()
        # popMatrix()
        # x1, y1, x2, y2, x3, y3 = self.create_creature_shape()
        # triangle(x1, y1, x2, y2, x3, y3)
        rect(self.x, self.y, 30, 10)

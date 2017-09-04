import matplotlib.pyplot as plt
# import numpy as np
import random
import math


class Environment():
    # assumes starting from point 0, 0
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.population = []
        self.fig = plt.figure()

    def draw_graph(self):
        ax = self.fig.add_subplot(111, aspect='equal')
        ax.set_xlim(0, (0 + self.width))
        ax.set_ylim(0, (0 + self.height))

class Fish():
    def __init__(self, fish_dict=None):
        if fish_dict is None:
            self.x = random.randint(0, environ_width)
            self.y = random.randint(0, environ_height)
            self.type = random.choice(fish_types)
            self.size = 10
            self.fish_colour = 'red'
        else:
            self.x = fish_dict['x']
            self.y = fish_dict['y']
            self.type = fish_dict['type']
            self.size = fish_dict['size']
            self.fish_colour = fish_dict['colour']
        # print('fish coords:', (self.x, self.y))
        # initial_dist.append([self.x, self.y])
        # environ.append([self.x, self.y, self.type])


    def create_fish_dict(self):
        return {'x': self.x, 'y': self.y, 'type': self.type, 'size': self.size, 'colour': self.fish_colour}

    def plot_fish(self):
        plt.plot(self.x, self.y, marker='o', markersize=self.size, color=self.fish_colour)



# class Whale(Fish):
#     def __init__(self, x, y):
#         self.x = random.randint(0, 15)
#         self.y = random.randint(0, 15)
#         self.size = whale_size
#         self.fish_colour = 'blue'
#
#
# class Tuna(Fish):
#     def __init__(self, x, y):
#         self.x = random.randint(0, 15)
#         self.y = random.randint(0, 15)
#         self.size = tuna_size
#         self.fish_colour = 'yellow'

class Movement():
    def __init__(self, fish_dict):
        self.x = fish_dict['x']
        self.y = fish_dict['y']
        self.type = fish_dict['type']
        self.size = fish_dict['size']
        self.fish_colour = fish_dict['colour']

    def closest_fish(self, environ):
        dist_list = []
        zero_dist_count = 0
        if len(environ) != 0: #if not first fish
            for other_fish in environ:
                # could change the following to a pythag function
                csquare = (self.x - other_fish['x']) ** 2 + (self.y - other_fish['y']) ** 2
                dist = math.sqrt(csquare)
                # to avoid it calculating the distance to itself
                if dist == 0 & zero_dist_count == 0:
                    zero_dist_count += 1
                    continue
                dist_list.append({'dist': dist, 'x': other_fish['x'], 'y': other_fish['y']})
            if len(dist_list) > 0:
                closest = min(dist_list, key=lambda x:x['dist'])  #closest fish as dict
                return closest

    def collision_detection(self, closest_fish):
        if closest_fish is None:
            return False
        if closest_fish['dist'] < min_dist:
            # print('collision! subject fish:', (self.x, self.y), 'closest fish:', (closest_fish['x'], closest_fish['y']), 'distance:', closest_fish['dist'])
            return True


    def move_fish(self):
        return {'x': self.x, 'y': self.y + 1, 'type': self.type, 'size': self.size, 'colour': self.fish_colour}



### inputs
fish_types = ['whale', 'tuna']
graph_file = 'initial_distribution.png'
environ_width = 15
environ_height = 15
fish_pop = 15
whale_size = 30
tuna_size = whale_size/2
min_dist = 3

initial_environ = Environment(environ_width, environ_height)
graph = initial_environ.draw_graph()

environ = []
collision_list = []
ok_locs = []


fish_num = 0
while fish_num < fish_pop:
    fishy = Fish()
    fish_num += 1
    fishy.plot_fish()
    # print(fishy.create_fish_dict())
    environ.append(fishy.create_fish_dict())
    # print(initial_positions)
    # print('fish dict', fishy.create_fish_dict())

for i in environ:
    move = Movement(i)
    closest = move.closest_fish(environ)
    if move.collision_detection(closest) is True:
        collision_list.append(i)
    else:
        ok_locs.append(i)

print('col list', len(collision_list))
print('ok list', len(ok_locs))
count = 0
for j in collision_list[count:]:
    move = Movement(j)
    moved = move.move_fish()
    moved = Movement(moved)
    closest = moved.closest_fish(ok_locs)
    if move.collision_detection(closest) is True:
        collision_list.append(j)
    else:
        j['colour'] = 'green'
        ok_locs.append(j)
        print('fixed')
    count += 1
    # collision_list = [j for j in collision_list if j['x'] and j['y']]

        # filter(lambda j: j, collision_list)
print('col list', len(collision_list))
print('ok list', len(ok_locs))
    # else:

    # if
    # print(i)
    #
    # fish_dict = fishy.create_fish_dict()
    # closest = fishy.closest_fish(environ)
    # move = Movement(fish_dict)
    # while True:
    #     move.collision_detection(closest)
    #     while True:
    #         move.collision_detection(closest)
    #         moved_fish = move.move_fish()
    #         fishy = Fish(moved_fish)
    #         fish_dict = fishy.create_fish_dict()
    #         closest = fishy.closest_fish(environ)
    #         move = Movement(fish_dict)
    #         if move.collision_detection(closest) is not True:
    #             break
    # print(fishy.closest_fish(environ))
    # fishy.plot_fish()
    # print('fish dict', fishy.create_fish_dict())

collision_env = Environment(environ_width, environ_height)
collision_graph = collision_env.draw_graph()

# for i in
for i in collision_list:
    f = Fish(i)
    f.plot_fish()

collision_env.fig.savefig('collision.png',dpi=90, bbox_inches='tight')
ok_env = Environment(environ_width, environ_height)
ok_graph = ok_env.draw_graph()
for x in ok_locs:
    g = Fish(x)
    g.plot_fish()

ok_env.fig.savefig('ok.png',dpi=90, bbox_inches='tight')

print(environ)
initial_environ.fig.savefig(graph_file, dpi=90, bbox_inches='tight')
print(collision_list)
print(ok_locs)


# problem with not adding to population
# look at getting rid of self.x etc in Whale, is it covered in the init statement for fish?
# need to get it to loop round - if it is too close, generate fish again (or just move fish??)
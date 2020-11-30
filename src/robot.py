from typing import Tuple
from random import choice
from environment import Environment
import queue
LEAVE_CHILD = 'L'
CLEAN = 'C'
MOVE = 'M'
TAKE_CHILD = 'T'

DR = [1, 0, -1, 0]
DC = [0, 1, 0, -1]


class Robot:
    def __init__(self, env: Environment , position: Tuple):
        self.env = env
        self.position = position

    def is_valid_position(self, position):
        return 0 <= position[0] < self.env.height and \
               0 <= position[1] < self.env.width and \
               not (self.env.there_is_child(position) and self.env.there_is_playpen(position)) and \
               not self.env.there_is_object(position)

    def move(self):
        pass


class RandomRobot(Robot):
    def get_possible_moves(self):
        possible_moves = []
        if self.env.there_is_garbage(self.position):
            possible_moves.append((CLEAN, self.position))
        if self.env.robot_carry_child and self.env.there_is_playpen(self.position):
            possible_moves.append((LEAVE_CHILD, self.position))
        for x_increment, y_increment in zip(DR, DC):
            new_x = self.position[0] + x_increment
            new_y = self.position[1] + y_increment
            new_position = (new_x, new_y)
            if self.is_valid_position(new_position):                
                if self.env.robot_carry_child:
                    if new_position not in self.env.children_positions:
                        possible_moves.append((MOVE, new_position))
                    for new_x_increment, new_y_increment in zip(DR, DC):
                        new_x = self.position[0] + new_x_increment
                        new_y = self.position[1] + new_y_increment
                        new_position = (new_x, new_y)
                        if (self.is_valid_position(new_position)) & (new_position not in self.env.children_positions):
                            possible_moves.append((MOVE, new_position))
                elif self.env.there_is_child(new_position):
                    possible_moves.append((TAKE_CHILD, new_position))
                else:
                    possible_moves.append((MOVE,new_position))
        return possible_moves

    def move(self):
        possible_moves = self.get_possible_moves()
        if len(possible_moves) == 0:
            return (False,self.position)
        action_name, next_position = choice(possible_moves)
        if action_name == LEAVE_CHILD:
            self.env.robot_carry_child = False
        elif action_name == CLEAN:
            self.env.garbage_positions.remove(next_position)
        elif action_name == TAKE_CHILD:
            self.env.robot_carry_child = True
        self.position = next_position        
        return (True,next_position)

class SmartRobot(Robot):
    def empty_playpens(self):#playpen empty
        return list(filter((lambda x: (x not in self.env.children_positions) or (x == self.position)),self.env.playpen_positions))

    def out_children(self):#ninnos that it's not in playpen
        return list(filter((lambda x: x not in self.env.playpen_positions),self.env.children_positions))
     
    def access_level(self):
        available_playpen = self.empty_playpens()
        a = {}.fromkeys(available_playpen, 0)
        for playpen in available_playpen:
            for i,j in zip(DR,DC):
                new_pos= (playpen[0] + i, playpen[1] + j)
                if (self.is_valid_position(new_pos)) or ((not(self.is_valid_position(new_pos))) and (new_pos == self.position)):
                    a[playpen] += 1                    
        return [(x, y) for x, y in zip(a.keys(), a.values())]

    def level_filter(self, sec:list, level:int):
        asw = []
        for s in sec:
            if s[1] == level:
                asw.append(s)
        return asw

    def bfs_target(self, position, target: list):
        q = queue.Queue()
        q.put(position)
        parents = {}
        parents[position] = None
        nod = self.bfs_visit(q, parents,target)
        while nod is not None and parents[nod] != position:
                nod = parents[nod]
           
        return nod

    def bfs_visit(self, q, parents, target:list):
        while not q.empty():
            nod = q.get()
            if nod in target:
                return nod
            else:
                for i, j in zip(DR, DC):
                    new_r = nod[0] + i
                    new_c = nod[1] + j
                    if (self.is_valid_position((new_r,new_c))) and ((new_r,new_c) not in parents.keys()):
                        parents[(new_r,new_c)] = nod
                        q.put((new_r,new_c))
        return None

class BabyRobot(SmartRobot):
    def move(self):
        if self.env.robot_carry_child:
            playpen_level = self.access_level()
            level = 1
            playpen = []
            while (len(playpen) == 0) and (level < 5):
                playpen.extend(self.level_filter(playpen_level, level))
                level += 1

            targets_list = []
            if len(playpen) > 0:
                playpen_pos = [x for (x,_) in playpen]
                if self.position in playpen_pos:
                    self.env.robot_carry_child = False                
                    return (True, self.position)
                else:    
                    targets_list.extend(playpen_pos)
            else:
                targets_list.extend(self.env.garbage_positions)
            pos = self.bfs_target(self.position, targets_list)
            if pos != None:
                self.env.children_positions.remove(self.position)
                self.env.children_positions.append(pos)
                self.position = pos
                return (True,pos)
            return (False, self.position)
        else:
            children = self.out_children()
            if len(children) > 0:
                pos = self.bfs_target(self.position,children)
                if pos != None:
                    self.position = pos
                    if pos in self.env.children_positions:
                        self.env.robot_carry_child = True
                    return (True,pos)
                return (False, self.position)
            elif self.position in self.env.garbage_positions:
                self.env.garbage_positions.remove(self.position)
                return(True,self.position)
            else:
                pos = self.bfs_target(self.position,self.env.garbage_positions)
                if pos != None:
                    self.position = pos
                    return (True,pos)
                return (False, self.position)

class ReactiveRobot(SmartRobot):
    def move(self):        
        if self.position in self.env.garbage_positions:
            self.env.garbage_positions.remove(self.position)
            return(True,self.position)
        elif self.env.robot_carry_child:
            playpen_level = self.access_level()
            level = 1
            playpen = []
            while (len(playpen) == 0) and (level < 5):
                playpen.extend(self.level_filter(playpen_level, level))
                level += 1
            
            targets_list = []
            if len(playpen) > 0:
                playpen_list = [x for (x,_) in playpen]
                if self.position in playpen_list:
                    self.env.robot_carry_child = False                
                    return (True, self.position)
                targets_list.extend(playpen_list)                
            targets_list.extend(self.env.garbage_positions)
            pos = self.bfs_target(self.position, targets_list)
            if pos != None:
                self.env.children_positions.remove(self.position)
                self.env.children_positions.append(pos)
                self.position = pos
                return (True, self.position)
            return (False, self.position)
        else:
            pos = self.bfs_target(self.position, self.env.garbage_positions + self.out_children())
            if pos != None:
                    self.position = pos
                    if pos in self.env.children_positions:
                        self.env.robot_carry_child = True
                    return (True,pos)
            return (False, self.position)


                 




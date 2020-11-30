import random

EMPTY_CELL = " _ "
GARBAGE = " @ "
OBJECT = " * "
CHILD = " ! "
ROBOT = " R "
ROBOT_WITH_CHILD = " & "
ROBOT_WITH_GARBAGE = " $ "
ROBOT_IN_PLAYPEN = "/R\\"
ROBOT_WITH_CHILD_IN_PLAYPEN = "/&\\"
ROBOT_WITH_CHILD_AND_GARBAGE = "&_@"
PLAYPEN = "/ \\"
CHILD_IN_PLAYPEN = "/!\\"

DR = [1, 0, -1, 0]
DC = [0, 1, 0, -1]

class Environment:
    def __init__(self, height, width, children_count, garbage_percent, objects_percent):
        self.height = height
        self.width = width
        self.children_count = children_count
        self.garbage_percent = garbage_percent
        self.objects_percent = objects_percent
        self.empty_cells = [(x, y) for x in range(height) for y in range(width)]
        self.garbage_max = self.garbage_top(self.children_count)

        self.robot_position = (-1,-1)
        self.robot_carry_child = False

        self.playpen_positions = self.place_playpen()
        self.children_positions = self.adding_to_field(children_count)  # adding childs
        initial_garbage = (self.height * self.width * self.garbage_percent) // 100
        self.garbage_positions = self.adding_to_field(initial_garbage)  # adding garbage
        initial_objects = (self.height * self.width * self.objects_percent) // 100
        self.objects_positions = self.adding_to_field(initial_objects)  # adding objects

    def __str__(self):
        f = ""
        for i in range(self.height):
            f = f + "| "
            for j in range(self.width):
                symbol = ""
                if (i,j) in self.empty_cells:
                    symbol = EMPTY_CELL
                elif self.robot_position == (i,j):
                    if self.there_is_child((i,j)):
                        if self.there_is_garbage((i,j)):
                            symbol = ROBOT_WITH_CHILD_AND_GARBAGE
                        elif self.there_is_playpen((i,j)):
                            symbol = ROBOT_WITH_CHILD_IN_PLAYPEN
                        else:
                            symbol = ROBOT_WITH_CHILD
                    elif self.there_is_garbage((i,j)):
                        symbol = ROBOT_WITH_GARBAGE
                    elif self.there_is_playpen((i,j)):
                        symbol = ROBOT_IN_PLAYPEN
                    else:
                        symbol = ROBOT
                elif self.there_is_child((i,j)):
                    if self.there_is_playpen((i,j)):
                        symbol = CHILD_IN_PLAYPEN  
                    else:
                        symbol = CHILD
                elif self.there_is_garbage((i,j)):
                    symbol =GARBAGE
                elif self.there_is_object((i,j)):
                    symbol = OBJECT
                elif self.there_is_playpen((i,j)):
                    symbol = PLAYPEN
                f = f + symbol + " "
            f = f + "|\n"
        return f
    #Chequearlo
    def variate(self):
        actual_children_positions = list(self.children_positions)
        for child in actual_children_positions:
            if (self.robot_position == child) | (self.there_is_playpen(child)):
                continue
            next_valid_positions = self.available_next_positions(child,CHILD)
            next_valid_positions.append(child) #including the option Do nothing
            next_position = random.choice(next_valid_positions)
            if next_position == child:#stay in place
                continue                            
            elif next_position in self.empty_cells: #is an empty cell
                self.children_positions.remove(child)
                self.children_positions.append(next_position)
                self.empty_cells.remove(next_position)
                self.empty_cells.append(child)         
                self.generate_garbage(next_position)
            else: # is an object
                can_move = self.try_to_push_object(child,next_position)
                if can_move:
                    self.empty_cells.append(child)  
                    self.empty_cells.remove(next_position)
                    self.children_positions.remove(child)
                    self.children_positions.append(next_position)
                    self.generate_garbage(next_position)
            
    def try_to_push_object(self,pusher, pushed):
        direction = (pushed[0] - pusher[0], pushed[1] - pusher[1])
        new_pushed_position = (pushed[0] + direction[0], pushed[1] + direction[1])
        #if is a valid position and there's empty or occupated for another object
        if(-1 < new_pushed_position[0] < self.height) & (-1 < new_pushed_position[1] < self.width):
            if new_pushed_position in self.empty_cells:
                self.objects_positions.append(new_pushed_position)
                self.objects_positions.remove(pushed)
                self.empty_cells.remove(new_pushed_position)
                self.empty_cells.append(pushed)
                return True
            elif new_pushed_position in self.objects_positions:
                if(self.try_to_push_object(pushed,new_pushed_position)):
                    self.objects_positions.append(new_pushed_position)
                    self.objects_positions.remove(pushed)
                    self.empty_cells.remove(new_pushed_position)                    
                    self.empty_cells.append(pushed)
                    return True
        return False

    def children_can_move(self):
        can = []
        can_not = []
        for child in self.children_positions:
            if not ((child in self.playpen_positions) or ((self.robot_carry_child) and (child == self.robot_position))):
                can.append(child)
            else:
                can_not.append(child)
        return (can, can_not)

    def variate_all(self):
        garbage_count = len(self.garbage_positions)
        objects_count = len(self.objects_positions)
        self.empty_cells.extend(self.garbage_positions)
        self.empty_cells.extend(self.objects_positions)
        children = self.children_can_move()
        self.empty_cells.extend(children[0])
        self.children_positions = self.adding_to_field(len(children[0]))
        self.children_positions.extend(children[1])
        self.garbage_positions = self.adding_to_field(garbage_count)
        self.objects_positions = self.adding_to_field(objects_count)

    def available_next_positions(self, position, pattern):
        next_valid_positions = []
        for index in range(4):
            cell_f = position[0] + DR[index]
            cell_c = position[1] + DC[index]
            if pattern == PLAYPEN:
                if (-1 < cell_f < self.height) & (-1 < cell_c < self.width) & ((cell_f,cell_c) in self.empty_cells):
                    next_valid_positions.append((cell_f, cell_c))
            if pattern == CHILD:
                if (-1 < cell_f < self.height) & (-1 < cell_c < self.width) & (((cell_f,cell_c) in self.empty_cells) | ((cell_f,cell_c) in self.objects_positions)):
                    next_valid_positions.append((cell_f, cell_c))
        return next_valid_positions

    def place_playpen(self):
        count = self.children_count - 1
        last_position = random.choice(self.empty_cells) # selecting a random position
        playpen_positions = [last_position]
        self.empty_cells.remove(last_position)
        while count > 0:           
            posible_positions = self.available_next_positions(last_position, PLAYPEN)
            if len(posible_positions) > 0:
                last_position = random.choice(posible_positions)
                playpen_positions.append(last_position)
                self.empty_cells.remove(last_position)
            count -= 1
        return playpen_positions

    def adding_to_field(self, count):
        position_list = []
        while (count != 0) & (len(self.empty_cells) > 0):
            r = random.randint(0, len(self.empty_cells) - 1)  # selecting a random position to place the pattern
            position = self.empty_cells.pop(r)
            position_list.append(position)
            count -= 1
        return position_list

    #this just update the robot position. almost try to do that
    def set_robot_position(self, position):
        if (self.robot_position not in self.playpen_positions) & (self.robot_position not in self.garbage_positions):
            self.empty_cells.append(self.robot_position)
        # if (self.robot_carry_child) and (self.robot_position in self.children_positions):
        #     self.children_positions.remove(self.robot_position)
        #     self.children_positions.append(position)
        self.robot_position = position
        if position in self.empty_cells:
            self.empty_cells.remove(position)
        # if position in self.children_positions:
            # self.robot_carry_child = True

    def garbage_top(self,count):
        if count == 1: 
            return 1
        if count == 2:
            return 3
        if count > 2:
            return 6
    
    def generate_garbage(self, position_next):
        garbage_count = random.randint(0,self.garbage_max)#how many garbage do you want to create?
        available_garbage = self.available_garbage_positions(position_next)
        while (garbage_count > 0) & (len(available_garbage) > 0):
            position = available_garbage.pop()
            if position in self.empty_cells:
                self.empty_cells.remove(position)
                if position not in self.garbage_positions:
                    self.garbage_positions.append(position)
                

    def available_garbage_positions(self,position_next):
        positions = []
        for i in DR:
            for j in DC:
                check_position = (position_next[0] + i,position_next[1] + j)
                if (-1 < check_position[0] < self.height) & (-1 < check_position[1] < self.width):
                    if check_position in self.empty_cells:
                        positions.append(check_position)
                        
        return positions

    def there_is_garbage(self, position):
        return position in self.garbage_positions

    def there_is_child(self, position):
        return position in self.children_positions

    def there_is_object(self, position):
        return position in self.objects_positions

    def there_is_playpen(self, position):
        return position in self.playpen_positions

    def dirty_cells_percent(self):
         return len(self.garbage_positions) * 100 // (self.height * self.width)

    def is_clean(self):
        return len(self.empty_cells) * 100 // (self.height * self.width) >= 60

    def is_dirty(self):
        return len(self.garbage_positions) * 100 // (self.height * self.width) >= 60

    def is_excellent(self):
        for child in self.children_positions:
            if child not in self.playpen_positions:
                return False        
        else:
            return len(self.garbage_positions) == 0

    def copy(self):
        new_env = Environment(self.height,self.width,self.children_count,self.garbage_percent,self.objects_percent)
        new_env.empty_cells = list(self.empty_cells)
        new_env.garbage_max = self.garbage_max
       
        new_env.robot_position = self.robot_position
        new_env.robot_carry_child = self.robot_carry_child

        new_env.playpen_positions = list(self.playpen_positions)
        new_env.children_positions = list(self.children_positions)
        new_env.garbage_positions = list(self.garbage_positions)
        new_env.objects_positions = list(self.objects_positions)
        return new_env


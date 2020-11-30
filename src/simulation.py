from random import choice
from environment import Environment
import robot

class Simulation:
    def __init__(self, config,variation_time, agent):
        self.config = config
        self.variation_time = variation_time
        self.agent = agent
        self.dirty_cells_percent = []
        self.fired_robot_count = 0
        self.excelent_robot_count = 0
        self.almost_clean = 0

    def __str__(self):
        sim = "Fired: " + str(self.fired_robot_count) + " Excelent: "+ str(self.excelent_robot_count) + " Almost clean: "+ str(self.almost_clean)
        sim = sim +  " Dirty cells percent average: " + str(sum(self.dirty_cells_percent)//len(self.dirty_cells_percent))
        return sim

    def simulation_loop(self):
        simulation_count = 30
        while simulation_count > 0:            
            env = Environment(self.config[0],self.config[1],self.config[2],self.config[3],self.config[4])
            robot_position = self.place_robot(env)
            if self.agent == "R":
                s_robot  = robot.ReactiveRobot(env,robot_position)
            elif self.agent == "A":
                s_robot  = robot.BabyRobot(env,robot_position)
            else:
                s_robot  = robot.MixRobot(env,robot_position)
            t = 0 
            while t < 100:
                before = env.robot_carry_child
                robot_move = s_robot.move()
                if robot_move[0]:
                    if before and env.robot_carry_child:
                        robot_move  = s_robot.move()
                        robot_position = robot_move[1]
                    robot_position = robot_move[1]
                    env.set_robot_position(robot_position)   
                env.variate()
                if self.variation_time == t:
                    env.variate_all()
                if env.is_excellent():
                    self.excelent_robot_count += 1
                    self.dirty_cells_percent.append(0)
                    break
                elif env.is_dirty():
                    self.fired_robot_count += 1
                    self.dirty_cells_percent.append(env.dirty_cells_percent())
                    break
                t += 1
            if t == 100:
                self.dirty_cells_percent.append(env.dirty_cells_percent())
                if env.is_clean():
                    self.almost_clean += 1
            simulation_count -= 1
    
    def place_robot(self, env:Environment):
        possible_positions = list(filter(lambda x: self.is_valid_robot_position(env, x), env.empty_cells +
                                    env.garbage_positions + env.playpen_positions))
        position = choice(possible_positions)
        env.set_robot_position(position)
        return position

    def is_valid_robot_position(self, env:Environment, position):
        from robot import DR, DC
        neighbor_positions = [(position[0] + x, position[0] + y) for x, y in zip(DR, DC)]
        return not all(map(env.there_is_object, neighbor_positions))


if __name__ == '__main__':
    environments = [((8, 9, 10, 10, 10), 50), ((8, 9, 20, 10, 10), 50), \
                    ((5, 5, 4, 20, 20), 20), ((5, 5, 4, 20, 20), 80),\
                    ((10, 8, 15, 10, 10), -1), ((10, 8, 15, 10, 10), 20),\
                    ((6, 8, 7, 5, 5),50), ((6, 8, 2, 5, 5), 50), \
                    ((3, 4, 2, 20, 20), 50), ((3, 4, 2, 20, 20), 20)]
    agents = ["A","R"]
    for env in environments:
        for aget in agents:
            print(env, " + ",aget)
            sim = Simulation(env[0], env[1], aget)
            sim.simulation_loop()
            print(sim)
    

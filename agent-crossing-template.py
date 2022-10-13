import gym
import gym_grid_driving
from gym_grid_driving.envs.grid_driving import LaneSpec, Point
import os 
import sys


FAST_DOWNWARD_DIRECTORY_ABSOLUTE_PATH = "/fast_downward/"
PDDL_FILE_ABSOLUTE_PATH = ""

class GeneratePDDL_Stationary :
    '''
    Class to generate the PDDL files given the environment description.
    '''
    def __init__ (self, env, num_lanes, width, file_name) :
        self.state = env.reset()
        self.num_lanes = num_lanes
        self.width = width
        self.file_name = file_name
        self.problem_file_name = self.file_name + 'problem.pddl' 
        self.domain_file_name = self.file_name + 'domain.pddl' 
        self.domain_string = ""
        self.type_string = ""
        self.predicate_strings = self.addHeader("predicates")
        self.action_strings = ""
        self.problem_string = ""
        self.object_strings = self.addHeader("objects")


    def addDomainHeader(self, name='default_header') :
        '''
        Adds the header in the domain file.

        Parameters : 
        name (string): domain name.
        '''
        self.domain_header = "(define (domain " + name +" ) \n" +"(:requirements :strips :typing) \n"


    def addTypes(self, types={}) :
        '''
        Adds the object types to the PDDL domain file.

        Parameters : 
        types (dict): contains a dictionary of (k,v) pairs, where k is the object type, and v is the supertype. If k has no supertype, v is None.
        '''
        type_string = "(:types "

        for _type, _supertype in types.items() :
            if _supertype is None :
                type_string += _type +  "\n"
            else : 
                type_string += _type + " - " + _supertype + "\n"
        type_string += ") \n"
        self.type_string = type_string


    def addPredicate(self, name='default_predicate', parameters = (), isLastPredicate=False) :
        '''
        Adds predicates to the PDDL domain file

        Parameters : 
        name (string) : name of the predicate.
        parameters (tuple or list): contains a list of (var_name, var_type) pairs, where var_name is an instance of object type var_type.
        isLastPredicate (bool) : True for the last predicate added.
        '''
        predicate_string = "(" + name
        for var_name, var_type in parameters :
            predicate_string += " ?" + var_name + " - " + var_type
        predicate_string += ") \n"
        self.predicate_strings+= predicate_string

        if isLastPredicate :
            self.predicate_strings += self.addFooter()


    def addAction(self, name='default_action', parameters=(), precondition_string= "", effect_string= "") :
        '''
        Adds actions to the PDDL domain file

        Parameters : 
        name (string) : name of the action.
        parameters (tuple or list): contains a list of (var_name, var_type) pairs, where var_name is an instance of object type var_type.
        precondition_string (string) : The precondition for the action.
        effect_string (string) : The effect of the action.
        '''
        action_string = name + "\n"
        parameter_string = ":parameters ("
        for var_name, var_type in parameters :
            parameter_string += " ?" + var_name + " - " + var_type
        parameter_string += ") \n"
        
        precondition_string = ":precondition " + precondition_string + "\n"
        effect_string = ":effect " + effect_string + "\n"
        action_string += parameter_string + precondition_string + effect_string
        action_string = self.addHeader("action") + action_string + self.addFooter()
        self.action_strings+= action_string

    def generateDomainPDDL(self) :
        '''
        Generates the PDDL domain file after all actions, predicates and types are added
        '''
        domain_file = open(PDDL_FILE_ABSOLUTE_PATH + self.domain_file_name, "w")
        PDDL_String = self.domain_header + self.type_string + self.predicate_strings + self.action_strings + self.addFooter()
        domain_file.write(PDDL_String)
        domain_file.close()

   
    def addProblemHeader(self, problem_name='default_problem_name', domain_name='default_domain_name') :
        '''
        Adds the header in the problem file.

        Parameters : 
        problem_name (string): problem name.
        domain_name (string): domain name.
        '''
        self.problem_header = "(define (problem " + problem_name + ") \n (:domain " + domain_name + ") \n"
    

    def addObjects(self, obj_type, obj_list=[], isLastObject=False) :
        '''
        Adds object instances of the same type to the problem file

        Parameters :
        obj_type (string) : the object type of the instances that are being added
        obj_list (list(str)) : a list of object instances to be added
        isLastObject (bool) : True for the last set of objects added.
        '''
        obj_string = ""
        for obj in obj_list :
            obj_string += obj + " "
        obj_string += " - " + obj_type
        self.object_strings += obj_string + "\n "
        if isLastObject :
            self.object_strings += self.addFooter()


    def addInitState(self) :
        '''
        Generates the complete init state
        '''
        initString = self.generateInitString()
        self.initString = self.addHeader("init") + initString + self.addFooter()


    def addGoalState(self) :
        '''
        Generates the complete goal state
        '''
        goalString = self.generateGoalString()
        self.goalString = self.addHeader("goal") + goalString + self.addFooter()


    def generateGridCells(self) :
        '''
        Generates the grid cell objects. 
        
        For a |X+1| x |Y+1| sized grid, |X+1| x |Y+1| objects to represent each grid cell are created. 
        pt0pt0, pt1pt0, .... ptxpt0
        pt0pt1, pt1pt1, .... ptxpt1
        ..       ..            ..
        ..       ..            ..
        pt0pty, pt1pty, .... ptxpty


        '''
        self.grid_cell_list = []
        for w in range(self.width) :
            for lane in range(self.num_lanes) :
                self.grid_cell_list.append("pt{}pt{}".format(w, lane))
 

    def generateInitString(self) :
        '''
        FILL ME : Should return the init string in the problem PDDL file. 
        Hint : Use the defined grid cell objects from genearateGridCells and predicates to construct the init string.

        Information that might be useful here :

        1. Initial State of the environment : self.state
        2. Agent's x position : self.state.agent.position.x
        3. Agent's y position : self.state.agent.position.y
        4. The object of type agent is called "agent1" (see generateProblemPDDLFile() ).
        5. Set of cars in the grid: self.state.cars
        6. For a car in self.state.cars, it's x position: car.position.x
        7. For a car in self.state.cars, it's y position: car.position.y
        8. List of grid cell objects : self.grid_cell_list
        9. Width of the grid: self.width
        10. Number of lanes in the grid : self.num_lanes
        
        Play with environment (https://github.com/cs4246/gym-grid-driving) to see the type of values above objects return

        Example: The following statement adds the initial condition string from https://github.com/pellierd/pddl4j/blob/master/pddl/logistics/p01.pddl  

        return "(at apn1 apt2) (at tru1 pos1) (at obj11 pos1) (at obj12 pos1) (at obj13 pos1) (at tru2 pos2) (at obj21 pos2) (at obj22 pos2)
                (at obj23 pos2) (in-city pos1 cit1) (in-city apt1 cit1) (in-city pos2 cit2) (in-city apt2 cit2)" 
        ''' 
        initString = ''
        max_time = self.width // abs(max(self.state.agent.speed_range)) + 1
        free_cells = [self.grid_cell_list[:] for _ in range(max_time)]
        for car in self.state.cars:
                x, y = car.position.x, car.position.y
                if(x!=0 or y!=0):
                    initString = initString + f"(at pt{x}pt{y} 0 car{car.id}) (blocked pt{x}pt{y} 0) "
                    free_cells[0].remove(f"pt{x}pt{y}")

        for t in range(1, max_time):
            for car in self.state.cars:
                speed = abs(car.speed_range[0])
                prev_x = (car.position.x - speed * (t-1)) if (car.position.x - speed * (t-1)) >= 0 else (car.position.x - ((speed * (t-1))%self.width) + self.width)%self.width

                new_x = (car.position.x - speed * t) if (car.position.x - speed * t) >= 0 else (car.position.x - ((speed * t)%self.width) + self.width)%self.width
                new_y = car.position.y

                if f"pt{new_x}pt{new_y}" in free_cells[t]: 
                    # if(new_x!=0 or new_y!=0):
                    initString = initString + f"(at pt{new_x}pt{new_y} {t} car{car.id}) (blocked pt{new_x}pt{new_y} {t}) "
                    free_cells[t].remove(f"pt{new_x}pt{new_y}")
                if(new_x < prev_x and speed > 1):
                    for x_co in range(new_x+1, prev_x):
                        if f"pt{x_co}pt{new_y}" in free_cells[t]: 
                            # if(x_co!=0 or new_y!=0):
                            initString = initString + f"(blocked pt{x_co}pt{new_y} {t}) "
                            free_cells[t].remove(f"pt{x_co}pt{new_y}")
                elif(new_x > prev_x):
                    for x_co in list(range(0, prev_x))+list(range(new_x+1, self.width)) :
                        if f"pt{x_co}pt{new_y}" in free_cells[t]: 
                            # if(x_co!=0 or new_y!=0):
                            initString = initString + f"(blocked pt{x_co}pt{new_y} {t}) "
                            free_cells[t].remove(f"pt{x_co}pt{new_y}")


            for cell in free_cells[t]:
                initString = initString + f"(not (blocked {cell} {t})) "


        initString = initString + f"(at pt{self.state.agent.position.x}pt{self.state.agent.position.y} 0 agent1) "
        if "pt0pt0" not in free_cells[t]: free_cells[t].append("pt0pt0") 
        for t in range(1, max_time):
            for cell in self.grid_cell_list:
                _, cur_x, cur_y = cell.split('pt')
                cur_x, cur_y = int(cur_x), int(cur_y)

                new_x = cur_x if cur_x == 0 else max(0, cur_x - 1)
                up_y = cur_y if cur_y == 0 else cur_y - 1
                new_up_y = up_y if f"pt{new_x}pt{up_y}" in free_cells[t] else cur_y
                down_y = cur_y if cur_y == self.num_lanes - 1 else cur_y + 1
                new_down_y = down_y if f"pt{new_x}pt{down_y}" in free_cells[t] else cur_y
                initString = initString + f"(up_next {cell} pt{new_x}pt{new_up_y} {t}) (down_next {cell} pt{new_x}pt{new_down_y} {t}) "
                # if(t==11):
                #     print(f"t={t} cell={cell} {new_x} {new_up_y} {new_down_y}")
                for s in range(1, 4):
                    new_x = cur_x if cur_x == 0 else max(0, cur_x - s)
                    initString = initString + f"(forward_next {cell} pt{new_x}pt{cur_y} {t} {-s})  "
        
        for i in range(max_time):
            initString = initString + f"(next_instant {i} {i+1}) "
        
        return initString


    def generateGoalString(self) :
        '''
        FILL ME : Should return the goal string in the problem PDDL file
        Hint : Use the defined grid cell objects from genearateGridCells and predicates to construct the goal string.

        Information that might be useful here :
        1. Goal x Position : self.state.finish_position.x
        2. Goal y Position : self.state.finish_position.y
        3. The object of type agent is called "agent1" (see generateProblemPDDLFile() ).
        Play with environment (https://github.com/cs4246/gym-grid-driving) to see the type of values above objects return

        Example: The following statement adds goal string from https://github.com/pellierd/pddl4j/blob/master/pddl/logistics/p01.pddl  

        return "(and (at obj11 apt1) (at obj23 pos1) (at obj13 apt1) (at obj21 pos1)))"
        '''    
        goalString = '(or ' 
        for i in range(self.width):
            goalString = goalString + f"(at pt{self.state.finish_position.x}pt{self.state.finish_position.y} {i} agent1) "
        goalString = goalString + " )"
        return goalString


    def generateProblemPDDL(self) :
        '''
        Generates the PDDL problem file after the object instances, init state and goal state are added
        '''
        problem_file = open(PDDL_FILE_ABSOLUTE_PATH + self.problem_file_name, "w")
        PDDL_String = self.problem_header + self.object_strings + self.initString + self.goalString + self.addFooter()
        problem_file.write(PDDL_String)
        problem_file.close()


    '''
    Helper Functions 
    '''
    def addHeader(self, name) :
        return "(:" + name + " "


    def addFooter(self) :
        return ") \n"


      

def initializeSystem(env):
    gen = GeneratePDDL_Stationary(env, len(env.lanes), width=env.width, file_name='HW1')
    return gen


def generateDomainPDDLFile(gen):
    '''
    Function that specifies the domain and generates the PDDL Domain File. 
    As a part of the assignemnt, you will need to add the actions here.
    '''
    gen.addDomainHeader("grid_world")
    gen.addTypes(types = {"car" : None, "agent" : "car", "gridcell" : None, "time": None, "speed": None})
    '''
    Predicate Definitions :
    (at ?pt ?t ?car) : car is at gridcell pt at time t.
    (up_next ?pt1 ?pt2 ?t) : pt2 is the next location of the car when it takes the UP action from pt1 at time t
    (down_next ?pt1 ?pt2 ?t) : pt2 is the next location of the car when it takes the DOWN action from pt1 at time t
    (forward_next ?pt1 ?pt2 ?t) : pt2 is the next location of the car when it takes the FORWARD action from pt1 at time t
    (blocked ?pt ?t) : The gridcell pt is occupied by a car and is "blocked" at time t
    '''

    gen.addPredicate(name="at", parameters=(("pt1" , "gridcell"), ("t", "time"), ("car", "car")))
    gen.addPredicate(name="up_next", parameters=(("pt1" , "gridcell"), ("pt2", "gridcell"), ("t", "time")))
    gen.addPredicate(name="down_next", parameters=(("pt1" , "gridcell"), ("pt2", "gridcell"), ("t", "time")))
    gen.addPredicate(name="forward_next", parameters=(("pt1" , "gridcell"), ("pt2", "gridcell"), ("t", "time"), ("s", "speed")))
    gen.addPredicate(name="next_instant", parameters=(("t1", "time"), ("t2", "time")))
    gen.addPredicate(name="blocked", parameters=[("pt1" , "gridcell"), ("t", "time")] , isLastPredicate=True)


    gen.addAction(name="UP", parameters=(("pt1" , "gridcell"), ("pt2", "gridcell"), ("t1", "time"), ("t2", "time")), 
            precondition_string="(and (at ?pt1 ?t1 agent1) (up_next ?pt1 ?pt2 ?t2) (not (blocked ?pt2 ?t2)) (next_instant ?t1 ?t2))", 
            effect_string="(at ?pt2 ?t2 agent1) ")

    gen.addAction(name="DOWN", parameters=(("pt1" , "gridcell"), ("pt2", "gridcell"), ("t1", "time"), ("t2", "time")), 
            precondition_string="(and (at ?pt1 ?t1 agent1) (down_next ?pt1 ?pt2 ?t2) (not (blocked ?pt2 ?t2)) (next_instant ?t1 ?t2))", 
            effect_string=" (at ?pt2 ?t2 agent1) ")

    gen.addAction(name="FORWARD", parameters=(("pt1" , "gridcell"), ("pt2", "gridcell"), ("t1", "time"), ("t2", "time"), ("s", "speed")),
            precondition_string="(and (at ?pt1 ?t1 agent1) (forward_next ?pt1 ?pt2 ?t2 ?s) (not (blocked ?pt2 ?t2)) (next_instant ?t1 ?t2))",
            effect_string=" (at ?pt2 ?t2 agent1) ")

    
    '''
    FILL ME : Add the actions UP, DOWN, FORWARD with the help of gen.addAction() as follows :

        gen.addAction(name="UP", parameters = (...), precondition_string = "...", effect_string="...")
        gen.addAction(name="DOWN", parameters = (...), precondition_string = "...", effect_string="...")
        gen.addAction(name="FORWARD", parameters = (...), precondition_string = "...", effect_string="...")
        
        You have to fill up the ... in each of gen.addAction() above.
        
    Example :

    The following statement adds the LOAD-TRUCK action from https://tinyurl.com/y3jocxdu [The domain file referenced in the assignment] to the domain file 
    gen.addAction(name="LOAD-TRUCK", 
                  parameters=(("pkg", "package"), ("truck" , "truck"), ("loc", "place")), 
                  precondition_string="(and (at ?truck ?loc) (at ?pkg ?loc))", 
                  effect_string= "(and (not (at ?pkg ?loc)) (in ?pkg ?truck))")
    '''
    gen.generateDomainPDDL()
    pass

def generateProblemPDDLFile(gen):
    '''
    Function that specifies the domain and generates the PDDL Domain File.
    Objects defined here should be used to construct the init and goal strings
    '''
    gen.addProblemHeader("parking", "grid_world")
    gen.addObjects("agent", ["agent1"])
    gen.addObjects("time", [str(x) for x in list(range(gen.width))])
    gen.addObjects("speed", [str(x) for x in list(range(-1, -4, -1))])
    gen.generateGridCells()
    gen.addObjects("gridcell", gen.grid_cell_list, isLastObject=True)
    gen.addInitState()
    gen.addGoalState()
    gen.generateProblemPDDL()
    pass

def runPDDLSolver(gen):
    '''
    Runs the fast downward solver to get the optimal plan
    '''
    os.system(FAST_DOWNWARD_DIRECTORY_ABSOLUTE_PATH + 'fast-downward.py ' + PDDL_FILE_ABSOLUTE_PATH + gen.domain_file_name + ' ' + PDDL_FILE_ABSOLUTE_PATH + gen.problem_file_name + ' --search  \"lazy_greedy([ff()], preferred=[ff()])\"' + ' > temp ')

def delete_files(gen) :
    '''
    Deletes PDDL and plan files created.
    '''
    os.remove(PDDL_FILE_ABSOLUTE_PATH + gen.domain_file_name)
    os.remove(PDDL_FILE_ABSOLUTE_PATH + gen.problem_file_name)
    os.remove('sas_plan')

def simulateSolution(env):
    '''
    Simulates the plan given by the solver on the environment
    '''
    env.render()
    plan_file = open('sas_plan', 'r')
    for line in plan_file.readlines() :
        if line[0] == '(' :
            action = line.split()[0][1:]
            print(action)
            coords = [points.split('pt')[2] for points in line.split()[1:3]]
            if action == 'up' :
                if(len(set(coords)) == 1):
                    env.step(env.actions[-1])
                else:
                    env.step(env.actions[0])
            if action == 'down' :
                if(len(set(coords)) == 1):
                    env.step(env.actions[-1])
                else:
                    env.step(env.actions[1])
            if action == 'forward' :
                speed = int(line.split()[-1][:-1])
                env.step(env.actions[speed])
            env.render()

def generatePlan(env):
    '''
    Extracts the plan given by the solver into a list of actions
    '''
    plan_file = open('sas_plan', 'r')
    action_sequence = []
    for line in plan_file.readlines() :
        if line[0] == '(' :
            action = line.split()[0][1:]
            coords = [points.split('pt')[2] for points in line.split()[1:3]]
            if action == 'up' :
                if(len(set(coords)) == 1):
                    action_sequence.append(env.actions[-1])
                else:
                    action_sequence.append(env.actions[0])
            if action == 'down' :
                if(len(set(coords)) == 1):
                    action_sequence.append(env.actions[-1])
                else:
                    action_sequence.append(env.actions[1])
            if action == 'forward' :
                speed = int(line.split()[-1][:-1])
                action_sequence.append(env.actions[speed])
    return action_sequence

def test():
    '''
    Generates the PDDL files, solves for the optimal solution and simulates the plan. The PDDL files are deleted at the end.
    '''

    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('problem', type=str, choices=['parking', 'crossing'], help='problem name')
    parser.add_argument('testcase', type=int, help='test case number')
    args = parser.parse_args()

    test_configs = {}
    test_configs['parking'] = [{'lanes' : [LaneSpec(2, [0, 0])] *3,'width' :5, 'seed' : 13},
                              {'lanes' :  [LaneSpec(2, [0, 0])] *3,'width' :5, 'seed' : 10},
                              {'lanes' :  [LaneSpec(3, [0, 0])] *4,'width' :10, 'seed' : 25},
                              {'lanes' :  [LaneSpec(4, [0, 0])] *4,'width' :10, 'seed' : 25},
                              {'lanes' :  [LaneSpec(8, [0, 0])] *7,'width' :20, 'seed' : 25},
                              {'lanes' :  [LaneSpec(7, [0, 0])] *10,'width' :20, 'seed' : 125}]


    test_configs['crossing'] = [{'lanes' : [LaneSpec(6, [-2, -2])] *10 + [LaneSpec(6, [-5, -5])] *2 +
                                           [LaneSpec(5, [-4, -4])] *2 + [LaneSpec(5, [-3, -3])] *3, 'width' :30, 'seed' : 101}]

    test_config = test_configs[args.problem]
    test_case_number = args.testcase
    LANES = test_config[test_case_number]['lanes']
    WIDTH = test_config[test_case_number]['width']
    RANDOM_SEED = test_config[test_case_number]['seed']

    env=gym.make('GridDriving-v0', lanes=LANES, width=WIDTH, random_seed=RANDOM_SEED, agent_speed_range=(-3,-1))
    gen = initializeSystem(env)
    generateDomainPDDLFile(gen)
    generateProblemPDDLFile(gen)
    runPDDLSolver(gen)
    simulateSolution(env)
    delete_files(gen)


try:
    from runner.abstracts import Agent
except:
    class Agent(object): pass

class PDDLAgent(Agent):
    def initialize(self, fast_downward_path, env):
        global FAST_DOWNWARD_DIRECTORY_ABSOLUTE_PATH
        FAST_DOWNWARD_DIRECTORY_ABSOLUTE_PATH = fast_downward_path
        self.env = env
        gen = initializeSystem(self.env)
        generateDomainPDDLFile(gen)
        generateProblemPDDLFile(gen)
        runPDDLSolver(gen)
        self.action_plan = generatePlan(self.env)
        self.time_step = 0
        delete_files(gen)

    def step(self, state, *args, **kwargs):
        action = self.action_plan[self.time_step]
        self.time_step +=1
        return action

def create_agent(test_case_env, *args, **kwargs):
    return PDDLAgent() 


if __name__ == '__main__':
    test()

class GridWorld:

    def __init__(self, height, width, goal, goal_value=5.0, danger=[], danger_value=-5.0, blocked=[], noise=0.0):
        """
        Initialize the GridWorld environment.
        Creates a gridworld like MDP
         - height (int): Number of rows
         - width (int): Number of columns
         - goal (int): Index number of goal cell
         - goal_value (float): Reward given for goal cell
         - danger (list of int): Indices of cells marked as danger
         - danger_value (float): Reward given for danger cell
         - blocked (list of int): Indices of cells marked as blocked (can't enter)
         - noise (float): probability of resulting state not being what was expected
        """

        self._width = width
        self._height = height
        self._grid_values = [0 for _ in range(height * width)] # Initialize state values.
        self._goal_value = goal_value
        self._danger_value = danger_value
        self._goal_cell = goal
        self._danger_cells = danger
        self._blocked_cells = blocked
        self._noise = noise # Noise level in the environment.
        assert noise >= 0.0 and noise < 1.0 # Ensure valid noise value.
        self.create_next_values() # Initialize the next state values.


    def reset(self):
        """
        Reset the state values to their initial state.
        """
        self._grid_values = [0 for _ in range(self._height * self._width)]
        self.create_next_values()


    def _inbounds(self, state):
        """
        Check if a state index is within the grid boundaries.
        """
        return state >= 0 and state < self._width * self._height

    def _inbounds_rc(self, state_r, state_c):
        """
        Check if row and column indices are within the grid boundaries.
        """
        return state_r >= 0 and state_r < self._height and state_c >= 0 and state_c < self._width

    def _state_to_rc(self, state):
        """
        Convert a state index to row and column indices.
        """
        return state // self._width, state % self._width

    def _state_from_action(self, state, action):
        """
        Gets the state as a result of applying the given action
        """
        #TO DO:
        row, col = self._state_to_rc(state)

        if action == "up":
            temp_row, temp_col = row - 1, col
        elif action == "down":
            temp_row, temp_col = row + 1, col
        elif action == "left":
            temp_row, temp_col = row, col - 1
        elif action == "right":
            temp_row, temp_col = row, col + 1

        temp_state = temp_row * self._width + temp_col

        #if temp state is valid and not blocked, thats the new state;return it
        if self._inbounds_rc(temp_row, temp_col):
            new_state = temp_state
            if new_state not in self._blocked_cells:
                return new_state
        return state #stay put if temp state invalid


    def is_terminal(self, state):
        """
        Returns true if a state is terminal (goal, or danger)
        """
        #To Do:
        if (state == self._goal_cell) or (state in self._danger_cells):
            return True

    def get_states(self):
        """
        Gets all non-terminal states in the environment
        """
        #TO DO:
        states = []
        for s in range(self._height * self._width):
            if not self.is_terminal(s) and s not in self._blocked_cells: #commenting out this part after the and statement doesn't change anything from what I can tell
                states.append(s)
        return states

    def get_actions(self, state):
        """
        Returns a list of valid actions given the current state
        """
        #TO DO:
        actions = []
        row, col = self._state_to_rc(state)
        #check surrouding tiles
        #if legal, in bounds, add to list of valid actions, return list
        if self._inbounds_rc(row - 1, col) and state - self._width not in self._blocked_cells:
            actions.append("up")
        if self._inbounds_rc(row + 1, col) and state + self._width not in self._blocked_cells:
            actions.append("down")
        if self._inbounds_rc(row, col - 1) and state - 1 not in self._blocked_cells:
            actions.append("left")
        if self._inbounds_rc(row, col + 1) and state + 1 not in self._blocked_cells:
            actions.append("right")
        return actions


    def get_reward(self, state):
        """
        Get the reward for being in the current state
        """
        assert self._inbounds(state)
        # Reward is non-zero for danger or goal
        #TO DO:
        if state == self._goal_cell:
            return self._goal_value
        elif state in self._danger_cells:
            return self._danger_value
        else:
            return 0.0

    def get_transitions(self, state, action):
        """
        Get a list of transitions as a result of attempting the action in the current state
        Each item in the list is a dictionary, containing the probability of reaching that state and the state itself
        """
        #TO DO:
        transitions = []
        if self.is_terminal(state):
            return transitions
        temp_state = self._state_from_action(state,action)
        #assuming we do that action, as inteneded
        transitions.append({'prob':1.0-self._noise, 'state':temp_state})
        #accounting for other actions due to noise
        for act in ['up', 'down', 'left', 'right']:
            if act != action:
                temp_state = self._state_from_action(state, act)
                transitions.append({'prob':self._noise/3, 'state':temp_state})

        return transitions


    def get_value(self, state):
        """
        Get the current value of the state
        """
        assert self._inbounds(state)
        return self._grid_values[state]

    def create_next_values(self):
        """
        Creates a temporary storage for state value updating
        If this is not used, then asynchronous updating may result in unexpected results
        To use properly, run this at the start of each iteration
        """
        #TO DO:
        self._next_values = []
        for _ in range(self._height * self._width):
            self._next_values.append(0.0)

    def set_next_values(self):
        """
        Set the state values from the temporary copied values
        To use properly, run this at the end of each iteration
        """
        # TO DO:
        self._grid_values = self._next_values.copy()

    def set_value(self, state, value):
        """
        Set the value of the state into the temporary copy
        This value will not update into main storage until self.set_next_values() is called.
        """
        assert self._inbounds(state)
        #TO DO:
        self._next_values[state] = value
    
    def solve_linear_system(self, discount_factor=1.0):
        """
        Solve the gridworld using a system of linear equations.
        :param discount_factor: The discount factor for future rewards.
        """
        #To Do:
        self.create_next_values()
        while True:
            
            max_diff = 0
            for state in self.get_states():
                if self.is_terminal(state):
                    continue
                #find new value for the state
                max_val = float('-inf')
                old_val = self.get_value(state)
                for action in self.get_actions(state):
                    val = 0
                    transitions = self.get_transitions(state, action)
                    for transition in transitions:
                        next_state = transition['state']
                        prob = transition['prob']
                        reward = self.get_reward(next_state) 
                        val += prob * (reward + discount_factor * self.get_value(next_state))
                    if val > max_val:
                        max_val = val
                self.set_value(state, max_val)
                max_diff = max(max_diff, abs(old_val - max_val))
            self.set_next_values()
            if max_diff < 0.001:
                break
            self.set_next_values()
        return self._grid_values
        

    

    def __str__(self):
        """
        Pretty print the state values
        """
        out_str = ""
        for r in range(self._height):
            for c in range(self._width):
                cell = r * self._width + c
                if cell in self._blocked_cells:
                    out_str += "{:>6}".format("----")
                elif cell == self._goal_cell:
                    out_str += "{:>6}".format("GOAL")
                elif cell in self._danger_cells:
                    out_str += "{:>6.2f}".format(self._danger_value)
                else:
                    out_str += "{:>6.2f}".format(self._grid_values[cell])
                out_str += " "
            out_str += "\n"
        return out_str

def value_iteration(gw, discount, tolerance=0.1):
    #TO DO:
    while True:
        max_diff = 0
        for state in gw.get_states():
            if gw.is_terminal(state):
                continue
            old_val = gw.get_value(state)
            max_val = float('-inf')
            for action in gw.get_actions(state):
                val = 0
                transitions = gw.get_transitions(state, action)
                for transition in transitions:
                    next_state = transition['state']
                    prob = transition['prob']
                    reward = gw.get_reward(next_state)
                    val += prob * (reward + discount * gw.get_value(next_state))
                if val > max_val:
                    max_val = val
            gw.set_value(state, max_val)
            max_diff = max(max_diff, abs(old_val - max_val))
        if max_diff < tolerance:
            break
    return gw._grid_values
import math
import math_tools as m


class Node:
    def __init__(self):
        self.x_ = 0.0  # double
        self.y_ = 0.0  # double
        self.phi_ = 0.0  # double
        self.step_size_ = -1  # double
        self.traversed_x_ = []  # double
        self.traversed_y_ = []  # double
        self.traversed_phi_ = []  # double
        self.x_grid_ = 0  # int
        self.y_grid_ = 0  # int
        self.phi_grid_ = 0  # int
        self.index_ = None  # String
        self.traj_cost_ = 0.0  # double
        self.heuristic_cost_ = 0.0  # double
        self.cost_ = 0.0  # double
        self.steering_ = 0.0  # double
        self.direction_ = True  # true for moving forward and false for moving backward

    def create_1(self, x, y, phi):  # вот замена конструктору
        self.x_ = x
        self.y_ = y
        self.phi_ = phi

    def get_cost(self):
        return self.traj_cost_ + self.heuristic_cost_

    def get_traj_cost(self):
        return self.traj_cost_

    def get_heu_cost(self):
        return self.heuristic_cost_

    def get_x_grid(self):
        return self.x_grid_

    def get_y_grid(self):
        return self.y_grid_

    def get_phi_grid(self):
        return self.phi_grid_

    def get_x(self):
        return self.x_

    def get_y(self):
        return self.y_

    def get_phi(self):
        return self.phi_

    def __eq__(self, other):
        return other.index_ == self.index_

    def get_index_(self):
        return self.index_

    def get_step_size_(self):
        return self.step_size_

    def get_direction(self):
        return self.direction_  # bool

    def get_steering(self):
        return self.steering_

    def get_xs(self):
        return self.traversed_x_

    def get_ys(self):
        return self.traversed_y_

    def get_phis(self):
        return self.traversed_phi_

    def set_direction(self, direct):
        self.direction_ = direct

    def set_traj_cost(self, cost):
        self.traj_cost_ = cost

    def set_heu_cost(self, cost):
        self.heuristic_cost_ = cost

    def set_steer(self, steer):
        self.steering_ = steer

    def create_2(self, x, y, phi, XYbounds):
        if len(XYbounds) != 4:
            print("XYbounds size is not 4, but")
            return
        self.x_ = x
        self.y_ = y
        self.phi_ = phi
        self.x_grid_ = (self.x_ - XYbounds[0] / 1)  # тут используются числа из конфиг файла,мб 0.05
        self.y_grid_ = (self.y_ - XYbounds[2] / 1)
        self.phi_grid_ = (self.phi_ - -math.pi) / 2
        self.traversed_x_.append(x)
        self.traversed_y_.append(y)
        self.traversed_phi_.append(phi)
        self.index_ = m.compute_string_index(self.x_grid_, self.y_grid_, self.phi_grid_)

    def create_3(self, traversed_x, traversed_y, traversed_phi, XYbounds):
        if len(XYbounds) != 4:
            print("XYbounds size is not 4, but")
            return
        if len(traversed_x) != len(traversed_y):
            return
        if len(traversed_x) != len(traversed_phi):
            return
        self.x_ = traversed_x[-1]
        self.y_ = traversed_y[-1]
        self.phi_ = traversed_phi[-1]
        self.x_grid_ = (self.x_ - XYbounds[0] / 1)  # тут используются числа из конфиг файла,мб 0.05
        self.y_grid_ = (self.y_ - XYbounds[2] / 1)
        self.phi_grid_ = (self.phi_ - -math.pi) / 2
        self.traversed_x_ = traversed_x
        self.traversed_y_ = traversed_y
        self.traversed_phi_ = traversed_phi
        self.index_ = m.compute_string_index(self.x_grid_, self.y_grid_, self.phi_grid_)
        self.step_size_ = len(traversed_x)

    def get_bounding_box(self):
        pass

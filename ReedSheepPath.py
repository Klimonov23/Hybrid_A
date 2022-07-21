import math
import math_tools as m


# import Node as n


class Path:
    def __init__(self):
        self.segs_length = []
        self.segs_types = []
        self.total_length = 0.00
        self.x = []  # x positions
        self.y = []  # y positions
        self.phi = []  # angle in radians
        self.directions = []  # directions (1:forward, -1:backward)


class RSParam:
    def __init__(self):
        self.flag = False
        self.t = 0.0
        self.u = 0.0
        self.v = 0.0


class ReedSheep:
    def __init__(self, ca):
        car = ca
        self.max_kappa = math.tan(car.max_steer_angle() / car.steer_ratio()) / car.wheel_base()

    def get_shortest_RSP(self, start_node, end_node, optimal_path):  # pick path from all combinations
        all_possible_paths = []
        if self.generate_RSPs(start_node, end_node,all_possible_paths):
            print("Fail to generate different combination of Reed Shepp paths")
            return False
        optimal_path_len = math.inf
        optimal_path_index = 0
        paths_size = len(all_possible_paths)
        for i in range(0, paths_size):
            if 0 < all_possible_paths[i].total_length < optimal_path_len:
                optimal_path_index = i
                optimal_path_length = all_possible_paths[i].total_length
        if self.generate_local_config(start_node, end_node, all_possible_paths[optimal_path_index]):
            print("Fail to generate local configurations(x, y, phi) in SetRSP")
            return False
        if abs(all_possible_paths[optimal_path_index].x[-1] - end_node.get_x) > 1e-3 or abs(
                all_possible_paths[optimal_path_index].y[-1] - end_node.get_y) > 1e-3 or abs(
            all_possible_paths[optimal_path_index].phi[-1] - end_node.get_pho) > 1e-3:
            print("RSP end position not right")
            return False
            # TODO сделать вывод ошибок
        optimal_path.x = all_possible_paths[optimal_path_index].x
        optimal_path.y = all_possible_paths[optimal_path_index].y
        optimal_path.phi = all_possible_paths[optimal_path_index].phi
        optimal_path.directions = all_possible_paths[optimal_path_index].directions
        optimal_path.total_length = all_possible_paths[optimal_path_index].total_length
        optimal_path.segs_types = all_possible_paths[optimal_path_index].segs_types
        optimal_path.segs_lengths = all_possible_paths[optimal_path_index].segs_lengths
        return True

    def generate_RSPs(self, start_node, end_node, all_possible_paths):  # generate all combinations and interpolate them
        if not self.generate_RSP_parallel(start_node, end_node, all_possible_paths):
            print("Fail to generate general profile of different RSPs")
            return False
        if not self.generate_RSP(start_node, end_node, all_possible_paths):
            print("Fail to generate general profile of different RSPs")
            return False
        return True

    def generate_RSP(self, start_node, end_node,
                     all_possible_paths):  # Set the general profile of the movement primitives
        dx = end_node.get_x() - start_node.get_x()
        dy = end_node.get_y() - start_node.get_y()
        dphi = end_node.get_phi() - start_node.get_phi()
        c = math.cos(start_node.get_phi())
        s = math.sin(start_node.get_phi())
        x = (c * dx + s * dy) * self.max_kappa
        y = (-s * dx + c * dy) * self.max_kappa
        if not self.SCS(x, y, dphi, all_possible_paths):
            print("Fail at SCS")

        if not self.CSC(x, y, dphi, all_possible_paths):
            print("Fail at CSC")

        if not self.CCC(x, y, dphi, all_possible_paths):
            print("Fail at CCC")

        if not self.CCCC(x, y, dphi, all_possible_paths):
            print("Fail at CCCC")

        if not self.CCSC(x, y, dphi, all_possible_paths):
            print("Fail at CCSC")

        if not self.CCSCC(x, y, dphi, all_possible_paths):
            print("Fail at CCSCC")

        if not all_possible_paths:
            print("No path generated by certain two configurations")
            return False

        return True

    def generate_RSP_parallel(self, start_node, end_node,
                              all_possible_paths):  # Set the general profile of the movement primitives parallel implementation
        dx = end_node.get_x - start_node.get_x
        dy = end_node.get_y - start_node.get_y
        dphi = end_node.get_phi - start_node.get_phi
        c = math.cos(start_node.get_phi)
        s = math.sin(start_node.get_phi)
        x = (c * dx + s * dy) * self.max_kappa
        y = (-s * dx + c * dy) * self.max_kappa
        xb = x * math.cos(dphi) + y * math.sin(dphi)
        yb = x * math.sin(dphi) - y * math.cos(dphi)
        RSP_nums = 46
        succ = True
        for i in range(RSP_nums):
            param = RSParam()
            tmp_length = 0
            RSP_length = [0.0, 0.0, 0.0, 0.0, 0.0]
            x_param = 1.0
            y_param = 1.0
            rd_type = None
            if i > 2 and i % 2:
                x_param = -1.0
            if i > 2 and i % 4 < 2:
                y_param = -1.0
            if i < 2:
                if i == 1:
                    y_param = -1.0
                    rd_type = "SRS"
                else:
                    rd_type = "SLS"
                self.SLS(x, y_param * y, y_param * dphi, param)
                tmp_length = 3
                RSP_length[0] = param.t
                RSP_length[1] = param.u
                RSP_length[2] = param.v
            elif i < 6:
                self.LSL(x_param * x, y_param * y, x_param * y_param * dphi, param)
                if y_param > 0:
                    rd_type = "LSL"
                else:
                    rd_type = "RSR"
                tmp_length = 3
                RSP_length[0] = x_param * param.t
                RSP_length[1] = x_param * param.u
                RSP_length[2] = x_param * param.v
            elif i < 10:
                self.LSR(x_param * x, y_param * y, x_param * y_param * dphi, param)
                if y_param > 0:
                    rd_type = "LSR"
                else:
                    rd_type = "RSL"
                tmp_length = 3
                RSP_length[0] = x_param * param.t
                RSP_length[1] = x_param * param.u
                RSP_length[2] = x_param * param.v
            elif i < 14:
                self.LRL(x_param * x, y_param * y, x_param * y_param * dphi, param)
                if y_param > 0:
                    rd_type = "LRL"
                else:
                    rd_type = "RLR"
                tmp_length = 3
                RSP_length[0] = x_param * param.t
                RSP_length[1] = x_param * param.u
                RSP_length[2] = x_param * param.v
            elif i < 18:
                self.LRL(x_param * xb, y_param * yb, x_param * y_param * dphi, param)
                if y_param > 0:
                    rd_type = "LRL"
                else:
                    rd_type = "RLR"
                tmp_length = 3
                RSP_length[0] = x_param * param.v
                RSP_length[1] = x_param * param.u
                RSP_length[2] = x_param * param.t
            elif i < 22:
                self.LRLRn(x_param * x, y_param * y, x_param * y_param * dphi, param)
                if y_param > 0.0:
                    rd_type = "LRLR"
                else:
                    rd_type = "RLRL"
                tmp_length = 4
                RSP_length[0] = x_param * param.t
                RSP_length[1] = x_param * param.u
                RSP_length[2] = -x_param * param.u
                RSP_length[3] = x_param * param.v
            elif i < 26:
                self.LRLRp(x_param * x, y_param * y, x_param * y_param * dphi, param)
                if y_param > 0.0:
                    rd_type = "LRLR"
                else:
                    rd_type = "RLRL"
                tmp_length = 4
                RSP_length[0] = x_param * param.t
                RSP_length[1] = x_param * param.u
                RSP_length[2] = -x_param * param.u
                RSP_length[3] = x_param * param.v
            elif i < 30:
                tmp_length = 4
                self.LRLRn(x_param * x, y_param * y, x_param * y_param * dphi, param)
                if y_param > 0.0:
                    rd_type = "LRSL"
                else:
                    rd_type = "RLSR"
                RSP_length[0] = x_param * param.t
                if x_param < 0 and y_param > 0:
                    RSP_length[1] = 0.5 * math.pi
                else:
                    RSP_length[1] = -0.5 * math.pi
                if x_param > 0 and y_param < 0:
                    RSP_length[2] = param.u
                else:
                    RSP_length[2] = -param.u
                RSP_length[3] = x_param * param.v
            elif i < 34:
                tmp_length = 4
                self.LRLRp(x_param * x, y_param * y, x_param * y_param * dphi, param)
                if y_param:
                    rd_type = "LRSR"
                else:
                    rd_type = "RLSL"
                RSP_length[0] = x_param * param.t
                if x_param < 0 and y_param > 0:
                    RSP_length[1] = 0.5 * math.pi
                else:
                    RSP_length[1] = -0.5 * math.pi
                RSP_length[2] = x_param * param.u
                RSP_length[3] = x_param * param.v
            elif i < 38:
                tmp_length = 4
                self.LRLRn(x_param * xb, y_param * yb, x_param * y_param * dphi, param)
                if y_param > 0:
                    rd_type = "LSRL"
                else:
                    rd_type = "RSLR"
                RSP_length[0] = x_param * param.v
                RSP_length[1] = x_param * param.u
                RSP_length[2] = -x_param * 0.5 * math.pi
                RSP_length[3] = x_param * param.t
            elif i < 42:
                tmp_length = 4
                self.LRLRp(x_param * xb, y_param * yb, x_param * y_param * dphi, param)
                if y_param > 0:
                    rd_type = "RSRL"
                else:
                    rd_type = "LSLR"
                RSP_length[0] = x_param * param.v
                RSP_length[1] = x_param * param.u
                RSP_length[2] = -x_param * math.pi * 0.5
                RSP_length[3] = x_param * param.t
            else:
                tmp_length = 5
                self.LRSLR(x_param * x, y_param * y, x_param * y_param * dphi, param)
                if y_param > 0.0:
                    rd_type = "LRSLR"
                else:
                    rd_type = "RLSRL"
                RSP_length[0] = x_param * param.t
                RSP_length[1] = -x_param * 0.5 * math.pi
                RSP_length[2] = x_param * param.u
                RSP_length[3] = -x_param * 0.5 * math.pi
                RSP_length[4] = x_param * param.v
            if tmp_length > 0:
                if param.flag == True and self.set_RSP_parallel(tmp_length, RSP_length, rd_type, all_possible_paths,
                                                                i) is False:
                    print("Fail at SetRSP, idx#: " + str(i))
                    succ = False
        if succ == False: return False
        if len(all_possible_paths) == 0: return False
        return True

    def generate_local_config(self, start_node, end_node,
                              shortest_path):  # Set local exact configurations profile of each
        # movement primitive
        step_scaled = 4 * self.max_kappa  # Пацаны,тут мб 0.5, при тесте узнаем
        point_num = math.floor(shortest_path.total_length / step_scaled + len(shortest_path.segs_lengths) + 4)
        px = [0.0 for i in range(point_num)]
        py = [0.0 for i in range(point_num)]
        py = [0.0 for i in range(point_num)]
        pphi = [0.0 for i in range(point_num)]
        pdirections = [True for i in range(point_num)]
        index = 1
        d = 0.0
        pd = 0.0
        ll = 0.0
        if shortest_path.segs_lengths[0] > 0.0:
            pdirections[0] = True
            d = step_scaled
        else:
            pdirections[0] = False
            d = -step_scaled
        pd = d
        for i in range(len(shortest_path.segs_types)):
            ma = shortest_path.segs_types[i]
            l = shortest_path.segs_lengths[i]
            if l > 0.0:
                d = step_scaled
            else:
                d = -step_scaled
            ox = px[index]
            oy = py[index]
            ophi = pphi[index]
            index = index - 1
            if i >= 1 and shortest_path.segs_lengths[i - 1] * shortest_path.segs_lengths[i] > 0:
                pd = -d - ll
            else:
                pd = d - ll
            while abs(pd) <= abs(l):
                index += 1
                self.interpolate(index, pd, ma, ox, oy, ophi, px, py, pphi, pdirections)
                pd += d
            ll = l - pd - d
            index += 1
            self.interpolate(index, l, ma, ox, oy, ophi, px, py, pphi, pdirections)
        epsilon = 1e-15
        while math.fabs(px[-1]) < epsilon and math.fabs(py[-1]) < epsilon and math.fabs(pphi[-1]) < epsilon and \
                pdirections[-1]:
            px.pop()
            py.pop()
            pphi.pop()
            pdirections.pop()
        for i in range(len(px)):
            shortest_path.x.append(
                math.cos(-start_node.get_phi()) * px[i] + math.sin(-start_node.get_phi()) * py[i] + start_node.get_x())
            shortest_path.y.append(
                -math.sin(-start_node.get_phi) * px[i] + math.cos(-start_node.get_phi) * py[i] + start_node.get_y())
            shortest_path.phi.append(m.normalize_angle(pphi[i] + start_node.get_phi()))
        shortest_path.directions = pdirections
        for i in range(len(shortest_path.segs_lengths)):
            shortest_path.segs_lengths[i] = shortest_path.segs_lengths[i] / self.max_kappa
        shortest_path.total_length = shortest_path.total_length / self.max_kappa
        return True

    def interpolate(self, ind, pd, m, ox, oy, ophi, px, py, pphi,
                    pdirections):  # interpolation is used in generate_local_config
        ldx = 0.0
        ldy = 0.0
        gdx = 0.0
        gdy = 0.0
        if m == 'S':
            px[ind] = ox + pd / self.max_kappa * math.cos(ophi)
            py[ind] = oy + pd / self.max_kappa * math.sin(ophi)
            pphi[ind] = ophi
        else:
            ldx = math.sin(pd) / self.max_kappa
            if m == 'L':
                ldy = (1.0 - math.cos(pd)) / self.max_kappa
            elif m == 'R':
                ldy = (1.0 - math.cos(pd)) / -self.max_kappa
            gdx = math.cos(-ophi) * ldx + math.sin(-ophi) * ldy
            gdy = -math.sin(-ophi) * ldx + math.cos(-ophi) * ldy
            px[ind] = ox + gdx
            py[ind] = oy + gdy
        if pd > 0.0:
            pdirections[ind] = True
        else:
            pdirections[ind] = False
        if m == 'L':
            pphi[ind] = ophi + pd
        elif m == 'R':
            pphi[ind] = ophi - pd

    def set_RSP(self, size, lengths, types, all_possible_paths):  # motion primitives combination setup function
        path = Path()
        length_vec = [lengths + size for i in range(lengths)]
        type_vec = [types[0] + size for i in range(types[0])]
        path.segs_lengths = length_vec
        path.segs_types = type_vec
        sum = 0.0
        for i in range(size):
            sum += abs(lengths[i])
        path.total_length = sum
        if path.total_length <= 0.0:
            print("total length smaller than 0")
            return False
        all_possible_paths.append(path)
        return True

    def set_RSP_parallel(self, size, lengths, types,
                         all_possible_paths, ind):  # motion primitives combination setup function(par impl)
        path = Path()
        length_vec = [lengths + size for i in range(lengths)]
        type_vec = [types[0] + size for i in range(types[0])]
        path.segs_lengths = length_vec
        path.segs_types = type_vec
        sum = 0.0
        for i in range(size):
            sum += abs(lengths[i])
        path.total_length = sum
        if path.total_length <= 0.0:
            print("total length smaller than 0")
            return False
        all_possible_paths[ind] = path
        return True

    def SCS(self, x, y, phi, all_possible_paths, ):
        sls_param = RSParam()
        self.SLS(x, y, phi, sls_param)
        sls_length = [sls_param.t, sls_param.u, sls_param.v]
        sls_types = "SLS"
        if sls_param.flag and not self.set_RSP(3, sls_length, sls_types, all_possible_paths):
            print("Fail at SetRSP with SLS_param")
            return False

        srs_param = RSParam()
        self.SLS(x, -y, -phi, sls_param)
        srs_length = [srs_param.t, srs_param.u, srs_param.v]
        srs_types = "SLS"
        if srs_param.flag and not self.set_RSP(3, srs_length, srs_types, all_possible_paths):
            print("Fail at SetRSP with SRS_param")
            return False
        return True

    def CSC(self, x, y, phi, all_possible_paths):
        LSL1_param = RSParam()
        self.LSL(x, y, phi, LSL1_param)
        LSL1_length = [LSL1_param.t, LSL1_param.u, LSL1_param.v]
        LSL1_types = "LSL"
        if LSL1_param.flag and not self.set_RSP(3, LSL1_length, LSL1_types, all_possible_paths):
            print("Fail at SetRSP with LSL_param")
            return False

        LSL2_param = RSParam()
        self.LSL(-x, y, -phi, LSL2_param)
        LSL2_lengths = [-LSL2_param.t, -LSL2_param.u, -LSL2_param.v]
        LSL2_types = "LSL"
        if LSL2_param.flag and not self.set_RSP(3, LSL2_lengths, LSL2_types, all_possible_paths):
            print("Fail at SetRSP with LSL_param")
            return False

        LSL3_param = RSParam()
        self.LSL(x, -y, -phi, LSL3_param)
        LSL3_lengths = [LSL3_param.t, LSL3_param.u, LSL3_param.v]
        LSL3_types = "RSR"
        if LSL3_param.flag and not self.set_RSP(3, LSL3_lengths, LSL3_types, all_possible_paths):
            print("Fail at SetRSP with LSL3_param")
            return False

        LSL4_param = RSParam()
        self.LSL(-x, -y, phi, LSL4_param)
        LSL4_lengths = [-LSL4_param.t, -LSL4_param.u, -LSL4_param.v]
        LSL4_types = "RSR"
        if LSL4_param.flag and not self.set_RSP(3, LSL4_lengths, LSL4_types, all_possible_paths):
            print("Fail at SetRSP with LSL4_param")
            return False

        LSR1_param = RSParam()
        self.LSR(x, y, phi, LSR1_param)
        LSR1_lengths = [LSR1_param.t, LSR1_param.u, LSR1_param.v]
        LSR1_types = "LSR"
        if LSR1_param.flag and not self.set_RSP(3, LSR1_lengths, LSR1_types, all_possible_paths):
            print("Fail at SetRSP with LSR1_param")
            return False

        LSR2_param = RSParam()
        self.LSR(-x, y, -phi, LSR2_param)
        LSR2_lengths = [-LSR2_param.t, -LSR2_param.u, -LSR2_param.v]
        LSR2_types = "LSR"
        if LSR2_param.flag and not self.set_RSP(3, LSR2_lengths, LSR2_types, all_possible_paths):
            print("Fail at SetRSP with LSR2_param")
            return False

        LSR3_param = RSParam()
        self.LSR(x, -y, -phi, LSR3_param)
        LSR3_lengths = [LSR3_param.t, LSR3_param.u, LSR3_param.v]
        LSR3_types = "RSL"
        if LSR3_param.flag and not self.set_RSP(3, LSR3_lengths, LSR3_types, all_possible_paths):
            print("Fail at SetRSP with LSR3_param")
            return False

        LSR4_param = RSParam()
        self.LSR(-x, -y, phi, LSR4_param)
        LSR4_lengths = [-LSR4_param.t, -LSR4_param.u, -LSR4_param.v]
        LSR4_types = "RSL"
        if LSR4_param.flag and not self.set_RSP(3, LSR4_lengths, LSR4_types, all_possible_paths):
            print("Fail at SetRSP with LSR4_param")
            return False
        return True

    def CCC(self, x, y, phi, all_possible_paths):
        LRL1_param = RSParam()
        self.LRL(x, y, phi, LRL1_param)
        LRL1_lengths = [LRL1_param.t, LRL1_param.u, LRL1_param.v]
        LRL1_types = "LRL"
        if LRL1_param.flag and not self.set_RSP(3, LRL1_lengths, LRL1_types, all_possible_paths):
            print("Fail at SetRSP with LRL_param")
            return False

        LRL2_param = RSParam()
        self.LRL(-x, y, -phi, LRL2_param)
        LRL2_lengths = [-LRL2_param.t, -LRL2_param.u, -LRL2_param.v]
        LRL2_types = "LRL"
        if LRL2_param.flag and not self.set_RSP(3, LRL2_lengths, LRL2_types, all_possible_paths):
            print("Fail at SetRSP with LRL2_param")
            return False

        LRL3_param = RSParam()
        self.LRL(x, -y, -phi, LRL3_param)
        LRL3_lengths = [LRL3_param.t, LRL3_param.u, LRL3_param.v]
        LRL3_types = "RLR"
        if LRL3_param.flag and not self.set_RSP(3, LRL3_lengths, LRL3_types, all_possible_paths):
            print("Fail at SetRSP with LRL3_param")
            return False

        LRL4_param = RSParam()
        self.LRL(-x, -y, phi, LRL4_param)
        LRL4_lengths = [-LRL4_param.t, -LRL4_param.u, -LRL4_param.v]
        LRL4_types = "RLR"
        if LRL4_param.flag and not self.set_RSP(3, LRL4_lengths, LRL4_types, all_possible_paths):
            print("Fail at SetRSP with LRL4_param")
            return False

        xb = x * math.cos(phi) + y * math.sin(phi)
        yb = x * math.sin(phi) - y * math.cos(phi)  # backwards points

        LRL5_param = RSParam()
        self.LRL(xb, yb, phi, LRL5_param)
        LRL5_lengths = [LRL5_param.v, LRL5_param.u, LRL5_param.t]
        LRL5_types = "LRL"
        if LRL5_param.flag and not self.set_RSP(3, LRL5_lengths, LRL5_types, all_possible_paths):
            print("Fail at SetRSP with LRL5_param")
            return False

        LRL6_param = RSParam()
        self.LRL(-xb, yb, -phi, LRL6_param)
        LRL6_lengths = [-LRL6_param.v, -LRL6_param.u, -LRL6_param.t]
        LRL6_types = "LRL"
        if LRL6_param.flag and not self.set_RSP(3, LRL6_lengths, LRL6_types, all_possible_paths):
            print("Fail at SetRSP with LRL6_param")
            return False

        LRL7_param = RSParam()
        self.LRL(xb, -yb, -phi, LRL7_param)
        LRL7_lengths = [LRL7_param.v, LRL7_param.u, LRL7_param.t]
        LRL7_types = "RLR"
        if LRL7_param.flag and not self.set_RSP(3, LRL7_lengths, LRL7_types, all_possible_paths):
            print("Fail at SetRSP with LRL7_param")
            return False

        LRL8_param = RSParam()
        self.LRL(-xb, -yb, phi, LRL8_param)
        LRL8_lengths = [-LRL8_param.v, -LRL8_param.u, -LRL8_param.t]
        LRL8_types = "RLR"
        if LRL8_param.flag and not self.set_RSP(3, LRL8_lengths, LRL8_types, all_possible_paths):
            print("Fail at SetRSP with LRL8_param")
            return False

        return True

    def CCCC(self, x, y, phi, all_possible_paths):
        LRLRn1_param = RSParam()
        self.LRLRn(x, y, phi, LRLRn1_param)
        LRLRn1_lengths = [LRLRn1_param.t, LRLRn1_param.u, -LRLRn1_param.u, LRLRn1_param.v]
        LRLRn1_types = "LRLR"
        if LRLRn1_param.flag and not self.set_RSP(4, LRLRn1_lengths, LRLRn1_types, all_possible_paths):
            print("Fail at SetRSP with LRLRn1_param")
            return False

        LRLRn2_param = RSParam()
        self.LRLRn(-x, y, -phi, LRLRn2_param)
        LRLRn2_lengths = [-LRLRn2_param.t, -LRLRn2_param.u, LRLRn2_param.u, -LRLRn2_param.v]
        LRLRn2_types = "LRLR"
        if LRLRn2_param.flag and not self.set_RSP(4, LRLRn2_lengths, LRLRn2_types, all_possible_paths):
            print("Fail at SetRSP with LRLRn2_param")
            return False

        LRLRn3_param = RSParam()
        self.LRLRn(x, -y, -phi, LRLRn3_param)
        LRLRn3_lengths = [LRLRn3_param.t, LRLRn3_param.u, -LRLRn3_param.u, LRLRn3_param.v]
        LRLRn3_types = "RLRL"
        if LRLRn3_param.flag and not self.set_RSP(4, LRLRn3_lengths, LRLRn3_types, all_possible_paths):
            print("Fail at SetRSP with LRLRn3_param")
            return False

        LRLRn4_param = RSParam()
        self.LRLRn(-x, -y, phi, LRLRn4_param)
        LRLRn4_lengths = [-LRLRn4_param.t, -LRLRn4_param.u, LRLRn4_param.u, -LRLRn4_param.v]
        LRLRn4_types = "RLRL"
        if LRLRn4_param.flag and not self.set_RSP(4, LRLRn4_lengths, LRLRn4_types, all_possible_paths):
            print("Fail at SetRSP with LRLRn4_param")
            return False

        LRLRp1_param = RSParam()
        self.LRLRp(x, y, phi, LRLRp1_param)
        LRLRp1_lengths = [LRLRp1_param.t, LRLRp1_param.u, LRLRp1_param.u, LRLRp1_param.v]
        LRLRp1_types = "LRLR"
        if LRLRp1_param.flag and not self.set_RSP(4, LRLRp1_lengths, LRLRp1_types, all_possible_paths):
            print("Fail at SetRSP with LRLRp1_param")
            return False

        LRLRp2_param = RSParam()
        self.LRLRp(-x, y, -phi, LRLRp2_param)
        LRLRp2_lengths = [-LRLRp2_param.t, -LRLRp2_param.u, -LRLRp2_param.u, -LRLRp2_param.v]
        LRLRp2_types = "LRLR"
        if LRLRp2_param.flag and not self.set_RSP(4, LRLRp2_lengths, LRLRp2_types, all_possible_paths):
            print("Fail at SetRSP with LRLRp2_param")
            return False

        LRLRp3_param = RSParam()
        self.LRLRp(x, -y, -phi, LRLRp3_param)
        LRLRp3_lengths = [LRLRp3_param.t, LRLRp3_param.u, LRLRp3_param.u, LRLRp3_param.v]
        LRLRp3_types = "RLRL"
        if LRLRp3_param.flag and not self.set_RSP(4, LRLRp3_lengths, LRLRp3_types, all_possible_paths):
            print("Fail at SetRSP with LRLRp3_param")
            return False

        LRLRp4_param = RSParam()
        self.LRLRp(-x, -y, phi, LRLRp4_param)
        LRLRp4_lengths = [-LRLRp4_param.t, -LRLRp4_param.u, -LRLRp4_param.u, -LRLRp4_param.v]
        LRLRp4_types = "RLRL"
        if LRLRp4_param.flag and not self.set_RSP(4, LRLRp4_lengths, LRLRp4_types, all_possible_paths):
            print("Fail at SetRSP with LRLRp4_param")
            return False

        return True

    def CCSC(self, x, y, phi, all_possible_paths):
        LRSL1_param = RSParam()
        self.LRSL(x, y, phi, LRSL1_param)
        LRSL1_lengths = [LRSL1_param.t, -0.5 * math.pi, -LRSL1_param.u,
                         LRSL1_param.v]
        LRSL1_types = "LRSL"
        if LRSL1_param.flag and not self.set_RSP(4, LRSL1_lengths, LRSL1_types, all_possible_paths):
            print("Fail at SetRSP with LRSL1_param")
            return False

        LRSL2_param = RSParam()
        self.LRSL(-x, y, -phi, LRSL2_param)
        LRSL2_lengths = [-LRSL2_param.t, 0.5 * math.pi, -LRSL2_param.u, -LRSL2_param.v]
        LRSL2_types = "LRSL"
        if LRSL2_param.flag and not self.set_RSP(4, LRSL2_lengths, LRSL2_types, all_possible_paths):
            print("Fail at SetRSP with LRSL2_param")
            return False

        LRSL3_param = RSParam()
        self.LRSL(x, -y, -phi, LRSL3_param)
        LRSL3_lengths = [LRSL3_param.t, -0.5 * math.pi, LRSL3_param.u, LRSL3_param.v]
        LRSL3_types = "RLSR"
        if LRSL3_param.flag and not self.set_RSP(4, LRSL3_lengths, LRSL3_types, all_possible_paths):
            print("Fail at SetRSP with LRSL3_param")
            return False

        LRSL4_param = RSParam()
        self.LRSL(-x, -y, phi, LRSL4_param)
        LRSL4_lengths = [-LRSL4_param.t, -0.5 * math.pi, -LRSL4_param.u, -LRSL4_param.v]
        LRSL4_types = "RLSR"
        if LRSL4_param.flag and not self.set_RSP(4, LRSL4_lengths, LRSL4_types, all_possible_paths):
            print("Fail at SetRSP with LRSL4_param")
            return False

        LRSR1_param = RSParam()
        self.LRSR(x, y, phi, LRSR1_param)
        LRSR1_lengths = [LRSR1_param.t, -0.5 * math.pi, LRSR1_param.u, LRSR1_param.v]
        LRSR1_types = "LRSR"
        if LRSR1_param.flag and not self.set_RSP(4, LRSR1_lengths, LRSR1_types, all_possible_paths):
            print("Fail at SetRSP with LRSR1_param")
            return False

        LRSR2_param = RSParam()
        self.LRSR(-x, y, -phi, LRSR2_param)
        LRSR2_lengths = [-LRSR2_param.t, 0.5 * math.pi, -LRSR2_param.u, -LRSR2_param.v]
        LRSR2_types = "LRSR"
        if LRSR2_param.flag and not self.set_RSP(4, LRSR2_lengths, LRSR2_types, all_possible_paths):
            print("Fail at SetRSP with LRSR2_param")
            return False

        LRSR3_param = RSParam()
        self.LRSR(x, -y, -phi, LRSR3_param)
        LRSR3_lengths = [LRSR3_param.t, -0.5 * math.pi, LRSR3_param.u, LRSR3_param.v]
        LRSR3_types = "RLSL"
        if LRSR3_param.flag and not self.set_RSP(4, LRSR3_lengths, LRSR3_types, all_possible_paths):
            print("Fail at SetRSP with LRSR3_param")
            return False

        LRSR4_param = RSParam()
        self.LRSR(-x, -y, phi, LRSR4_param)
        LRSR4_lengths = [-LRSR4_param.t, 0.5 * math.pi, -LRSR4_param.u, -LRSR4_param.v]
        LRSR4_types = "RLSL"
        if LRSR4_param.flag and not self.set_RSP(4, LRSR4_lengths, LRSR4_types, all_possible_paths):
            print("Fail at SetRSP with LRSR4_param")
            return False

        # backward

        xb = x * math.cos(phi) + y * math.sin(phi)
        yb = x * math.sin(phi) - y * math.cos(phi)

        LRSL5_param = RSParam()
        self.LRSL(xb, yb, phi, LRSL5_param)
        LRSL5_lengths = [LRSL5_param.v, LRSL5_param.u, -0.5 * math.pi, LRSL5_param.t]
        LRSL5_types = "LSRL"
        if LRSL5_param.flag and not self.set_RSP(4, LRSL5_lengths, LRSL5_types, all_possible_paths):
            print("Fail at SetRSP with LRLRn_param")
            return False

        LRSL6_param = RSParam()
        self.LRSL(-xb, yb, -phi, LRSL6_param)
        LRSL6_lengths = [-LRSL6_param.v, -LRSL6_param.u, 0.5 * math.pi, -LRSL6_param.t]
        LRSL6_types = "LSRL"
        if LRSL6_param.flag and not self.set_RSP(4, LRSL6_lengths, LRSL6_types, all_possible_paths):
            print("Fail at SetRSP with LRSL6_param")
            return False

        LRSL7_param = RSParam()
        self.LRSL(xb, -yb, -phi, LRSL7_param)
        LRSL7_lengths = [LRSL7_param.v, LRSL7_param.u, -0.5 * math.pi, LRSL7_param.t]
        LRSL7_types = "RSLR"
        if LRSL7_param.flag and not self.set_RSP(4, LRSL7_lengths, LRSL7_types, all_possible_paths):
            print("Fail at SetRSP with LRSL7_param")
            return False

        LRSL8_param = RSParam()
        self.LRSL(-xb, -yb, phi, LRSL8_param)
        LRSL8_lengths = [-LRSL8_param.v, -LRSL8_param.u, 0.5 * math.pi, -LRSL8_param.t]
        LRSL8_types = "RSLR"
        if LRSL8_param.flag and not self.set_RSP(4, LRSL8_lengths, LRSL8_types, all_possible_paths):
            print("Fail at SetRSP with LRSL8_param")
            return False

        LRSR5_param = RSParam()
        self.LRSR(xb, yb, phi, LRSR5_param)
        LRSR5_lengths = [LRSR5_param.v, LRSR5_param.u, -0.5 * math.pi, LRSR5_param.t]
        LRSR5_types = "RSRL"
        if LRSR5_param.flag and not self.set_RSP(4, LRSR5_lengths, LRSR5_types, all_possible_paths):
            print("Fail at SetRSP with LRSR5_param")
            return False

        LRSR6_param = RSParam()
        self.LRSR(-xb, yb, -phi, LRSR6_param)
        LRSR6_lengths = [-LRSR6_param.v, -LRSR6_param.u, 0.5 * math.pi, -LRSR6_param.t]
        LRSR6_types = "RSRL"
        if LRSR6_param.flag and not self.set_RSP(4, LRSR6_lengths, LRSR6_types, all_possible_paths):
            print("Fail at SetRSP with LRSR6_param")
            return False

        LRSR7_param = RSParam()
        self.LRSR(xb, -yb, -phi, LRSR7_param)
        LRSR7_lengths = [LRSR7_param.v, LRSR7_param.u, -0.5 * math.pi, LRSR7_param.t]
        LRSR7_types = "LSLR"
        if LRSR7_param.flag and not self.set_RSP(4, LRSR7_lengths, LRSR7_types, all_possible_paths):
            print("Fail at SetRSP with LRSR7_param")
            return False

        LRSR8_param = RSParam()
        self.LRSR(-xb, -yb, phi, LRSR8_param)
        LRSR8_lengths = [-LRSR8_param.v, -LRSR8_param.u, 0.5 * math.pi, -LRSR8_param.t]
        LRSR8_types = "LSLR"
        if LRSR8_param.flag and not self.set_RSP(4, LRSR8_lengths, LRSR8_types, all_possible_paths):
            print("Fail at SetRSP with LRSR8_param")
            return False
        return True

    def CCSCC(self, x, y, phi, all_possible_paths):
        LRSLR1_param = RSParam()
        self.LRSLR(x, y, phi, LRSLR1_param)
        LRSLR1_lengths = [LRSLR1_param.t, -0.5 * math.pi, LRSLR1_param.u, -0.5 * math.pi, LRSLR1_param.v]
        LRSLR1_types = "LRSLR"
        if LRSLR1_param.flag and not self.set_RSP(5, LRSLR1_lengths, LRSLR1_types, all_possible_paths):
            print("Fail at SetRSP with LRSLR1_param")
            return False

        LRSLR2_param = RSParam()
        self.LRSLR(-x, y, -phi, LRSLR2_param)
        LRSLR2_lengths = [-LRSLR2_param.t, 0.5 * math.pi, -LRSLR2_param.u, 0.5 * math.pi, -LRSLR2_param.v]
        LRSLR2_types = "LRSLR"
        if LRSLR2_param.flag and not self.set_RSP(5, LRSLR2_lengths, LRSLR2_types, all_possible_paths):
            print("Fail at SetRSP with LRSLR2_param")
            return False

        LRSLR3_param = RSParam()
        self.LRSLR(x, -y, -phi, LRSLR3_param)
        LRSLR3_lengths = [LRSLR3_param.t, -0.5 * math.pi, LRSLR3_param.u, -0.5 * math.pi, LRSLR3_param.v]
        LRSLR3_types = "RLSRL"
        if LRSLR3_param.flag and not self.set_RSP(5, LRSLR3_lengths, LRSLR3_types, all_possible_paths):
            print("Fail at SetRSP with LRSLR3_param")
            return False

        LRSLR4_param = RSParam()
        self.LRSLR(-x, -y, phi, LRSLR4_param)
        LRSLR4_lengths = [-LRSLR4_param.t, 0.5 * math.pi, -LRSLR4_param.u, 0.5 * math.pi, -LRSLR4_param.v]
        LRSLR4_types = "RLSRL"
        if LRSLR4_param.flag and not self.set_RSP(5, LRSLR4_lengths, LRSLR4_types, all_possible_paths):
            print("Fail at SetRSP with LRSLR4_param")
            return False

        return True

    def LSL(self, x, y, phi, rs_param):
        polar = m.cartesian_to_polar(x - math.sin(phi), y - 1.0 + math.cos(phi))
        u = polar[0]
        t = polar[1]
        v = 0.0
        if t >= 0.0:
            v = m.normalize_angle(phi - t)
            if v >= 0.0:
                rs_param.flag = True
                rs_param.u = u
                rs_param.t = t
                rs_param.v = v

    def LSR(self, x, y, phi, rs_param):
        polar = m.cartesian_to_polar(x + math.sin(phi), y - 1.0 - math.cos(phi))
        u1 = polar[0] * polar[0]
        t1 = polar[1]
        u = 0.0
        theta = 0.0
        t = 0.0
        v = 0.0
        if u1 >= 4.0:
            u = math.sqrt(u1 - 4.0)
            theta = math.atan2(2.0, u)
            t = m.normalize_angle(t1 + theta)
            v = m.normalize_angle(t - phi)
            if t >= 0.0 and v >= 0.0:
                rs_param.flag = True
                rs_param.u = u
                rs_param.t = t
                rs_param.v = v

    def LRL(self, x, y, phi, rs_param):
        polar = m.cartesian_to_polar(x - math.sin(phi), y - 1.0 + math.cos(phi))
        u1 = polar[0]
        t1 = polar[1]
        u = 0.0
        t = 0.0
        v = 0.0
        if u1 <= 4.0:
            u = -2.0 * math.asin(0.25 * u1)
            t = m.normalize_angle(t1 + 0.5 * u + math.pi)
            v = m.normalize_angle(phi - t + u)
            if t >= 0.0 and u <= 0.0:
                rs_param.flag = True
                rs_param.u = u
                rs_param.t = t
                rs_param.v = v

    def SLS(self, x, y, phi, rs_param):
        phi_mod = m.normalize_angle(phi)
        xd = 0.0
        u = 0.0
        t = 0.0
        v = 0.0
        epsilon = 1e-1
        if y > 0.0 and epsilon < phi_mod < math.pi:
            xd = -y / math.tan(phi_mod) + x
            t = xd - math.tan(phi_mod / 2.0)
            u = phi_mod
            v = math.sqrt((x - xd) * (x - xd) + y * y) - math.tan(phi_mod / 2.0)
            rs_param.flag = True
            rs_param.u = u
            rs_param.t = t
            rs_param.v = v
        elif y < 0.0 and epsilon < phi_mod < math.pi:
            xd = -y / math.tan(phi_mod) + x
            t = xd - math.tan(phi_mod / 2.0)
            u = phi_mod
            v = - math.sqrt((x - xd) * (x - xd) + y * y) - math.tan(phi_mod / 2.0)
            rs_param.flag = True
            rs_param.u = u
            rs_param.t = t
            rs_param.v = v

    def LRLRn(self, x, y, phi, rs_param):
        xi = x + math.sin(phi)
        eta = y - 1.0 - math.cos(phi)
        rho = 0.25 * (2.0 + math.sqrt(xi * xi + eta * eta))
        u = 0.0
        if 1.0 >= rho >= 0.0:
            u = math.acos(rho)
            if 0 <= u <= 0.5 * math.pi:
                tau_omega = m.calc_tau_omega(u, -u, xi, eta, phi)
                if tau_omega[0] >= 0.0 and tau_omega[1] <= 0.0:
                    rs_param.flag = True
                    rs_param.u = u
                    rs_param.t = tau_omega[0]
                    rs_param.v = tau_omega[1]

    def LRLRp(self, x, y, phi, rs_param):
        xi = x + math.sin(phi)
        eta = y - 1.0 - math.cos(phi)
        rho = (20.0 - xi * xi - eta * eta) / 16.0
        u = 0.0
        if 1.0 >= rho >= 0.0:
            u = math.acos(rho)
            if 0 <= u <= 0.5 * math.pi:
                tau_omega = m.calc_tau_omega(u, u, xi, eta, phi)
                if tau_omega[0] >= 0.0 and tau_omega[1] >= 0.0:
                    rs_param.flag = True
                    rs_param.u = u
                    rs_param.t = tau_omega[0]
                    rs_param.v = tau_omega[1]

    def LRSR(self, x, y, phi, rs_param):
        xi = x + math.sin(phi)
        eta = y - 1.0 - math.cos(phi)
        polar = m.cartesian_to_polar(-eta, xi)
        rho = polar[0]
        theta = polar[1]
        t = 0.0
        u = 0.0
        v = 0.0
        if rho >= 2.0:
            t = theta
            u = 2.0 - rho
            v = m.normalize_angle(t + 0.5 * math.pi - phi)
            if t >= 0.0 and u <= 0.0 and v <= 0.0:
                rs_param.flag = True
                rs_param.u = u
                rs_param.t = t
                rs_param.v = v

    def LRSL(self, x, y, phi, rs_param):
        xi = x - math.sin(phi)
        eta = y - 1.0 + math.cos(phi)
        polar = m.cartesian_to_polar(xi, eta)
        rho = polar[0]
        theta = polar[1]
        r = 0.0
        t = 0.0
        u = 0.0
        v = 0.0
        if rho >= 2.0:
            r = math.sqrt(rho * rho - 4.0)
            u = 2.0 - rho
            t = m.normalize_angle(theta + math.atan2(r, -2.0))
            v = m.normalize_angle(phi - 0.5 * math.pi - t)
            if t >= 0.0 and u <= 0.0 and v <= 0.0:
                rs_param.flag = True
                rs_param.u = u
                rs_param.t = t
                rs_param.v = v

    def LRSLR(self, x, y, phi, rs_param):
        xi = x + math.sin(phi)
        eta = y - 1.0 - math.cos(phi)
        polar = m.cartesian_to_polar(xi, eta)
        rho = polar[0]
        t = 0.0
        u = 0.0
        v = 0.0
        if rho >= 2.0:
            u = 4.0 - math.sqrt(rho * rho - 4.0)
            if u <= 0.0:
                t = m.normalize_angle(math.atan2((4.0 - u) * xi - 2.0 * eta, -2.0 * xi + (u - 4.0) * eta))
                v = m.normalize_angle(t - phi)
                if t >= 0.0 and v >= 0.0:
                    rs_param.flag = True
                    rs_param.u = u
                    rs_param.t = t
                    rs_param.v = v

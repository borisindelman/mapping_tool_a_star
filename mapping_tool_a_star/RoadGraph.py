import matplotlib.pyplot as plt
import math

from mapping_tool_a_star.PriorityQueue import PriorityQueue


class RoadGraph:
    def __init__(self, width=0, height=0, resolution=0):
        self.width = width
        self.height = height
        self.resolution = resolution
        self.intersections = {}

    def neighbours(self, intersection_id):
        return self.intersections[intersection_id]

    def cost(self, from_node, to_node):
        return self.intersections[from_node][to_node]

    def compare_points(self, point_a, point_b):
        point_a = (int(point_a[0]), int(point_a[1]))
        point_b = (int(point_b[0]), int(point_b[1]))
        for idx in range(-self.resolution, self.resolution + 1):
            for idy in range(-self.resolution, self.resolution + 1):
                current_node = (point_a[0] + idx, point_a[1] + idy)
                if current_node == point_b:
                    return True
        return False

    def node_exists(self, node):
        node = (int(node[0]), int(node[1]))
        for idx in range(-self.resolution, self.resolution + 1):
            for idy in range(-self.resolution, self.resolution + 1):
                current_node = (node[0] + idx, node[1] + idy)
                if current_node in self.intersections:
                    return current_node
        return False

    def rod_exists(self, node_a, node_b):
        node_a = (int(node_a[0]), int(node_a[1]))
        node_b = (int(node_b[0]), int(node_b[1]))
        if self.node_exists(node_a) and self.node_exists(node_b) and node_a != node_b:
            if node_b in self.intersections[node_a]:
                return True
        return False

    def add_node(self, node):
        node = (int(node[0]), int(node[1]))
        if not self.node_exists(node):
            self.intersections[node] = {}
            return True
        return False

    def remove_node(self, node):
        node = (int(node[0]), int(node[1]))
        node = self.node_exists(node)
        if node:
            del self.intersections[node]
            for each in self.intersections:
                if node in self.intersections[each]:
                    del self.intersections[each][node]
            return True
        else:
            return False

    def add_rod(self, node_a, node_b, path, add_nodes=False):
        if not add_nodes:
            nearest_node_a = self.node_exists(node_a)
            nearest_node_b = self.node_exists(node_b)
            if nearest_node_a and nearest_node_b:
                if nearest_node_b not in self.intersections[nearest_node_a]:
                    self.intersections[nearest_node_a][nearest_node_b] = path
                else:
                    print("\nWarning: Rod already Exists!!\n")
                    return False
            else:
                print("\nError: One or Both of the nodes do not exist!!\n")
                return False
            return True
        else:
            self.add_node(node_a)
            self.add_node(node_b)
            self.add_rod(node_a, node_b)

    def remove_rod(self, node_a, node_b):
        node_a = (int(node_a[0]), int(node_a[1]))
        node_b = (int(node_b[0]), int(node_b[1]))
        if self.rod_exists(node_a, node_b):
            del self.intersections[node_a][node_b]
            return True
        return False

    def plot_map(self, plot=True, mirror=False):
        X = []
        Y = []

        plt.figure()

        for each in self.intersections:
            x = list(each)[0]
            if mirror:
                y = -list(each)[1]
            else:
                y = list(each)[1]

            X.append(x)
            Y.append(y)

            for neighbour in self.neighbours(each):
                xx = list(neighbour)[0]
                if mirror:
                    yy = -list(neighbour)[1]
                else:
                    yy = list(neighbour)[1]
                plt.plot([x, xx], [y, yy], 'r')
                # plt.text((xx+x)/2, (yy+y)/2, str(graph.intersections[each][neighbour]))

        plt.plot(X, Y, 'bs')

        plt.axis('image')

        if plot:
            plt.show()

    @staticmethod
    def heuristic(a, b, type):
        if type == 'Euclidean':
            (x1, y1) = a
            (x2, y2) = b
            return abs(x1 - x2) + abs(y1 - y2)

    def calculate_cost(self, node_a, node_b):
        # if self.node_exists(nodeA) and self.node_exists(nodeB) and nodeB in self.intersections[nodeA]:
        cost = 0
        prev = self.intersections[node_a][node_b][0]
        for each in self.intersections[node_a][node_b][1:]:
            cost += math.sqrt((each[0] - prev[0])**2 + (each[1] - prev[1])**2)
        return int(cost)

    def a_star_search(self, start, goal):
        if self.node_exists(start) and self.node_exists(goal):
            frontier = PriorityQueue()
            frontier.put(start, 0)
            came_from = dict()
            cost_so_far = dict()
            came_from[start] = None
            cost_so_far[start] = 0

            while not frontier.empty():
                current = frontier.get()

                if current == goal:
                    break

                for next in self.neighbours(current):
                    new_cost = cost_so_far[current] + self.calculate_cost(current, next)
                    if next not in cost_so_far or new_cost < cost_so_far[next]:
                        # TODO check if next in next line is correct
                        cost_so_far[next] = new_cost
                        priority = new_cost + self.heuristic(goal, next, 'Euclidean')
                        frontier.put(next, priority)
                        came_from[next] = current

            return came_from, cost_so_far

    def plot_route(self, route, goal):
        # plot map
        self.plot_map(plot=False)
        X = []
        Y = []
        next_point = goal
        # plot route on map
        X.append(list(goal)[0])
        Y.append(list(goal)[1])
        while route[next_point]:
            next_point = route[next_point]
            x = list(next_point)[0]
            y = list(next_point)[1]
            X.append(x)
            Y.append(y)
        plt.plot(X[0], Y[0], 'rs')
        plt.plot(X[-1], Y[-1], 'gs')
        plt.plot(X, Y, 'b')
        plt.show()

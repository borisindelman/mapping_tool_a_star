from pyqtgraph.Qt import QtCore

from mapping_tool_a_star.ParkingLotGraph import ParkingLotGraph
from mapping_tool_a_star.MappingGuiParams import MappingGuiParams


class MapMarkingThread(QtCore.QThread):
    """
    Handles the marking of the map and graph creation
    """
    SIGNAL_plot_data = QtCore.pyqtSignal(str, bool, bool, int, list)
    SIGNAL_remove_connected_rods = QtCore.pyqtSignal(tuple)
    __gui_params = MappingGuiParams()

    def __init__(self, resolution):
        super().__init__()
        self.road_map = ParkingLotGraph(resolution=resolution)  # self.__gui_params.MapGraph['Resolution']
        self.intersection_connection_list = []
        self.undrivable_zones_list = []
        self.undrivable_zones_list_id = 0
        self.parking_zones_list = []
        self.parking_zones_list_id = 0
        self.parking_spaces_list = []
        self.parking_spaces_list_id = 0
        self.pickup_zones_list = []
        self.pickup_zones_list_id = 0

    def add_data(self, mark_type, point):
        if mark_type == self.__gui_params.MarkingLabels[0]:  # 'Intersections'
            self.add_node(point)
            self.intersection_connection_list = []
        elif mark_type == self.__gui_params.MarkingLabels[1]:  # 'Intersections Connection'
            if len(self.intersection_connection_list) > 0:
                if not self.road_map.node_exists(point):
                    self.intersection_connection_list.append(point)
                    plot_type = self.__gui_params.MarkingLabels[1]  # 'Intersections Connection'
                    self.SIGNAL_plot_data.emit(plot_type, False, True, -1, self.intersection_connection_list)

                elif self.road_map.node_exists(point) == self.intersection_connection_list[0]:
                    self.intersection_connection_list = []
                else:
                    self.intersection_connection_list.append(self.road_map.node_exists(point))
                    if self.add_intersection(self.intersection_connection_list):
                        self.intersection_connection_list = []
                    else:
                        self.intersection_connection_list = self.intersection_connection_list[:-1]
            else:
                if self.road_map.node_exists(point):
                    self.intersection_connection_list.append(self.road_map.node_exists(point))
        elif mark_type == self.__gui_params.MarkingLabels[2]:  # 'Undrivable Zone'
            if len(self.undrivable_zones_list) > 0:
                if self.road_map.compare_points(self.undrivable_zones_list[0], point):
                    self.add_data('Close ' + mark_type, ())
                else:
                    self.undrivable_zones_list.append(point)
                    plot_type = self.__gui_params.MarkingLabels[2]  # 'Undrivable Zone'
                    self.SIGNAL_plot_data.emit(plot_type, False, True, -1, self.undrivable_zones_list)
            else:
                self.undrivable_zones_list.append(point)
        elif mark_type == self.__gui_params.MarkingLabels[3]:  # 'Parking Zone'
            if len(self.parking_zones_list) > 0:
                if self.road_map.compare_points(self.parking_zones_list[0], point):
                    self.add_data('Close ' + mark_type, ())
                else:
                    self.parking_zones_list.append(point)
                    plot_type = self.__gui_params.MarkingLabels[3]  # 'Parking Zone'
                    self.SIGNAL_plot_data.emit(plot_type, False, True, -1, self.parking_zones_list)
            else:
                self.parking_zones_list.append(point)
        elif mark_type == self.__gui_params.MarkingLabels[4]:  # 'Parking Space'
            if len(self.parking_spaces_list) > 0:
                if self.road_map.compare_points(self.parking_spaces_list[0], point):
                    self.add_data('Close ' + mark_type, ())
                else:
                    self.parking_spaces_list.append(point)
                    plot_type = self.__gui_params.MarkingLabels[4]  # 'Parking Space'
                    self.SIGNAL_plot_data.emit(plot_type, False, True, -1, self.parking_spaces_list)
            else:
                self.parking_spaces_list.append(point)
        elif mark_type == self.__gui_params.MarkingLabels[5]:  # 'Pickup Zone'
            if len(self.pickup_zones_list) > 0:
                if self.road_map.compare_points(self.pickup_zones_list[0], point):
                    self.add_data('Close Parking Space Connection', ())
                else:
                    self.pickup_zones_list.append(point)
                    plot_type = self.__gui_params.MarkingLabels[5]  # 'Pickup Zone'
                    self.SIGNAL_plot_data.emit(plot_type, False, True, -1, self.pickup_zones_list)
            else:
                self.pickup_zones_list.append(point)

        elif mark_type == 'Close ' + self.__gui_params.MarkingLabels[2]:  # 'Close Undrivable Zone'
            self.undrivable_zones_list.append(self.undrivable_zones_list[0])
            self.road_map.undrivable_zones_segment[self.undrivable_zones_list_id] = self.undrivable_zones_list
            plot_type = self.__gui_params.MarkingLabels[2]  # 'Undrivable Zone'
            self.SIGNAL_plot_data.emit(plot_type, True, True, self.undrivable_zones_list_id,
                                       self.undrivable_zones_list)
            self.undrivable_zones_list = []
            self.undrivable_zones_list_id += 1
        elif mark_type == 'Close ' + self.__gui_params.MarkingLabels[3]:  # 'Parking Zone'
            # TODO: is the following line correct??
            self.parking_zones_list.append(self.parking_zones_list[0])
            self.road_map.parking_zones_segment[self.parking_zones_list_id] = self.parking_zones_list
            plot_type = self.__gui_params.MarkingLabels[3]  # 'Parking Zone'
            self.SIGNAL_plot_data.emit(plot_type, True, True, self.parking_zones_list_id,
                                       self.parking_zones_list)
            self.parking_zones_list = []
            self.parking_zones_list_id += 1
        elif mark_type == 'Close ' + self.__gui_params.MarkingLabels[4]:  # 'Parking Space'
            # TODO: is the following line correct??
            self.parking_spaces_list.append(self.parking_spaces_list[0])
            self.road_map.parking_spaces_segment[self.parking_spaces_list_id] = self.parking_spaces_list
            plot_type = self.__gui_params.MarkingLabels[4]  # 'Parking Space'
            self.SIGNAL_plot_data.emit(plot_type, True, True, self.parking_spaces_list_id,
                                       self.parking_spaces_list)
            self.parking_spaces_list = []
            self.parking_spaces_list_id += 1
        elif mark_type == 'Close ' + self.__gui_params.MarkingLabels[5]:  # 'Pickup Zone'
            # TODO: is the following line correct??
            self.pickup_zones_list.append(self.pickup_zones_list[0])
            self.road_map.pickup_zones_segment[self.pickup_zones_list_id] = self.pickup_zones_list
            plot_type = self.__gui_params.MarkingLabels[5]  # 'Pickup Zone'
            self.SIGNAL_plot_data.emit(plot_type, True, True, self.pickup_zones_list_id,
                                       self.pickup_zones_list)
            self.pickup_zones_list = []
            self.pickup_zones_list_id += 1

        # TODO: finish changing the clear messages...

        elif mark_type == 'Clear ' + self.__gui_params.MarkingLabels[1]:  # 'Intersections Connection'
            self.intersection_connection_list = []
            print('cleared ' + mark_type)
        elif mark_type == 'Clear ' + self.__gui_params.MarkingLabels[2]:  # 'Undrivable Zone'
            self.undrivable_zones_list = []
            print('cleared ' + mark_type)
        elif mark_type == 'Clear ' + self.__gui_params.MarkingLabels[3]:  # 'Parking Zone'
            self.parking_zones_list = []
            print('cleared ' + mark_type)
        elif mark_type == 'Clear ' + self.__gui_params.MarkingLabels[4]:  # 'Parking Space'
            self.parking_spaces_list = []
            print('cleared ' + mark_type)
        elif mark_type == 'Clear ' + self.__gui_params.MarkingLabels[5]:  # 'Pickup Zone'
            self.pickup_zones_list = []
            print('cleared ' + mark_type)

        elif mark_type == 'Remove ' + self.__gui_params.MarkingLabels[0]:  # 'Intersections'
            if self.road_map.remove_node(point):
                self.SIGNAL_remove_connected_rods.emit(point)
                print(self.__gui_params.MarkingLabels[0] + ' at ' + str(point) + ' was removed successfully')
            else:
                print(self.__gui_params.MarkingLabels[0] + ' at ' + str(point) + ' does not exists')
        elif mark_type == 'Remove ' + self.__gui_params.MarkingLabels[1]:  # 'Intersections Connection'
            node_a = point[0]
            node_b = point[1]
            if self.road_map.remove_rod(node_a, node_b):
                print(self.__gui_params.MarkingLabels[1] + ' between ' + str(node_a) + ' and ' + str(node_b) + ' was removed successfully')
            else:
                print(self.__gui_params.MarkingLabels[1] + ' between ' + str(node_a) + ' and ' + str(node_b) + ' does not exists')
        # elif mark_type == 'Remove ' + self.__gui_params.MarkingLabels[2]: # 'Undrivable Zone'
        #     id = point[0]
        #     if self.road_map.remove_undrivable_zone(id):
        #         print(self.__gui_params.MarkingLabels[2] + ' was removed')
        #     else:
        #         print(self.__gui_params.MarkingLabels[2] + ' does not exists')
        # elif mark_type == 'Remove ' + self.__gui_params.MarkingLabels[3]: # 'Parking Zone'
        #     id = point[0]
        #     if self.road_map.remove_parking_zone(id):
        #         print(self.__gui_params.MarkingLabels[3] + ' was removed')
        #     else:
        #         print(self.__gui_params.MarkingLabels[3] + ' does not exists')
        # elif mark_type == 'Remove ' + self.__gui_params.MarkingLabels[4]: # 'Parking Space'
        #     id = point[0]
        #     if self.road_map.remove_parking_space(id):
        #         print(mark_type + ' was removed')
        #     else:
        #         print(mark_type + ' does not exists')
        # elif mark_type == 'Remove ' + self.__gui_params.MarkingLabels[5]: # 'Pickup Zone'
        #     id = point[0]
        #     if self.road_map.remove_pickup_zone(id):
        #         print(mark_type + ' was removed')
        #     else:
        #         print(mark_type + ' does not exists')

        elif mark_type == 'Reset All':
            self.intersection_connection_list = []
            self.undrivable_zones_list = []
            self.parking_zones_list = []
            self.parking_spaces_list = []
            self.pickup_zones_list = []

    def add_node(self, node):
        if self.road_map.add_node(node):
            plot_type = self.__gui_params.MarkingLabels[0]  # 'Intersections'
            self.SIGNAL_plot_data.emit(plot_type, True, True, -1, [node])

    def add_intersection(self, nodes):
        node_a = nodes[0]
        node_b = nodes[-1]
        if self.road_map.add_rod(node_a, node_b, nodes):
            plot_type = self.__gui_params.MarkingLabels[1]  # 'Intersections Connection'
            self.SIGNAL_plot_data.emit(plot_type, True, True, -1, nodes)
            return True
        return False

    def re_plot_graph(self, option):
        max_id_undrivable_zones = 0
        max_id_parking_zones = 0
        max_id_parking_spaces = 0
        max_id_pickup_zones = 0
        if option == self.__gui_params.LegendBoxLabels[1] or option == 'all':  # 'Intersections Connections'
            for key in self.road_map.intersections.keys():
                for key2 in self.road_map.intersections[key].keys():
                    plot_type = self.__gui_params.MarkingLabels[1]  # 'Intersections Connection'
                    self.SIGNAL_plot_data.emit(plot_type, True, False, -1,
                                               self.road_map.intersections[key][key2])
        if option == self.__gui_params.LegendBoxLabels[2] or option == 'all':  # 'Undrivable Zones'
            for key in self.road_map.undrivable_zones_segment.keys():
                plot_type = self.__gui_params.MarkingLabels[2]  # 'Undrivable Zone'
                self.SIGNAL_plot_data.emit(plot_type, True, False, key,
                                           self.road_map.undrivable_zones_segment[key])
                if key > max_id_undrivable_zones:
                    max_id_undrivable_zones = key
            self.undrivable_zones_list_id = max_id_undrivable_zones + 1
        if option == self.__gui_params.LegendBoxLabels[3] or option == 'all':  # 'Parking Zones'
            # print('la')
            # print(self.road_map.parking_zones_segment)
            # TODO: problem here!!!
            for key in self.road_map.parking_zones_segment.keys():

                plot_type = self.__gui_params.MarkingLabels[3]  # 'Parking Zone'
                self.SIGNAL_plot_data.emit(plot_type, True, False, key,
                                           self.road_map.parking_zones_segment[key])
                if key > max_id_parking_zones:
                    max_id_parking_zones = key
            self.parking_zones_list_id = max_id_parking_zones + 1
        if option == self.__gui_params.LegendBoxLabels[4] or option == 'all':  # 'Parking Space'
            for key in self.road_map.parking_spaces_segment.keys():
                plot_type = self.__gui_params.MarkingLabels[4]  # 'Parking Zone'
                self.SIGNAL_plot_data.emit(plot_type, True, False, key,
                                           self.road_map.parking_spaces_segment[key])
                if key > max_id_parking_spaces:
                    max_id_parking_spaces = key
            self.parking_spaces_list_id = max_id_parking_spaces + 1
        if option == self.__gui_params.LegendBoxLabels[5] or option == 'all':  # 'Pickup Zone'
            for key in self.road_map.pickup_zones_segment.keys():
                plot_type = self.__gui_params.MarkingLabels[5]  # 'Parking Zone'
                self.SIGNAL_plot_data.emit(plot_type, True, False, key,
                                           self.road_map.pickup_zones_segment[key])
                if key > max_id_pickup_zones:
                    max_id_pickup_zones = key
            self.pickup_zones_list_id = max_id_pickup_zones + 1
        if option == self.__gui_params.LegendBoxLabels[0] or option == 'all':  # 'Intersections'
            for key in self.road_map.intersections.keys():
                plot_type = self.__gui_params.MarkingLabels[0]  # 'Intersections'
                self.SIGNAL_plot_data.emit(plot_type, True, False, -1, [key])

    def route_plan(self, route_list):
        if len(route_list) == 2:
            start = route_list[0]
            goal = route_list[1]
            route_reversed, cost = self.road_map.a_star_search(start, goal)
            # print(route)
            # keys = route.keys()
            # first = True
            route = [goal]
            next_point = goal
            while route_reversed[next_point]:
                route.append(route_reversed[next_point])
                next_point = route_reversed[next_point]
            prev = route[-1]
            for each in reversed(route[:-1]):
                self.SIGNAL_plot_data.emit(self.__gui_params.MarkingLabels[1] + ' AStar', True, True, -1, [prev, each])
                prev = each

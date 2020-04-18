import matplotlib.image
import matplotlib.pyplot as plt

from mapping_tool_a_star.RoadGraph import RoadGraph


class ParkingLotGraph(RoadGraph):
    def __init__(self, width=0, height=0, resolution=0):
        super().__init__(width=width, height=height, resolution=resolution)
        self.undrivable_zones_segment = {0: []}
        self.parking_zones_segment = {0: []}
        self.parking_spaces_segment = {0: []}
        self.pickup_zones_segment = {0: []}

        self.segments = {'Undrivable Zone': {0: []},
                         'Parking Zone': {0: []},
                         'Parking Space': {0: []},
                         'Pickup Zone': {0: []}}

        # TODO: Change to dictionary

    def plot_map(self, plot=True, mirror=False, img_path=None):
        X = []
        Y = []

        plt.figure()

        if img_path:
            img = matplotlib.image.imread(img_path)
            plt.imshow(img)

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

        plt.plot(X, Y, 'bs')

        if img_path:
            for each in self.segments['Undrivable Zone']:
                if self.segments['Undrivable Zone'][each]:
                    plt.fill([x[0] for x in self.segments['Undrivable Zone'][each]],
                             [y[1] for y in self.segments['Undrivable Zone'][each]], 'g')

            for each in self.segments['Parking Zone']:
                if self.segments['Parking Zone'][each]:
                    plt.fill([x[0] for x in self.segments['Parking Zone'][each]],
                             [y[1] for y in self.segments['Parking Zone'][each]], 'y')

        plt.axis('image')

        if plot:
            plt.show()

    def remove_segment(self, segment_type, segment_id):

        if segment_type in self.segments:
            if segment_id in self.segments[segment_type]:
                del self.segments[segment_type][segment_id]
                return True
            return False

    # def remove_undrivable_zone(self, id):
    #     if id in self.segments['Undrivable Zone']:
    #         del self.segments['Undrivable Zone'][id]
    #         return True
    #     return False
    #
    # def remove_parking_zone(self, id):
    #     if id in self.segments['Parking Zone']:
    #         del self.segments['Parking Zone'][id]
    #         return True
    #     return False
    #
    # def remove_parking_space(self, id):
    #     if id in self.segments['Parking Space']:
    #         del self.segments['Parking Space'][id]
    #         return True
    #     return False
    #
    # def remove_pickup_zone(self, id):
    #     if id in self.segments['Pickup Zone']:
    #         del self.segments['Pickup Zone'][id]
    #         return True
    #     return False

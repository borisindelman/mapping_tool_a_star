import matplotlib.image
from PyQt5 import QtGui
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore
import sys
import pickle
import numpy as np
import os.path

# from mapping_tool_a_star import ParkingLotGraph, MappingGuiParams, MapViewBox, ScatterWithSelection, PlotCurveItemWithSelection, MapMarkingThread
from mapping_tool_a_star.ParkingLotGraph import ParkingLotGraph
from mapping_tool_a_star.MappingGuiParams import MappingGuiParams
from mapping_tool_a_star.MapViewBox import MapViewBox
from mapping_tool_a_star.ScatterWithSelection import ScatterWithSelection
from mapping_tool_a_star.PlotCurveItemWithSelection import PlotCurveItemWithSelection
from mapping_tool_a_star.MapMarkingThread import MapMarkingThread


class MappingTool(QtGui.QWidget):
    SIGNAL_add_data = QtCore.pyqtSignal(str, tuple)
    SIGNAL_replot_graph = QtCore.pyqtSignal(str)
    SIGNAL_Message = QtCore.pyqtSignal(str)
    SIGNAL_plan_route = QtCore.pyqtSignal(list)
    __gui_params = MappingGuiParams()

    def __init__(self, *args, **kwds):

        super().__init__(*args, **kwds)

        # Set PyQtGraph to display images correctly
        pg.setConfigOptions(imageAxisOrder='row-major')

        # General Window settings
        self.setWindowTitle(self.__gui_params.GuiTitle + ' (' + self.__gui_params.GuiVersion + ')')

        # Creating main layout for the gui
        self.map_gui_layout = QtGui.QGridLayout()

        # Creating box and layout for displaying image and markings
        self.map_image_widget = pg.GraphicsLayoutWidget()
        self.map_image_view_box = MapViewBox(invertY=True)
        self.map_image_item = pg.ImageItem()

        # image values used for evaluating if curser inside image and restore image from file
        self.map_image_resolution = ()
        self.img_file_name = None

        # Calling functions to create the different Widgets
        self.create_menu_buttons_widget()
        self.create_marking_buttons_widget()
        self.create_legend_buttons_widget()
        self.create_navigation_buttons_widget()
        self.create_map_image_widget()

        # self.navigation_buttons[self.__gui_params__.NavigationButtonsLabels[0]].setEnabled(True)

        # TODO: add other shapes
        self.plot_items_list = {}
        for each in self.__gui_params.MarkingLabels:
            self.plot_items_list[each] = {}
            self.plot_items_list[each + ' id'] = 0
        # self.plot_items_list = {self.__gui_params__.MarkingLabels[0]: {},
        #                         self.__gui_params__.MarkingLabels[0] + ' id': 0,
        #                         self.__gui_params__.MarkingLabels[1]: {},
        #                         self.__gui_params__.MarkingLabels[1] + ' id': 0,
        #                         self.__gui_params__.MarkingLabels[2]: {},
        #                         self.__gui_params__.MarkingLabels[2] + ' id': 0,
        #                         self.__gui_params__.MarkingLabels[3]: {},
        #                         self.__gui_params__.MarkingLabels[3] + ' id': 0,
        #                         self.__gui_params__.MarkingLabels[4]: {},
        #                         self.__gui_params__.MarkingLabels[4] + ' id': 0,
        #                         self.__gui_params__.MarkingLabels[5]: {},
        #                         self.__gui_params__.MarkingLabels[5] + ' id': 0,
        #                         }

        # Create a thread for dealing with the graph representation of the map. resolution will define the circle of reference for each point in the graph
        self.map_marking_thread = MapMarkingThread(self.__gui_params.MapGraph['Resolution'])

        # Connect all the signals
        self.connect_signals()

        # Initialize trackers for chosen and unfinished plot items
        self.unfinished_plot_item = None
        self.chosen_plot_item = None

        # assign the layout to the main window
        self.setLayout(self.map_gui_layout)

        # define ration between the columns
        self.map_gui_layout.setColumnStretch(0, 1)
        self.map_gui_layout.setColumnStretch(1, 10)

        # set the size of the window relative to the screen resolution
        self.default_size(self.__gui_params.MapWidgetResizeFactor)

        # start marking threds
        self.map_marking_thread.start()

        print('MappingGuiQWidget Initialized')

    def connect_signals(self):
        self.map_marking_thread.SIGNAL_plot_data.connect(self.plot_data)
        self.map_marking_thread.SIGNAL_remove_connected_rods.connect(self.remove_connected_rods)

        self.map_image_view_box.SIGNAL_left_click.connect(self.add_data)
        self.map_image_view_box.SIGNAL_right_click.connect(self.reset_last_mark)
        self.map_image_view_box.SIGNAL_dbl_right_click.connect(self.reset_marking)
        self.map_image_view_box.SIGNAL_dbl_left_click.connect(self.close_shape)
        self.map_image_view_box.SIGNAL_diselect_item.connect(self.diselect_plot_item)
        self.map_image_view_box.SIGNAL_delete_item.connect(self.remove_item)

        self.SIGNAL_Message.connect(self.show_message)
        self.SIGNAL_add_data.connect(self.map_marking_thread.add_data)
        self.SIGNAL_replot_graph.connect(self.map_marking_thread.re_plot_graph)
        self.SIGNAL_plan_route.connect(self.map_marking_thread.route_plan)

    def create_menu_buttons_widget(self):
        # Create containers for the buttons
        self.menu_buttons = {}

        # Creating box, layout and group for the menu (push buttons)
        self.menu_buttons_group = QtGui.QButtonGroup()
        self.menu_buttons_layout = QtGui.QVBoxLayout()
        self.menu_buttons_box = QtGui.QGroupBox()

        # Create menu buttons and assign a function for each
        for id, each in enumerate(self.__gui_params.MainButtonsLabels):
            self.menu_buttons[each] = QtGui.QPushButton(each)
            self.menu_buttons_group.addButton(self.menu_buttons[each], id)
            self.menu_buttons_layout.addWidget(self.menu_buttons[each])
            if each == self.__gui_params.MainButtonsLabels[0]:  # 'Load Map Image'
                self.menu_buttons[each].clicked.connect(self.load_image_file)
            elif each == self.__gui_params.MainButtonsLabels[1]:  # 'Load Markings From File'
                self.menu_buttons[each].clicked.connect(self.load_map_markings)
            elif each == self.__gui_params.MainButtonsLabels[2]:  # 'Save Marking to File'
                self.menu_buttons[each].clicked.connect(self.save_map_markings)
            elif each == self.__gui_params.MainButtonsLabels[3]:  # 'Add Markings to map'
                self.menu_buttons[each].clicked.connect(self.mark_map)
            elif each == self.__gui_params.MainButtonsLabels[4]:  # 'Navigation'
                pass
                # self.menu_buttons[each].clicked.connect(self.)

        # Add menu widget to the Gui layout
        row = self.__gui_params.MainButtonsBoxLayoutLocation[0]
        col = self.__gui_params.MainButtonsBoxLayoutLocation[1]
        self.map_gui_layout.addWidget(self.menu_buttons_box, row, col)
        self.menu_buttons_box.setLayout(self.menu_buttons_layout)

    def create_marking_buttons_widget(self):
        # Create containers for the buttons
        self.Marking_buttons = {}

        # Creating box, layout and group for the marking choices (radio buttons)
        self.Marking_buttons_group = QtGui.QButtonGroup()
        self.Marking_buttons_layout = QtGui.QVBoxLayout()
        self.Marking_buttons_box = QtGui.QGroupBox()

        # reset radio previous state for the Gui tracking
        self.Marking_buttons_previous_state = -1

        # Create marking buttons and add them to layout and box
        for id, each in enumerate(self.__gui_params.MarkingLabels):
            self.Marking_buttons[each] = QtGui.QRadioButton(each)
            self.Marking_buttons[each].setEnabled(False)
            self.Marking_buttons_group.addButton(self.Marking_buttons[each], id)
            self.Marking_buttons_layout.addWidget(self.Marking_buttons[each])

        # set button to be exclusive and a function
        self.Marking_buttons_group.setExclusive(True)
        self.Marking_buttons_group.buttonClicked.connect(self.radio_button_action)

        # Add marking widget to the Gui layout
        self.Marking_buttons_box.setLayout(self.Marking_buttons_layout)
        self.Marking_buttons_box.setTitle(self.__gui_params.MarkingBoxText)
        row = self.__gui_params.MarkingBoxLayoutLocation[0]
        col = self.__gui_params.MarkingBoxLayoutLocation[1]
        self.map_gui_layout.addWidget(self.Marking_buttons_box, row, col)

    def create_legend_buttons_widget(self):
        # Create containers for the buttons
        self.legend_buttons = {}

        # Creating box, layout and group for the Legend selection (check buttons)
        self.legend_buttons_group = QtGui.QButtonGroup()
        self.legend_buttons_layout = QtGui.QVBoxLayout()
        self.legend_buttons_box = QtGui.QGroupBox()

        # Set Buttons to not be exclusive
        self.legend_buttons_group.setExclusive(False)

        # Create legend buttons and add them to layout and box and connect to their function
        for id, each in enumerate(self.__gui_params.LegendBoxLabels):
            self.legend_buttons[each] = QtGui.QCheckBox(each)
            # self.legend_buttons[each].setEnabled(False)
            self.legend_buttons[each].setCheckState(QtCore.Qt.Checked)
            self.legend_buttons[each].clicked.connect(self.update_tree_selection)
            self.legend_buttons_group.addButton(self.legend_buttons[each], id)
            self.legend_buttons_layout.addWidget(self.legend_buttons[each])

        # Initialize state tracker for the legend
        self.legend_prev_state = {}
        for each in self.__gui_params.LegendBoxLabels:
            self.legend_prev_state[each] = True

        # Add marking widget to the Gui layout
        self.legend_buttons_box.setLayout(self.legend_buttons_layout)
        self.legend_buttons_box.setTitle(self.__gui_params.LegendTitle)
        row = self.__gui_params.LegendBoxLayoutLocation[0]
        col = self.__gui_params.LegendBoxLayoutLocation[1]
        self.map_gui_layout.addWidget(self.legend_buttons_box, row, col)

        print('CreateLegendButtonsWidget')

    def create_navigation_buttons_widget(self):
        self.navigation_mode = None
        self.naigation_points = []
        # Create containers for the buttons
        self.navigation_buttons = {}

        # Creating box, layout and group for the menu (push buttons)
        self.navigation_buttons_group = QtGui.QButtonGroup()
        self.navigation_buttons_layout = QtGui.QVBoxLayout()
        self.navigation_buttons_box = QtGui.QGroupBox()

        # Create menu buttons and assign a function for each
        for id, each in enumerate(self.__gui_params.NavigationButtonsLabels):
            self.navigation_buttons[each] = QtGui.QPushButton(each)
            self.navigation_buttons[each].setEnabled(False)
            self.navigation_buttons_group.addButton(self.navigation_buttons[each], id)
            self.navigation_buttons_layout.addWidget(self.navigation_buttons[each])
            if each == self.__gui_params.NavigationButtonsLabels[0]:
                self.navigation_buttons[each].clicked.connect(self.route_planner)
                self.navigation_buttons[each].setEnabled(True)
            if each == self.__gui_params.NavigationButtonsLabels[1]:
                self.navigation_buttons[each].clicked.connect(self.plot_graph)
                self.navigation_buttons[each].setEnabled(True)

        self.navigation_buttons_box.setLayout(self.navigation_buttons_layout)
        self.navigation_buttons_box.setTitle(self.__gui_params.NavigationBoxText)

        # Add menu widget to the Gui layout
        row = self.__gui_params.NavigationButtonsBoxLayoutLocation[0]
        col = self.__gui_params.NavigationButtonsBoxLayoutLocation[1]
        self.map_gui_layout.addWidget(self.navigation_buttons_box, row, col)

    def create_map_image_widget(self):
        self.map_image_view_box.setAspectLocked(True)
        self.map_image_widget.addItem(self.map_image_view_box)
        self.map_gui_layout.addWidget(self.map_image_widget, 0, 1, 8, 1)
        print('CreateMapImageWidget')

    def default_size(self, resize_factor=0.8):
        geometry = QtGui.QApplication.instance().desktop().availableGeometry()
        geometry.setHeight(int(resize_factor * geometry.height()))
        geometry.setWidth(int(resize_factor * geometry.width()))
        self.resize(geometry.width(), geometry.height())
        print('Window set to deafult size')

    def radio_button_action(self):
        marking_buttons_current_state = self.Marking_buttons_group.checkedId()
        if marking_buttons_current_state != -1 and marking_buttons_current_state != self.Marking_buttons_previous_state:
            self.SIGNAL_add_data.emit('Reset All', ())

    def load_image_file(self, use_existing=False):
        for item in self.map_image_view_box.scene().items():
            if type(item) == type(ScatterWithSelection()) or type(item) == type(PlotCurveItemWithSelection()) or type(item) == type(
                    pg.ImageItem()):
                self.map_image_view_box.removeItem(item)
        self.reset_all()
        if not use_existing:
            try:
                file_name = QtGui.QFileDialog().getOpenFileName(filter=(r"Images (*.png *.jpg)"))
                self.img_file_name = file_name[0]
            except:
                pass
        if self.img_file_name:
            print('loading image file from: ' + str(self.img_file_name))

            img = matplotlib.image.imread(self.img_file_name)
            self.map_image_resolution = (img.shape[1], img.shape[0])
            self.map_image_item.setImage(img)
            self.map_image_view_box.addItem(self.map_image_item)
            self.setWindowTitle(self.__gui_params.GuiTitle + ' (' + self.__gui_params.GuiVersion + '): ' + file_name[0].split('/')[-1])
            self.map_image_view_box.autoRange()
            if os.path.exists(self.img_file_name.split('.')[0] + '.pd'):
                user_input = self.show_message('Markings Exists')
                if user_input == QtGui.QMessageBox.Ok:
                    self.load_map_markings(self.img_file_name.split('.')[0] + '.pd')
            # self.SIGNAL_Message.emit('Map Image Loaded')
        else:
            self.SIGNAL_Message.emit('Cannot Load Image')

    def load_map_markings(self, file_name=None):
        self.reset_all()
        if file_name is None or type(file_name) != str:
            try:
                file_name = QtGui.QFileDialog().getOpenFileName(filter=(r"MapGraphs (*.pd )"))
                file_name = file_name[0]
            except:
                file_name = None

        if file_name:
            print('loading marking from file at: ' + str(file_name))

            for item in self.map_image_view_box.scene().items():
                if type(item) == type(ScatterWithSelection()) or type(item) == type(PlotCurveItemWithSelection()):
                    self.map_image_view_box.removeItem(item)
            self.map_marking_thread.road_map = ParkingLotGraph(resolution=4)

            self.map_marking_thread.road_map = pickle.load(open(file_name, 'rb'))
            self.reset_all()
            self.SIGNAL_replot_graph.emit('all')
            self.map_image_view_box.autoRange()
            print('Marking Loaded Successfully')
            # self.SIGNAL_Message.emit('Markings Loaded')
        else:
            self.SIGNAL_Message.emit('Cannot Load Markings')

    def save_map_markings(self, temp=False):
        if not temp:
            self.enable_radio_buttons(False)
            self.SIGNAL_add_data.emit('Reset All', ())
            try:
                file_name = QtGui.QFileDialog().getSaveFileName(filter=(r"MapGraphs (*.pd)"))
                file_name = file_name[0]
                if file_name:

                    if file_name.split('.')[-1] != 'pd':
                        file_name = file_name + '.pd'
                    pickle.dump(self.map_marking_thread.road_map, open(file_name, 'wb'))
                    print('marking saved to :' + str(file_name))
                    self.SIGNAL_Message.emit('Markings Saved')
                else:
                    self.SIGNAL_Message.emit('Cannot Save Markings')

            except:
                pass
        else:
            pickle.dump(self.map_marking_thread.road_map, open('temporary_map_graph.pd', 'wb'))

    def mark_map(self):
        self.reset_all()
        self.enable_radio_buttons(True)

    def enable_radio_buttons(self, enable=True):
        self.SIGNAL_add_data.emit('Reset All', ())

        self.unfinished_plot_item = None
        # self.unfinished_arrow_item = None

        for _, each in enumerate(self.__gui_params.MarkingLabels):
            self.Marking_buttons[each].setEnabled(enable)
            if not enable:
                self.Marking_buttons[each].setChecked(False)

    def enable_legend_buttons(self, Enable=True):
        self.SIGNAL_add_data.emit('Reset All', ())
        self.unfinished_plot_item = None
        # self.unfinished_arrow_item = None
        for id, each in enumerate(self.__gui_params.LegendBoxLabels):
            self.legend_buttons[each].setEnabled(Enable)
        if Enable:
            print('Marking Enabled')
        else:
            print('Marking Disabled')

    def check_all_buttons(self):
        for _, each in enumerate(self.__gui_params.LegendBoxLabels):
            self.legend_buttons[each].setCheckState(QtCore.Qt.Checked)

    def is_enabled_marking_buttons(self):
        for _, each in enumerate(self.__gui_params.MarkingLabels):
            if not self.Marking_buttons[each].isEnabled():
                return False
        return True

    def add_data(self, point):
        if self.map_image_resolution != ():
            if 0 <= point[0] < self.map_image_resolution[0] and 0 <= point[1] < self.map_image_resolution[1]:
                if self.Marking_buttons_group.checkedId() != -1 and self.Marking_buttons[self.__gui_params.MarkingLabels[self.Marking_buttons_group.checkedId()]].isEnabled():
                    mark_type = self.__gui_params.MarkingLabels[self.Marking_buttons_group.checkedId()]
                    legend_type = mark_type + 's'
                    if self.legend_buttons[legend_type].checkState() == QtCore.Qt.Checked:
                        print('adding: ' + str(mark_type) + ' at ' + str(point))
                        self.SIGNAL_add_data.emit(mark_type, point)
                    else:
                        self.SIGNAL_Message.emit('Legend Off')
            else:
                print('point out of box')
        else:
            pass

    def show_message(self, message_type):
        # print(self.__gui_params__.MessageTypes[type])

        if message_type in self.__gui_params.MessageTypes:
            msg = QtGui.QMessageBox()
            if self.__gui_params.MessageTypes[message_type]['Title'] == 'Warning':
                msg.setIcon(QtGui.QMessageBox.Warning)
                msg.setDefaultButton(QtGui.QMessageBox.Ok)
            elif self.__gui_params.MessageTypes[message_type]['Title'] == 'Error':
                msg.setIcon(QtGui.QMessageBox.Critical)
                msg.setDefaultButton(QtGui.QMessageBox.Ok)
            elif self.__gui_params.MessageTypes[message_type]['Title'] == 'Information':
                msg.setIcon(QtGui.QMessageBox.Information)
                msg.setDefaultButton(QtGui.QMessageBox.Ok)
            elif self.__gui_params.MessageTypes[message_type]['Title'] == 'Question':
                msg.setIcon(QtGui.QMessageBox.Question)
                print('la di da')
                msg.setStandardButtons(QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel)
            msg.setWindowTitle(self.__gui_params.MessageTypes[message_type]['Title'])
            msg.setText(self.__gui_params.MessageTypes[message_type]['Text'])
            msg.setInformativeText(self.__gui_params.MessageTypes[message_type]['InformativeText'])
            return msg.exec_()

    def reset_marking(self):
        if self.Marking_buttons_group.checkedId() != -1 and self.unfinished_plot_item is not None:
            mark_type = self.__gui_params.MarkingLabels[self.Marking_buttons_group.checkedId()]
            if mark_type in self.__gui_params.MarkingLabels:
                self.SIGNAL_add_data.emit('Clear ' + mark_type, ())

            self.map_image_view_box.removeItem(self.unfinished_plot_item)
            self.unfinished_plot_item = None
            self.SIGNAL_add_data.emit('Reset All', ())

    def reset_last_mark(self):
        pass

    def close_shape(self):
        """
        Handle Double Click = Closing shapes
        Returns:

        """
        checkedId = self.Marking_buttons_group.checkedId()
        if checkedId != -1:
            plot_type = self.__gui_params.MarkingLabels[checkedId]
            if plot_type in self.__gui_params.MarkingButtonTypes:
                if self.__gui_params.MarkingButtonTypes[plot_type] == self.__gui_params.MarkingTypes[2]:  # 'Zones'
                    self.SIGNAL_add_data.emit('Close ' + plot_type, ())

    def plot_data(self, plot_type, close_mark, bring_nodes_to_front, plot_id, nodes):
        plot_check = False
        a_star = False
        if plot_type == self.__gui_params.MarkingLabels[1] + ' AStar':
            plot_type = self.__gui_params.MarkingLabels[1]
            a_star = True

        node_x = np.array([])
        node_y = np.array([])

        plot_item = []

        if nodes:
            for each in nodes:
                node_x = np.append(node_x, each[0])
                node_y = np.append(node_y, each[1])

                id2 = self.__gui_params.MarkingLabels.index(plot_type)

                if self.__gui_params.MarkingButtonTypes[plot_type] == self.__gui_params.MarkingTypes[0]:  # 'Node'
                    node_size = self.__gui_params.PlottingStyles['Intersection Unselected Width']
                    plot_item = ScatterWithSelection(plot_type, nodes[0], node_x, node_y, size=node_size, clickable=True)
                    plot_check = self.legend_buttons[self.__gui_params.LegendBoxLabels[id2]].checkState() == QtCore.Qt.Checked
                elif self.__gui_params.MarkingButtonTypes[plot_type] == self.__gui_params.MarkingTypes[1]:  # 'Rod'
                    plot_item = PlotCurveItemWithSelection(plot_type, (nodes[0], nodes[-1]), node_x, node_y, clickable=True)
                    plot_check = self.legend_buttons[self.__gui_params.LegendBoxLabels[id2]].checkState() == QtCore.Qt.Checked
                elif self.__gui_params.MarkingButtonTypes[plot_type] == self.__gui_params.MarkingTypes[2]:  # 'Zone'
                    plot_item = PlotCurveItemWithSelection(plot_type, (plot_id, 0), node_x, node_y, clickable=True)
                    plot_check = self.legend_buttons[self.__gui_params.LegendBoxLabels[id2]].checkState() == QtCore.Qt.Checked

            if self.unfinished_plot_item is not None and self.chosen_plot_item is not None and self.chosen_plot_item == self.unfinished_plot_item:
                self.set_chosen_pen(plot_item, plot_type)
            else:
                self.set_pen(plot_item, plot_type)

            if a_star:
                self.set_chosen_pen(plot_item, self.__gui_params.MarkingLabels[1])

            plot_item.sigClicked.connect(self.item_clicked)

            if self.unfinished_plot_item is not None:
                self.map_image_view_box.removeItem(self.unfinished_plot_item)

            if plot_check:
                self.map_image_view_box.addItem(plot_item)

            if close_mark:
                plot_id = self.plot_items_list[plot_type + ' id']
                if plot_type in self.__gui_params.MarkingLabels:
                    self.plot_items_list[plot_type][plot_id] = plot_item
                    self.plot_items_list[plot_type + ' id'] += 1
                self.unfinished_plot_item = None
                self.save_map_markings(True)
            else:
                self.unfinished_plot_item = plot_item

        if bring_nodes_to_front and self.legend_buttons[self.__gui_params.LegendBoxLabels[0]].checkState() == QtCore.Qt.Checked:
            self.bring_intersections_to_front()

    def set_pen(self, item, plot_type):
        # TODO: scale down!!
        if self.__gui_params.MarkingButtonTypes[plot_type] == self.__gui_params.MarkingTypes[0]:  # 'node'
            color = self.__gui_params.PlottingStyles[plot_type + ' Unselected Color']
            brush = pg.mkBrush(color=color)
            pen = pg.mkPen(color=color)
            item.setBrush(brush)
            item.setPen(pen)
        if self.__gui_params.MarkingButtonTypes[plot_type] == self.__gui_params.MarkingTypes[1]:  # 'rod'
            color = self.__gui_params.PlottingStyles[plot_type + ' Unselected Color']
            width = self.__gui_params.PlottingStyles[plot_type + ' Unselected Width']
            pen = pg.mkPen(color=color, width=width)
            brush = pg.mkBrush(color=color)
            item.setPen(pen)
            item.arrow.setStyle(pen=pen, brush=brush)
        if self.__gui_params.MarkingButtonTypes[plot_type] == self.__gui_params.MarkingTypes[2]:  # 'zone'
            color = self.__gui_params.PlottingStyles[plot_type + ' Unselected Color']
            width = self.__gui_params.PlottingStyles[plot_type + ' Unselected Width']
            pen = pg.mkPen(color=color, width=width)
            item.setPen(pen)
        # if plot_type == self.__gui_params__.MarkingLabels[0]:  # 'Intersection'
        #     color = self.__gui_params__.PlottingStyles[plot_type + ' Unselected Color']
        #     brush = pg.mkBrush(color = color)
        #     item.setBrush(brush)
        # elif plot_type == self.__gui_params__.MarkingLabels[1]:  # 'Intersections Connection'
        #     color = self.__gui_params__.PlottingStyles[plot_type + ' Unselected Color']
        #     width = self.__gui_params__.PlottingStyles[plot_type + ' Unselected Width']
        #     pen = pg.mkPen(color = color, width = width)
        #     brush = pg.mkBrush(color=color)
        #     item.setPen(pen)
        #     item.arrow.setStyle(pen = pen, brush = brush)
        # elif plot_type == self.__gui_params__.MarkingLabels[2]: # 'Undrivable Zone'
        #     color =self.__gui_params__.PlottingStyles[plot_type + ' Unselected Color']
        #     width = self.__gui_params__.PlottingStyles[plot_type + ' Unselected Width']
        #     pen = pg.mkPen(color = color, width = width)
        #     item.setPen(pen)
        # elif plot_type == self.__gui_params__.MarkingLabels[3]: # 'Parking Zone'
        #     color = self.__gui_params__.PlottingStyles[plot_type + ' Unselected Color']
        #     width = self.__gui_params__.PlottingStyles[plot_type + ' Unselected Width']
        #     pen = pg.mkPen(color = color , width = width)
        #     item.setPen(pen)

    def set_chosen_pen(self, item, plot_type):

        color = self.__gui_params.PlottingStyles['Item Selected Color']
        width = self.__gui_params.PlottingStyles['Item Selected Width']
        brush = pg.mkBrush(color=color)
        pen = pg.mkPen(color=color, width=width)

        # if plot_type in self.__gui_params__.MarkingLabels
        if plot_type == self.__gui_params.MarkingLabels[0]:
            item.setBrush(brush)
            item.setPen(pen)
        elif plot_type in self.__gui_params.MarkingLabels:
            item.setPen(pen)
            if plot_type == self.__gui_params.MarkingLabels[1]:
                item.arrow.setStyle(pen=pen, brush=brush)

    def item_clicked(self, item, new_chosen=True):
        """
        Handles the event when an item was clicked: changing color and remembering item incase a delete request follows

        Args:
            item:
            new_chosen:

        Returns:

        """

        if self.chosen_plot_item != None:
            self.set_pen(self.chosen_plot_item, self.chosen_plot_item.type)
            self.chosen_plot_item = None
        if new_chosen:
            plot_type = item.type
            self.set_chosen_pen(item, item.type)
            self.chosen_plot_item = item
            if self.navigation_mode == 'Route Planner':
                if plot_type == self.__gui_params.MarkingLabels[0]:
                    print(self.map_marking_thread.road_map.intersections[item.graph_ref])
                    self.naigation_points.append(item.graph_ref)
                    if len(self.naigation_points) == 2:
                        print('Two')
                        self.SIGNAL_plan_route.emit(self.naigation_points)
                        self.naigation_points = []
                    else:
                        print('One')
            elif plot_type == self.__gui_params.MarkingLabels[0]:  # 'Intersection'
                self.map_image_view_box.SIGNAL_left_click.emit(item.graph_ref)
                print(self.map_marking_thread.road_map.intersections[item.graph_ref])

            else:
                pos = self.map_image_view_box.mapSceneToView(item.pos)
                pos = (int(pos.x()), int(pos.y()))
                print(pos)
                self.map_image_view_box.SIGNAL_left_click.emit(pos)

    def diselect_plot_item(self):
        self.item_clicked(None, False)

    def remove_item(self):
        if self.chosen_plot_item is not None:
            plot_type = self.chosen_plot_item.type
            if plot_type in self.__gui_params.MarkingLabels:
                for key in self.plot_items_list[plot_type]:
                    if self.plot_items_list[plot_type][key] == self.chosen_plot_item and self.plot_items_list[plot_type][key] is not None:
                        self.plot_items_list[plot_type][key] = None
                self.SIGNAL_add_data.emit('Remove ' + plot_type, self.chosen_plot_item.graph_ref)
            self.map_image_view_box.removeItem(self.chosen_plot_item)
            self.chosen_plot_item = None
            self.SIGNAL_add_data.emit('Reset All', ())
            self.map_image_view_box.removeItem(self.unfinished_plot_item)
            self.unfinished_plot_item = None

    def remove_connected_rods(self, node):
        plot_type = self.__gui_params.MarkingLabels[1]  # 'Intersections connection'
        for key in self.plot_items_list[plot_type]:
            if self.plot_items_list[plot_type][key] is not None:
                if self.plot_items_list[plot_type][key].graph_ref[0] == node or self.plot_items_list[plot_type][key].graph_ref[1] == node:
                    self.map_image_view_box.removeItem(self.plot_items_list[plot_type][key])
                    self.plot_items_list[plot_type][key] = None

    def bring_intersections_to_front(self):
        plot_type = self.__gui_params.MarkingLabels[0]
        for key in self.plot_items_list[plot_type]:
            if self.plot_items_list[plot_type][key] is not None:
                self.map_image_view_box.removeItem(self.plot_items_list[plot_type][key])
                self.map_image_view_box.addItem(self.plot_items_list[plot_type][key])

    def update_tree_selection(self):
        intersection_show = False
        for key in self.legend_buttons:
            current_state = self.legend_buttons[key].checkState() == QtCore.Qt.Checked
            if current_state != self.legend_prev_state[key]:
                if current_state:
                    if key != self.__gui_params.LegendBoxLabels[0]:  # 'Intersections'
                        self.SIGNAL_replot_graph.emit(key)
                    intersection_show = True
                    print('show all: ' + str(self.__gui_params.LegendBoxLabels[0]))
                else:
                    for id, each in enumerate(self.__gui_params.LegendBoxLabels):
                        if key == each:  # 'Intersections'
                            plot_type = self.__gui_params.MarkingLabels[id]
                            for key2 in self.plot_items_list[plot_type]:
                                if self.plot_items_list[plot_type][key2] is not None:
                                    self.map_image_view_box.removeItem(self.plot_items_list[plot_type][key2])
                    print('hide all: ' + str(key))
                self.legend_prev_state[key] = current_state
        if intersection_show:
            self.SIGNAL_replot_graph.emit(self.__gui_params.LegendBoxLabels[0])  # 'Intersections'

    def reset_all(self):
        self.enable_radio_buttons(False)
        self.SIGNAL_add_data.emit('Reset All', ())
        self.navigation_mode = None
        self.check_all_buttons()

    def route_planner(self):
        self.reset_all()
        self.navigation_mode = 'Route Planner'
        print(self.navigation_mode)

    def plot_graph(self):
        self.map_marking_thread.road_map.plot_map(mirror=True)


def main():
    app = QtGui.QApplication([])
    mapping_tool = MappingTool()
    print('MappingGuiThred Initialized')
    mapping_tool.show()

    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        print('Qt Executed')
        print('______________________')
        app.instance().exec_()


if __name__ == '__main__':
    main()

# TODO: Document

# TODO: reset once only last line, reset twice the whole line, how to fill shape with opacity?


# TODO: 1. fix deleting intersection.

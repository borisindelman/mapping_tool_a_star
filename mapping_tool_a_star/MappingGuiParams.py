class MappingGuiParams:
    """
    program parameters class
    """

    def __init__(self):
        self.MapGraph = {'Resolution': 4}
        self.PlottingStyles = {'Intersection Unselected Color': 'm',
                               'Intersection Unselected Width': 6,
                               'Intersections Connection Unselected Color': (0, 250, 255),
                               'Intersections Connection Unselected Width': 2,
                               'Undrivable Zone Unselected Color': (204, 24, 0),
                               'Undrivable Zone Unselected Width': 2,
                               'Parking Zone Unselected Color': (25, 151, 0),
                               'Parking Zone Unselected Width': 2,
                               'Parking Space Unselected Color': (72, 232, 15),
                               'Parking Space Unselected Width': 2,
                               'Pickup Zone Unselected Color': (255, 149, 0),
                               'Pickup Zone Unselected Width': 3,
                               'Item Selected Color': 'y',
                               'Item Selected Width': 2}
        self.MapWidgetResizeFactor = 0.8
        self.GuiTitle = 'Mapping Utility'
        self.GuiVersion = '2.0'

        # Widget labels
        self.MainButtonsLabels = ['Load Map Image',
                                  'Load Markings From File',
                                  'Save Marking to File',
                                  'Add Markings to map']
        # 'Navigation']
        self.MarkingBoxText = 'Choose marking type:'
        self.MarkingLabels = ['Intersection',
                              'Intersections Connection',
                              'Undrivable Zone',
                              'Parking Zone',
                              'Parking Space',
                              'Pickup Zone']
        self.LegendBoxLabels = []
        for each in self.MarkingLabels:
            self.LegendBoxLabels.append(each + 's')
        self.LegendTitle = 'Legend:'
        self.NavigationBoxText = 'Choose navigation mode:'
        self.NavigationButtonsLabels = ['Plan route to destination',
                                        'Plot Graph',
                                        'Drive to selected Parking Space',
                                        'Park in parking lot (exploration)',
                                        'Pickup driver']
        self.ArrowSize = 14

        # Widget layouts
        self.MainButtonsBoxLayoutLocation = [0, 0]
        self.MarkingBoxLayoutLocation = [1, 0]
        self.LegendBoxLayoutLocation = [3, 0]
        self.NavigationButtonsBoxLayoutLocation = [2, 0]
        self.ViewBoxLayoutLocation = [0, 1, 8, 1]

        self.MarkingTypes = ['Node', 'Rod', 'Zone']

        self.MarkingButtonTypes = {self.MarkingLabels[0]: self.MarkingTypes[0],
                                   self.MarkingLabels[1]: self.MarkingTypes[1],
                                   self.MarkingLabels[2]: self.MarkingTypes[2],
                                   self.MarkingLabels[3]: self.MarkingTypes[2],
                                   self.MarkingLabels[4]: self.MarkingTypes[2],
                                   self.MarkingLabels[5]: self.MarkingTypes[2],
                                   }

        self.MessageTypes = {'Cannot Load Image': {'Title': 'Error', 'Text': 'Cannot Load Image', 'InformativeText': 'Please choose a valid map image file'},
                             'Legend Off': {'Title': 'Warning', 'Text': 'Cannot Add Marking', 'InformativeText': 'Marking is disabled when legend is set to not show'},
                             'Cannot Load Markings': {'Title': 'Error', 'Text': 'Cannot Load Markings',
                                                      'InformativeText': 'Please choose a valid map markings file'},
                             'Cannot Save Markings': {'Title': 'Error', 'Text': 'Cannot Save Markings',
                                                      'InformativeText': 'PLease enter a valid file name'},
                             'Markings Saved': {'Title': 'Information', 'Text': 'Markings Saved Succefully',
                                                'InformativeText': ''},
                             'Markings Loaded': {'Title': 'Information', 'Text': 'Markings Loaded Succefully',
                                                 'InformativeText': ''},
                             'Map Image Loaded': {'Title': 'Information', 'Text': 'Map Image Loaded Succefully',
                                                  'InformativeText': ''},
                             'Intersection Connection Exists': {'Title': 'Information', 'Text': 'Intersection connection already exists',
                                                                'InformativeText': 'Only one connection can exists between two intersections'},
                             'Markings Exists': {'Title': 'Question', 'Text': 'Markings Exists For This Map',
                                                 'InformativeText': 'Would you like to load markings?'}
                             }

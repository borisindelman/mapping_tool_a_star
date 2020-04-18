# Mapping Tool

This application demonstrates how roads and parking lots can be represented as graphs and how A* can be used to find optimal path between 2 points.

The application provides a GUI with the option to load maps and annotate intersections, roads, parking spots etc.

If existing annotation exists, the GUI will suggest to use them.

As well, an A* demonstration is provided by choosing 2 intersections. The application will calculate the best route and show it on the map.

The annotation can be presented as a graph to understand how the A* algorithm perceives the scene.

![](media/mapping_tool_demo.gif)

# Installing

* Create a python virtual environment and install packages using:
```
cd path/to/repo
pip install -r requirements.txt
```

* Activate python's virtual environment:
```
source venv/bin/activate
```

* run the application:
```
python mapping_tool_a_star/MappingTool.py
```   
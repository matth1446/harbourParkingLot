### HOW TO
Start pyqt5 designer (terminal): >>> qt5-tools designer

### UI for DSS
- Provide UI for user 
- On a grid, a user draws a parking layout 
- The grid is then transformed into a JSON file 
  - Each color in the user grid is one type of tile 
  - Roads consist of start and end coordinates
  - Parking lots attach to roads
  - Gates are the exit points, they don'd need connections

### Tile
A tile can look like this
```
{
        "node_id": 0,
        "type": "road",
        "capacity": "0",
        "allowed_veh": [
            "cars",
            "trucks"
        ],
        "start_pos": {
            "x": 0,
            "y": 0
        },
        "end_pos": {
            "x": 0,
            "y": 0
        },
        "connectsTo": [
            "0,0",
            "0,0"
        ]
    },
```
A node that reaches from x = 0, y = 0 to x = 3, y = 3 looks like this:
```
{
        "node_id": 0,
        "type": "road",
        "capacity": 10,
        "allowed_veh": [
            "cars",
            "trucks"
        ],
        "start_pos": {
            "x": 0,
            "y": 0
        },
        "end_pos": {
            "x": 3,
            "y": 0
        },
        "connectsTo": [
            "1,3"
        ]
    },
```
The attribute "connectsTo" consists of two integer values. The first value identifies the\
id of the road it is connected to. The seconds value identifies the position in the queue of\
the road, where cars will be added. 


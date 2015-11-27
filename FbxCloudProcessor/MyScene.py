#Scene related data and functions







class MyMesh() :    

    transform = [[ 1, 0, 0, 0],
                 [ 0, 1, 0, 0],
                 [ 0, 0, 1, 0],
                 [ 0, 0, 0, 0]]
    controlPoints = []
    vertexIndicesArray = []

    def __init__(self):
        self.transform = [[ 1, 0, 0, 0],
                        [ 0, 1, 0, 0],
                        [ 0, 0, 1, 0],
                        [ 0, 0, 0, 0]]
        self.controlPoints = []
        self.vertexIndicesArray = []

class MyPolygon() :

    mesh = 0        
    vertexIndicesArray = []
    depth = 0

    def __init__(self):
        mesh = 0        
        vertexIndicesArray = []
        depth = 0
import svgwrite
import MyMaths
import MyScene
from PIL import Image 

#This class receives a mesh with control points [on world space] and the camera transform 
class Renderer:

    dwg = {}

    imageWidth = 500
    imageHeight = 500

    worldToCamera = []
    mesh = {}
    polygons = []
    sortedPolygons = [] 
    worldBoundaries = []

    renderXRange = 0
    renderYRange = 0
    ZRange = 0

    minProjX = 0
    minProjY = 0
    minZ = 0

    def __init__(self):

        self.imageWidth = 500
        self.imageHeight = 500

        self.worldToCamera = []
        self.mesh = {}
        self.polygons = []
        self.sortedPolygons = []  
        self.worldBoundaries = [] 

        renderXRange = 0
        renderYRange = 0
        ZRange = 0

        self.minProjX = 0
        self.minProjY = 0
        self.minZ = 0

        self.dwg = svgwrite.Drawing('render.svg' ,size=(self.imageWidth, self.imageHeight))


    def Render(self, _mesh) :
        self.mesh = _mesh
        self.projectControlPoints()
        self.calculatePolygons()
        self.sortPolygons()
        self.drawPolygons()


    def SetCamera (self, _worldToCamera) :
        self.worldToCamera = _worldToCamera


    def SetWorldBoundaries (self, bound) :

        maxX = 0
        maxY = 0
        maxZ = 0

        minX = 0
        minY = 0
        minZ = 0

        self.worldBoundaries = bound
        count = range(len(self.worldBoundaries))
        for i in count:

            """project bounding box points"""
            self.worldBoundaries[i] = MyMaths.vectorDotMatrix(self.worldBoundaries[i], self.worldToCamera)                
            self.worldBoundaries[i] = [self.worldBoundaries[i][0], -self.worldBoundaries[i][1], self.worldBoundaries[i][2]]

            """check boundaries"""
            if (self.worldBoundaries[i][0] > maxX) :
                maxX = self.worldBoundaries[i][0]
            if (self.worldBoundaries[i][0] < minX) :
                minX = self.worldBoundaries[i][0]
            if (self.worldBoundaries[i][1] > maxY) :
                maxY = self.worldBoundaries[i][1]
            if (self.worldBoundaries[i][1] < minY) :
                minY = self.worldBoundaries[i][1]
            if (self.worldBoundaries[i][2] > maxZ) :
                maxZ = self.worldBoundaries[i][2]
            if (self.worldBoundaries[i][2] < minZ) :
                minZ = self.worldBoundaries[i][2]
        
        self.renderXRange = maxX - minX
        self.renderYRange = maxY - minY
        self.ZRange = maxZ - minZ

        self.minProjX = minX
        self.minProjY = minY
        self.minZ = minZ


    def projectControlPoints (self) :

        """transform to camera coordinates and project each control point of each mesh"""
        count = range(len(self.mesh.controlPoints))
        for i in count:    
               
            #control points must be in world coordinates                
            """controlPoints world->camera space"""                         
            self.mesh.controlPoints[i] = MyMaths.vectorDotMatrix(self.mesh.controlPoints[i], self.worldToCamera)                
            self.mesh.controlPoints[i] = [self.mesh.controlPoints[i][0], -self.mesh.controlPoints[i][1], self.mesh.controlPoints[i][2]]

            """normalize respect the image size and adapt to svg coordinates (Y axis inverted)"""
            self.mesh.controlPoints[i] = [self.mesh.controlPoints[i][0] - self.minProjX, self.mesh.controlPoints[i][1] - self.minProjY, self.mesh.controlPoints[i][2]]
            self.mesh.controlPoints[i] = [self.mesh.controlPoints[i][0]/self.renderXRange*self.imageWidth, self.mesh.controlPoints[i][1]/self.renderYRange*self.imageHeight, self.mesh.controlPoints[i][2]/self.ZRange]
            
        return         

    
    def calculatePolygons(self) :
        
        count = range(len(self.mesh.vertexIndicesArray))
        for i in count:   
            _myPolygon = MyScene.MyPolygon()            
            _myPolygon.vertexIndicesArray = self.mesh.vertexIndicesArray[i]
            z1 = self.mesh.controlPoints[_myPolygon.vertexIndicesArray[0]][2]
            z2 = self.mesh.controlPoints[_myPolygon.vertexIndicesArray[1]][2]
            z3 = self.mesh.controlPoints[_myPolygon.vertexIndicesArray[2]][2]
            _myPolygon.depth = (z1 + z2 + z3)/3 
            self.polygons.append(_myPolygon)

    def sortPolygons(self) :
        self.sortedPolygons =  sorted(self.polygons, key=lambda poly: poly.depth, reverse=False)                    
    
    def drawPolygons(self) :
        
        """background"""
        """dwg.add(dwg.rect(insert=(0, 0), size=('100%', '100%'), rx=None, ry=None, fill='rgb(255,255,255)'))"""            
        
        #evaluate color on a point of an image
        im = Image.open("Wood.jpg") #255x255 px
        imData = im.getdata()
        color = {}
        color = imData[0]

        
        for i in range(len(self.sortedPolygons)):
            polygon = svgwrite.shapes.Polygon()           
            for j in range(0,3) :            
                """take the corresponding control points for forming this polygon"""
                p = self.mesh.controlPoints[self.sortedPolygons[i].vertexIndicesArray[j]]
                p = [p[0], p[1]]
                polygon.points.append(p) 
                s = "rgb("+str(color[0])+","+str(color[1])+","+str(color[2])+")"
                polygon.fill(s)       
                                   
            self.dwg.add(polygon)

    def SaveImage(self) :

        self.dwg.save()



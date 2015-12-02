from __future__ import division
import svgwrite
import MyMaths
import MyScene
from PIL import Image 
import math

import cProfile

def do_cprofile(func):
    def profiled_func(*args, **kwargs):
        profile = cProfile.Profile()
        try:
            profile.enable()
            result = func(*args, **kwargs)
            profile.disable()
            return result
        finally:
            profile.print_stats()
    return profiled_func

#This class receives a mesh with control points [on world space] and the camera transform 
class Renderer:

    image = {}
    zRender = {}

    depthBuffer = []

    imageWidth = 0
    imageHeight = 0
    aspectRatio = 0

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

    colorBuffer = []

    def __init__(self, width, height):

        self.imageWidth = width
        self.imageHeight = height
        self.aspectRatio = 0

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

        #This will be the render target
        self.image = Image.new('RGB', (width, height))
        self.zRender = Image.new('RGB', (self.imageWidth, self.imageHeight))

        # TO-DO: change the camera to perspective and initialize this array with -1s
        # Creates a list containing 5 lists initialized to 2
        self.depthBuffer = [[2 for x in range(height)] for y in range(width)]
        
        self.colorBuffer = [(0,0,0) for x in range(width * height)]


    #@do_cprofile
    def Render(self, _mesh) :

        self.polygons = []
        self.sortedPolygons = []

        self.mesh = _mesh
        print 'Projecting control points'
        self.projectControlPoints()
        print 'Calculating polygons'
        self.calculatePolygons()
        print 'Sorting polygons'
        self.sortPolygons()
        print 'Drawing polygons'
        self.drawPolygons()

        #For debugging purposes
        self.renderZBuffer()
        
            

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

        self.aspectRatio = self.renderYRange/self.renderYRange


    def projectControlPoints (self) :

        """transform to camera coordinates and project each control point of each mesh"""
        count = range(len(self.mesh.controlPoints))
        for i in count:    
               
            #control points must be in world coordinates                
            """controlPoints world->camera space"""                         
            self.mesh.controlPoints[i] = MyMaths.vectorDotMatrix(self.mesh.controlPoints[i], self.worldToCamera)                
            self.mesh.controlPoints[i] = [self.mesh.controlPoints[i][0], -self.mesh.controlPoints[i][1], self.mesh.controlPoints[i][2]]

            """normalize respect the image size and adapt to screen coordinates (Y axis inverted)"""
            self.mesh.controlPoints[i] = [self.mesh.controlPoints[i][0] - self.minProjX, self.mesh.controlPoints[i][1] - self.minProjY, self.mesh.controlPoints[i][2] - self.minZ]
            #self.mesh.controlPoints[i] = [self.mesh.controlPoints[i][0]/self.renderXRange*self.imageWidth, self.mesh.controlPoints[i][1]/self.renderYRange*self.imageHeight, (self.mesh.controlPoints[i][2])/self.ZRange]

            if(self.aspectRatio < 1) :
                self.mesh.controlPoints[i] = [self.mesh.controlPoints[i][0]/self.renderXRange*self.imageWidth, self.mesh.controlPoints[i][1]/self.renderXRange*self.imageWidth, (self.mesh.controlPoints[i][2])/self.ZRange]
            if(self.aspectRatio >= 1) :
                self.mesh.controlPoints[i] = [self.mesh.controlPoints[i][0]/self.renderYRange*self.imageHeight, self.mesh.controlPoints[i][1]/self.renderYRange*self.imageHeight, (self.mesh.controlPoints[i][2])/self.ZRange]
                           


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
        #self.sortedPolygons =  sorted(self.polygons, key=lambda poly: poly.depth, reverse=False)                    
        self.sortedPolygons = self.polygons

    def drawPolygons(self) :
        
        """background"""
        """dwg.add(dwg.rect(insert=(0, 0), size=('100%', '100%'), rx=None, ry=None, fill='rgb(255,255,255)'))"""          
        
        
        texture = Image.open(".\\Assets\\" + self.mesh.textures[0].encode("ascii"))
                
        for i in range(len(self.sortedPolygons)):   
            
            #Control points in screen space
            a = self.mesh.controlPoints[self.sortedPolygons[i].vertexIndicesArray[0]]
            b = self.mesh.controlPoints[self.sortedPolygons[i].vertexIndicesArray[1]]
            c = self.mesh.controlPoints[self.sortedPolygons[i].vertexIndicesArray[2]]         
            
            uvs = []
            uvs.append(self.mesh.textureCoordinates[self.mesh.uvCoordsIndexArray[i][0]])
            uvs.append(self.mesh.textureCoordinates[self.mesh.uvCoordsIndexArray[i][1]])
            uvs.append(self.mesh.textureCoordinates[self.mesh.uvCoordsIndexArray[i][2]])


            #uvs.append([0.0, 0.0])
            #uvs.append([1.0, 0.00])
            #uvs.append([0.5, 0.25])

            #Get the triangle boundaries
            max_x = int(max(a[0], max(b[0], c[0])))+1
            if(max_x >= self.imageWidth) :
                max_x = self.imageWidth - 1
            min_x = int(min(a[0], min(b[0], c[0])))-1
            if(min_x < 0) :
                min_x = 0
            max_y = int(max(a[1], max(b[1], c[1])))+1
            if(max_y >= self.imageHeight) :
                max_y = self.imageHeight - 1
            min_y = int(min(a[1], min(b[1], c[1])))-1
            if(min_y < 0) :
                min_y = 0

            #Scan the pixels inside the boundaries rectangle
            for x in range (min_x, max_x):
                for y in range (min_y, max_y):
                    check = self.is_point_in_tri([x, y], a, b, c)
                    if check[0]:
                        #interpolate vertex parameters
                        uv = self.get_frag_uvs([check[1], check[2], check[3]], [uvs[0], uvs[1], uvs[2]])  
                        depth = self.get_frag_depth([check[1], check[2], check[3]], [a[2],b[2],c[2]])
                        
                        #check z-buffer before writing on the image
                        check = self.depthBuffer[x][y] < depth
                        if check :
                            hi = 5
                        if (self.depthBuffer[x][y] == 2 or self.depthBuffer[x][y] < depth) :
                            self.depthBuffer[x][y] = depth
                            (width, height) = texture.size                      
                            color = texture.getpixel((uv[0] * width, uv[1] * height))
                            self.draw_pixel(x, y, color)


            #Painting in SVG format
            """polygon = svgwrite.shapes.Polygon()
               
            for j in range(0,3) :            
                #take the corresponding control points for forming this polygon
                p = self.mesh.controlPoints[self.sortedPolygons[i].vertexIndicesArray[j]]
                p = [p[0], p[1]]
                polygon.points.append(p) 
                s = "rgb("+str(color[0])+","+str(color[1])+","+str(color[2])+")"
                polygon.fill(s)       
                                   
            self.dwg.add(polygon)"""

    def draw_pixel(self, x, y, color):
        
        #self.image.putpixel((x, y), color)
        #depthFactor = self.depthBuffer[x][y]
        #self.colorBuffer[y * self.imageWidth + x] = (int(color[0] * depthFactor), int(color[1] * depthFactor), int(color[2] * depthFactor), int(color[3] * depthFactor))
        self.colorBuffer[y * self.imageWidth + x] = color

        return

    def SaveImage(self) :

        #Save the frame
        self.image.putdata(self.colorBuffer)
        self.image.save("Assets/render.PNG")
        self.zRender.save("Assets/renderZBuffer.PNG")


    def renderZBuffer(self) :        

        countRow = range(0, self.imageHeight)
        for j in countRow :
            countColumn = range(0, self.imageWidth)
            for i in countColumn :
                color = (0, 0, 0)
                if (self.depthBuffer[i][j] == 2) :
                   color = (0, 0, 0)
                else:
                   factor = int(self.depthBuffer[i][j] * 255) #depth between 0-1
                   color = (factor, factor, factor)
                
                self.zRender.putpixel((i, j), color)
                        
        return


    #Returns a 4-value tuple with:
    #[0] = boolean stating wether the point is inside the triangle or not
    #[1, 2, 3] = barycentric coords of the point
    def is_point_in_tri(self, P, A, B, C):

        #Compute vectors        
        v0 = [C[0] - A[0], C[1] - A[1]]
        v1 = [B[0] - A[0], B[1] - A[1]]
        v2 = [P[0] - A[0], P[1] - A[1]]
    
        #Compute dot products
        dot00 = MyMaths.vector2ScalarProduct(v0, v0)
        dot01 = MyMaths.vector2ScalarProduct(v0, v1)
        dot02 = MyMaths.vector2ScalarProduct(v0, v2)
        dot11 = MyMaths.vector2ScalarProduct(v1, v1)
        dot12 = MyMaths.vector2ScalarProduct(v1, v2)

        #check if denom == 0, discard if neccessary
        denom = (dot00 * dot11 - dot01 * dot01)
        if(denom == 0) :
            return [False,0,0,0]

        #Compute barycentric coordinates
        invDenom = 1 / denom
        u = (dot11 * dot02 - dot01 * dot12) * invDenom
        v = (dot00 * dot12 - dot01 * dot02) * invDenom

        #Check if point is in triangle and return the barycentric coords
        return [(u >= 0) and (v >= 0) and (u + v < 1), u, v, 1 - u - v]


    def get_frag_uvs(self, bar_coords, uvs):

        u = bar_coords[0] * uvs[2][0] + bar_coords[1] * uvs[1][0] + bar_coords[2] * uvs[0][0]
        v = bar_coords[0] * uvs[2][1] + bar_coords[1] * uvs[1][1] + bar_coords[2] * uvs[0][1]

        return [u, 1-v]


    def get_frag_depth(self, bar_coords, depths):

        result = bar_coords[0] * depths[2] + bar_coords[1] * depths[1] + bar_coords[2] * depths[0]        

        return result



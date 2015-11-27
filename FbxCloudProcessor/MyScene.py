import fbx
import MyMaths

import svgwrite
from PIL import Image 

class Scene () :
    #Scene related data and functions

    renderer = {}

    imageWidth = 500
    imageHeight = 500

    meshes = []    
    root = {}

    cameraToWorld = []
    worldToCamera =  []

    def __init__(self):

        self.imageWidth = 500
        self.imageHeight = 500

        self.meshes = []
        self.polygons = []
        self.sortedPolygons = []
        self.root = {}

        self.cameraToWorld = []
        self.worldToCamera =  []

        self.renderer = {}


    def InitializeScene (self, fileName, _renderer) :

        self.renderer = _renderer
        manager = fbx.FbxManager.Create()
        importer = fbx.FbxImporter.Create(manager, 'myImporter')        
        status = importer.Initialize(fileName)
        if status == False :
            print 'fbx initialization failed'
            #print 'Error: %s' % importer.GetLastErrorString()
            sys.exit()

        fbxScene = fbx.FbxScene.Create( manager, 'myScene')
        importer.Import(fbxScene)
        importer.Destroy()
        
        root = fbxScene.GetRootNode() 

        self.InitializeCamera()
        self.exploreScene(root)

    def Render (self) :
        self.projectVertices()
        self.calculatePolygons()
        self.sortPolygons()
        self.drawPolygons()
    

    def InitializeCamera (self) :

        cameraToWorld = [[ 1, 0, 0, 0],
                         [ 0, 1, 0, 0],
                         [ 0, 0, 1, 0],
                         [ 0, 0, 0, 0]]    
        """rotate the camera to have an isometric point of view"""
        """careful: right handed euler rotation"""
        self.cameraToWorld = MyMaths.rotateMatrix(cameraToWorld, 45, -45, 0)
        self.worldToCamera = MyMaths.transposeMatrix(self.cameraToWorld) 


    def exploreScene(self, node) :   

        mesh = node.GetMesh()  
          
        if(mesh != None and (mesh.IsTriangleMesh()) == False) :
            print "Found a mesh not triangulated"     

        if(mesh != None and mesh.IsTriangleMesh()) :
            self.exploreMesh(node)            

        childNumber = node.GetChildCount()
        count = list(range(childNumber))
        for i in count:
            self.exploreScene(node.GetChild(i))   
                           
        return


    def exploreMesh (self, node) :

        mesh = node.GetMesh()
        m = MyMesh()

        fbxMatrix = fbx.FbxAMatrix()
        fbxMatrix = node.EvaluateGlobalTransform()
        for i in range (0, 4) :
            for j in range (0, 4) :
                m.transform[i][j] = fbxMatrix.Get(i, j)             

        cPoints = mesh.GetControlPoints();
        count = list(range(len(cPoints)))
        for i in count:
            p = [cPoints[i][0], cPoints[i][1], cPoints[i][2], 1]  
            """apply their global rotation"""
            p = MyMaths.vectorDotMatrix(p, m.transform)          
            m.controlPoints.append(p)

        polygonCount = mesh.GetPolygonCount()
        count = list(range(polygonCount))
        for i in count:       
            """Get indices for the current triangle"""   
            _indices = []   
            for j in range(0, 3): 
                _indices.append(mesh.GetPolygonVertex(i, j))

            """Check if the polygon is facing the camera, discard it if not""" 
            _normals = []
            for j in range(0, 3): 
                normal = fbx.FbxVector4()
                mesh.GetPolygonVertexNormal(i, j, normal) 
                """ rotate the normals too for culling purposes """ 
                normal = MyMaths.vectorDotMatrix(normal, m.transform)                  
                _normals.append([normal[0], normal[1], normal[2], normal[3]])

            """Here we have the normals of the 3 vertices. Interpolate and compare with the camera z vector"""
            interpolatedNormal = MyMaths.interpolate3Vectors(_normals[0], _normals[1], _normals[2])
            if (MyMaths.vector4ScalarProduct(interpolatedNormal, self.cameraToWorld[2]) > 0) :
                m.vertexIndicesArray.append(_indices)

        self.meshes.append(m)        
                                       
        return    
    
    def projectVertices (self) :

        maxRenderX = 0
        minRenderX = 0
        maxRenderY = 0
        minRenderY = 0

        """transform to camera coordinates and project each control point of each mesh"""
        for k in range(len(self.meshes)):       
            m = self.meshes[k]
            count = range(len(m.controlPoints))
            for i in count:       
                """controlPoints local->world space, not here, cause we have already culled them"""
                """m.controlPoints[i] = vectorDotMatrix(m.controlPoints[i], m.transform)"""
                """controlPoints world->camera space"""                         
                m.controlPoints[i] = MyMaths.vectorDotMatrix(m.controlPoints[i], self.worldToCamera)
                
                m.controlPoints[i] = [m.controlPoints[i][0], -m.controlPoints[i][1], m.controlPoints[i][2]]
                """check projected boundaries"""
                if (m.controlPoints[i][0] > maxRenderX) :
                    maxRenderX = m.controlPoints[i][0]
                if (m.controlPoints[i][0] < minRenderX) :
                    minRenderX = m.controlPoints[i][0]
                if (m.controlPoints[i][1] > maxRenderY) :
                    maxRenderY = m.controlPoints[i][1]
                if (m.controlPoints[i][1] < minRenderY) :
                    minRenderY = m.controlPoints[i][1]

        renderXRange = maxRenderX - minRenderX
        renderYRAnge = maxRenderY - minRenderY


        for k in range(len(self.meshes)):       
            m = self.meshes[k]
            count = range(len(m.controlPoints))
            for i in count:             
                """normalize respect the image size and adapt to svg coordinates (Y axis inverted)"""
                m.controlPoints[i] = [m.controlPoints[i][0] - minRenderX, m.controlPoints[i][1] - minRenderY, m.controlPoints[i][2]]
                m.controlPoints[i] = [m.controlPoints[i][0]/renderXRange*self.imageWidth, m.controlPoints[i][1]/renderYRAnge*self.imageHeight, m.controlPoints[i][2]]
        return     

    def calculatePolygons(self) :
        for k in range(len(self.meshes)):       
            m = self.meshes[k]
            count = range(len(m.vertexIndicesArray))
            for i in count:   
                _myPolygon = MyPolygon()
                _myPolygon.mesh = k
                _myPolygon.vertexIndicesArray = m.vertexIndicesArray[i]
                z1 = m.controlPoints[_myPolygon.vertexIndicesArray[0]][2]
                z2 = m.controlPoints[_myPolygon.vertexIndicesArray[1]][2]
                z3 = m.controlPoints[_myPolygon.vertexIndicesArray[2]][2]
                _myPolygon.depth = (z1 + z2 + z3)/3 
                self.polygons.append(_myPolygon)

    def sortPolygons(self) :
        self.sortedPolygons =  sorted(self.polygons, key=lambda poly: poly.depth, reverse=False)                    
    
    def drawPolygons(self) :
        dwg = svgwrite.Drawing('render.svg' ,size=(self.imageWidth, self.imageHeight))
        """background"""
        """dwg.add(dwg.rect(insert=(0, 0), size=('100%', '100%'), rx=None, ry=None, fill='rgb(255,255,255)'))"""            
        
        #evaluate color on a point of an image
        im = Image.open("Wood.jpg") #255x255 px
        imData = im.getdata()
        color = {}
        color = imData[0]

        
        for i in range(len(self.sortedPolygons)):
            polygon = svgwrite.shapes.Polygon()
            m = self.sortedPolygons[i].mesh
            for j in range(0,3) :            
                """take the corresponding control points for forming this polygon"""
                p = self.meshes[m].controlPoints[self.sortedPolygons[i].vertexIndicesArray[j]]
                p = [p[0], p[1]]
                polygon.points.append(p) 
                s = "rgb("+str(color[0])+","+str(color[1])+","+str(color[2])+")"
                polygon.fill(s)            
                                   
            dwg.add(polygon)
        dwg.save()   
    
    
    

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
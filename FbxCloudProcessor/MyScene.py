import fbx
import MyMaths
import MyRenderer

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
        boundaries = self.calculateWorldBoundaries()
        self.renderer.SetCamera(self.worldToCamera)
        self.renderer.SetWorldBoundaries(boundaries)
        count = list(range(len(self.meshes)))
        for i in count: 
            self.renderer.Render(self.meshes[i])
        self.renderer.SaveImage()
        return
    

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
    
    
    def calculateWorldBoundaries (self) :

        maxX = 0
        minX = 0
        maxY = 0
        minY = 0
        maxZ = 0
        minZ = 0

        boundaries = []
        
        for k in range(len(self.meshes)):       
            m = self.meshes[k]
            count = range(len(m.controlPoints))
            for i in count:       
                #control points must be in world coordinates
                """check boundaries"""
                if (m.controlPoints[i][0] > maxX) :
                    maxX = m.controlPoints[i][0]
                if (m.controlPoints[i][0] < minX) :
                    minX = m.controlPoints[i][0]
                if (m.controlPoints[i][1] > maxY) :
                    maxY = m.controlPoints[i][1]
                if (m.controlPoints[i][1] < minY) :
                    minY = m.controlPoints[i][1]
                if (m.controlPoints[i][2] > maxZ) :
                    maxZ = m.controlPoints[i][2]
                if (m.controlPoints[i][2] < minZ) :
                    minZ = m.controlPoints[i][2]

        boundaries.append([maxX, maxY, maxZ, 1])
        boundaries.append([maxX, minY, maxZ, 1]) 
        boundaries.append([minX, maxY, maxZ, 1])
        boundaries.append([minX, minY, maxZ, 1])

        boundaries.append([maxX, maxY, minZ, 1])
        boundaries.append([maxX, minY, minZ, 1])
        boundaries.append([minX, maxY, minZ, 1])
        boundaries.append([minX, minY, minZ, 1])                 
        
        return boundaries        

    
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


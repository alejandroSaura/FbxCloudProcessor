import fbx
import MyMaths
import MyRenderer
import sys
#import svgwrite
from PIL import Image 

class Scene () :
    #Scene related data and functions

    scene = {}

    renderer = {}   
    time = {}
    animationEvaluator = {}

    meshes = []    
    root = {}
    boundaries = []

    cameraToWorld = []
    worldToCamera =  []

    def __init__(self):   
        
        self.scene = {}     

        self.time = {}
        self.animationEvaluator = {}

        self.meshes = []
        self.polygons = []
        self.sortedPolygons = []
        self.root = {}
        self.boundaries = []
        
        self.cameraToWorld = []
        self.worldToCamera =  []

        self.renderer = {}


    def InitializeScene (self, fileName, _renderer) :

        self.time = fbx.FbxTime()
        #self.time.SetFrame(50)

        self.renderer = _renderer
        manager = fbx.FbxManager.Create()
        importer = fbx.FbxImporter.Create(manager, 'myImporter')        
        status = importer.Initialize(fileName)
        if status == False :
            print 'Scene: fbx initialization failed'
            print 'Scene: Error, %s' % importer.GetLastErrorString()
            sys.exit()

        self.scene = fbx.FbxScene.Create( manager, 'myScene')      

        importer.Import(self.scene)
        importer.Destroy()
        
        self.animationEvaluator = self.scene.GetAnimationEvaluator()

        self.root = self.scene.GetRootNode() 
        # self.InitializeCamera()
        #self.exploreScene(self.root) 


    def setTime(self, _time) :
        self.time.SetFrame(_time)    

    def clear(self) :
        self.meshes = []
        self.polygons = []
        self.sortedPolygons = []

        self.renderer.clear()

    def setBoundaries(self, newBoundaries) :
        self.boundaries = newBoundaries        

    def Render (self, fileName) :
        #print "Calculating world boundaries"
        #boundaries = self.calculateWorldBoundaries()

        boundaries = self.boundaries
        
        self.renderer.SetCamera(self.worldToCamera)
        self.renderer.SetWorldBoundaries(boundaries)

        count = list(range(len(self.meshes)))
        for i in count: 
            print "Frame "+ str(self.time.GetFrameCount())+", Scene: Rendering mesh " + str(i)+'\n'
            self.renderer.Render(self.meshes[i], fileName)
        #self.renderer.Render(self.meshes[3])

        #print "Saving final images"
        self.renderer.SaveImage()
        return
    

    def InitializeCamera (self, angleY) :

        self.cameraToWorld = [[ 1, 0, 0, 0],
                         [ 0, 1, 0, 0],
                         [ 0, 0, 1, 0],
                         [ 0, 0, 0, 0]]    
        """rotate the camera to have an isometric point of view"""
        """careful: right handed euler rotation"""
        self.cameraToWorld = MyMaths.rotateMatrix(self.cameraToWorld, -angleY, -45, 0)        
        self.worldToCamera = MyMaths.transposeMatrix(self.cameraToWorld) 


    def exploreScene(self, node) :         

        mesh = node.GetMesh() 
        if(mesh != None and (mesh.IsTriangleMesh()) == False) :
            print "Scene: Found a mesh not triangulated"

        if(mesh != None and mesh.IsTriangleMesh()) :
            self.exploreMesh(node)            

        childNumber = node.GetChildCount()
        count = list(range(childNumber))
        for i in count:
            self.exploreScene(node.GetChild(i))   
                           
        return

    def extractSkinWeights (self, mesh) :

        bones = []
        vertextBoneBindings = []
        for c in range(0,mesh.GetControlPointsCount()) :
            vertextBoneBindings.append([])

        deformersCount = mesh.GetDeformerCount()
        if(deformersCount == 0) :
            return ([], [])
        deformer = mesh.GetDeformer(0)

        defType = deformer.GetDeformerType()
        if (defType == 1) : #0 - unkwown, 1 - skin
            #print 'skin modifier found'
            clusterCount = deformer.GetClusterCount()
            for i in range(0,clusterCount) :
                cluster = deformer.GetCluster(i)
                lClusterMode = cluster.GetLinkMode()
                boneName = cluster.GetLink().GetName();

                # matrices for bind and inverse bind
                kLinkMatrix = fbx.FbxAMatrix()
                #transform of the cluster at binding time
                cluster.GetTransformLinkMatrix(kLinkMatrix)

                # transform of the cluster at time T
                kLinkMatrixT = fbx.FbxAMatrix()
                kLinkMatrixT = cluster.GetLink().EvaluateGlobalTransform(self.time);
                # inverse of the transform of the cluster at time T
                kInvLinkMatrixT = fbx.FbxAMatrix()
                kInvLinkMatrixT = kLinkMatrixT.Inverse()

                kTM = fbx.FbxAMatrix()
                #transform of the mesh at binding time
                cluster.GetTransformMatrix(kTM);

                kInvLinkMatrix = fbx.FbxAMatrix()
                kInvLinkMatrix = kLinkMatrix.Inverse()

                kM = fbx.FbxAMatrix()
                #skinning matrix
                kM = kInvLinkMatrix * kTM
                

                indexCount = cluster.GetControlPointIndicesCount() #here, count vertex, not indices
                indices = cluster.GetControlPointIndices()
                weights = cluster.GetControlPointWeights()
                
                bone = MyBone()
                bone.name = boneName

                bone.bindPoseMAtrix = kLinkMatrix
                bone.inverseBindPose = kInvLinkMatrix

                bone.boneMatrixT = kLinkMatrixT
                bone.inverseBoneMatrixT = kInvLinkMatrixT

                bone.kM = kM

                bone.vertexWeightsArray = [0] * mesh.GetControlPointsCount()                         

                for k in range(0, indexCount) :
                    #pair = [indices[k], weights[k]]
                    bone.vertexWeightsArray[indices[k]] = weights[k]                    
                    if(weights[k] != 0) : vertextBoneBindings[indices[k]].append(i)
                bones.append(bone)
            
        return (bones, vertextBoneBindings)


    def extractTextures(self, node, textureList):
        for materialIndex in range( 0, node.GetMaterialCount() ):
            #materialCount = node.GetMaterialCount()
            material = node.GetMaterial( materialIndex )
        for propertyIndex in range( 0, fbx.FbxLayerElement.sTypeTextureCount() ):

            property = material.FindProperty( fbx.FbxLayerElement.sTextureChannelNames( propertyIndex ) )

            for textureIndex in range( 0, property.GetSrcObjectCount( fbx.FbxFileTexture.ClassId ) ):

                texture = property.GetSrcObject( fbx.FbxFileTexture.ClassId, textureIndex )
                textureList.append(texture.GetRelativeFileName())
                #print texture.GetFileName()   

    def exploreMesh (self, node) :
        """
        if node.GetName() == 'Bone002' :
            print 'test bone'
        """

        mesh = node.GetMesh()         

        #this will transform the UVs from byPolygon to byControlPoint
        #mesh.SplitPoints()

        m = MyMesh()
        m.node = node;

        (m.bones, m.vertexBoneBindings) = self.extractSkinWeights(mesh)

        mesh_uvs = mesh.GetLayer( 0 ).GetUVs()
        if( not mesh_uvs ):
            print "Scene: Error, No UV coordinates found for the mesh"
            return 

        if( mesh_uvs.GetMappingMode() != 2 ):
            print "Scene: Error, UV mapping mode not supported, please use EMappingMode.eByPolygonVertex"
            return 


        uvs_array = mesh_uvs.GetDirectArray()
        uvs_count = uvs_array.GetCount()
        uv_values = []
        uv_indices = []

        for k in range( uvs_count ):
            uv = uvs_array.GetAt( k )
            uv = [ uv[ 0 ], uv[ 1 ] ]
            uv_values.append( uv )       


        

        m.textureCoordinates = uv_values
        self.extractTextures(node, m.textures)
        

        fbxMatrix = fbx.FbxAMatrix()
        fbxMatrix = node.EvaluateGlobalTransform(self.time)
        for i in range (0, 4) :
            for j in range (0, 4) :
                m.transform[i][j] = fbxMatrix.Get(i, j)             

        #print 'Scene: skinning mesh '+str(len(self.meshes))
        cPoints = mesh.GetControlPoints();
        count = list(range(len(cPoints)))
        for i in count:
            #local-space
            p = [cPoints[i][0], cPoints[i][1], cPoints[i][2], 1] 
             
            #to world-space coordinates
            p = MyMaths.vectorDotMatrix(p, m.transform)

            vertexToInterpolate = [] #one per bone skinned
            
            if(len(m.bones) != 0) :
                boneCount = len(m.vertexBoneBindings[i])
                for j in range(0,boneCount) :
                    boneIndex = m.vertexBoneBindings[i][j]
                    #if weight is 0, discard
                    weight = m.bones[boneIndex].vertexWeightsArray[i]                    
                    if weight == 0 : continue

                    #for Vertex -> get world coords in t=0, set vertex in bone-space, get vertex back to world-space with the bone's transform in t=x                    
                    boneNode = self.GetNode(self.root, m.bones[boneIndex].name)

                    vertex = p

                    t0 = fbx.FbxTime()
                    t0.SetFrame(0)

                    #boneTransform0 = self.animationEvaluator.GetNodeGlobalTransform(boneNode, t0)
                    boneInvTransform0 = m.bones[boneIndex].inverseBindPose
                    myboneInvTransform0 = [[ 1, 0, 0, 0],[ 0, 1, 0, 0],[ 0, 0, 1, 0],[ 0, 0, 0, 0]]                    
                    for y in range (0, 4) :
                        for z in range (0, 4) :
                            myboneInvTransform0[y][z] = boneInvTransform0.Get(y, z)

                    #myboneInvTransform0 = MyMaths.transposeMatrix(myboneTransform0)
                    pInBoneCoords0 = MyMaths.vectorDotMatrix(vertex, myboneInvTransform0)
                    

                    """boneTransformT = self.animationEvaluator.GetNodeGlobalTransform(boneNode, self.time) #frame x
                    myboneTransformT = [[ 1, 0, 0, 0],[ 0, 1, 0, 0],[ 0, 0, 1, 0],[ 0, 0, 0, 0]]
                    for y in range (0, 4) :
                        for z in range (0, 4) :
                            myboneTransformT[y][z] = boneTransformT.Get(y, z)

                    vertex = MyMaths.vectorDotMatrix(pInBoneCoords0, myboneTransformT)"""



                    boneTransform0 = m.bones[boneIndex].boneMatrixT
                    myboneTransform0 = [[ 1, 0, 0, 0],[ 0, 1, 0, 0],[ 0, 0, 1, 0],[ 0, 0, 0, 0]]                    
                    for y in range (0, 4) :
                        for z in range (0, 4) :
                            myboneTransform0[y][z] = boneTransform0.Get(y, z)

                    #myboneInvTransform0 = MyMaths.transposeMatrix(myboneTransform0)
                    vertex = MyMaths.vectorDotMatrix(pInBoneCoords0, myboneTransform0)

                    #apply bone weight 
                    vertex = [vertex[0]*weight, vertex[1]*weight, vertex[2]*weight, 1] 
                    vertexToInterpolate.append(vertex)                    
             
            if len(vertexToInterpolate) > 0 :
                p = [0, 0, 0]       
                for n in range(0, len(vertexToInterpolate)) :
                
                    p = [p[0] + vertexToInterpolate[n][0],  p[1] + vertexToInterpolate[n][1], p[2] + vertexToInterpolate[n][2], 1]
                              
            m.controlPoints.append(p)


            #mesh.text
            #m.textureCoordinates.append(mesh.GetAllChannelUV

        #print 'skinning finished'

        polygonCount = mesh.GetPolygonCount()
        count = list(range(polygonCount))

        vertex_id = 0

        for i in count:       
            """Get indices for the current triangle"""   
            _indices = []   
            poly_uvs = []

            """Check if the polygon is facing the camera, discard it if not""" 

            for j in range(0, 3): 

                _indices.append(mesh.GetPolygonVertex(i, j))


                uv_texture_index = mesh_uvs.GetIndexArray().GetAt(vertex_id)
                poly_uvs.append( uv_texture_index )

                vertex_id += 1

            v1 = m.controlPoints[_indices[0]]
            v2 = m.controlPoints[_indices[1]]
            v3 = m.controlPoints[_indices[2]]

            v1v2 = [v2[0]-v1[0], v2[1]-v1[1], v2[2]-v1[2], 0]
            v1v3 = [v3[0]-v1[0], v3[1]-v1[1], v3[2]-v1[2], 1]

            normal = MyMaths.vector4CrossProduct(v1v2, v1v3)
            if (MyMaths.vector4ScalarProduct(normal, self.cameraToWorld[2]) > 0) :
                m.vertexIndicesArray.append(_indices)
                m.uvCoordsIndexArray.append(poly_uvs)

        self.meshes.append(m)        
                                       
        return    


    def GetNode (self, node, name) :

        if  node.GetName() == name :
            return node

        childNumber = node.GetChildCount()
        count = list(range(childNumber))
        
        for i in count:
            n = self.GetNode(node.GetChild(i), name)            
            if n != False :
                return n   
                           
        return False
    
    
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

    node = {}

    transform = [[ 1, 0, 0, 0],
                    [ 0, 1, 0, 0],
                    [ 0, 0, 1, 0],
                    [ 0, 0, 0, 0]]
    controlPoints = []
    textureCoordinates = [] #uv coordinates
    uvCoordsIndexArray = []
    vertexIndicesArray = []
    textures = [] #paths to textures

    vertexBoneBindings = []

    bones = []

    def __init__(self):
        self.node = {}
        self.transform = [[ 1, 0, 0, 0],
                        [ 0, 1, 0, 0],
                        [ 0, 0, 1, 0],
                        [ 0, 0, 0, 0]]
        self.controlPoints = []
        self.vertexIndicesArray = []
        self.textures = []
        self.textureCoordinates = []
        self.uvCoordsIndexArray = []
        self.bones = []
        self.vertexBoneBindings = []

class MyPolygon() :

    mesh = 0        
    vertexIndicesArray = []
    depth = 0

    def __init__(self):
        self.mesh = 0        
        self.vertexIndicesArray = []
        self.depth = 0

class MyBone() :

    name = {}        
    vertexWeightsArray = []    

    bindPoseMAtrix = {}
    inverseBindPose = {}
    kM = {}

    boneMatrixT = {}
    inverseBoneMatrixT = {}

    def __init__(self):
        self.name = {}        
        self.vertexWeightsArray = []
        self.bindPoseMAtrix = {}
        self.inverseBindPose = {}
        self.kM = {}
        self.boneMatrixT = {}
        self.inverseBoneMatrixT = {}

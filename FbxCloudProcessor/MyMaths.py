import math

#Custom Maths module

def transposeMatrix (matrix) :

    """from 'python cookbook' """
    t = [[r[col] for r in matrix] for col in range(len(matrix[0]))] 

    return t

def vectorDotMatrix (vector, matrix) :

    if len(vector) < 4 :
        print 'vector length error'

    result = [0] * 4
    for i in range(4) :
        result[i] = vector[0] * matrix[0][i] + vector[1] * matrix[1][i] + vector[2] * matrix[2][i] + vector[3] * matrix[3][i]
        
    return result

def matrixDotMatrix (m1, m2) :
    result = [[ 1, 0, 0, 0],
                [ 0, 1, 0, 0],
                [ 0, 0, 1, 0],
                [ 0, 0, 0, 0]]
    for i in range(4) :
        for j in range(4) :
            result[i][j] = m1[i][0] * m2[0][j] + m1[i][1] * m2[1][j] + m1[i][2] * m2[2][j] + m1[i][3] * m2[3][j];
    return result

def rotateMatrix (matrix, Yaw, Pitch, Roll) :

    y = Yaw * math.pi/180;
    x = Pitch * math.pi/180;
    z = Roll * math.pi/180;
    result = matrix

    yawRotationMatrix = [[ math.cos(y), 0, -math.sin(y), 0],
                        [ 0, 1, 0, 0],
                        [ math.sin(y), 0, math.cos(y), 0],
                        [ 0, 0, 0, 0]]
    result = matrixDotMatrix(result, yawRotationMatrix);

    pitchRotationMatrixLocal = [[ 1, 0, 0, 0],
                        [ 0, math.cos(x), math.sin(x), 0],
                        [ 0, -math.sin(x), math.cos(x), 0],
                        [ 0, 0, 0, 0]]
    """F(g->g) = I(g->l) * F(l->l) * I(l->g) . Transform local->local rotation to global->global"""
    pitchRotationMatrixGlobal = matrixDotMatrix(matrixDotMatrix(transposeMatrix(result), pitchRotationMatrixLocal), result)
    result = matrixDotMatrix(result, pitchRotationMatrixGlobal);

    rollRotationMatrixLocal = [[ math.cos(z), math.sin(z), 0, 0],
                        [ -math.sin(z), math.cos(z), 0, 0],
                        [ 0, 0, 1, 0],
                        [ 0, 0, 0, 0]]
    rollRotationMatrixGlobal = matrixDotMatrix(matrixDotMatrix(transposeMatrix(result), rollRotationMatrixLocal), result)
    result = matrixDotMatrix(result, rollRotationMatrixGlobal);        

    return result

def interpolate3Vectors(v1, v2, v3) :
    result = [0, 0, 0, 0]
    for i in range(4):
        result[i] = (v1[i] + v2[i] + v3[i])/3
    return result

def vector4ScalarProduct (v1, v2) :
    result = v1[0]*v2[0] + v1[1]*v2[1] + v1[2]*v2[2];
    return result;

def vector2ScalarProduct(vec_a, vec_b):
    return (vec_a[0] * vec_b[0] + vec_a[1] * vec_b[1])

def vector4CrossProduct(vec_a, vec_b):
    s1 = (vec_a[1] * vec_b[2] - vec_a[2] * vec_b[1])
    s2 = (vec_a[2] * vec_b[0] - vec_a[0] * vec_b[2])
    s3 = (vec_a[0] * vec_b[1] - vec_a[1] * vec_b[0])

    return [s1, s2, s3, 0]

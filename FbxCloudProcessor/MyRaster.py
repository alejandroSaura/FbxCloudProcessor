from __future__ import division

from PIL import Image

import ImageDraw
import sys


#Some dummy vertex data
#Assume that the vertices are inside the viewport coords
vertices = []
vertices.append([10, 10])
vertices.append([790, 10])
vertices.append([400, 400])

uvs = []
uvs.append([0.0, 0.0])
uvs.append([1.0, 0.00])
uvs.append([0.5, 0.25])

indices = []
indices.append(0)
indices.append(1)
indices.append(2)

#This will be the render target
im = Image.new('RGB', (800, 800))

#Texture used to test
texture = Image.open('Assets/check.PNG')
#rgb_im = im.convert('RGB')


draw_triangle(indices[0], indices[1], indices[2])

#Save the frame
im.save("Assets/test.PNG")



def draw_pixel(x, y, color):
    #The image is defined as a global variable now, could be passed as argumetn
    im.putpixel((x, y), color)
    return


def draw_triangle(i0, i1, i2):
    a = vertices[i0]
    b = vertices[i1]
    c = vertices[i2]


    print "Drawing triangle"
    #Get the triangle boundaries
    max_x = max(a[0], max(b[0], c[0]))
    min_x = min(a[0], min(b[0], c[0]))
    max_y = max(a[1], max(b[1], c[1]))
    min_y = min(a[1], min(b[1], c[1]))

    #Scan the pixels inside the boundaries rectangle
    for x in range (min_x, max_x):
        for y in range (min_y, max_y):
            check = is_point_in_tri([x, y], a, b, c)
            if check[0]:
                uv = get_frag_uvs([check[1], check[2], check[3]], [uvs[i0], uvs[i1], uvs[i2]])
                #The texture is defined as a global variable now, could be passed as argumetn
                color = texture.getpixel((uv[0] * texture.width, uv[1] * texture.height))
                draw_pixel(x, y, color)


def get_frag_uvs(bar_coords, uvs):
    u = bar_coords[0] * uvs[0][0] + bar_coords[1] * uvs[1][0] + bar_coords[2] * uvs[2][0]
    v = bar_coords[0] * uvs[0][1] + bar_coords[1] * uvs[1][1] + bar_coords[2] * uvs[2][1]
    return [u, v]

def dot(vec_a, vec_b):
    return (vec_a[0] * vec_b[0] + vec_a[1] * vec_b[1])



#Returns a 4-value tuple with:
#[0] = boolean stating wether the point is inside the triangle or not
#[1, 2, 3] = barycentric coords of the point
def is_point_in_tri(P, A, B, C):
    #Compute vectors        
    v0 = [C[0] - A[0], C[1] - A[1]]
    v1 = [B[0] - A[0], B[1] - A[1]]
    v2 = [P[0] - A[0], P[1] - A[1]]
    
    #Compute dot products
    dot00 = dot(v0, v0)
    dot01 = dot(v0, v1)
    dot02 = dot(v0, v2)
    dot11 = dot(v1, v1)
    dot12 = dot(v1, v2)

    #Compute barycentric coordinates
    invDenom = 1 / (dot00 * dot11 - dot01 * dot01)
    u = (dot11 * dot02 - dot01 * dot12) * invDenom
    v = (dot00 * dot12 - dot01 * dot02) * invDenom

    #Check if point is in triangle and return the barycentric coords
    return [(u >= 0) and (v >= 0) and (u + v < 1), u, v, 1 - u - v]



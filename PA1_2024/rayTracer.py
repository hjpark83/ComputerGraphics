#!/usr/bin/env python3
# -*- coding: utf-8 -*
# sample_python aims to allow seamless integration with lua.
# see examples below

# python rayTracer.py scenes/one-sphere.xml
# python rayTracer.py scenes/four-spheres.xml

import os
import sys
import pdb  # use pdb.set_trace() for debugging
import code # or use code.interact(local=dict(globals(), **locals()))  for debugging.
import xml.etree.ElementTree as ET
import numpy as np
from PIL import Image 

MIN_DISTANCE = np.inf

class Color:    
    def __init__(self, colorArray):
        self.color = colorArray.astype(np.float64)
        
    # Gamma corrects this color.
    # @param gamma the gamma value to use (2.2 is generally used).
    def gammaCorrect(self, gamma):
        inverseGamma = 1.0 / gamma
        self.color=np.power(self.color, inverseGamma)

    def toUINT8(self):
        return (np.clip(self.color, 0,1)*255).astype(np.uint8)

class Camera:
    def __init__(self, viewPoint, viewDir, projNormal, viewUp, projDistance, viewWidth, viewHeight):
        self.viewPoint = viewPoint
        self.viewDir = viewDir
        self.projNormal = projNormal
        self.viewUp = viewUp
        self.projDistance = projDistance
        self.viewWidth = viewWidth
        self.viewHeight = viewHeight
    
class Light:
    def __init__(self, position, intensity):
        self.position = position
        self.intensity = intensity
    
class Shader:
    def __init__(self, name, type):
        self.name = name
        self.type = type
    
class Lambertian(Shader):
    def __init__(self, diffuseColor):
        self.diffuseColor = diffuseColor

class Phong(Shader):
    def __init__(self, diffuseColor, specularColor, exponent):
        self.diffuseColor = diffuseColor
        self.specularColor = specularColor
        self.exponent = exponent

class Sphere:
    def __init__(self, shader, center, radius):
        self.shader = shader
        self.center = center
        self.radius = radius

def normalized_vector(d):
    return d / np.linalg.norm(d)

def raytracing(surface_list, ray, viewPoint):
    global MIN_DISTANCE
    t = MIN_DISTANCE
    closest = -1
    cnt = 0

    for surface in surface_list:
        if isinstance(surface, Sphere):
            d = ray
            p = viewPoint - surface.center
            dd = np.dot(d, d)
            dp = np.dot(d, p)
            pp = np.sum(np.power(p, 2))
            discriminant = np.power(dp, 2) - np.dot(dd, (pp - np.power(surface.radius, 2))) # dp^2 - dd(pp - r^2)

            if discriminant >= 0:
                delta_t = np.sqrt(discriminant)
                t1 = -dp + delta_t
                t2 = -dp - delta_t

                if t1 >= 0:
                    if t >= t1 / dd:
                        t = t1 / dd
                        closest = cnt
                if t2 >= 0:
                    if t >= t2 / dd:
                        t = t2 / dd
                        closest = cnt
        cnt += 1 
    return [t, closest]


def shading(ray, viewPoint, lights, surface_list, t, closest):
    if closest == -1:
        return np.array([0, 0, 0]) # Background color
    else:
        colorArray = np.array([0, 0, 0]).astype(np.float64) # R, G, B
        n = np.array([0, 0, 0])
        v = - t * ray # view direction
            
        if isinstance(surface_list[closest], Sphere):
            n = normalized_vector(viewPoint - surface_list[closest].center + t * ray) # normal vector
                    
        for light in lights:
            l = normalized_vector(v + light.position - viewPoint) # light direction
            blocked = raytracing(surface_list, -l , light.position) # block 여부 확인
            
            if blocked[1] == closest:
                for i in range(3):
                    Lambertian_shading = surface_list[closest].shader.diffuseColor[i] * light.intensity[i] * max(0, np.dot(n, l)) # L_d = k_d * I * max(0, n . l)
                    Phong_shading = 0
                    
                    if isinstance(surface_list[closest].shader, Phong):
                        Phong_shading = surface_list[closest].shader.specularColor[i] * light.intensity[i] * np.power(max(0, np.dot(n, normalized_vector(v + l))), surface_list[closest].shader.exponent[0]) # L_s = k_s * I * max(0, n . h)^p
                        
                    colorArray[i] += Lambertian_shading + Phong_shading
        
        # color = Color(R, G, B)
        color = Color(colorArray)
        color.gammaCorrect(2.2)
        return color.toUINT8()


def main():
    tree = ET.parse(sys.argv[1])
    root = tree.getroot()
    
    # set default values
    viewPoint = np.array([0, 0, 0]).astype(np.float64)
    viewDir = np.array([0, 0, -1]).astype(np.float64)
    viewUp = np.array([0, 1, 0]).astype(np.float64)
    viewProjNormal = -1 * viewDir
    viewWidth = 1.0
    viewHeight = 1.0
    projDistance = 1.0
    intensity = np.array([1, 1, 1]).astype(np.float64)  # how bright the light is.

    # Create an empty image
    imgSize = np.array(root.findtext('image').split()).astype(np.int32)
    channels = 3
    img = np.zeros((imgSize[1], imgSize[0], channels), dtype=np.uint8)
    img[:, :] = 0


    surface_list = []
    light_list = []

    # read data from xml
    for c in root.findall('camera'):
        viewPoint = np.array(c.findtext('viewPoint').split()).astype(np.float64)
        if(c.findtext('viewDir')):
            viewDir = np.array(c.findtext('viewDir').split()).astype(np.float64)
        if(c.findtext('projNormal')):
            viewProjNormal = np.array(c.findtext('projNormal').split()).astype(np.float64)
        if(c.findtext('viewUp')):
            viewUp = np.array(c.findtext('viewUp').split()).astype(np.float64)
        if(c.findtext('projDistance')):
            projDistance = np.array(c.findtext('projDistance').split()).astype(np.float64)
        if(c.findtext('viewWidth')):
            viewWidth=np.array(c.findtext('viewWidth').split()).astype(np.float64)
        if(c.findtext('viewHeight')):
            viewHeight = np.array(c.findtext('viewHeight').split()).astype(np.float64)
            
    camera = Camera(viewPoint, viewDir, viewProjNormal, viewUp, projDistance, viewWidth, viewHeight)
    
    for c in root.findall('surface'):
        if c.get('type') == 'Sphere':
            center = np.array(c.findtext('center').split()).astype(np.float64)
            radius = np.array(c.findtext('radius').split()).astype(np.float64)

            ref = ''
            for check in c:
                if check.tag == 'shader':
                    ref = check.get('ref')

            for d in root.findall('shader'):
                if d.get('name') == ref:
                    if d.get('type') == 'Lambertian':
                        diffuseColor = np.array(d.findtext('diffuseColor').split()).astype(np.float64)
                        shader = Lambertian(diffuseColor)
                        sphere = Sphere(shader, center, radius)
                        surface_list.append(sphere)
                    elif d.get('type') == 'Phong':
                        diffuseColor = np.array(d.findtext('diffuseColor').split()).astype(np.float64)
                        specularColor = np.array(d.findtext('specularColor').split()).astype(np.float64)
                        exponent = np.array(d.findtext('exponent').split()).astype(np.float64)
                        shader = Phong(diffuseColor, specularColor, exponent)
                        sphere = Sphere(shader, center, radius)
                        surface_list.append(sphere)
                        
    for c in root.findall('light'):
        position = np.array(c.findtext('position').split()).astype(np.float64)
        intensity = np.array(c.findtext('intensity').split()).astype(np.float64)
        light = Light(position, intensity)
        light_list.append(light)
    
    pixel_x = camera.viewWidth / imgSize[0]
    pixel_y = camera.viewHeight / imgSize[1]
    
    w = normalized_vector(camera.viewDir)
    u = normalized_vector(np.cross(w, camera.viewUp))
    v = normalized_vector(np.cross(w, u))
    
    img_origin = w * camera.projDistance - (u * pixel_x * ((imgSize[0]/2) + 1/2) + v * pixel_y * ((imgSize[1]/2) + 1/2))
    
    for y in range(imgSize[0]):
        for x in range(imgSize[1]):
            ray = img_origin + u * x * pixel_x + v * y * pixel_y
            trace = raytracing(surface_list, ray, camera.viewPoint)
            img[y][x] = shading(ray, camera.viewPoint, light_list, surface_list, trace[0], trace[1])
            
            
    rawimg = Image.fromarray(img, 'RGB')
    rawimg.save(sys.argv[1]+'.png')
    
if __name__=="__main__":
    main()
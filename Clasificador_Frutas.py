# -*- coding: utf-8 -*-
"""
Created on Wed Oct 26 21:38:13 2022

@author: Cristian
"""

import cv2
import numpy as np
from scipy import ndimage
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from matplotlib import cm

def caracteristicas(img):
    
    I = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    umbral,_ = cv2.threshold(I, 0, 255, cv2.THRESH_OTSU)
    mascara = np.uint8((I<umbral)*255)
    output = cv2.connectedComponentsWithStats(mascara,4,cv2.CV_32S)
    cantObj = output[0]
    labels = output[1]
    stats = output[2]
    mascara = (np.argmax(stats[:,4][1:])+1==labels)
    mascara = ndimage.binary_fill_holes(mascara).astype(int)
    rojo = np.sum(mascara*img[:,:,0]/255)/np.sum(mascara)
    verde = np.sum(mascara*img[:,:,1]/255)/np.sum(mascara)
    
    mascara1 = np.uint8(mascara*255)
    
    contours,_ = cv2.findContours(mascara1,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    cnt = contours[0]
    rect = cv2.minAreaRect(cnt)
    box = cv2.boxPoints(rect)
    box = np.int0(box)
    m,n = mascara1.shape
    ar = np.zeros((m,n))
    mascaraRect = cv2.fillConvexPoly(ar, box, 1)
    mascaraRect = np.uint8(mascaraRect.copy()*255)
    
    contoursR,_ = cv2.findContours(mascaraRect,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    cntR = contoursR[0]
    
    centro, dimensiones,rotacion = cv2.minAreaRect(cntR)
    
    tasaAspecto = float(dimensiones[1])/float(dimensiones[0]) if dimensiones[1]<dimensiones[0] else float(dimensiones[0])/float(dimensiones[1])
    return rojo, verde, tasaAspecto                                                                                      
     
#img = cv2.imread('banano25.jpg')
#rojo, verde, tasa = caracteristicas(img)
datos = []
etiquetas = []
                    
for i in range(1,37):
    datos.append(caracteristicas(cv2.imread('banano{}.jpg'.format(i))))
    etiquetas.append(1)
    datos.append(caracteristicas(cv2.imread('manzana{}.jpg'.format(i))))
    etiquetas.append(-1)

datos = np.array(datos)
etiquetas = np.array(etiquetas)

fig = plt.figure()
ax = fig.add_subplot(111,projection='3d')
for i in range(72):
    if etiquetas[i] == 1:
        ax.scatter(datos[i,0], datos[i,1], datos[i,2], marker='*', c='y')
    else:
        ax.scatter(datos[i,0], datos[i,1], datos[i,2], marker='^', c='r')
        
ax.set_xlabel('Rojo')
ax.set_ylabel('Verde')
ax.set_zlabel('tasa aspecto')

############################### ENTRENAMIENTO ####################

A = np.zeros((4,4))
b = np.zeros((4,1))

for i in range(72):
    x = np.append([1],datos[i])
    x = x.reshape((4,1))
    y = etiquetas[i]
    A = A + x*x.T
    b = b + x*y
    
inv = np.linalg.inv(A)
w = np.dot(inv,b)
X = np.arange(0,1,0.1)
Y = np.arange(0,1,0.1)
X,Y = np.meshgrid(X,Y)
Z = -(w[0]+w[1]*X+w[2]*Y)/w[3]
surf = ax.plot_surface(X,Y,Z, cmap = cm.Blues)

################################# ERROR DE ENTRENAMIENTO ###########

prediccion = []

for i in range(0,72):
    x = np.append([1],datos[i])
    x = x.reshape((4,1))
    prediccion.append(np.sign(np.dot(w.T,x)))
    
prediccion = np.array(prediccion).reshape((72))
efectividadEntrenamiento = (np.sum(prediccion==etiquetas)/72)*100
errorEntrenamiento = 100-efectividadEntrenamiento
print("Efectividad entrenamiento "+str(efectividadEntrenamiento)+"%")
print("Error entrenamiento "+str(errorEntrenamiento)+"%")

########################## DATOS PRUEBA ##########################


datosPrueba = []
etiquetasPrueba = []
                    
for i in range(1,7):
    datosPrueba.append(caracteristicas(cv2.imread('pruebaBanano{}.jpg'.format(i))))
    etiquetasPrueba.append(1)
    datosPrueba.append(caracteristicas(cv2.imread('pruebaManzana{}.jpg'.format(i))))
    etiquetasPrueba.append(-1)
datosPrueba = np.array(datosPrueba)
etiquetasPrueba = np.array(etiquetasPrueba)

for i in range(12):
    if etiquetas[i] == 1:
        ax.scatter(datosPrueba[i,0], datosPrueba[i,1], datosPrueba[i,2], marker='*', c='black')
    else:
        ax.scatter(datosPrueba[i,0], datosPrueba[i,1], datosPrueba[i,2], marker='^', c='blue')
        
prediccionPrueba = []

for i in range(0,12):
    x = np.append([1],datosPrueba[i])
    x = x.reshape((4,1))
    prediccionPrueba.append(np.sign(np.dot(w.T,x)))
    
prediccionPrueba = np.array(prediccionPrueba).reshape((12))
efectividadEntrenamientoPrueba = (np.sum(prediccionPrueba==etiquetasPrueba)/12)*100
errorEntrenamientoPrueba = 100-efectividadEntrenamientoPrueba

print("Efectividad prueba: "+str(efectividadEntrenamientoPrueba)+"%")
print("Error prueba: "+str(errorEntrenamientoPrueba)+"%")

####################### PREDICCIÓN EN UNA IMAGEN ####################

img = cv2.imread('pruebabanano6.jpg')
x = np.append([1],caracteristicas(img))
if np.sign(np.dot(w.T,x)) == 1:
    print('Es un banano')
else:
    print('Es una manzana')
    
        

    
    
    
    
    
    
    
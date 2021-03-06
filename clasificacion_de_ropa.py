# -*- coding: utf-8 -*-
"""Clasificacion de ropa.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1cEvHV_0h9lxefnsAk6etAZdGLqBM-_6X
"""

import tensorflow as tf
import tensorflow_datasets as tfds

datos, metadatos=tfds.load('fashion_mnist', as_supervised=True, with_info=True)

metadatos

datos_entrenamiento, datos_prueba= datos['train'],datos['test']

nombre_clases = metadatos.features['label'].names

nombre_clases

def normalizar(imagenes,etiquetas):
  imagenes=tf.cast(imagenes, tf.float32)
  imagenes/= 255 #aqui lo pasa de 0-255 a 0-1
  return imagenes,etiquetas

#normalizar los datos de entrenamiento y pruebas de la funcion
  datos_entrenamiento= datos_entrenamiento.map(normalizar)
  datos_prueba= datos_prueba.map(normalizar)

#Agregar los datos a cache, puesto que usar memoria en lugar de disco eficientiza el entrenamiento de los datos
datos_entrenamiento= datos_entrenamiento.cache()
datos_prueba= datos_prueba.cache()

#Mostrar una imagen de los datos de pruebas, de momento mostremos la primera
for imagen, etiqueta in datos_entrenamiento.take(1):
  break
imagen = imagen.numpy().reshape((28,28)) #Redimensionar, cosas de tensores, lo veremos despues

import matplotlib.pyplot as plt

#Dibujar dibujar
plt.figure()
plt.imshow(imagen, cmap=plt.cm.binary)
plt.colorbar()
plt.grid(False)
plt.show()

#creacion del modelo
modelo=tf.keras.Sequential([
 tf.keras.layers.Flatten(input_shape=(28,28,1)), #se encarga de hacer todo blanco y negro
 tf.keras.layers.Dense(50, activation=tf.nn.relu),
 tf.keras.layers.Dense(50, activation=tf.nn.relu),
 tf.keras.layers.Dense(10, activation=tf.nn.softmax)#softmax se suele usar en las redes de clasificacion, en la capa de salida para que la suma de cada imagen de 1 como valor entre los % finales

])

modelo.compile(
    optimizer='adam',
    loss=tf.keras.losses.SparseCategoricalCrossentropy(),
    metrics=['accuracy']
)

num_ej_entrenamiento=metadatos.splits['train'].num_examples
num_ej_pruebas=metadatos.splits['test'].num_examples

print(num_ej_entrenamiento),
print(num_ej_pruebas)

tam_lote=35
datos_entrenamiento= datos_entrenamiento.repeat().shuffle(num_ej_entrenamiento).batch(tam_lote)
datos_prueba=datos_prueba.batch(tam_lote)

import math
#parte donde se hace el entrenamiento
historial=modelo.fit(datos_entrenamiento,epochs=9,steps_per_epoch=math.ceil(num_ej_entrenamiento/tam_lote))

plt.xlabel(['# Iteracion'])
plt.ylabel(['# Magnitud de perdida'])
plt.plot(historial.history["loss"])

#Pintar una cuadricula con varias predicciones, y marcar si fue correcta (azul) o incorrecta (roja)
import numpy as np

for imagenes_prueba, etiquetas_prueba in datos_prueba.take(1):
  imagenes_prueba = imagenes_prueba.numpy()
  etiquetas_prueba = etiquetas_prueba.numpy()
  predicciones = modelo.predict(imagenes_prueba)
  
def graficar_imagen(i, arr_predicciones, etiquetas_reales, imagenes):
  arr_predicciones, etiqueta_real, img = arr_predicciones[i], etiquetas_reales[i], imagenes[i]
  plt.grid(False)
  plt.xticks([])
  plt.yticks([])
  
  plt.imshow(img[...,0], cmap=plt.cm.binary)

  etiqueta_prediccion = np.argmax(arr_predicciones)
  if etiqueta_prediccion == etiqueta_real:
    color = 'blue'
  else:
    color = 'red'
  
  plt.xlabel("{} {:2.0f}% ({})".format(nombre_clases[etiqueta_prediccion],
                                100*np.max(arr_predicciones),
                                nombre_clases[etiqueta_real]),
                                color=color)
  
def graficar_valor_arreglo(i, arr_predicciones, etiqueta_real):
  arr_predicciones, etiqueta_real = arr_predicciones[i], etiqueta_real[i]
  plt.grid(False)
  plt.xticks([])
  plt.yticks([])
  grafica = plt.bar(range(10), arr_predicciones, color="#777777")
  plt.ylim([0, 1]) 
  etiqueta_prediccion = np.argmax(arr_predicciones)
  
  grafica[etiqueta_prediccion].set_color('red')
  grafica[etiqueta_real].set_color('blue')
  
filas = 5
columnas = 5
num_imagenes = filas*columnas
plt.figure(figsize=(2*2*columnas, 2*filas))
for i in range(num_imagenes):
  plt.subplot(filas, 2*columnas, 2*i+1)
  graficar_imagen(i, predicciones, etiquetas_prueba, imagenes_prueba)
  plt.subplot(filas, 2*columnas, 2*i+2)
  graficar_valor_arreglo(i, predicciones, etiquetas_prueba)

#Exportacion del modelo a h5
modelo.save('modelo_exportado.h5')

#Instalar tensorflowjs para convertir el h5 a un modelo que pueda cargar tensorflowjs en un explorador
!pip install tensorflowjs

#Convertir el archivo h5 a formato de tensorflowjs
!mkdir tfjs_target_dir
!tensorflowjs_converter --input_format keras modelo_exportado.h5 tfjs_target_dir

#Veamos si si creo la carpeta
!ls

#Veamos el contenido de la carpeta
!ls tfjs_target_dir
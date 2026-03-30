# Chapter 1: Introducción al Aprendizaje Automático

## 1.1 ¿Qué es el aprendizaje automático?

El **aprendizaje automático** es una rama de la inteligencia artificial que
permite a los sistemas aprender de los datos sin ser programados explícitamente.
En lugar de seguir reglas predefinidas, un modelo de aprendizaje automático
construye su propio conjunto de reglas a partir de ejemplos.

Los tres tipos principales de aprendizaje automático son:

1. **Aprendizaje supervisado**: el modelo aprende a partir de un conjunto de
   entrenamiento etiquetado.
2. **Aprendizaje no supervisado**: el modelo identifica patrones en datos sin
   etiquetas.
3. **Aprendizaje por refuerzo**: un agente aprende a tomar decisiones mediante
   recompensas y penalizaciones.

## 1.2 El proceso de entrenamiento

El proceso de entrenamiento de un modelo consiste en los siguientes pasos:

- Preparar el conjunto de datos.
- Dividir los datos en conjunto de entrenamiento, conjunto de validación y
  conjunto de prueba.
- Seleccionar una arquitectura de modelo adecuada.
- Minimizar la función de pérdida mediante gradiente descendente.
- Evaluar el rendimiento sobre el conjunto de prueba.

```python
# Ejemplo básico de entrenamiento en Python
import numpy as np

X_train = np.array([[1, 2], [3, 4], [5, 6]])
y_train = np.array([0, 1, 0])

# El modelo se entrenaría aquí
print("Entrenamiento completado")
```

## 1.3 Sobreajuste y subajuste

Dos de los problemas más comunes en el aprendizaje automático son el
**sobreajuste** y el **subajuste**:

- El **sobreajuste** ocurre cuando el modelo memoriza los datos de entrenamiento
  y no generaliza bien a nuevos datos.
- El **subajuste** ocurre cuando el modelo es demasiado simple para capturar la
  estructura subyacente de los datos.

La **tasa de aprendizaje** y la complejidad del modelo son hiperparámetros
clave que influyen en este balance.

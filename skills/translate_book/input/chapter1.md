# Capítulo 1 — Introducción al Aprendizaje Automático

## 1.1 ¿Qué es el aprendizaje automático?

El **aprendizaje automático** es una rama de la inteligencia artificial que
permite a los sistemas aprender y mejorar automáticamente a partir de la
experiencia, sin ser explícitamente programados.

### Tipos de aprendizaje

Existen tres paradigmas principales:

1. **Aprendizaje supervisado** — el modelo se entrena con pares de entrada y
   salida etiquetados.
2. **Aprendizaje no supervisado** — el modelo descubre patrones en datos sin
   etiquetar.
3. **Aprendizaje por refuerzo** — un agente aprende tomando acciones en un
   entorno y recibiendo recompensas.

## 1.2 El pipeline de entrenamiento

Un pipeline típico de entrenamiento incluye los siguientes pasos:

| Paso | Descripción |
|------|-------------|
| Recolección de datos | Obtener y limpiar el conjunto de datos |
| Preprocesamiento | Normalización, codificación, división |
| Entrenamiento | Ajustar los parámetros del modelo |
| Evaluación | Medir el desempeño en datos de validación |
| Despliegue | Publicar el modelo en producción |

## 1.3 Ejemplo de código

El siguiente fragmento muestra una red neuronal sencilla en Python:

```python
import torch
import torch.nn as nn

class SimpleNet(nn.Module):
    def __init__(self, input_size: int, hidden_size: int, output_size: int) -> None:
        super().__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(hidden_size, output_size)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.fc2(self.relu(self.fc1(x)))
```

> **Nota:** La función de activación `ReLU` es una de las más utilizadas en
> redes neuronales profundas debido a su simplicidad y eficacia.

## 1.4 Sobreajuste y subajuste

Dos problemas frecuentes en el entrenamiento son el **sobreajuste** y el
**subajuste**.

- **Sobreajuste** ocurre cuando el modelo memoriza los datos de entrenamiento y
  no generaliza bien.
- **Subajuste** ocurre cuando el modelo es demasiado simple para capturar la
  complejidad de los datos.

La **validación cruzada** y la regularización son técnicas habituales para
mitigar estos problemas.

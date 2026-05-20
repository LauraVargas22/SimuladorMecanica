# ⚙️ Simulador Mecánico — Polea & Plano Inclinado

Aplicación educativa e interactiva desarrollada con **Streamlit** para simular el comportamiento dinámico de un sistema de dos cuerpos conectados mediante polea ideal y plano inclinado. A continuación encontrará el proyecto desplegado: 
https://simuladormecanica-proyectouis.streamlit.app/

---

## 📁 Estructura del Proyecto

```
simulador/
│
├── app.py                      # Punto de entrada — orquestador principal
│
├── physics/                    # Módulo de cálculos físicos
│   ├── __init__.py
│   ├── forces.py               # Fuerzas, aceleración, tensión (leyes de Newton)
│   └── sensitivity.py          # Barrido de ángulos para análisis de sensibilidad
│
├── ui/                         # Módulo de interfaz de usuario
│   ├── __init__.py
│   ├── styles.py               # Estilos CSS globales
│   ├── sidebar.py              # Panel lateral con controles de entrada
│   ├── results.py              # Panel de resultados y métricas
│   ├── diagram.py              # Diagrama matplotlib del sistema físico
│   └── charts.py               # Gráficas de sensibilidad (aceleración y tensión)
│
├── utils/                      # Utilidades generales
│   ├── __init__.py
│   └── validation.py           # Validación de parámetros de entrada
│
├── requirements.txt
└── README.md
```

---

## 🚀 Instalación y Ejecución

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Ejecutar la aplicación
cd simulador
python -m streamlit run app.py
```

---

## 🔬 Física del Sistema

### Fuerzas sobre m₁ (plano inclinado)
| Magnitud | Fórmula |
|---|---|
| Componente paralela | `F∥ = m₁ · g · sin(θ)` |
| Fuerza normal | `N = m₁ · g · cos(θ)` |
| Fricción | `Ff = μ · N` |

### Fuerza sobre m₂ (suspendido)
| Magnitud | Fórmula |
|---|---|
| Peso | `P₂ = m₂ · g` |

### Sistema
| Magnitud | Fórmula |
|---|---|
| Fuerza neta | `Fnet = P₂ − F∥ ± Ff` |
| Aceleración | `a = Fnet / (m₁ + m₂)` |
| Tensión | `T = m₂ · (g − a)` |

### Estados del sistema
- **Equilibrio**: `|P₂ − F∥| ≤ Ff_max`
- **m₂ desciende**: `P₂ > F∥ + Ff_max`
- **m₁ desciende**: `P₂ < F∥ − Ff_max`

---

## 📦 Dependencias

```
streamlit >= 1.32.0
numpy     >= 1.26.0
matplotlib>= 3.8.0
```

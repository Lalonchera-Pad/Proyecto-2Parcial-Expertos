import re
import itertools
import matplotlib.pyplot as plt
import pandas as pd

class Nodo:
    def __init__(self, valor):
        self.valor = valor
        self.izquierda = None
        self.derecha = None

def extraer_proposiciones(enunciado):
    # Modificar el enunciado para utilizar símbolos lógicos y reemplazar "NO" por "~"
    enunciado_modificado = enunciado.replace(" y ", "∧").replace(" o ", "∨").replace(" NO ", "~")
    
    # Extraer proposiciones, incluyendo las que contienen "NO "
    proposiciones = re.split(r',|\s+y\s+|\s+o\s+|\s+NO\s+', enunciado)
    variables = {}
    formula = enunciado_modificado

    for i, p in enumerate(proposiciones):
        p = p.strip()
        var = chr(112 + i)  # Generar variable p, q, r, ...
        
        # Si la proposición tiene "NO", asignar `~<variable>`
        if "~" in p:
            p_sin_no = p.replace("~", "").strip()  # Eliminar "~" para obtener solo la proposición
            variables[var] = p_sin_no  # Guardar la proposición sin "~" en variables
            formula = formula.replace(p, f"~{var}")
        else:
            variables[var] = p  # Guardar la proposición en variables sin cambios
            formula = formula.replace(p, var)
    
    return variables, formula

def construir_arbol(variables):
    if not variables:
        return None

    lista_variables = list(variables.keys())
    raiz = Nodo(lista_variables[0])
    cola = [(raiz, 1)]

    while cola:
        padre, idx = cola.pop(0)

        if idx < len(lista_variables):
            var_actual = lista_variables[idx]
            p_nodo_true = Nodo(f"{var_actual} = True")
            p_nodo_false = Nodo(f"{var_actual} = False")

            padre.izquierda = p_nodo_true
            padre.derecha = p_nodo_false

            cola.append((p_nodo_true, idx + 1))
            cola.append((p_nodo_false, idx + 1))

    return raiz

def graficar_arbol(nodo, ax, x, y, dx):
    if nodo is not None:
        ax.text(x, y, nodo.valor, ha='center', va='center', bbox=dict(boxstyle='round', facecolor='wheat'))

        if nodo.izquierda:
            ax.plot([x, x - dx], [y - 0.1, y - 0.4], 'k-')
            graficar_arbol(nodo.izquierda, ax, x - dx, y - 0.4, dx / 2)

        if nodo.derecha:
            ax.plot([x, x + dx], [y - 0.1, y - 0.4], 'k-')
            graficar_arbol(nodo.derecha, ax, x + dx, y - 0.4, dx / 2)

def evaluar_formula(formula, valores):
    for var, val in valores.items():
        formula = formula.replace(var, str(val))
    try:
        return eval(formula.replace('~', 'not ').replace('∧', ' and ').replace('∨', ' or '))
    except Exception:
        return None

def tabla_de_verdad(variables, formula):
    lista_variables = list(variables.keys())
    combinaciones = list(itertools.product([False, True], repeat=len(lista_variables)))
    resultados = []

    for combinacion in combinaciones:
        valores = dict(zip(lista_variables, combinacion))
        evaluar_formula(formula, valores)
        resultados.append(valores)

    return pd.DataFrame(resultados)

def estado_variables(formula):
    # Crear una tabla que muestra el estado de cada variable según la presencia de "~" en la fórmula
    estados = {}
    for var in set(re.findall(r'[pqrs]', formula)):  # Extraer variables p, q, r, ...
        estados[var] = False if f"~{var}" in formula else True
            
    return pd.DataFrame.from_dict(estados, orient='index', columns=["Valor"])

# Ejemplo de uso
enunciado = input("Introduce un enunciado: ")
variables, formula = extraer_proposiciones(enunciado)

# Imprimir resultados
print("Variables y proposiciones:")
for var, prop in variables.items():
    print(f"{var}: \"{prop}\"")

print("\nFórmula de lógica proposicional:")
print(formula)

# Construir el árbol de estados
arbol = construir_arbol(variables)

# Graficar el árbol
fig, ax = plt.subplots(figsize=(10, 6))
ax.axis('off')
graficar_arbol(arbol, ax, 0, 0, 4)
plt.title("Árbol de Estados")
plt.show()

# Generar y mostrar la tabla de verdad
tabla = tabla_de_verdad(variables, formula)
print("\nTabla de Verdad:")
print(tabla)

# Generar y mostrar la tabla de estados de las variables
tabla_estados = estado_variables(formula)
print("\nTabla de Estados de Variables:")
print(tabla_estados)

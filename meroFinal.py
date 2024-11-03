import re
import itertools
import matplotlib.pyplot as plt
import pandas as pd
import json

class Nodo:
    def __init__(self, valor):
        self.valor = valor
        self.izquierda = None
        self.derecha = None

# Variable global para el contador de variables
contador_variables = 1

def extraer_proposiciones(enunciado):
    global contador_variables
    enunciado_modificado = enunciado.replace(" y ", "∧").replace(" o ", "∨").replace(" NO ", " ~")
    proposiciones = re.split(r',|\s+y\s+|\s+o\s+|\s+NO\s+', enunciado)
    variables = {}
    formula = enunciado_modificado

    for p in proposiciones:
        p = p.strip()
        var = f"A{contador_variables}"
        contador_variables += 1

        if "NO" in p:
            p_sin_no = p.replace("NO", "").strip()
            variables[var] = p_sin_no
            formula = formula.replace(p, f"~{var}")
        else:
            variables[var] = p
            formula = formula.replace(p, var)

    formula = formula.replace("NO", "~")
    
    return variables, formula

def construir_arbol(variables):
    if not variables:
        return None
    lista_variables = list(variables.keys())
    raiz = Nodo(lista_variables[0])
    cola = [(raiz, 0)]

    while cola:
        padre, idx = cola.pop(0)

        if idx < len(lista_variables):
            var_actual = lista_variables[idx]

            p_nodo_true = Nodo(f"{var_actual} = True")
            p_nodo_false = Nodo(f"{var_actual} = False")

            padre.derecha = p_nodo_true
            padre.izquierda = p_nodo_false

            cola.append((p_nodo_false, idx + 1))
            cola.append((p_nodo_true, idx + 1))

    return raiz

def construir_arbol_global(estado_global):
    lista_variables = list(estado_global.keys())
    raiz = Nodo("Estado Global")
    cola = [(raiz, 0)]

    while cola:
        padre, idx = cola.pop(0)

        if idx < len(lista_variables):
            var_actual = lista_variables[idx]

            p_nodo_true = Nodo(f"{var_actual} = {estado_global[var_actual]['Valor']}")
            p_nodo_false = Nodo(f"{var_actual} = {not estado_global[var_actual]['Valor']}")

            padre.derecha = p_nodo_true
            padre.izquierda = p_nodo_false

            cola.append((p_nodo_false, idx + 1))
            cola.append((p_nodo_true, idx + 1))

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
        resultado = evaluar_formula(formula, valores)
        valores['Resultado'] = resultado
        resultados.append(valores)

    return pd.DataFrame(resultados)

def estado_variables(formula):
    estados = {}
    for var in set(re.findall(r'A\d+', formula)):
        estados[var] = False if f"~{var}" in formula else True
            
    return pd.DataFrame.from_dict(estados, orient='index', columns=["Valor"])

def actualizar_estado(tabla_estados):
    while True:
        print("\nTabla de Estados de Variables Actual:")
        print(tabla_estados)

        variable = input("Ingresa la variable que deseas cambiar (o escribe 'fin' para terminar): ")
        if variable.lower() == 'fin':
            break

        if variable in tabla_estados.index:
            nuevo_valor = input(f"Ingresa el nuevo valor para {variable} (True/False): ").strip().capitalize()
            if nuevo_valor in ["True", "False"]:
                tabla_estados.at[variable, "Valor"] = True if nuevo_valor == "True" else False
            else:
                print("Valor no válido, ingresa 'True' o 'False'.")
        else:
            print("Variable no encontrada en la tabla de estados.")

    return tabla_estados.to_dict(orient='index')  # Devolver la tabla de estados actualizada como diccionario

def guardar_json(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

def cargar_json(filename):
    with open(filename, 'r') as f:
        return json.load(f)

def guardar_cambios_en_json(resultados, filename):
    with open(filename, 'w') as f:
        json.dump(resultados, f, indent=4)

# Ejemplo de uso
opcion = input("¿Quieres (1) introducir enunciados o (2) cargar resultados desde un archivo JSON? (1/2): ")

if opcion == '1':
    enunciados = []

    print("Introduce hasta 20 enunciados (escribe 'fin' para terminar):")
    while len(enunciados) < 20:
        enunciado = input(f"Enunciado {len(enunciados) + 1}: ")
        if enunciado.lower() == 'fin':
            break
        enunciados.append(enunciado)

    resultados_totales = []

    for enunciado in enunciados:
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

        # Guardar en resultados totales
        data_to_save = {
            'enunciado': enunciado,
            'variables': variables,
            'formula': formula,
            'tabla': tabla.to_dict(orient='records'),
            'tabla_estados': tabla_estados.to_dict(orient='index')
        }
        resultados_totales.append(data_to_save)

    # Permitir al usuario cambiar el estado de las variables al final
    print("\nTodos los enunciados han sido procesados. Ahora puedes modificar las variables.")
    estado_global = {}

    for resultado in resultados_totales:
        tabla_estados = pd.DataFrame.from_dict(resultado['tabla_estados'], orient='index', columns=["Valor"])
        tabla_estados_actualizada = actualizar_estado(tabla_estados)
        resultado['tabla_estados'] = tabla_estados_actualizada  # Actualizar el resultado con la nueva tabla de estados
        estado_global.update(tabla_estados_actualizada)  # Actualizar el estado global
        print("\nTabla de Estados de Variables Final:")
        print(tabla_estados)

    # Generar y mostrar la tabla global de estados
    tabla_global_estados = pd.DataFrame.from_dict(estado_global, orient='index', columns=["Valor"])
    print("\nTabla Global de Estados de Variables:")
    print(tabla_global_estados)

    # Graficar el árbol global de estados
    arbol_global = construir_arbol_global(estado_global)
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.axis('off')
    graficar_arbol(arbol_global, ax, 0, 0, 4)
    plt.title("Árbol Global de Estados")
    plt.show()

    # Guardar todos los resultados en un archivo JSON
    guardar_json(resultados_totales, 'resultados.json')
    print("\nDatos guardados en 'resultados.json'.")

elif opcion == '2':
    filename = input("Introduce el nombre del archivo JSON a cargar: ")
    try:
        resultados = cargar_json(filename)
        for resultado in resultados:
            print("\nEnunciado:", resultado['enunciado'])
            print("Variables y proposiciones:")
            for var, prop in resultado['variables'].items():
                print(f"{var}: \"{prop}\"")
            print("\nFórmula de lógica proposicional:")
            print(resultado['formula'])

            # Mostrar tabla de verdad
            tabla = pd.DataFrame(resultado['tabla'])
            print("\nTabla de Verdad:")
            print(tabla)

            # Mostrar tabla de estados de las variables
            tabla_estados = pd.DataFrame.from_dict(resultado['tabla_estados'], orient='index', columns=["Valor"])
            print("\nTabla de Estados de Variables:")
            print(tabla_estados)

            # Permitir al usuario cambiar el estado de las variables
            tabla_estados_actualizada = actualizar_estado(tabla_estados)
            resultado['tabla_estados'] = tabla_estados_actualizada  # Actualizar el resultado con la nueva tabla de estados
            print("\nTabla de Estados de Variables Final:")
            print(tabla_estados)

            # Generar estado global
            if 'estado_global' not in locals():
                estado_global = {}
            estado_global.update(tabla_estados_actualizada)

            # Guardar los cambios en el JSON
            guardar_cambios_en_json(resultados, filename)

            # Graficar el árbol de estados
            variables = resultado['variables']
            arbol = construir_arbol(variables)
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.axis('off')
            graficar_arbol(arbol, ax, 0, 0, 4)
            plt.title("Árbol de Estados")
            plt.show()

        # Generar y mostrar la tabla global de estados
        tabla_global_estados = pd.DataFrame.from_dict(estado_global, orient='index', columns=["Valor"])
        print("\nTabla Global de Estados de Variables:")
        print(tabla_global_estados)

        # Graficar el árbol global de estados
        arbol_global = construir_arbol_global(estado_global)
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.axis('off')
        graficar_arbol(arbol_global, ax, 0, 0, 4)
        plt.title("Árbol Global de Estados")
        plt.show()

    except FileNotFoundError:
        print("El archivo no fue encontrado. Asegúrate de que el nombre sea correcto.")
    except json.JSONDecodeError:
        print("Error al leer el archivo JSON. Asegúrate de que esté en el formato correcto.")

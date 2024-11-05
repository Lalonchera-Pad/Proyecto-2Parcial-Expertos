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
resultados_totales = []
estado_global = {}


contador_variables = 1
proposiciones_globales = {}  # Diccionario para almacenar proposiciones y sus variables

def extraer_proposiciones(enunciado, proposiciones_existentes):
    global contador_variables
    # Reemplazo inicial para los operadores lógicos
    enunciado_modificado = enunciado.replace(" y ", " ∧ ").replace(" o ", " ∨ ").replace(" NO ", " ~")
    
    # Separar las proposiciones usando el nuevo formato
    proposiciones = re.split(r',|\s+∧\s+|\s+∨\s+', enunciado_modificado)
    variables = {}
    formula = ""
    operadores = re.findall(r'[∧∨]', enunciado_modificado)  # Obtener operadores en el mismo orden

    for i, p in enumerate(proposiciones):
        p = p.strip()
        if p == "":
            continue  # Ignorar entradas vacías

        # Verificar si la proposición está negada
        negada = "NO" in enunciado.split(p)[0]  # Ver si hay un "NO" antes de la proposición
        
        # Verificar si la proposición ya existe
        if p in variables.values():
            # Si ya existe, usar el mismo identificador
            var = [key for key, value in variables.items() if value == p][0]  # Obtener la variable existente
            p_modificado = f"~{var}" if negada else var  # Negar si está negada
        else:
            var = f"A{contador_variables}"
            contador_variables += 1
            
            # Guardar la proposición sin "NO"
            variables[var] = p if not negada else p.replace("NO", "").strip()
            # Crear la representación modificada de la proposición
            p_modificado = f"~{var}" if negada else var

            proposiciones_existentes.add(p)  # Agregar la proposición al conjunto

        if formula:  # Añadir el operador antes de la proposición excepto para la primera
            operador = operadores.pop(0) if operadores else "∧"  # Obtener el operador correspondiente
            formula += f" {operador} {p_modificado}"
        else:
            formula += p_modificado  # Añadir la primera proposición

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

            padre.izquierda = p_nodo_false
            padre.derecha = p_nodo_true

            cola.append((p_nodo_true, idx + 1))
            cola.append((p_nodo_false, idx + 1))
        else:
            # Aquí se modifican los nodos de los niveles más bajos
            # En lugar de usar A6=true y A6=false, usar las variables originales
            p_nodo_izquierda = Nodo(f"{variables[lista_variables[idx - 1]]} = {False}")
            p_nodo_derecha = Nodo(f"{variables[lista_variables[idx - 1]]} = {True}")

            padre.izquierda = p_nodo_izquierda
            padre.derecha = p_nodo_derecha

    return raiz



def construir_arbol_global(estado_global):
    if not estado_global:
        return None
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

def evaluar_formula(formula, valores):
    for var, val in valores.items():
        formula = formula.replace(var, str(val))
    try:
        return eval(formula.replace('¬', 'not ').replace('∧', ' and ').replace('∨', ' or '))
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

def estado_variables(formula, variables):
    estados = {}
    for var in set(re.findall(r'A\d+', formula)):
        # Asignar la proposición en lugar de true o false
        if f"¬{var}" in formula:
            estados[var] = f"NO {variables[var]}"  # Formato para negación
        else:
            estados[var] = variables[var]  # Usar la proposición original

    # Retornar un DataFrame con el estado de las variables
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

def guardar_txt(resultados, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("Cláusulas de Horn:\n")
        for resultado in resultados:
            variables = list(resultado['tabla_estados'].keys())
            estados = list(resultado['tabla_estados'].values())
            combinaciones = list(itertools.product(*[(var, f"¬{var}") if estado else (f"¬{var}", var) for var, estado in zip(variables, estados)]))
            
            for combinacion in combinaciones:
                clause = " ∧ ".join(combinacion)
                valor = "Verdadero" if any(estados) else "Falso"
                f.write(f"{clause} → {valor}\n")

def cargar_txt(filename):
    with open(filename, 'r') as f:
        return [line.strip() for line in f.readlines()]

def mostrar_formulas():
    for resultado in resultados_totales:
        print("\nEnunciado:", resultado['enunciado'])
        print("Fórmula de lógica proposicional:", resultado['formula'])

def mostrar_tablas_verdad():
    for resultado in resultados_totales:
        tabla = pd.DataFrame(resultado['tabla'])
        print("\nTabla de Verdad:")
        print(tabla)

def mostrar_estado_variables():
    for resultado in resultados_totales:
        tabla_estados = pd.DataFrame.from_dict(resultado['tabla_estados'], orient='index', columns=["Valor"])
        print("\nTabla de Estados de Variables:")
        print(tabla_estados)

def cambiar_valor_variables():
    for resultado in resultados_totales:
        tabla_estados = pd.DataFrame.from_dict(resultado['tabla_estados'], orient='index', columns=["Valor"])
        tabla_estados_actualizada = actualizar_estado(tabla_estados)
        resultado['tabla_estados'] = tabla_estados_actualizada

def graficar_arbol(nodo, ax, x, y, dx):
    if nodo is not None:
        ax.text(x, y, nodo.valor, ha='center', va='center', bbox=dict(boxstyle='round', facecolor='wheat'))

        if nodo.izquierda:
            ax.plot([x, x - dx], [y - 0.1, y - 0.4], 'k-')
            graficar_arbol(nodo.izquierda, ax, x - dx, y - 0.4, dx / 2)

        if nodo.derecha:
            ax.plot([x, x + dx], [y - 0.1, y - 0.4], 'k-')
            graficar_arbol(nodo.derecha, ax, x + dx, y - 0.4, dx / 2)

def mostrar_graficos():
    for resultado in resultados_totales:
        variables = resultado['variables']
        arbol = construir_arbol(variables)  # Esta función construirá el árbol con el nuevo formato
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.axis('off')
        graficar_arbol(arbol, ax, 0, 0, 4)  # Visualiza el árbol
        plt.title("Árbol de Estados")
        plt.show()


def obtener_variables_globales():
    variables_globales = {}
    for resultado in resultados_totales:
        for var in resultado['variables']:
            variables_globales[var] = resultado['tabla_estados'].get(var, {'Valor': False})  # Agrega el valor actual de la variable

    return variables_globales

def construir_arbol_global(variables_globales):
    if not variables_globales:
        return None
    
    lista_variables = list(variables_globales.keys())
    raiz = Nodo("Estado Global")
    cola = [(raiz, 0)]

    while cola:
        padre, idx = cola.pop(0)

        if idx < len(lista_variables):
            var_actual = lista_variables[idx]

            # Obtener el valor de la variable actual
            valor_actual = variables_globales[var_actual]['Valor']
            p_nodo_true = Nodo(f"{var_actual} = {valor_actual}")
            p_nodo_false = Nodo(f"{var_actual} = {not valor_actual}")

            padre.derecha = p_nodo_true
            padre.izquierda = p_nodo_false

            cola.append((p_nodo_false, idx + 1))
            cola.append((p_nodo_true, idx + 1))

    return raiz

def graficar_estado_global():
    variables_globales = obtener_variables_globales()
    if not variables_globales:
        print("No hay variables globales disponibles para mostrar.")
        return
    
    tabla_global_estados = pd.DataFrame.from_dict(variables_globales, orient='index', columns=["Valor"])
    print("\nTabla Global de Estados de Variables:")
    print(tabla_global_estados)

    arbol_global = construir_arbol_global(variables_globales)
    if arbol_global is None:
        print("No se pudo construir el árbol global.")
        return

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.axis('off')
    graficar_arbol(arbol_global, ax, 0, 0, 4)
    plt.title("Árbol Global de Estados")
    plt.show()

def menu():
    while True:
        print("\nMenú:")
        print("1. Mostrar fórmulas")
        print("2. Mostrar tablas de verdad")
        print("3. Mostrar estado de variables")
        print("4. Cambiar el valor de las variables")
        print("5. Mostrar gráficos")
        print("6. Mostrar gráfico global de estados")
        print("7. Salir")
        
        opcion = input("Selecciona una opción: ")

        if opcion == '1':
            mostrar_formulas()
        elif opcion == '2':
            mostrar_tablas_verdad()
        elif opcion == '3':
            mostrar_estado_variables()
        elif opcion == '4':
            cambiar_valor_variables()
        elif opcion == '5':
            mostrar_graficos()
        elif opcion == '6':
            graficar_estado_global()
        elif opcion == '7':
            guardar_json(resultados_totales, 'resultados.json')
            guardar_txt(resultados_totales, 'clausulas_horn.txt')
            print("\nDatos guardados. Saliendo...")
            break
        else:
            print("Opción no válida, intenta nuevamente.")

# Ejemplo de uso
opcion = input("¿Quieres (1) introducir enunciados, (2) cargar resultados desde un archivo JSON o (3) cargar enunciados desde un archivo TXT? (1/2/3): ")

if opcion == '1':
    enunciados = []
    proposiciones_existentes = set()  # Conjunto para llevar el control de las proposiciones

    print("Introduce hasta 20 enunciados (escribe 'fin' para terminar):")
    while len(enunciados) < 20:
        enunciado = input(f"Enunciado {len(enunciados) + 1}: ")
        if enunciado.lower() == 'fin':
            break
        enunciados.append(enunciado)

    for enunciado in enunciados:
        variables, formula = extraer_proposiciones(enunciado, proposiciones_existentes)

        # Guardar en resultados totales
        data_to_save = {
            'enunciado': enunciado,
            'variables': variables,
            'formula': formula,
            'tabla': tabla_de_verdad(variables, formula).to_dict(orient='records'),
            'tabla_estados': estado_variables(formula, variables).to_dict(orient='index')
        }
        resultados_totales.append(data_to_save)

elif opcion == '2':
    filename = input("Introduce el nombre del archivo JSON a cargar: ")
    try:
        resultados_totales = cargar_json(filename)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print("Error al cargar el archivo:", e)

elif opcion == '3':
    filename = input("Introduce el nombre del archivo TXT a cargar: ")
    try:
        enunciados = cargar_txt(filename)
        resultados_totales = []
        proposiciones_existentes = set()
        for enunciado in enunciados:
            variables, formula = extraer_proposiciones(enunciado, proposiciones_existentes)

            # Guardar en resultados totales
            data_to_save = {
                'enunciado': enunciado,
                'variables': variables,
                'formula': formula,
                'tabla': tabla_de_verdad(variables, formula).to_dict(orient='records'),
                'tabla_estados': estado_variables(formula, variables).to_dict(orient='index')

            }
            resultados_totales.append(data_to_save)

    except FileNotFoundError:
        print("El archivo no fue encontrado. Asegúrate de que el nombre sea correcto.")

# Llamar al menú
menu()

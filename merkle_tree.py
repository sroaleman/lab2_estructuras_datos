import hashlib

def sha256(texto): 
    return hashlib.sha256(texto.encode()).hexdigest() 

class ArbolMerkle: 
    def __init__(self, transacciones): 
        self.transacciones = transacciones  # Lista con los bloques/transacciones originales
        self.niveles = []                   # Matriz que almacenará cada nivel del árbol (de hojas a raíz)
        self.construir_arbol()              # Ejecuta la construcción al instanciar la clase

    def construir_arbol(self): 
        # 1. NIVEL 0 (Hojas): Genera el Hash SHA-256 para cada transacción original
        hojas = [sha256(tx) for tx in self.transacciones] 
        nivel_actual = hojas 
        self.niveles.append(nivel_actual) 

        # 2. Construcción Bottom-Up (de abajo hacia arriba) hasta llegar a 1 solo Hash (La Raíz)
        while len(nivel_actual) > 1: 
            # Si el nivel tiene nodos impares, pues se duplica el último elemento
            if len(nivel_actual) % 2 != 0: 
                nivel_actual.append(nivel_actual[-1]) 

            siguiente_nivel = [] 
            # se agrupa los nodos de 2 en 2 para calcular el nodo padre
            for i in range(0, len(nivel_actual), 2): 
                # se concatena Hash Izquierdo + Hash Derecho y aplica SHA-256
                padre = sha256(nivel_actual[i] + nivel_actual[i + 1]) 
                siguiente_nivel.append(padre) 

            self.niveles.append(siguiente_nivel)  # Se guarda el nuevo nivel en el árbol
            nivel_actual = siguiente_nivel       # Se sube al siguiente nivel

    def obtener_raiz(self): 
        # Se devuelve el único Hash que se encuentra en la cúspide (Merkle Root)
        return self.niveles[-1][0] 

    def obtener_prueba(self, indice): 
        # Se Genera el Merkle Proof (camino de hermanos necesarios para verificar sin todo el árbol)
        prueba = [] 
        for nivel in self.niveles[:-1]:  # Recorre los niveles excluyendo la raíz
            if len(nivel) % 2 != 0: 
                nivel = nivel + [nivel[-1]]  # Asegura el emparejamiento par en el cálculo de prueba

            # Si el índice es par, su hermano está a la derecha; si es impar, a la izquierda
            if indice % 2 == 0: 
                hermano_idx = indice + 1 
                posicion = 'derecha' 
            else: 
                hermano_idx = indice - 1 
                posicion = 'izquierda' 
             
            prueba.append((nivel[hermano_idx], posicion)) 
            indice = indice // 2  # Calcula la posición del padre en el siguiente nivel
             
        return prueba 

    def verificar_prueba(self, datos_tx, prueba, raiz_esperada): 
        # Se recalcula la raíz a partir del dato proporcionado y los hermanos entregados en la prueba
        hash_actual = sha256(datos_tx) 
        for hash_hermano, posicion in prueba: 
            if posicion == 'derecha': 
                combinado = hash_actual + hash_hermano 
            else: 
                combinado = hash_hermano + hash_actual 
            hash_actual = sha256(combinado) 
         
        # Se compara si el hash recalculado es exactamente igual a la Merkle Root guardada
        return hash_actual == raiz_esperada 

    def mostrar_diagrama(self): 
        # Se imprime visualmente el árbol de la Raíz (arriba) a las Hojas (abajo)
        print("\n--- DIAGRAMA DEL ÁRBOL (HOJAS Y RAMAS) ---") 
        for i, nivel in enumerate(reversed(self.niveles)): 
            pos = len(self.niveles) - 1 - i 
            nombre = "MERKLE ROOT (Raíz)" if pos == len(self.niveles) - 1 else ("NIVEL 0 (Hojas)" if pos == 0 else f"NIVEL {pos} (Ramas)")
            print(f"\n[{nombre}]") 
            
            # Luego imprime hashes truncados a 8 caracteres para legibilidad y resalta el nodo duplicado
            if len(nivel) % 2 != 0 and pos != len(self.niveles) - 1:
                for nodo in nivel: 
                    print(f"  └── {nodo[:12]}...") 
                print(f"  └── {nivel[-1][:12]}... [DUPLICADO PARA PAREJA PAR]")
            else:
                for nodo in nivel: 
                    print(f"  └── {nodo[:12]}...") 


# Función auxiliar para realizar la prueba automática (dato correcto vs. dato alterado)
def verificar_bloque_automatico(arbol, bloques, num_bloque):
    indice = num_bloque - 1
    bloque_real = bloques[indice]
    
    # Simula una alteración maliciosa en el dato
    bloque_falso = bloque_real.replace("pesos", "MILLONES de pesos")

    prueba = arbol.obtener_prueba(indice)
    raiz = arbol.obtener_raiz()
    
    # Evaluación de integridad
    valido = arbol.verificar_prueba(bloque_real, prueba, raiz)
    invalido = arbol.verificar_prueba(bloque_falso, prueba, raiz)
    
    print(f"\n--- VERIFICACIÓN DEL BLOQUE {num_bloque} ---")
    print(f"1. [DATO REAL]:     '{bloque_real}' -> Resultado: {valido}")
    print(f"2. [DATO ALTERADO]: '{bloque_falso}' -> Resultado: {invalido}")


# ========================================== 
# EXPERIMENTO DE EJECUCIÓN
# ========================================== 
if __name__ == "__main__": 
    # 1. Definición de los 5 bloques originales
    bloques = [ 
        "Tx1: Juan paga 10 pesos a Sebas", 
        "Tx2: Slleider paga 67 pesos a Juan", 
        "Tx3: Samuel paga 30 pesos a Ana",     # Bloque por defecto
        "Tx4: Ana paga 20 pesos a Maria", 
        "Tx5: Luis paga 30 pesos a Carlos"     # Bloque impar
    ] 

    # 2. Construcción e impresión gráfica del árbol
    print("=== 1. CONSTRUCCIÓN DEL ÁRBOL ===") 
    arbol = ArbolMerkle(bloques) 
    raiz = arbol.obtener_raiz() 
    print("Merkle Root (Raíz):", raiz[:12] + "...") 
    arbol.mostrar_diagrama() 

    # 3. Demostración del Efecto Avalancha (Cambio de Raíz al alterar un bloque)
    print("\n" + "="*45) 
    print("=== 2. MODIFICAR BLOQUE Y MOSTRAR CAMBIO DE RAÍZ ===") 
    bloques_editados = bloques.copy() 
    bloques_editados[0] = "Tx1: Juan paga 5 pesos a Sebas" 
     
    arbol_editado = ArbolMerkle(bloques_editados) 
    print("Raíz Original: ", raiz[:12] + "...") 
    print("Nueva Raíz:    ", arbol_editado.obtener_raiz()[:12] + "...") 
    print("¿La raíz cambió?:", raiz != arbol_editado.obtener_raiz()) 
   
    # 4. Prueba interactiva de inclusión
    print("\n" + "="*45) 
    print("=== 3. PRUEBA DE INCLUSIÓN ===") 
    
    entrada = input("Presione [Enter] para verificar el Bloque 3 o digite el número de bloque (1-5): ")
    
    if entrada.strip() == "" or not entrada.isdigit() or not (1 <= int(entrada) <= 5):
        num_bloque_elegido = 3
        print("-> Seleccionado: Bloque 3 (Predeterminado)")
    else:
        num_bloque_elegido = int(entrada)
        print(f"-> Seleccionado: Bloque {num_bloque_elegido}")

    verificar_bloque_automatico(arbol, bloques, num_bloque_elegido)
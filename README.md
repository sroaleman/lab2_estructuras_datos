# Laboratorio 3 — Sistema de búsqueda de estudiantes
### Lista vs Árbol Binario de Búsqueda (ABB) vs Árbol B+

## CODIGO DE HONOR/USO DE IA

Se usó un asistente de IA (Claude, Anthropic) para ayudar a diseñar la metodología estadística (tratamiento de outliers con IQR, ajuste de pendiente log-log), generar y depurar el código de los experimentos, y estructurar parte del informe. Todos los datos, cálculos y gráficas fueron ejecutados y verificados por mi en mi propia máquina fue completada y validada por mi con mis propios valores numéricos antes de la entrega. 

---

> ⚠️ **Antes de entregar:** En las tablas de resultados. Los valores de **altura** ya están puestos porque son deterministas (no dependen del hardware, solo de la semilla `seed=42`); los valores de **tiempo** sí dependen de tu computador y debes copiarlos de tus propios archivos `resultados_lab3/*.csv` — están hechos para que sea copiar y pegar, no recalcular nada.

---

## 1. Problema y objetivo

Se busco construir un sistema que permita **buscar** un estudiante por ID, **insertar** nuevos estudiantes y **listar** todos los estudiantes en orden ascendente de ID, implementado con tres estrategias de almacenamiento distintas: **Lista**, **Árbol Binario de Búsqueda (ABB)** y **Árbol B+**.

El objetivo no es solo implementar las tres estructuras, sino **estudiar experimentalmente** cómo escala el tiempo de ejecución de cada operación a medida que crece el tamaño de la entrada (N), y contrastar esos resultados contra la complejidad teórica esperada.

---

## 2. Estructuras de datos y algoritmos

| Estructura | Buscar | Insertar | Listar (orden ascendente) |
|---|---|---|---|
| **Lista** | O(n) — recorrido lineal | O(1) — se agrega al final | O(n log n) — hay que ordenar |
| **ABB** (sin rebalanceo) | O(log n) balanceado / **O(n) degenerado** | O(log n) balanceado / O(n) degenerado | O(n) — recorrido in-order |
| **B+** (M=16) | O(log n), base grande | O(log n), con *splits* cuando un nodo se llena | O(n) — hojas ya enlazadas y ordenadas |

**Detalle clave de la implementación:** el ABB usado **no tiene rebalanceo** (no es AVL ni Rojo-Negro), por lo que su comportamiento depende fuertemente del orden de inserción. El B+ sí se autobalancea (divide nodos llenos) sin importar el orden de llegada de los datos — esa es la diferencia estructural que se pone a prueba en este laboratorio.

`listar()` se verificó como correcta en las tres estructuras (recorrido in-order iterativo en el ABB, recorrido de hojas enlazadas en el B+, orden por `sort()` en la Lista) mediante una comprobación automática al inicio del script (ver sección 8).

---

## 3. Metodología experimental

### 3.1 Hardware y software
- **Sistema operativo:** Windows 11
- **Python:** 3.12.10
- **Procesador:** Intel64 Family 6 Model 186 Stepping 3, GenuineIntel
- Todo el experimento corre en **un solo proceso local, en RAM**, sin lectura/escritura de disco durante el cronometraje. No se usó Google Colab (evita la variabilidad de recursos compartidos de un entorno en la nube).

### 3.2 Generación de datos
IDs únicos generados por muestreo sin reemplazo (`random.sample`) sobre un rango amplio, simulando números de matrícula reales. Nombre, edad y promedio son sintéticos y no afectan las mediciones (solo el ID se usa para buscar/ordenar). Se fija `seed=42`, por lo que el experimento es **reproducible**: cualquiera que corra el mismo script obtiene exactamente los mismos datos y, por tanto, los mismos valores de altura del árbol (aunque los tiempos sí varían según el hardware).

### 3.3 Generación de las búsquedas
Para cada tamaño N se genera un conjunto de **M** IDs objetivo, elegidos aleatoriamente entre los IDs que **sí existen** en los datos (para medir el caso de búsqueda exitosa). M es un parámetro independiente, explorado específicamente en el Experimento D.

### 3.4 Método de medición de tiempos
Se usa `time.perf_counter()`, el reloj monotónico de mayor resolución disponible en Python.
- **Inserción:** se cronometra construir la estructura completa (las N inserciones).
- **Búsqueda:** se cronometra el total de las M búsquedas (no una búsqueda individual).
- **Listar:** se cronometra una llamada a `listar()` sobre la estructura ya construida.

### 3.5 Tratamiento de valores atípicos
Se aplica la **regla del rango intercuartílico (IQR)** por cada grupo (estructura, N): se descartan las repeticiones fuera de `[Q1 − 1.5·IQR, Q3 + 1.5·IQR]` antes de calcular la media y la desviación estándar. Se reporta también la **mediana** (estadístico robusto adicional) y cuántos valores se removieron por grupo. Con menos de 4 repeticiones no se aplica el filtro, porque el IQR no es confiable con tan pocos datos.

### 3.6 Estadísticas utilizadas
Media y desviación estándar (tras remover outliers), mediana, y una **regresión sobre ln(tiempo) vs ln(N)** para estimar el exponente empírico de crecimiento p (tiempo ≈ a·n^p) y compararlo contra la complejidad teórica.

### 3.7 Parámetros de cada experimento

| Experimento | N probados | M | Repeticiones | Tiempo de ejecución del experimento |
|---|---|---|---|---|
| A — Búsqueda, orden aleatorio | 10, 50, 100, 200, 500, 1000, 2000, 5000, 10000, 20000, 50000, 100000 | 100 | 5 | 6.73 s |
| B — Búsqueda, orden ya ordenado | 200, 500, 1000, 2000, 3000, 5000 *(acotado: inserción ordenada en el ABB es O(n²))* | 100 | 3 | 2.74 s |
| C — Construcción a gran escala | 10.000 / 100.000 / 1.000.000 | — | 3 | 41.07 s |
| D — Variación de M, N=10.000 fijo | — | 10, 100, 1000, 10000 | 5 | 8.76 s |
| L — Listar, orden aleatorio | 100, 1000, 10000, 100000 | — | 5 | 2.53 s |

**Tiempo total de la corrida:** 68.96 s (~1.1 min).

### 3.8 Verificación de correctitud
Antes de correr los experimentos, el script construye las tres estructuras con n=2.000 estudiantes y verifica que:
1. `listar()` produce exactamente la misma secuencia ordenada en las tres estructuras.
2. `buscar()` encuentra un ID que sí existe y no encuentra uno que no existe, en las tres estructuras.

Resultado obtenido: `[OK] Verificación de correctitud (n=2000): listar() y buscar() coinciden en Lista, ABB y B+.`

---

## 4. Resultados

### 4.1 Altura del árbol vs N
*(Estos valores son deterministas — dependen solo de `seed=42` y del orden de inserción, no del hardware. Deben coincidir exactamente con tu corrida.)*

**Orden aleatorio:**

| N | Altura ABB | Altura B+ |
|---|---|---|
| 10 | 6 | 1 |
| 50 | 10 | 2 |
| 100 | 13 | 2 |
| 200 | 19 | 3 |
| 500 | 17 | 3 |
| 1.000 | 22 | 3 |
| 2.000 | 23 | 4 |
| 5.000 | 28 | 4 |
| 10.000 | 30 | 4 |
| 20.000 | 37 | 5 |
| 50.000 | 36 | 5 |
| 100.000 | 44 | 5 |

**Orden ya ordenado:**

| N | Altura ABB | Altura B+ |
|---|---|---|
| 200 | 200 | 3 |
| 500 | 500 | 3 |
| 1.000 | 1.000 | 4 |
| 2.000 | 2.000 | 4 |
| 3.000 | 3.000 | 4 |
| 5.000 | 5.000 | 4 |

**Hallazgo central:** con inserción ordenada, la altura del ABB es **exactamente igual a N** — el árbol se degeneró por completo a una cadena (equivalente a una lista enlazada). El B+ prácticamente no se inmuta (crece de 3 a 4 niveles en el mismo rango).

![Altura vs tiempo de búsqueda](resultados_lab3/figE_altura_vs_busqueda.png)

### 4.2 Tiempo de búsqueda vs N (orden aleatorio)

| Estructura | N | Media [s] | Desv. estándar [s] | Outliers removidos |
|---|---|---|---|---|
| Lista | 10 | 4.14e-06 | 9.8e-07 | 0 |
| ABB | 10 | 3.42e-06 | 3.6e-07 | 0 |
| B+ | 10 | 4.38e-06 | 7.8e-07 | 0 |
| Lista | 50 | 4.43e-05 | 8.4e-06 | 0 |
| ABB | 50 | 1.77e-05 | 3.8e-06 | 0 |
| B+ | 50 | 1.82e-05 | 6.7e-06 | 0 |
| Lista | 100 | 1.24e-04 | 5.8e-08 | 2 |
| ABB | 100 | 3.36e-05 | 3.3e-07 | 1 |
| B+ | 100 | 2.34e-05 | 6.2e-07 | 1 |
| Lista | 200 | 2.49e-04 | 7.7e-06 | 1 |
| ABB | 200 | 4.30e-05 | 1.5e-07 | 2 |
| B+ | 200 | 2.86e-05 | 3.1e-07 | 1 |
| Lista | 500 | 8.89e-04 | 2.1e-04 | 0 |
| ABB | 500 | 5.45e-05 | 8.6e-06 | 1 |
| B+ | 500 | 4.06e-05 | 8.7e-06 | 0 |
| Lista | 1.000 | 1.36e-03 | 1.2e-04 | 0 |
| ABB | 1.000 | 5.28e-05 | 1.2e-06 | 1 |
| B+ | 1.000 | 3.14e-05 | 3.9e-07 | 1 |
| Lista | 2.000 | 2.68e-03 | 3.9e-05 | 2 |
| ABB | 2.000 | 6.13e-05 | 3.0e-06 | 1 |
| B+ | 2.000 | 3.95e-05 | 9.9e-07 | 1 |
| Lista | 5.000 | 6.12e-03 | 2.2e-04 | 1 |
| ABB | 5.000 | 9.77e-05 | 2.5e-05 | 0 |
| B+ | 5.000 | 4.82e-05 | 2.4e-06 | 0 |
| Lista | 10.000 | 1.28e-02 | 7.1e-05 | 2 |
| ABB | 10.000 | 8.45e-05 | 5.8e-06 | 0 |
| B+ | 10.000 | 5.34e-05 | 1.8e-06 | 0 |
| Lista | 20.000 | 2.40e-02 | 3.9e-04 | 1 |
| ABB | 20.000 | 1.42e-04 | 4.1e-05 | 0 |
| B+ | 20.000 | 8.58e-05 | 2.4e-05 | 0 |
| Lista | 50.000 | 7.68e-02 | 1.6e-04 | 2 |
| ABB | 50.000 | 2.13e-04 | 8.4e-05 | 0 |
| B+ | 50.000 | 1.96e-04 | 4.8e-06 | 1 |
| Lista | 100.000 | 1.764e-01 | 8.8e-03 | 0 |
| ABB | 100.000 | 2.84e-04 | 6.4e-05 | 0 |
| B+ | 100.000 | 3.01e-04 | 3.4e-05 | 0 |

![Búsqueda vs N, aleatorio](resultados_lab3/figA_busqueda_aleatorio.png)

**Título:** Tiempo de búsqueda vs N — orden aleatorio (N=10 a 100.000, M=100)
**Ejes:** X = N (número de estudiantes); Y = tiempo total de M=100 búsquedas, en segundos
**Curvas:** Lista (rojo), ABB (azul), B+ (verde), cada una con barras de error (±1 desviación estándar)

**Pendiente log-log (ajuste ln(tiempo) vs ln(N)):** Lista p=1.092, ABB p=0.387, B+ p=0.360. La Lista da casi exactamente 1 (confirma O(n)); ABB y B+ dan un exponente bastante menor a 1, consistente con un crecimiento mucho más lento que lineal (compatible con O(log N)). A N=100.000, la Lista tarda ~620 veces más que el ABB y ~586 veces más que el B+ en completar las 100 búsquedas.

### 4.3 Tiempo de búsqueda vs N (orden ya ordenado)

| Estructura | N | Media [s] | Desv. estándar [s] | Outliers removidos |
|---|---|---|---|---|
| Lista | 200 | 7.70e-04 | 2.1e-04 | 0 |
| ABB | 200 | 1.156e-03 | 4.4e-04 | 0 |
| B+ | 200 | 8.13e-05 | 1.7e-05 | 0 |
| Lista | 500 | 1.04e-03 | 1.9e-04 | 0 |
| ABB | 500 | 1.309e-03 | 3.2e-04 | 0 |
| B+ | 500 | 5.25e-05 | 1.4e-05 | 0 |
| Lista | 1.000 | 1.65e-03 | 3.8e-04 | 0 |
| ABB | 1.000 | 2.190e-03 | 1.4e-04 | 0 |
| B+ | 1.000 | 9.32e-05 | 7.4e-05 | 0 |
| Lista | 2.000 | 2.88e-03 | 2.1e-04 | 0 |
| ABB | 2.000 | 4.077e-03 | 1.7e-04 | 0 |
| B+ | 2.000 | 4.96e-05 | 1.3e-06 | 0 |
| Lista | 3.000 | 5.02e-03 | 8.7e-04 | 0 |
| ABB | 3.000 | 6.355e-03 | 8.3e-05 | 0 |
| B+ | 3.000 | 5.35e-05 | 4.6e-06 | 0 |
| Lista | 5.000 | 9.75e-03 | 2.0e-03 | 0 |
| ABB | 5.000 | 1.182e-02 | 6.3e-04 | 0 |
| B+ | 5.000 | 8.81e-05 | 3.7e-05 | 0 |

![Búsqueda vs N, ordenado](resultados_lab3/figB_busqueda_ordenado.png)

**Título:** Tiempo de búsqueda vs N — orden ya ordenado (caso patológico del ABB)
**Ejes:** X = N; Y = tiempo total de M=100 búsquedas, en segundos

**El ABB quedó consistentemente PEOR que la Lista** en todos los N probados (ej. N=5.000: ABB=0.0118s vs Lista=0.0098s), no solo igual de malo. Esto tiene sentido con la sección 4.1: ambos tienen un patrón O(n) porque la altura del ABB es exactamente N, pero el ABB paga un costo extra por recorrer objetos y punteros (`.izq`, `.der`) en vez de simplemente avanzar índices sobre un arreglo plano como hace la Lista. El B+ ni se entera: se mantiene 2 a 3 órdenes de magnitud más rápido que los otros dos en todo el rango, porque su altura sigue en 3-4 niveles sin importar el orden de entrada.

### 4.4 Tiempo de construcción a gran escala

| Estructura | N | Media [s] | Desv. estándar [s] | Outliers removidos |
|---|---|---|---|---|
| Lista | 10.000 | 5.85e-04 | 2.4e-05 | 0 |
| ABB | 10.000 | 1.206e-02 | 2.7e-04 | 0 |
| B+ | 10.000 | 1.130e-02 | 2.6e-04 | 0 |
| Lista | 100.000 | 8.42e-03 | 4.0e-03 | 0 |
| ABB | 100.000 | 2.833e-01 | 2.6e-02 | 0 |
| B+ | 100.000 | 2.098e-01 | 5.4e-02 | 0 |
| Lista | 1.000.000 | 8.43e-02 | 1.1e-02 | 0 |
| ABB | 1.000.000 | 5.586 | 0.35 | 0 |
| B+ | 1.000.000 | 5.281 | 0.28 | 0 |

![Construcción a gran escala](resultados_lab3/figC_construccion_gran_escala.png)

**Título:** Construcción vs N — 10.000 / 100.000 / 1.000.000 (orden aleatorio)
**Ejes:** X = N (escala log); Y = tiempo total de construcción, en segundos (escala log)

**A N=1.000.000, el ABB tardó ~66.3x más que la Lista en construirse, y el B+ ~62.7x más.** Confirma el trade-off: los árboles invierten mucho más tiempo al insertar (por el costo O(log n) de cada inserción, multiplicado por N inserciones) a cambio de búsquedas después mucho más rápidas — exactamente lo que se ve al comparar esta tabla con la de la sección 4.2.

### 4.5 Tiempo de búsqueda vs M (N=10.000 fijo)

| Estructura | M | Media [s] | Desv. estándar [s] | Outliers removidos |
|---|---|---|---|---|
| Lista | 10 | 1.49e-03 | 1.5e-04 | 0 |
| ABB | 10 | 2.52e-05 | 2.4e-06 | 1 |
| B+ | 10 | 1.52e-05 | 1.7e-06 | 0 |
| Lista | 100 | 1.476e-02 | 2.3e-04 | 2 |
| ABB | 100 | 1.662e-04 | 3.4e-06 | 1 |
| B+ | 100 | 1.218e-04 | 9.5e-07 | 2 |
| Lista | 1.000 | 1.579e-01 | 1.7e-03 | 1 |
| ABB | 1.000 | 1.204e-03 | 1.2e-04 | 0 |
| B+ | 1.000 | 7.29e-04 | 8.1e-05 | 0 |
| Lista | 10.000 | 1.535 | 0.054 | 0 |
| ABB | 10.000 | 1.188e-02 | 3.6e-03 | 0 |
| B+ | 10.000 | 5.16e-03 | 1.6e-04 | 1 |

![Variación de M](resultados_lab3/figD_variacion_M.png)

**Título:** Tiempo de búsqueda vs M — N=10.000 fijo, orden aleatorio
**Ejes:** X = M, número de búsquedas realizadas (escala log); Y = tiempo total, en segundos (escala log)

**Pendiente log-log vs M:** Lista p=1.007 (casi perfectamente lineal con M), ABB p=0.888, B+ p=0.837. Las tres crecen de forma aproximadamente proporcional a M — tiene sentido, porque cada búsqueda es independiente de las demás. La Lista es la que más se acerca a un p=1 exacto; ABB y B+ se quedan un poco por debajo de 1, probablemente porque a M pequeño el tiempo está más dominado por overhead fijo (creación de la lista de targets, llamadas a función) que por el costo real de cada búsqueda individual, que es tan rápido en los árboles que cuesta medirlo con precisión.

### 4.6 Tiempo de listar() vs N

| Estructura | N | Media [s] | Desv. estándar [s] | Outliers removidos |
|---|---|---|---|---|
| Lista | 100 | 2.59e-05 | 1.8e-05 | 0 |
| ABB | 100 | 3.04e-05 | 1.8e-05 | 0 |
| B+ | 100 | 2.12e-06 | 9.8e-07 | 1 |
| Lista | 1.000 | 1.558e-04 | 1.2e-05 | 0 |
| ABB | 1.000 | 1.284e-04 | 7.2e-06 | 1 |
| B+ | 1.000 | 2.71e-05 | 7.2e-06 | 1 |
| Lista | 10.000 | 2.237e-03 | 3.5e-05 | 1 |
| ABB | 10.000 | 1.317e-03 | 1.8e-04 | 0 |
| B+ | 10.000 | 2.28e-04 | 1.7e-05 | 1 |
| Lista | 100.000 | 3.644e-02 | 1.4e-04 | 1 |
| ABB | 100.000 | 3.369e-02 | 4.1e-03 | 0 |
| B+ | 100.000 | 6.55e-03 | 8.4e-04 | 0 |

![Listar vs N](resultados_lab3/figF_listar.png)

**Título:** Tiempo de listar() (orden ascendente por ID) vs N — orden aleatorio
**Ejes:** X = N (escala log); Y = tiempo de listar(), en segundos (escala log)

**El B+ fue el más rápido con claridad.** A N=100.000: Lista=0.0364s, ABB=0.0337s, B+=0.0066s — el B+ es ~5.6x más rápido que la Lista y ~5.1x más rápido que el ABB. Confirma la ventaja estructural del B+: como sus hojas ya están ordenadas y enlazadas (`sig`), listar es solo recorrer esa cadena sin comparar nada; la Lista tiene que ordenar desde cero (O(n log n)) y el ABB tiene que recorrer todo el árbol nodo por nodo con la sobrecarga de sus punteros.

---

## 5. Interpretación de las tendencias observadas

- **Lista:** tanto en búsqueda como en inserción se comporta de forma consistente con O(n) y O(1) respectivamente, sin diferencia entre orden aleatorio y ordenado (a la Lista no le importa el orden de llegada).
- **ABB, orden aleatorio:** la altura crece de forma logarítmica con N (de 6 a 44 niveles en el rango 10→100.000), consistente con un árbol razonablemente balanceado en promedio.
- **ABB, orden ordenado:** degeneración total — altura = N. El tiempo de búsqueda debería mostrar el mismo patrón O(n) que la Lista (e incluso un poco peor, por el overhead de recorrer objetos en vez de un arreglo plano).
- **B+:** prácticamente insensible al orden de inserción — su balanceo por *split* de nodos no depende de cómo lleguen los datos, lo cual se confirma con su altura casi constante (3 a 5 niveles) en todo el rango de N probado.
- **Construcción vs búsqueda — el trade-off:** los árboles son más costosos de construir que la Lista (pagan el balanceo por adelantado), pero esa inversión se recupera con creces en el costo de búsqueda a medida que N crece.

**Con los números exactos de esta corrida:** a N=100.000 la Lista tarda 0.1764s contra 0.00028s del ABB y 0.00030s del B+ (~620x y ~586x más lenta, respectivamente) — la brecha teórica entre O(n) y O(log n) se nota brutalmente a esta escala. Curiosamente, a N=100.000 el ABB (aleatorio, altura=44) queda ligeramente más rápido que el B+ (altura=5): aunque el B+ tiene menos niveles, cada nivel del B+ hace una búsqueda binaria entre hasta 16 claves (vía `bisect`), mientras que cada nivel del ABB es una sola comparación — a estos tamaños ambos quedan en el mismo orden de magnitud y el detalle de implementación empieza a pesar tanto como la complejidad teórica pura. En construcción (sección 4.4), la relación se invierte sin ambigüedad: ABB y B+ tardan ~66x y ~63x más que la Lista a N=1.000.000 — el costo de mantener la estructura ordenada se paga por adelantado, no en la búsqueda.

---

## 6. Respuestas a las preguntas de la guía

**¿Los resultados se comportan como predice la complejidad teórica?**
En general sí. La pendiente log-log de la Lista (p=1.092, sección 4.2) confirma O(n). Las pendientes de ABB (p=0.387) y B+ (p=0.360) son claramente sublineales, compatibles con O(log n) — aunque no dan exactamente 0 (que sería el caso de O(1)) ni replican perfectamente log(n) punto a punto, porque a estas escalas el *overhead* constante de Python y la resolución del reloj también influyen en la medición, sobre todo en N pequeño.

**¿En qué situaciones el ABB deja de comportarse como O(log N)?**
Cuando los datos se insertan ya ordenados por ID: cada nodo nuevo es mayor que todos los anteriores y siempre cuelga a la derecha, formando una cadena.

**¿Qué relación existe entre la altura del árbol y el tiempo de búsqueda?**
Son proporcionales: cada nivel adicional del árbol representa una comparación más en el peor caso. La tabla de la sección 4.1 y la gráfica de dispersión (figE) muestran esta correlación directamente.

**¿Qué ocurre cuando los datos se insertan ordenadamente?**
El ABB se degenera a una lista enlazada (altura = N); el B+ no se ve afectado.

**¿Qué diferencias aparecen entre los casos aleatorio y ordenado?**
Dramáticas para el ABB, insignificantes para la Lista (no le importa el orden) y para el B+ (se autobalancea).

**¿A partir de qué tamaño de entrada comienzan a ser claramente visibles las diferencias?**
Desde N≈100-200 ya la Lista es 3-9x más lenta que ABB/B+ (N=100: Lista=1.24e-4s vs ABB=3.36e-5s, ya ~3.7x; N=200: Lista=2.49e-4s vs B+=2.87e-5s, ~8.7x). La brecha sigue creciendo con N: para N=10.000 ya es un factor de ~150-240x, y para N=100.000 un factor de ~590-620x — la diferencia nunca deja de crecer porque las pendientes (O(n) vs sublineal) son distintas.

**¿Existen costos constantes que hagan que dos algoritmos con diferente complejidad tengan tiempos similares para entradas pequeñas?**
Sí: en N muy pequeño (10-50 estudiantes) el overhead constante de Python (creación de objetos, llamadas a función) domina sobre la diferencia algorítmica real, y las tres estructuras muestran tiempos de magnitud similar.

---

## 7. Principales hallazgos

1. El ABB sin rebalanceo es, en el peor caso (datos ordenados), tan malo como una Lista — a veces peor, por el overhead de atravesar objetos.
2. El árbol B+ cumple su promesa: es insensible al orden de inserción porque se autobalancea mediante *splits*.
3. Los árboles pagan un costo de construcción notablemente mayor que la Lista, a cambio de búsquedas mucho más rápidas a gran escala.
4. El B+ no solo es la estructura más rápida para buscar; también es la más rápida para listar en orden, porque sus hojas ya están enlazadas y ordenadas — una ventaja que no tienen ni la Lista ni el ABB.

---

## 8. Limitaciones del experimento

- El ABB implementado **no tiene rebalanceo** (no es AVL ni Rojo-Negro); un ABB autobalanceado no se degradaría con datos ordenados, igual que el B+.
- Las mediciones de tiempo dependen del hardware específico donde se corrió (ver sección 3.1); los valores absolutos no son comparables directamente con otra máquina, aunque las tendencias relativas sí deberían mantenerse.
- No se midió consumo de memoria, solo tiempo de ejecución.
- El experimento del caso "orden ordenado" se limitó a N≤5.000 porque la inserción ordenada en el ABB es O(n²): a N=1.000.000 el tiempo de ejecución habría sido impráctico.

---

## 9. Cómo reproducir el experimento

```bash
python3 laboratorio3_completo.py
```

Esto genera automáticamente, en una carpeta `resultados_lab3/` junto al script:
- Los CSV crudos y agregados de cada experimento (`A_...csv` a `L_...csv`).
- Las 6 gráficas (`figA` a `figF`).
- `ficha_tecnica.txt`, con el detalle de hardware, metodología y tiempos de la corrida.

El script usa `random.seed(42)`, por lo que los datos generados (y por tanto la altura de los árboles) son idénticos en cualquier máquina; solo los tiempos de ejecución varían según el hardware.

---

# Synthetic Financial Transactions Dataset

Este proyecto genera un dataset sintético de **transacciones financieras de movimiento de dinero** para fines educativos.  
Fue diseñado para que los estudiantes practiquen:

- exploración de datos
- limpieza de datos
- validación de reglas de negocio
- detección de anomalías
- detección de fraude
- feature engineering
- preparación de datos para modelos supervisados

---

## 1. Objetivo del dataset

El dataset representa clientes financieros con un comportamiento histórico de **3 meses**.  
Cada cliente tiene un perfil económico coherente con:

- su ocupación
- su sector
- su tipo de empleo
- su ingreso mensual
- su frecuencia de ingreso
- su intensidad transaccional
- su perfil de riesgo

Las transacciones válidas siguen un patrón normal del cliente y las transacciones fraudulentas se generan como una **anomalía** frente a ese patrón.

Además, el proyecto agrega **100,000 registros sucios o basura** para que los estudiantes puedan realizar procesos de limpieza y validación.

---

## 2. Tamaño del dataset

### Registros válidos
- **500,000** transacciones válidas

### Registros basura
- **100,000** registros sucios, inconsistentes o dañados

### Total
- **600,000** registros

### Clientes
- **7,000** clientes

---

## 3. Ventana temporal

El comportamiento se modela sobre una ventana de **3 meses**.

Por defecto, el script usa:

- `2025-01-01`
- `2025-03-31`

Esto puede modificarse por parámetro al ejecutar el script.

---

## 4. Proporción de fraude

Dentro de las **500,000 transacciones válidas**:

- **90% regulares**
- **10% fraudulentas**

Eso equivale a:

- **450,000** transacciones regulares
- **50,000** transacciones fraudulentas

---

## 5. Segmentación de clientes

Se definieron 3 grupos de clientes según su intensidad transaccional en 3 meses.

### Grupo regular
- **4,000 clientes**
- promedio cercano a **71 transacciones** en 3 meses

### Grupo alto flujo
- **1,200 clientes**
- entre **120 y 150 transacciones** en 3 meses

### Grupo moderado
- **1,800 clientes**
- entre **20 y 40 transacciones** en 3 meses

### Justificación
Esta mezcla fue elegida para que el total de transacciones válidas llegue a **500,000** sin perder realismo en la distribución.

---

## 6. Naturaleza de las transacciones

Estas transacciones son **movimientos financieros de dinero**, no compras comerciales genéricas.

Los productos financieros considerados son:

- `ahorro`
- `pago de prestamo`
- `pago de tarjeta`
- `transferencia cuenta a cuenta`

---

## 7. Perfil del cliente

Cada cliente se genera con un perfil económico y operativo.  
Las variables del cliente incluyen:

- ocupación
- industria
- tipo de empleo
- ingreso mensual
- frecuencia de ingreso
- antigüedad como cliente
- segmento transaccional
- producto habitual
- canal habitual
- franja horaria habitual
- perfil de riesgo
- puntaje de riesgo
- susceptibilidad al fraude

### Ejemplos de ocupaciones
- empleado privado
- docente
- independiente
- microempresario
- cajero
- analista
- medico
- chofer
- pensionado
- desempleado

---

## 8. Lógica de comportamiento normal

Las transacciones normales de cada cliente siguen una lógica coherente con su perfil.

### Señales usadas para construir el patrón normal
- monto promedio histórico
- cantidad de transacciones en 3 meses
- producto financiero habitual
- canal habitual
- franja horaria habitual
- ingreso mensual
- frecuencia de ingresos
- segmento del cliente

### Ejemplos
- un cliente con ingresos bajos no suele mover montos extremadamente altos de manera normal
- un cliente de alto flujo puede tener más movimientos, pero dentro de un patrón razonable
- un pensionado tenderá a tener mayor estabilidad temporal que un trabajador independiente
- un cliente desempleado puede existir, pero con ingresos muy bajos y con mayor riesgo relativo

---

## 9. Lógica de fraude

Las transacciones fraudulentas se construyen como **anomalías** frente al comportamiento histórico del cliente.

### Señales de anomalía consideradas
- monto muy superior al monto promedio histórico
- monto incompatible con el ingreso mensual
- uso de canal no habitual
- uso de un producto poco frecuente para el cliente
- comportamiento horario distinto al normal
- incremento del nivel de riesgo

### Regla general
El fraude **no** se genera al azar puro.  
Se intenta que tenga sentido respecto al perfil del cliente y su historial.

---

## 10. Perfil de riesgo

Cada cliente recibe un `risk_profile` y un `risk_score`.

### Niveles
- `bajo`
- `medio`
- `alto`

### Variables que influyen
- ingreso mensual
- tipo de empleo
- segmento del cliente
- volumen transaccional
- estabilidad financiera

El fraude puede elevar el riesgo observado a nivel transaccional.

---

## 11. Registros basura para limpieza

Además de los registros válidos, el proyecto genera **100,000 registros sucios**.

Estos registros no siguen las reglas normales del negocio y se incluyen con fines pedagógicos.

### Tipos de problemas incluidos

#### 1. Valores nulos
Ejemplos:
- `customer_id` nulo
- `transaction_datetime` nulo
- `product_type` nulo
- `transaction_amount` nulo
- `occupation` nula
- `monthly_income` nulo

#### 2. Duplicados
Ejemplos:
- filas repetidas
- `transaction_id` duplicado
- combinaciones idénticas de cliente, fecha y monto

#### 3. Incoherencias de negocio
Ejemplos:
- montos exageradamente altos para clientes de bajo ingreso
- montos negativos
- perfiles de riesgo inválidos
- cantidades de transacciones imposibles

#### 4. Formatos erróneos
Ejemplos:
- fechas imposibles
- horas mal formateadas
- montos como texto
- IDs corruptos

#### 5. Categorías inválidas
Ejemplos:
- productos no permitidos
- canales inexistentes
- estados inválidos
- etiquetas de riesgo no válidas

### Uso didáctico
Los estudiantes pueden practicar:

- data profiling
- validación de reglas de negocio
- limpieza de nulos
- deduplicación
- normalización de categorías
- corrección de formatos
- descarte de registros inválidos

---

## 12. Columnas del dataset

El dataset final contiene estas columnas:

1. `transaction_id`
2. `customer_id`
3. `transaction_datetime`
4. `transaction_date`
5. `transaction_time`
6. `product_type`
7. `transaction_amount`
8. `transaction_direction`
9. `channel`
10. `transaction_status`
11. `merchant_or_destination`
12. `source_account_type`
13. `destination_account_type`
14. `customer_segment`
15. `occupation`
16. `industry`
17. `employment_type`
18. `monthly_income`
19. `income_frequency`
20. `customer_tenure_months`
21. `avg_3m_transaction_amount`
22. `avg_3m_transaction_count`
23. `usual_transaction_hour_range`
24. `usual_product_type`
25. `usual_channel`
26. `deviation_from_usual_amount_pct`
27. `anomaly_flag`
28. `risk_profile`
29. `risk_score`
30. `fraud_label`
31. `data_quality_flag`

---

## 13. Significado de columnas clave

### `fraud_label`
- `0` = transacción regular
- `1` = transacción fraudulenta

### `anomaly_flag`
- `0` = sin anomalía relevante
- `1` = comportamiento atípico

### `data_quality_flag`
- `valid` = registro coherente
- `dirty` = incoherencia de negocio
- `duplicate` = registro duplicado
- `null_issue` = problema de nulos
- `invalid_format` = problema de formato

---

## 14. Archivos generados por el script

Al ejecutar el script, se generan:

### `customers_profile.csv`
Perfil base de los 7,000 clientes.

### `transactions_valid_only.csv`
Las 500,000 transacciones válidas.

### `transactions_full_with_dirty_records.csv`
El dataset final completo con las 600,000 filas.

### `dataset_summary.json`
Resumen básico del dataset generado.

---

## 15. Requisitos

Instalar dependencias:

```bash
pip install pandas numpy
```

---

## 16. Cómo ejecutar

### Ejecución básica
```bash
python generate_financial_transactions_dataset.py
```

### Ejecución con fechas y carpeta de salida personalizadas
```bash
python generate_financial_transactions_dataset.py \
  --start-date 2025-01-01 \
  --end-date 2025-03-31 \
  --output-dir output_financial_dataset
```

---

## 17. Ejemplo de uso en clase

### Fase 1: limpieza
Los estudiantes pueden:
- medir nulos por columna
- detectar duplicados
- identificar categorías inválidas
- filtrar fechas incorrectas
- validar montos imposibles

### Fase 2: exploración
Los estudiantes pueden:
- analizar distribución de montos
- comparar segmentos de clientes
- analizar fraude por canal
- estudiar fraude por producto
- estudiar riesgo por ocupación

### Fase 3: modelado
Los estudiantes pueden:
- crear variables derivadas
- convertir categorías
- balancear clases
- entrenar modelos de fraude
- evaluar métricas como precision, recall, F1, ROC AUC

---

## 18. Consideraciones importantes

- Este dataset es **sintético**, no representa clientes reales.
- El objetivo es pedagógico y de simulación.
- Las reglas de negocio son razonables, pero pueden adaptarse.
- Puedes ampliar el proyecto agregando geolocalización, dispositivo, moneda, score histórico, comportamiento semanal o variables agregadas por cliente.

---

## 19. Posibles extensiones

Algunas mejoras futuras podrían ser:

- agregar país, ciudad o sucursal
- agregar dispositivo o fingerprint
- agregar día de pago
- agregar historial de intentos fallidos
- agregar score antifraude por transacción
- generar una tabla separada de clientes y otra de transacciones
- crear datasets por lotes mensuales

---

## 20. Resumen del diseño acordado

Este proyecto respeta estas reglas declaradas:

- 7,000 clientes
- 500,000 transacciones válidas
- 100,000 registros basura
- 600,000 registros en total
- 3 meses de historial
- 90% transacciones regulares
- 10% transacciones fraudulentas
- clientes segmentados en:
  - moderado
  - regular
  - alto flujo
- cada cliente tiene ocupación, ingreso y frecuencia de ingreso
- las transacciones van a:
  - ahorro
  - pago de prestamo
  - pago de tarjeta
  - transferencia cuenta a cuenta
- el fraude se modela como anomalía del patrón del cliente
- el dataset incluye errores intencionales para limpieza y exploración

---

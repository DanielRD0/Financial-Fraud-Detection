# Resumen tecnico - Seccion de Daniel
## Proceso de ajuste y correccion de fechas/horas

---

## Idea central

El dataset tiene 3 columnas de tiempo:
- `transaction_datetime` — fecha + hora juntas
- `transaction_date` — solo fecha
- `transaction_time` — solo hora

Muchas tienen valores invalidos o nulos. La decision fue **recuperar primero, marcar despues, nunca eliminar** porque cada fila representa una transaccion financiera real.

---

## Codigo por codigo

### Celda 1 — Diagnostico

```python
print("DIAGNOSTICO...")
df['transaction_datetime'].isnull().sum()
```

**Por que:** Antes de tocar cualquier dato hay que saber el estado real. Se confirmaron 16,220 nulos en `transaction_datetime` y que las columnas eran tipo `object` (texto), lo que confirmo que habia trabajo por hacer.

**Alternativa descartada:** Saltar el diagnostico e ir directo a limpiar — malo porque no sabes cuanto problema hay ni si tu codigo funciono.

---

### Celda 2 — Estandarizar transaction_time

```python
def estandarizar_hora(valor):
    re.fullmatch(r'\d{1,2}:\d{2}:\d{2}', s)
    if 0 <= h <= 23 and 0 <= m <= 59 and 0 <= seg <= 59:
        return f"{h:02d}:{m:02d}:{seg:02d}"
    return np.nan
```

**Por que:** `transaction_time` tenia 0 nulos pero podia tener valores imposibles como `25:61:99`. Se uso regex para validar el formato y luego verificacion numerica de rangos. Los invalidos se marcan `NaN` en lugar de eliminarlos.

**Que es regex:** Un patron de texto que verifica si un valor tiene exactamente la forma esperada. `\d{1,2}:\d{2}:\d{2}` significa "1 o 2 digitos, dos puntos, 2 digitos, dos puntos, 2 digitos" — exactamente el formato `HH:MM:SS`.

**Alternativa descartada:** `pd.to_datetime(errors='coerce')` — convierte a datetime completo cuando solo se necesitaba validar la hora como texto. Innecesariamente pesado.

---

### Celda 3 — Recuperar transaction_datetime

```python
mask_recover = df['transaction_datetime'].isnull() & df['transaction_date'].notnull()
fecha_str + ' ' + hora_str → pd.to_datetime(...)
```

**Por que:** Si `transaction_datetime` es nulo pero `transaction_date` existe, se puede reconstruir combinando fecha + hora. Es recuperar informacion que ya esta en el dataset, solo separada en columnas distintas. Si `transaction_time` tambien falta se usa `00:00:00` (medianoche) como valor neutro.

**Alternativa descartada:** Eliminar todos los registros con `transaction_datetime` nulo — se perderian miles de transacciones reales.

---

### Celda 4 — Recuperar transaction_date

```python
mask_date = df['transaction_date'].isnull() & df['transaction_datetime'].notnull()
df.loc[mask_date, 'transaction_date'] = df.loc[mask_date, 'transaction_datetime'].dt.normalize()
```

**Por que:** `.normalize()` extrae solo la parte de fecha de un datetime. Si el datetime es valido, la fecha se puede derivar directamente sin inventar ningun valor.

**Alternativa descartada:** Imputar con la fecha mas frecuente o la mediana — no tiene sentido en fechas de transacciones, cada una tiene su fecha real.

---

### Celda 5 — Validar rango de fechas

```python
FECHA_INICIO = pd.Timestamp('2025-01-01')
FECHA_FIN    = pd.Timestamp('2025-03-31 23:59:59')
df.loc[mask_fuera, 'data_quality_flag'] = 'invalid_format'
```

**Por que:** El dataset cubre enero a marzo 2025. Fechas fuera de ese rango son registros basura intencionales del generador. Se marcan en `data_quality_flag` (columna que ya existia para eso) en lugar de eliminarlas.

**Alternativa descartada:** Eliminar las filas fuera de rango — viola el criterio del proyecto, en datasets financieros no se borra.

---

### Celda 6 — Sincronizar y resumen final

```python
df.loc[mask_dt_valido, 'transaction_date'] = df.loc[mask_dt_valido, 'transaction_datetime'].dt.normalize()
```

**Por que:** Garantiza consistencia entre las tres columnas. Si `transaction_datetime` es `2025-01-16 06:18:07`, entonces `transaction_date` debe ser `2025-01-16` y `transaction_time` debe ser `06:18:07`. Sin este paso podrian quedar contradicciones dentro del mismo registro.

**Alternativa descartada:** Dejar cada columna independiente — genera inconsistencias que confunden a los modelos de Machine Learning.

---

## Contexto del proyecto completo

**Que es:** Dataset sintetico de 600,000 transacciones financieras — 500,000 validas y 100,000 registros basura intencionales para practicar limpieza.

**Para que:** Simula el trabajo real de un Data Scientist en una institucion financiera. El objetivo es limpiar los datos antes de poder detectar fraude o analizar el comportamiento de los clientes.

**Por que no se eliminan filas:** Cada transaccion representa un movimiento de dinero real. Eliminarla significa perder informacion para los modelos de Machine Learning que detectan fraude. Se prefiere marcar los problemas en `data_quality_flag` y dejar que el modelo decida que hacer con ellos.

### Que hace cada integrante

| Persona | Tarea |
|---|---|
| Arlene | Eliminar duplicados exactos, preservar transacciones similares legitimas |
| Adison | Homogeneizar texto (minusculas, sin acentos) y manejar valores nulos |
| **Daniel** | **Estandarizar y recuperar fechas/horas sin eliminar filas** |
| Roni | Ajuste de columnas numericas (transaction_amount, monthly_income) |
| Felix | Deteccion de outliers con metodo IQR sobre transaction_amount |

### Columnas clave de la seccion de Daniel

| Columna | Tipo final | Rol |
|---|---|---|
| `transaction_datetime` | datetime64 | Fuente de verdad principal |
| `transaction_date` | datetime64 | Fecha derivada, debe ser consistente |
| `transaction_time` | string HH:MM:SS | Hora derivada, debe ser consistente |
| `data_quality_flag` | string | Marca registros problematicos: `invalid_format`, `dirty`, `valid` |

---

## GitHub — Como se hizo y para que sirve

### Que es GitHub
GitHub es una plataforma donde se guardan versiones del codigo. Cada vez que alguien hace un cambio y lo sube, queda registrado quien lo hizo, cuando y que cambio. Es como un historial de versiones del notebook que todo el grupo puede ver y editar.

### Lo que se hizo paso a paso

1. **Se inicializo un repositorio local** dentro de la carpeta `Modulo 10` con `git init`. Esto convierte la carpeta en un repositorio con control de versiones.

2. **Se creo un `.gitignore`** para excluir el archivo CSV (demasiado pesado para GitHub) y archivos temporales de Python.

3. **Se hizo el primer commit** con `git add` y `git commit`. Un commit es una fotografia del estado del proyecto en ese momento con un mensaje que describe que se cambio.

4. **Se creo el repositorio en github.com** con el nombre `limpieza-datos-modulo10` de forma publica para que toda la clase pueda acceder.

5. **Se conecto el repo local con GitHub** con `git remote add origin` y se subio todo con `git push`.

6. **Se vinculo la cuenta de GitHub** al equipo para no tener que escribir contrasena cada vez.

### Comandos para el dia a dia

```bash
# Subir cambios al repo
git add limpiezadedatos.ipynb
git commit -m "descripcion del cambio"
git push

# Descargar cambios que hicieron otros
git pull

# Clonar el repo en otra computadora
git clone https://github.com/DanielRD0/limpieza-datos-modulo10.git
```

### Por que es util para el grupo
Cada compañero puede trabajar en su seccion, subir sus cambios y el historial queda guardado. Si alguien rompe algo, se puede volver a una version anterior. El profesor puede ver el repo directamente con el link sin necesidad de que le envien el archivo por WhatsApp.

**Link del repositorio:** https://github.com/DanielRD0/limpieza-datos-modulo10

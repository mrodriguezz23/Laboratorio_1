import os
import pandas as pd
import plotly.express as px
import glob
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import seaborn as sns 

# ruta de la carpeta con los datos
ruta_archivos = os.path.join(os.path.dirname(__file__), 'data', '*.csv')

# cargamos todos los datos en un solo dataframe
archivos = glob.glob(ruta_archivos)

# lista de archivos encontrados
print("Archivos encontrados:", archivos)

# verificamos si se encontraron archivos
if not archivos:
    print("No se encontraron archivos CSV en la ruta especificada.")
else:
    dataframes = []
    for archivo in archivos:
        df = pd.read_csv(archivo)
        print(f"Archivo: {archivo}, Filas: {len(df)}")
        dataframes.append(df)
    
    datos_ventas = pd.concat(dataframes, ignore_index=True)

    # mostramos las primeras filas del df combinado y los nombres de las columnas
    print(datos_ventas.head())
    print("Columnas del DataFrame:", datos_ventas.columns)
    print(f"Total de filas en el DataFrame combinado: {len(datos_ventas)}")

    # eliminamos filas con datos faltantes
    datos_ventas = datos_ventas.dropna()

    # columnas del tipo correcto
    datos_ventas['Cantidad Pedida'] = pd.to_numeric(datos_ventas['Cantidad Pedida'], errors='coerce')
    datos_ventas['Precio Unitario'] = pd.to_numeric(datos_ventas['Precio Unitario'], errors='coerce')

    # eliminamos filas con datos no numéricos en las columnas cantidad pedida y precio unitario
    datos_ventas = datos_ventas.dropna(subset=['Cantidad Pedida', 'Precio Unitario'])

    # convertimos la columna de fecha a tipo datetime
    datos_ventas['Fecha de Pedido'] = pd.to_datetime(datos_ventas['Fecha de Pedido'], format='%m/%d/%y %H:%M', errors='coerce')

    # fechas no validas se eliminan
    datos_ventas = datos_ventas.dropna(subset=['Fecha de Pedido'])

    # caracteristicas importantes
    datos_ventas['Mes'] = datos_ventas['Fecha de Pedido'].dt.month
    datos_ventas['Hora'] = datos_ventas['Fecha de Pedido'].dt.hour
    datos_ventas['Día de la Semana'] = datos_ventas['Fecha de Pedido'].dt.dayofweek
    datos_ventas['Ciudad'] = datos_ventas['Dirección de Envio'].apply(lambda x: x.split(',')[1].strip())

    # calculamos el ingreso total generado
    datos_ventas['Total_Ventas'] = datos_ventas['Cantidad Pedida'] * datos_ventas['Precio Unitario']

    # 1. Comportamiento de las Ventas en los Distintos Meses
    # agrupamos por mes y sumamos
    ventas_por_mes = datos_ventas.groupby('Mes')['Total_Ventas'].sum()

    
    print("Ingreso total generado por mes:")
    print(ventas_por_mes)

    # gráfico de barras de ventas por mes
    plt.figure(figsize=(10, 6))
    ax = ventas_por_mes.plot(kind='bar')
    plt.title('Ingresos por Ventas Mensuales')
    plt.xlabel('Mes')
    plt.ylabel('Ingresos Totales ($)')
    
    # mostrar valores sin notación científica
    ax.yaxis.set_major_formatter(mtick.StrMethodFormatter('{x:,.0f}'))
    plt.show()

    # 2. Optimización de la Publicidad y Patrón de Ventas por Hora

    ventas_por_hora = datos_ventas.groupby('Hora')['Total_Ventas'].sum()

    # grafico de barras de ventas por hora
    plt.figure(figsize=(10, 6))
    ax = ventas_por_hora.plot(kind='bar')
    plt.title('Ingresos por Ventas según Hora del Día')
    plt.xlabel('Hora del Día')
    plt.ylabel('Ingresos Totales ($)')
    ax.yaxis.set_major_formatter(mtick.StrMethodFormatter('{x:,.0f}'))
    plt.show()

    # patrones de venta por hora a lo largo del año
    ventas_por_mes_hora = datos_ventas.groupby(['Mes', 'Hora'])['Total_Ventas'].sum().unstack()

    # gráfico de calor de ventas por hora a lo largo del año
    plt.figure(figsize=(12, 8))
    sns.heatmap(ventas_por_mes_hora, cmap='viridis')
    plt.title('Patrones de Ingresos por Ventas por Hora a lo Largo del Año')
    plt.xlabel('Hora del Día')
    plt.ylabel('Mes')
    plt.show()


    
    # horas de mayor actividad
    horas_mayor_actividad = ventas_por_hora.nlargest(5).index

    # filtramos los datos para las horas de mayor actividad
    datos_horas_mayor_actividad = datos_ventas[datos_ventas['Hora'].isin(horas_mayor_actividad)]

    # agrupamos por mes y hora
    ventas_horas_mayor_actividad = datos_horas_mayor_actividad.groupby(['Mes', 'Hora'])['Total_Ventas'].sum().unstack()

    plt.close('all')

    # creamos la figura
    fig, ax = plt.subplots(figsize=(12, 8))

    # graficar los datos
    ventas_horas_mayor_actividad.plot(kind='line', marker='o', ax=ax)

    # titulo y etiquetas
    ax.set_title('Modificaciones en los Patrones de Ventas Durante las Horas de Mayor Actividad')
    ax.set_xlabel('Mes')
    ax.set_ylabel('Total de Ventas')
    ax.legend(title='Hora del Día')

    plt.show()
    plt.close(fig)
    
    
    #3 Distribución de Ventas por Ubicación
    
    # agrupamos por ciudad
    
    ventas_por_ciudad = datos_ventas.groupby('Ciudad')['Total_Ventas'].sum()


    print("Ventas por Ciudad:")
    print(ventas_por_ciudad)

    # grafico de barras de ventas por ciudad
    plt.figure(figsize=(12, 8))
    ax = ventas_por_ciudad.plot(kind='bar')
    plt.title('Ventas por Ciudad ($)')
    plt.xlabel('Ciudad')
    plt.ylabel('Total de Ventas ($)')
    ax.yaxis.set_major_formatter(mtick.StrMethodFormatter('{x:,.0f}'))
    plt.show()

    # extraer el estado de la dirección de envío
    datos_ventas['Estado'] = datos_ventas['Dirección de Envio'].apply(lambda x: x.split(',')[2].strip().split(' ')[0])

    # agrupamos por estado
    ventas_por_estado = datos_ventas.groupby('Estado')['Total_Ventas'].sum()

    # mostrar las ventas por estado
    print("Ventas por Estado:")
    print(ventas_por_estado)


    # Nuevo código para el mapa coroplético
    ventas_por_estado_df = pd.DataFrame({'Estado': ventas_por_estado.index, 'Ventas totales ($)': ventas_por_estado.values})

    fig = px.choropleth(ventas_por_estado_df,
                    locations='Estado', 
                    locationmode="USA-states",
                    color='Ventas totales ($)',
                    scope="usa",
                    color_continuous_scale="RdYlGn",
                    title='Ventas Totales ($) por Estado')

    fig.show()
    

    #4. Análisis del Producto Más Vendido
    # agrupamos por producto para calcular la cantidad vendida
    cantidad_por_producto = datos_ventas.groupby('Producto')['Cantidad Pedida'].sum()

    # mostrar el producto más vendido en términos de cantidad
    producto_mas_vendido = cantidad_por_producto.idxmax()
    cantidad_producto_mas_vendido = cantidad_por_producto.max()
    print(f"El producto más vendido en términos de cantidad es: {producto_mas_vendido} con un total de {cantidad_producto_mas_vendido} unidades vendidas")

    # gráfico de torta de ventas por cantidad de producto
    plt.figure(figsize=(14, 10))
    explode = [0.1 if i == producto_mas_vendido else 0 for i in cantidad_por_producto.index]  # Resaltar el producto más vendido
    cantidad_por_producto.plot(kind='pie', autopct='%1.1f%%', startangle=90, explode=explode, textprops={'fontsize': 10})
    plt.title('Distribución de Ventas por Cantidad de Producto')
    plt.ylabel('')  # Ocultar la etiqueta del eje Y
    plt.show()

    # agrupamos por mes y producto para calcular la cantidad vendida
    cantidad_por_mes_producto = datos_ventas.groupby(['Mes', 'Producto'])['Cantidad Pedida'].sum().unstack()

    # mostrar el producto más vendido en cada mes en términos de cantidad
    producto_mas_vendido_por_mes = cantidad_por_mes_producto.idxmax(axis=1)
    print("El producto más vendido en cada mes en términos de cantidad es:")
    print(producto_mas_vendido_por_mes)

    # gráfico de calor de ventas por cantidad de producto a lo largo de los meses
    plt.figure(figsize=(16, 10))  # aumentar el tamaño de la figura
    sns.heatmap(cantidad_por_mes_producto, cmap='viridis', annot=False)
    plt.title('Ventas por Cantidad de Producto a lo Largo de los Meses')
    plt.xlabel('Producto')
    plt.ylabel('Mes')

    # rotamos las etiquetas del eje x para que sean legibles
    plt.xticks(rotation=45, ha='right')

    # evitar que las etiquetas se corten
    plt.tight_layout()

    plt.show()



    #5. Tendencia de Ventas
    # agrupamos por día del mes
    ventas_por_dia_mes = datos_ventas.groupby(datos_ventas['Fecha de Pedido'].dt.day)['Cantidad Pedida'].sum()

    # mostrar las ventas por día del mes
    print("Ventas por Día del Mes (en términos de cantidad):")
    print(ventas_por_dia_mes)

    # grafico de líneas de ventas por día del mes
    plt.figure(figsize=(12, 8))
    ax = ventas_por_dia_mes.plot(kind='line', marker='o')
    plt.title('Ventas por Día del Mes (en términos de cantidad)')
    plt.xlabel('Día del Mes')
    plt.ylabel('Cantidad de Productos Vendidos')
    ax.yaxis.set_major_formatter(mtick.StrMethodFormatter('{x:,.0f}'))
    plt.show()

    # agrupamos por día de la semana
    ventas_por_dia_semana = datos_ventas.groupby('Día de la Semana')['Cantidad Pedida'].sum()

    # mostrar las ventas por día de la semana
    print("Ventas por Día de la Semana (en términos de cantidad):")
    print(ventas_por_dia_semana)

    # grafico de barras de ventas por día de la semana con etiquetas de datos
    plt.figure(figsize=(12, 8))
    ax = ventas_por_dia_semana.plot(kind='bar')
    plt.title('Ventas por Día de la Semana (en términos de cantidad)')
    plt.xlabel('Día de la Semana')
    plt.ylabel('Cantidad de Productos Vendidos')
    ax.set_xticklabels(['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'], rotation=0)
    ax.yaxis.set_major_formatter(mtick.StrMethodFormatter('{x:,.0f}'))

    # agregar etiquetas de datos
    for i in ax.containers:
        ax.bar_label(i, label_type='edge', fmt='%.0f')

    plt.show()

    # agrupamos por día laborable y fin de semana
    datos_ventas['Es Fin de Semana'] = datos_ventas['Día de la Semana'].apply(lambda x: 1 if x >= 5 else 0)
    ventas_por_tipo_dia = datos_ventas.groupby('Es Fin de Semana')['Cantidad Pedida'].sum()

    # mostrar las ventas por tipo de día
    print("Ventas por Tipo de Día (0 = Laborable, 1 = Fin de Semana) (en términos de cantidad):")
    print(ventas_por_tipo_dia)

    # grafico de barras de ventas por tipo de día
    plt.figure(figsize=(12, 8))
    ax = ventas_por_tipo_dia.plot(kind='bar')
    plt.title('Ventas por Tipo de Día (en términos de cantidad)')
    plt.xlabel('Tipo de Día')
    plt.ylabel('Cantidad de Productos Vendidos')
    ax.set_xticklabels(['Laborable', 'Fin de Semana'], rotation=0)
    ax.yaxis.set_major_formatter(mtick.StrMethodFormatter('{x:,.0f}'))
    plt.show()

    #6. Análisis de Eventos Especiales
    # definir una lista de días festivos o eventos especiales
    eventos_especiales = [
        '2019-01-01',  # Año Nuevo
        '2019-07-04',  # Día de la Independencia
        '2019-11-28',  # Día de Acción de Gracias
        '2019-12-25',  # Navidad
    ]

    # convertir la columna de fecha a solo fecha (sin hora)
    datos_ventas['Fecha'] = datos_ventas['Fecha de Pedido'].dt.date

    # crear una columna que indique si el día es un evento especial
    datos_ventas['Es Evento Especial'] = datos_ventas['Fecha'].apply(lambda x: 1 if str(x) in eventos_especiales else 0)

    # agrupo por dia y sumo las ventas
    ventas_por_dia = datos_ventas.groupby('Fecha')['Total_Ventas'].sum().reset_index()

    # añadir la columna de evento especial al dataframe de ventas por día
    ventas_por_dia['Es Evento Especial'] = ventas_por_dia['Fecha'].apply(lambda x: 1 if str(x) in eventos_especiales else 0)

    # comparar las ventas en días de eventos especiales con días normales
    ventas_eventos_especiales = ventas_por_dia[ventas_por_dia['Es Evento Especial'] == 1]
    ventas_dias_normales = ventas_por_dia[ventas_por_dia['Es Evento Especial'] == 0]

    # calcular estadísticas descriptivas
    media_ventas_eventos = ventas_eventos_especiales['Total_Ventas'].mean()
    media_ventas_normales = ventas_dias_normales['Total_Ventas'].mean()

    print(f"Media de ventas en días de eventos especiales: ${media_ventas_eventos:,.2f}")
    print(f"Media de ventas en días normales: ${media_ventas_normales:,.2f}")

    # gráfico de barras comparando ventas en días de eventos especiales y días normales
    plt.figure(figsize=(12, 8))
    labels = ['Días Normales', 'Eventos Especiales']
    medias = [media_ventas_normales, media_ventas_eventos]
    plt.bar(labels, medias, color=['blue', 'orange'])
    plt.title('Comparación de Ventas en Días Normales y Eventos Especiales')
    plt.xlabel('Tipo de Día')
    plt.ylabel('Media de Ventas')
    plt.show()

    # gráfico de líneas de ventas a lo largo del tiempo, destacando eventos especiales
    plt.figure(figsize=(12, 8))
    plt.plot(ventas_por_dia['Fecha'], ventas_por_dia['Total_Ventas'], label='Ventas Diarias')
    plt.scatter(ventas_eventos_especiales['Fecha'], ventas_eventos_especiales['Total_Ventas'], color='red', label='Eventos Especiales')
    plt.title('Ventas Diarias con Eventos Especiales Destacados')
    plt.xlabel('Fecha')
    plt.ylabel('Total de Ventas')
    plt.legend()
    plt.show()
    


    # agrupamos las ventas por producto y mes, pero ahora usando 'Cantidad Pedida'
    ventas_por_producto_mes = datos_ventas.groupby(['Producto', 'Mes'])['Cantidad Pedida'].sum().unstack()

    # calculamos el crecimiento mensual de ventas por producto
    crecimiento_mensual = ventas_por_producto_mes.pct_change(axis=1) * 100

    # crecimiento promedio anual de cada producto
    crecimiento_promedio_anual = crecimiento_mensual.mean(axis=1)

    # identificar el producto con mayor crecimiento promedio anual
    producto_mayor_crecimiento = crecimiento_promedio_anual.idxmax()
    crecimiento_mayor_producto = crecimiento_promedio_anual.max()
    print(f"El producto con mayor crecimiento en cantidad vendida mes a mes es: {producto_mayor_crecimiento} con un crecimiento promedio de {crecimiento_mayor_producto:.2f}%")

    print("\nTop 5 productos por crecimiento promedio en cantidad vendida:")
    print(crecimiento_promedio_anual.nlargest(5))

    datos_producto_mayor_crecimiento = ventas_por_producto_mes.loc[producto_mayor_crecimiento]

    # grafico de lineas
    plt.figure(figsize=(10, 6))
    ax = datos_producto_mayor_crecimiento.plot(kind='line', marker='o')
    plt.title(f'Crecimiento Mensual de Cantidad Vendida del Producto: {producto_mayor_crecimiento}')
    plt.xlabel('Mes')
    plt.ylabel('Cantidad de Productos Vendidos')
    ax.yaxis.set_major_formatter(mtick.StrMethodFormatter('{x:,.0f}'))
    plt.show()
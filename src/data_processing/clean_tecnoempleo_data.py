import os
import re
import pandas as pd

raw_data   = 'data/raw/tecnoempleo_jobs.csv'
clean_data = 'data/processed/clean_tecnoempleo_jobs.csv'


def carga_datos(ruta: str) -> pd.DataFrame:
    df = pd.read_csv(ruta)
    print('Dataset cargado correctamente:')
    print(f'Filas: {df.shape[0]}')
    print(f'Columnas: {df.shape[1]}')
    return df


def limpiar_texto(valor):
    if pd.isna(valor):
        return None
    valor = str(valor)
    valor = valor.strip()
    valor = re.sub(r'\s+', ' ', valor)
    return valor


def limpiar_columnas(df: pd.DataFrame) -> pd.DataFrame:
    columnas_texto = [
        'titulo', 'empresa', 'ubicacion', 'salario',
        'tipo_contrato', 'skills', 'busqueda'
    ]
    for columna in columnas_texto:
        df[columna] = df[columna].apply(limpiar_texto)
    return df


def normalizar_texto(df: pd.DataFrame):
    columnas_a_normalizar = [
        'titulo', 'empresa', 'ubicacion',
        'tipo_contrato', 'skills', 'busqueda'
    ]
    for columna in columnas_a_normalizar:
        df[columna] = df[columna].str.lower()

    # CAMBIO 1: la columna 'url' NO se normaliza a minúsculas.
    # CHANGE 1: the 'url' column is NOT lowercased.
    # Las URLs son case-sensitive — convertirlas a minúsculas las rompería.
    # URLs are case-sensitive — lowercasing them would break them.
    # Simplemente la dejamos tal como viene del scraper.
    # We simply leave it as it comes from the scraper.

    return df


def eliminar_dupl(df: pd.DataFrame) -> pd.DataFrame:
    antes = df.shape[0]
    df = df.drop_duplicates(
        subset=['titulo', 'empresa', 'ubicacion', 'salario', 'tipo_contrato'],
        keep='first'
    )
    despues = len(df)
    print(f"Filas antes: {antes}")
    print(f"Filas después: {despues}")
    print(f"Filas eliminadas: {antes - despues}")
    return df


def limpiar_skills(valor):
    if pd.isna(valor):
        return None
    lista_skills = valor.split(',')
    skills_limpias = []
    for skill in lista_skills:
        skill = skill.strip().lower()
        if skill and skill not in skills_limpias:
            skills_limpias.append(skill)
    return ', '.join(skills_limpias)


def crear_modalidad(df: pd.DataFrame) -> pd.DataFrame:
    def obtener_desde_ubi(ubicacion):
        if pd.isna(ubicacion):
            return 'No especificado'
        ubicacion = ubicacion.lower()
        if 'remoto' in ubicacion:
            return 'En Remoto'
        if 'híbrido' in ubicacion or 'hibrido' in ubicacion:
            return 'Híbrido'
        if 'presencial' in ubicacion:
            return 'Presencial'
        return 'No especificado'
    df['modalidad'] = df['ubicacion'].apply(obtener_desde_ubi)
    return df


def crear_ciudad(df: pd.DataFrame) -> pd.DataFrame:
    def obtener_ciudad(ubicacion):
        if pd.isna(ubicacion):
            return None
        ubicacion = ubicacion.lower()
        ubicacion = ubicacion.replace(' - españa', '')
        ubicacion = ubicacion.replace('(híbrido)', '')
        ubicacion = ubicacion.replace('(hibrido)', '')
        ubicacion = ubicacion.replace('(presencial)', '')
        ubicacion = ubicacion.replace('(remoto)', '')
        ubicacion = ubicacion.replace('100% remoto', 'remoto')
        ubicacion = ubicacion.strip()
        if ubicacion == 'remoto':
            return 'remoto'
        return ubicacion
    df['ciudad'] = df['ubicacion'].apply(obtener_ciudad)
    return df


def limpiar_salarios(df: pd.DataFrame) -> pd.DataFrame:
    def obtener_salarios(salario):
        if pd.isna(salario):
            return pd.Series([None, None, None])
        num = re.findall(r'\d+(?:[.,\s]\d+)*', salario)
        num_limpio = []
        for numero in num:
            numero = numero.replace('.', '')
            numero = numero.replace(',', '.')
            try:
                num_limpio.append(float(numero))
            except ValueError:
                continue
        if len(num_limpio) >= 2:
            salario_min = num_limpio[0]
            salario_max = num_limpio[1]
            if ('month' in salario or '/month' in salario
                    or 'monthly' in salario or 'mes' in salario
                    or 'b/m' in salario):
                salario_min *= 12
                salario_max *= 12
            salario_medio = (salario_min + salario_max) / 2
            return pd.Series([salario_min, salario_max, salario_medio])
        return pd.Series([None, None, None])
    df[['salario_min', 'salario_max', 'salario_medio']] = df['salario'].apply(obtener_salarios)
    return df


def outlier_salario(df: pd.DataFrame) -> pd.DataFrame:
    salarios = df['salario_medio'].dropna()
    if salarios.empty:
        df['es_outlier'] = False
        return df
    percentil_25 = salarios.quantile(0.25)
    percentil_75 = salarios.quantile(0.75)
    rango        = percentil_75 - percentil_25
    limite_inf   = percentil_25 - 1.5 * rango
    limite_sup   = percentil_75 + 3 * rango
    df['es_outlier'] = (
        (df['salario_medio'] < limite_inf) | (df['salario_medio'] > limite_sup)
    )
    antes   = len(df)
    df      = df[df["salario_medio"].isna() | (df["salario_min"] >= 10000)]
    despues = len(df)
    print(f"\nLímite inferior de salario: {limite_inf}")
    print(f"Límite superior de salario: {limite_sup}")
    print(f"Filas eliminadas por salario no cuantificable: {antes - despues}")
    return df


def guardar_datos_limpios(df: pd.DataFrame, ruta: str) -> None:
    os.makedirs('data/processed', exist_ok=True)
    df.to_csv(ruta, index=False, encoding='utf-8-sig')
    print(f'Dataset guardado correctamente en: {ruta}')


def main():
    df = carga_datos(raw_data)
    df = normalizar_texto(df)
    df = eliminar_dupl(df)

    df['skills'] = df['skills'].apply(limpiar_skills)

    df = crear_modalidad(df)
    df = crear_ciudad(df)
    df = limpiar_salarios(df)
    df = outlier_salario(df)

    # CAMBIO: verificamos que la columna 'url' existe antes de guardar.
    # CHANGE: we verify the 'url' column exists before saving.
    # Antes no se guardaba porque no estaba en el CSV raw (el scraper no la incluía).
    # Before it wasn't saved because it wasn't in the raw CSV (the scraper didn't include it).
    # Ahora el scraper sí la genera, así que la conservamos en el CSV procesado
    # para que la app Streamlit pueda mostrar el enlace directo a cada oferta.
    # Now the scraper generates it, so we keep it in the processed CSV
    # so the Streamlit app can show the direct link to each offer.
    if 'url' in df.columns:
        print(f"\n✅ Columna 'url' detectada — se conserva en el CSV procesado")
        print(f"   URLs disponibles: {df['url'].notna().sum()} de {len(df)}")
    else:
        print("\n⚠️  Columna 'url' no encontrada en el CSV raw.")
        print("   Vuelve a ejecutar el scraper para generarla.")

    guardar_datos_limpios(df, clean_data)


if __name__ == '__main__':
    main()

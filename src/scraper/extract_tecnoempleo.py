import os
import time
import requests
import pandas as pd
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
}

BUSQUEDAS = [
    "data-scientist",
    "data-analyst",
    "data-engineer",
    "machine-learning",
    "business-intelligence",
    "programador",
    "analista-programador",
    "arquitecto-tic",
    "desarrollador-web",
    "full-stack",
    "devops",
    "ciberseguridad",
    "tester",
    "junior",
    "soporte-tecnico",
    "administrador-sistemas",
    "redes",
    "dba",
    "base-datos",
    "big-data",
    "cloud",
    "mobile",
    "software",
    "web",
]


def limpiar_lineas(texto: str) -> list:
    return [linea.strip() for linea in texto.splitlines() if linea.strip()]


def extraer_datos_detalle(url: str, session: requests.Session) -> dict:
    datos = {
        "ubicacion": None,
        "tipo_contrato": None
    }

    try:
        response = session.get(url, headers=HEADERS, timeout=15)

        if response.status_code != 200:
            return datos

        soup = BeautifulSoup(response.text, "html.parser")

        items = soup.select("li.list-item")

        for item in items:
            texto_item = item.get_text(" ", strip=True).lower()

            valor = item.select_one("span.float-end")

            if not valor:
                continue

            valor_limpio = valor.get_text(" ", strip=True)

            if "ubicación" in texto_item or "ubicacion" in texto_item:
                datos["ubicacion"] = valor_limpio

            elif "tipo contrato" in texto_item or "tipo de contrato" in texto_item:
                datos["tipo_contrato"] = valor_limpio

    except requests.RequestException:
        return datos

    return datos


def extraer_oferta(card, termino: str, session: requests.Session) -> dict:
    titulo_tag = card.select_one("h3 a")
    empresa_tag = card.select_one("a.text-primary.link-muted")

    info_tag = card.select_one("div.col-12.col-lg-3.text-gray-700")
    info_lineas = limpiar_lineas(info_tag.get_text("\n", strip=True)) if info_tag else []

    salario = None

    for linea in info_lineas:
        if "€" in linea:
            salario = linea
            break

    url = titulo_tag["href"] if titulo_tag and titulo_tag.has_attr("href") else None

    datos_detalle = {
        "ubicacion": None,
        "tipo_contrato": None
    }

    if url:
        datos_detalle = extraer_datos_detalle(url, session)
        time.sleep(0.4)

    skills = [
        skill.get_text(strip=True)
        for skill in card.select("span.hidden-md-down span.badge")
    ]

    return {
        "titulo": titulo_tag.get_text(strip=True) if titulo_tag else None,
        "empresa": empresa_tag.get_text(strip=True) if empresa_tag else None,
        "ubicacion": datos_detalle["ubicacion"],
        "salario": salario,
        "tipo_contrato": datos_detalle["tipo_contrato"],
        "skills": ", ".join(dict.fromkeys(skills)) if skills else None,
        "busqueda": termino
    }


def scrape_busqueda(termino: str, max_paginas: int = 3) -> list:
    ofertas = []

    with requests.Session() as session:
        for page in range(1, max_paginas + 1):

            if page == 1:
                url = f"https://www.tecnoempleo.com/ofertas-trabajo/{termino}"
            else:
                url = f"https://www.tecnoempleo.com/ofertas-trabajo/{termino}?pagina={page}"

            print(f"    Página {page}: {url}")

            try:
                response = session.get(url, headers=HEADERS, timeout=15)

            except requests.RequestException:
                print(f"    Error de conexión en página {page}")
                break

            if response.status_code != 200:
                print(f"    Error {response.status_code} en página {page}")
                break

            soup = BeautifulSoup(response.text, "html.parser")

            if termino == BUSQUEDAS[0] and page == 1:
                os.makedirs("data/raw", exist_ok=True)

                with open("data/raw/debug_page.html", "w", encoding="utf-8") as f:
                    f.write(soup.prettify())

            cards = soup.select("div.p-3.border.rounded.mb-3.bg-white")

            if not cards:
                print(f"    Sin resultados en página {page}, parando '{termino}'")
                break

            for card in cards:
                oferta = extraer_oferta(card, termino, session)

                if oferta["titulo"]:
                    ofertas.append(oferta)

            time.sleep(1)

    return ofertas


def main():
    all_ofertas = []

    for termino in BUSQUEDAS:
        print(f"Buscando: '{termino}'...")

        data = scrape_busqueda(termino, max_paginas=3)

        print(f"  → {len(data)} ofertas")

        all_ofertas.extend(data)

    df = pd.DataFrame(all_ofertas)

    df.drop_duplicates(subset=["titulo", "empresa"], inplace=True)

    columnas = [
        "titulo",
        "empresa",
        "ubicacion",
        "salario",
        "tipo_contrato",
        "skills",
        "busqueda"
    ]

    df = df[columnas]

    os.makedirs("data/raw", exist_ok=True)

    ruta_salida = "data/raw/tecnoempleo_jobs.csv"

    df.to_csv(
        ruta_salida,
        index=False,
        encoding="utf-8-sig"
    )

    print(f"\nCSV generado con {len(df)} ofertas → {ruta_salida}")


if __name__ == "__main__":
    main()
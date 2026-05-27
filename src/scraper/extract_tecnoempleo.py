import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

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

def scrape_busqueda(termino: str, max_paginas: int = 5) -> list:
    ofertas = []
    for page in range(1, max_paginas + 1):
        if page == 1:
            url = f"https://www.tecnoempleo.com/ofertas-trabajo/{termino}"
        else:
            url = f"https://www.tecnoempleo.com/ofertas-trabajo/{termino}?pagina={page}"

        response = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(response.text, "html.parser")

        if termino == BUSQUEDAS[0] and page == 1:
            with open("data/raw/debug_page.html", "w", encoding="utf-8") as f:
                f.write(soup.prettify())

        bloques = soup.select("div.col-10, div.col-md-9, .oferta, [class*='border-bottom']")
        titulos = soup.select("h3 a, h2 a")

        if not titulos:
            print(f"    Sin resultados en página {page}, parando '{termino}'")
            break

        for h in titulos:
            bloque = h.find_parent("div") or h.find_parent("article")
            empresa = bloque.select_one(".text-primary") if bloque else None
            ubicacion = bloque.select_one("span[class*='d-none']") if bloque else None
            salario = bloque.select_one(".text-success") if bloque else None
            contrato = bloque.select_one(".badge") if bloque else None
            skills = [s.get_text(strip=True) for s in bloque.select(".badge-secondary")] if bloque else []

            ofertas.append({
                "titulo": h.get_text(strip=True),
                "empresa": empresa.get_text(strip=True) if empresa else None,
                "ubicacion": ubicacion.get_text(strip=True) if ubicacion else None,
                "salario": salario.get_text(strip=True) if salario else None,
                "tipo_contrato": contrato.get_text(strip=True) if contrato else None,
                "skills": ", ".join(skills) if skills else None,
                "busqueda": termino
            })

        time.sleep(1.5)
    return ofertas


def main():
    all_ofertas = []
    for termino in BUSQUEDAS:
        print(f"Buscando: '{termino}'...")
        data = scrape_busqueda(termino)
        print(f"  → {len(data)} ofertas")
        all_ofertas.extend(data)

    df = pd.DataFrame(all_ofertas)
    df.drop_duplicates(subset=["titulo", "empresa"], inplace=True)
    df.to_csv("data/raw/tecnoempleo_jobs.csv", index=False, encoding="utf-8-sig")
    print(f"\nCSV generado con {len(df)} ofertas → data/raw/tecnoempleo_jobs.csv")


if __name__ == "__main__":
    main()
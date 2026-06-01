<div align="center">

  <img src="app/assets/logo/logo.png" alt="Logotipo de TinderJob con estética similar a la de Tinder, app de citas" width="50%"> 
</div> 

---

<h1 align="center"><b>TinderJob</b></h1>

<p align="center">
  <i>Proyecto de analítica avanzada y automatización desarrollado para <b>DataTalent Solutions S.L.</b></i>
</p>

---

## 📌 1. Contexto de Negocio y Objetivos

*DataTalent Solutions S.L.* necesita optimizar sus programas de formación y reskilling tecnológico. Para ello, este proyecto busca responder de manera empírica a las siguientes preguntas críticas de negocio:

* **Skills Demandadas:** ¿Qué habilidades técnicas se piden con más frecuencia en los roles de datos en España?
* **Distribución Salarial:** ¿Existen sesgos en los salarios según género, ubicación geográfica o modalidad de contrato?
* **Sectores Líderes:** ¿Qué sectores industriales concentran el mayor número de ofertas y las mejores bandas salariales?
* **Correlaciones de Mercado:** ¿Cuál es la relación matemática entre los años de experiencia, las habilidades técnicas y el salario ofertado?
* **Decisiones con Datos Sesgados:** ¿Qué impacto potencial tiene tomar decisiones estratégicas basándose en datos incompletos (MNAR) o subrepresentados?

---

## 🧭 2. Pivote Estratégico y Fuentes de Datos

Inicialmente, el proyecto contemplaba el uso del dataset de ofertas de LinkedIn. Sin embargo, aplicando un criterio de **control de calidad ágil (QA)**, detectamos un severo **sesgo de geolocalización**: todos los registros del dataset recomendado, pertenecían a Estados Unidos. Por lo que no era una muestra válida en el desarrollo de nuestro proyecto.

Para solucionar este problema y alinear el proyecto al 100% con los objetivos del cliente en España, tomamos la decisión estratégica de pivotar y combinar dos fuentes complementarias:

1.  **Stack Overflow Developer Survey (2025/2026):** Macroencuesta global utilizada para filtrar perfiles específicos de datos en España, ideal para el análisis profundo de sesgos demográficos y éticos.
2. **Data Science Job Salaries**: Recolección de datos relacionados con los salarios dentro del marco de la Ciencia de Datos y perfiles Tech. 
2.  **Web Scraping sobre Tecnoempleo (Desarrollo Propio):** Extracción automatizada en tiempo real de las ofertas de empleo activas en el portal líder del sector tecnológico en España, capturando títulos, salarios y las herramientas exactas que pide el mercado actual.

---

## 🏗️ 3. Arquitectura del Repositorio

El proyecto mantiene una estructura modular y limpia para facilitar la reproducibilidad y el mantenimiento del código:

```text
TinderJob/
├───app
│   ├───images
│   │   └───logo
│   ├───static
│   │   ├───css
│   │   └───js
│   └───templates
├───data
│   ├───metadata
│   ├───processed
│   └───raw
├───docs
├───notebooks
├───presentation
├───src
│   ├───analytics
│   ├───data_processing
│   └───scraper                   
├───venv
├── .gitignore               
└── README.md
```                
## 👥 4. Organización del Equipo
Para garantizar la entrega el 03/06 sin cuellos de botella, el equipo se ha organizado en roles individuales altamente especializados:

| Miembro | Rol | Especialización Técnica | GitHub |
| :--- | :--- | :--- | :--- |
| **Verónica Melero** | Product Owner | Front-end Developer | [@vmelero13](https://github.com/vmelero13) |
| **Elena Díaz** | Scrum Master | Team Support / QA & Presentation Lead | [@HelenDiMo](https://github.com/HelenDiMo) |
| **Adriana Aránguez** | Desarrolladora | Analytics & Bias Reporter | [@adrianaarang](https://github.com/adrianaarang) |
| **Joel Ibarra** | Desarrollador | Data Cleaning & Integration | [@jowel2701](https://github.com/jowel2701) |
| **Luis El Allali** | Desarrollador | Scraper Engineer | [@luiselallali18-hub](https://github.com/luiselallali18-hub) |

## 🛠️ 5. Requisitos e Instalación

(Sección en desarrollo a medida que los ingenieros entreguen el código)

Para ejecutar este proyecto de forma local, clona este repositorio e instala las dependencias:

```bash
git clone https://github.com/HelenDiMo/TinderJob.git
cd TinderJob
```
---
# [Aquí añadiremos cómo arrancar el front y el scraper]
---
## 6. 🕷️ Extracción, Limpieza y Preparación de Datos

El proyecto implementa un pipeline completo de ingeniería de datos que abarca desde la recolección automatizada hasta la limpieza y el tratamiento estadístico de la información salarial.

🌐 **A. Extracción Automatizada (Web Scraping)**

Se desarrolló un scraper optimizado para recopilar ofertas de empleo en tiempo real del portal **Tecnoempleo**, barriendo un abanico de **24 perfiles profesionales clave del sector** TIC (como *Data Scientist, Cloud, DevOps, Ciberseguridad*, entre otros).

> 🛠️ ***Stack Tecnológico utilizado:***

`requests`: Gestión de peticiones HTTP con `User-Agent` personalizado para evitar bloqueos.

`BeautifulSoup (bs4)`: Parseo del árbol HTML y extracción precisa de los bloques de ofertas.

`pandas`: Procesamiento, estructuración inicial y exportación a CSV.

`time`: Control de pausas (rate-limiting) de 1.5s para garantizar un comportamiento ético.

> 🔧 Mejoras de Extracción Implementadas:

Para evitar la pérdida o el desalineamiento de datos de la versión inicial, se reestructuró el scraper para capturar limpiamente:

* El **título** de la vacante y el nombre de la empresa.

* La **ubicación real** de cada oferta de empleo.

* La **información salarial** explícita (cuando está disponible).

* La separación exacta de las **habilidades y tecnologías (skills)**, impidiendo que campos como el salario o la modalidad de trabajo se almacenasen erróneamente en esta variable.

🧼 **B. Limpieza y Estandarización de Datos**

Una vez generado el dataset en bruto (`data/raw/tecnoempleo_jobs.csv`), se ejecuta un proceso automático de curación de datos mediante Pandas:

* **Normalización**: Eliminación de espacios en blanco innecesarios y estandarización de textos.

* **Duplicados**: Eliminación de ofertas repetidas basándose en la combinación de *titulo* y *empresa*.

* **Valores Nulos**: Tratamiento específico de vacíos en campos opcionales como salarios o skills.

📊 **C. Procesamiento Salarial y Outliers**

> 💵 Tratamiento de Salarios

Debido a la disparidad de formatos en las ofertas (salarios anuales, mensuales o sin especificar), el pipeline procesa la información y genera tres variables métricas normalizadas:

`salario_min`

`salario_max`

`salario_medio` (calculado a partir de la banda salarial capturada).

> 📈 Detección de Valores Atípicos (Outliers)

Para evitar distorsiones en el análisis del mercado, se aplica el método estadístico del Rango Intercuartílico (IQR) sobre las variables salariales:

Se calculan los percentiles 25 ($Q_1$) y 75 ($Q_3$).

Se define el Rango Intercuartílico: $IQR = Q_3 - Q_1$.

Se establecen límites inferiores ($Q_1 - 1.5 \times IQR$) y superiores ($Q_3 + 1.5 \times IQR$) para identificar y aislar salarios atípicos o erróneos del portal.

> 🚀 Modo de Uso

Para ejecutar el pipeline, y scraper, completo de extracción de datos:

```bash
python scraper.py
```

*Salida del scraper*: `data/raw/tecnoempleo_jobs.csv` (con un archivo de depuración temporal en `data/raw/debug_page.html`).

## 7. 📓 Notebooks de Análisis

El análisis estadístico completo y la exploración profunda del mercado laboral se encuentran estructurados en 3 notebooks secuenciales dentro de la carpeta `notebooks/`:

📊 `analisis_01_exploracion_y_descriptiva.ipynb`

*Punto de partida del análisis*: Carga el dataset limpio generado por el pipeline de curación e inspecciona su estructura inicial.

* **Diagnóstico de datos**: Inspección de dimensiones `.shape`, tipos de datos `.dtypes` y estadísticos básicos `.describe()`.

* **Tratamiento de vacíos**: Cuantificación sistemática de valores nulos con `.isnull().sum()` y documentación de decisiones de imputación o descarte.

* **Filtro estadístico**: Detección y aislamiento de outliers mediante el método del Rango Intercuartílico ($IQR$).

* **Análisis descriptivo**: Cálculo de medias, medianas y desviaciones estándar de las variables clave del mercado.

* **Distribuciones**: Visualización de la oferta según perfiles demandados y análisis de distribución salarial mediante histogramas con curvas de estimación de densidad de kernel ($KDE$) y el test de normalidad de Shapiro-Wilk.

🔗 `analisis_02_correlaciones_agrupaciones_probabilidad.ipynb`

Módulo orientado a responder de manera cuantitativa las preguntas de negocio clave de DataTalent Solutions.

* **Análisis multivariante**: Generación de matrices de correlación y visualización mediante mapas de calor (heatmaps con `.corr()`).

* **Demanda de Skills**: Extracción y ordenación del Top 20 de tecnologías más demandadas en el ecosistema español.

* **Estructura laboral**: Distribución de ofertas según su modalidad de trabajo y cruce multidimensional de *Experiencia × Tamaño de Empresa* mediante tablas dinámicas (`pivot_table()`).

* **Dispersión salarial**: Agrupaciones salariales medianas mediante `.groupby()` y boxplots comparativos para evaluar la variabilidad del mercado.

* **Probabilidad Condicional**: Modelado de tres escenarios clave $P(A|B)$:

    1. Probabilidad de obtener un salario alto según el nivel de experiencia.
    2. Probabilidad de acceso a trabajo en remoto según el tamaño de la compañía.
    3. Probabilidad de flexibilidad horaria/laboral según la ciudad de la oferta.

⚖️ `analisis_03_informe_sesgos.ipynb` (Ética en los Datos)

*Evaluación de los límites metodológicos, sesgos sistémicos de captura y su impacto real en las decisiones estratégicas de reskilling.*

* **Análisis MNAR (Missing Not At Random)**: Evaluación de la enorme tasa de salarios ocultos (80.7% de nulos en Tecnoempleo). Se demuestra con código que la falta de publicación de salario no es aleatoria, sino que correlaciona fuertemente con el tipo de perfil técnico.

* **Sesgo de Selección del Scraper**: Análisis del impacto de limitar las búsquedas del scraper a 24 términos predefinidos en lugar de realizar una exploración abierta de todo el portal de empleo.

* **Sesgo de Representación Geográfica**: Contraste con el dataset global *DS Salaries*, donde España representa únicamente el 2.3% del volumen total de registros (14 de 607 ofertas).

## 8. 📈 Estadísticas del Análisis y Hallazgos Clave

### A. Resumen del Mercado Español (Portal: Tecnoempleo)

> **Muestreo General**

|  Métrica  |  Valor  |
| --------- | ------- | 
| Total ofertas analizadas | 1.148 |
| Perfiles tech cubiertos | 24 |
| Ofertas con skills etiquetadas | 1.148 (100.0%) |
| Ofertas con salario publicado | 221 (19.3%) |

> **Demanda de Competencias Técnicas (Top 5 Skills)**

| Skill | Volumen de Ofertas |
| --------- | ------- | 
| Python | 168 |
| Java | 159 |
| SQL | 96 |
| Angular | 61 |
| Azure | 58 |

> **Roles Profesionales con Mayor Volumen (Top 5 Perfiles)**

| Perfil Profesional | Volumen de Ofertas |
| --------- | ------- |
| Data Scientist | 84 |
| Programador | 76 |
| Soporte Técnico | 76 |
| Arquitecto TIC | 72 |
| Ciberseguridad | 72 |

> **Distribución de Ofertas según Modalidad**

| Modalidad de Trabajo | Volumen de Ofertas | Porcentaje (%) |
| --------- | ------- | ------ |
| No especificado | 459 | 40.0% |
| Híbrido | 405 | 35.3% |
| En Remoto | 200 | 17.4% |
| Presencial | 84 | 7.3% |

### B. Referencia Salarial Global (Dataset: DS Salaries)

Para enriquecer la perspectiva de la consultora con un contexto internacional, se analizó un dataset de referencia global enfocado exclusivamente en roles de datos.

| Métrica Analizada | Valor de Referencia | 
| --------- | ------- |
| Registros totales del histórico | 607 |
| Salario mediano global | €93.444 / año |
| Salario mediano (Nivel Junior) | €51.980 / año |
| Salario mediano (Nivel Senior) | €124.660 / año |
| Correlación Salario ↔ Remoto | 0.13 (Correlación muy débil) | 

### C. Dashboard y Visualizaciones Clave

*(Inserta aquí las capturas de pantalla de tus 6 gráficos explicativos o el acceso directo a la aplicación interactiva de Streamlit)*

Este bloque metodológico y visual permite a los consultores de **DataTalent Solutions S.L.** tomar decisiones de diseño curricular de *reskilling* basadas en evidencias empíricas sólidas, conociendo de antemano las limitaciones y los sesgos del mercado analizado.
<div align="center">

  <img src="app/images/logo/logo.png" alt="Logotipo de TinderJob con estética similar a la de Tinder, app de citas" width="50%"> 
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

```
git clone https://github.com/HelenDiMo/TinderJob.git
cd TinderJob
```

# [Aquí añadiremos cómo arrancar el front y el scraper]

## 📊 6. Hallazgos Clave y Dashboard
(Aquí insertaremos las capturas de los 6 gráficos y el enlace a la aplicación web cuando estén listos)

## ⚖️ 7. Extracto del Informe de Sesgos (Ética en los Datos)
(Sección teórica preliminar)
La encuesta de Stack Overflow cuenta con sesgos demográficos conocidos (subrepresentación de género y sesgo de juventud). Nuestro análisis evalúa activamente cómo la falta de datos salariales por ocultación voluntaria (Missing Not At Random - MNAR) altera la media del mercado, advirtiendo a la consultora sobre los riesgos de entrenar algoritmos de selección automatizada de personal con estos datos.

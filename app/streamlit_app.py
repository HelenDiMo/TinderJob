import pdfplumber
import io
import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from scipy import stats

# -------------------------------------------------- CONFIGURACIÓN -----------------------

st.set_page_config(
    page_title="TinderJobs",
    page_icon="💕",
    layout="wide"
)

# --------------------------------------------------
# ESTILOS

st.markdown("""
<style>

/* Fondo general */
.main {
    background-color: #ffffff;
}

/* Título principal */
h1 {
    color: #ff0a54;
    font-weight: 900;
    font-size: 3rem;
    letter-spacing: -1px;
    margin-bottom: 0;
}

/* Subtítulo */
h3 {
    color: #444444;
    margin-top: 0;
}

/* KPIs */
div[data-testid="stMetric"] {
    background: linear-gradient(135deg, #ff0a54, #ff477e);
    padding: 18px;
    border-radius: 18px;
    border: none;
    color: white;
    box-shadow: 0px 6px 20px rgba(255, 10, 84, 0.25);
}

div[data-testid="stMetric"] label {
    color: white !important;
}

div[data-testid="stMetric"] div {
    color: white !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg,
        #fff0f5 0%,
        #ffe4ec 100%
    );
}

/* Selectboxes */
.stSelectbox label {
    color: #ff0a54;
    font-weight: 600;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    border-bottom: 2px solid #ff0a54;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 10px 10px 0 0;
    padding: 8px 20px;
    font-weight: 600;
    color: #888;
}
.stTabs [aria-selected="true"] {
    background: #ff0a54 !important;
    color: white !important;
}

</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# CARGA DE DATOS

@st.cache_data
def load_data():
    df = pd.read_csv("data/processed/clean_tecnoempleo_jobs.csv")
    df.columns = df.columns.str.strip().str.lower()
    return df

@st.cache_data
def load_salaries():
    try:
        df = pd.read_csv("data/ds_salaries.csv")
    except FileNotFoundError:
        df = pd.read_csv("../data/ds_salaries.csv")
    df['salary_in_eur'] = df['salary_in_usd'] * 0.92
    nivel_map = {
        'EN': 'Entry-level (Junior)',
        'MI': 'Mid-level (Semi-senior)',
        'SE': 'Senior',
        'EX': 'Executive / Director'
    }
    df['experience_label']   = df['experience_level'].map(nivel_map)
    df['company_size_label'] = df['company_size'].map(
        {'S': 'Pequeña (<50)', 'M': 'Mediana (50-250)', 'L': 'Grande (>250)'})
    return df

df     = load_data()
df_sal = load_salaries()

orden_exp  = ['Entry-level (Junior)', 'Mid-level (Semi-senior)', 'Senior', 'Executive / Director']
orden_size = ['Pequeña (<50)', 'Mediana (50-250)', 'Grande (>250)']

# Paleta Tinder / Tinder palette
TINDER_RED   = "#ff0a54"
TINDER_PINK  = "#ff477e"
TINDER_LIGHT = "#ff7096"
COLORS = [TINDER_RED, TINDER_PINK, TINDER_LIGHT, "#ff9a8b", "#ffc3c3", "#ffb3c6"]

# -------------------------------------------------- VALIDACIÓN ----------------------

required_cols = ["ciudad", "skills", "salario_medio"]
missing = [c for c in required_cols if c not in df.columns]
if missing:
    st.error(f"Faltan columnas en el CSV: {missing}")
    st.stop()

df = df.dropna(subset=required_cols)

# --------------------------------------------------
# FORMATEO DE TEXTOS

def format_skills(skills):
    return ", ".join(
        skill.strip().title()
        for skill in str(skills).split(",")
        if skill.strip()
    )

df["ciudad"] = df["ciudad"].astype(str).str.strip().str.title()

if "tipo_contrato" in df.columns:
    df["tipo_contrato"] = df["tipo_contrato"].astype(str).str.strip().str.title()

if "titulo" in df.columns:
    df["titulo"] = df["titulo"].astype(str).str.strip().str.title()

if "empresa" in df.columns:
    df["empresa"] = df["empresa"].astype(str).str.strip().str.title()

df["skills"] = df["skills"].apply(format_skills)

# --------------------------------------------------
# SKILLS

all_skills = (
    df["skills"].dropna().astype(str)
    .str.split(",").explode().str.strip().unique()
)

# --------------------------------------------------
# HEADER

st.markdown("""
<div style="
    background: linear-gradient(135deg, #ff0a54, #ff477e);
    padding: 25px;
    border-radius: 20px;
    text-align: center;
    margin-bottom: 20px;
">
<h1 style="color: white; margin:0; font-size: 3.2rem; font-weight: 900;">
TinderJobs
</h1>
<p style="color: white; font-size: 1.2rem; margin-top: 10px;">
Descubre qué skills te acercan a tu próximo trabajo
</p>
</div>
""", unsafe_allow_html=True)

# --------------------------------------------------
# SIDEBAR

st.sidebar.image("app/assets/logo/logo.png", use_container_width=True)
st.sidebar.markdown("---")
st.sidebar.header("Filtros")

selected_city = st.sidebar.selectbox(
    "Ciudad",
    ["Todas"] + sorted(df["ciudad"].dropna().unique().tolist()),
    key="city_select"
)

selected_skill = st.sidebar.selectbox(
    "Skill",
    ["Todas"] + sorted(all_skills),
    key="skill_select"
)

selected_position = st.sidebar.selectbox(
    "Tipo de posición",
    ["Todas"] + sorted(df["tipo_contrato"].dropna().unique().tolist()),
    key="position_select"
)

# --------------------------------------------------
# FILTROS

filtered_df = df.copy()

if selected_city != "Todas":
    filtered_df = filtered_df[filtered_df["ciudad"] == selected_city]

if selected_skill != "Todas":
    filtered_df = filtered_df[
        filtered_df["skills"].astype(str).str.contains(selected_skill, case=False, na=False)]

if selected_position != "Todas":
    filtered_df = filtered_df[filtered_df["tipo_contrato"] == selected_position]

# --------------------------------------------------
# KPIs

avg_salary = int(filtered_df["salario_medio"].mean()) if len(filtered_df) else 0
offers     = len(filtered_df)
top_city   = filtered_df["ciudad"].mode()[0] if len(filtered_df) else "-"
top_skill  = filtered_df["skills"].mode()[0] if len(filtered_df) else "-"

col1, col2, col3 = st.columns(3)
col1.metric("Salario medio", f"{avg_salary:,.0f} €")
col2.metric("Ofertas", offers)
col3.metric("Ciudad líder", top_city)

# --------------------------------------------------
# GRÁFICOS PRINCIPALES (código original de Verónica)

col_left, col_right = st.columns(2)

with col_left:
    skills_count = (
        filtered_df["skills"].dropna().astype(str)
        .str.split(",").explode().str.strip()
        .value_counts().reset_index()
    )
    skills_count.columns = ["Skill", "Count"]
    fig_skills = px.bar(
        skills_count, x="Skill", y="Count",
        title="Skills más demandadas"
    )
    st.plotly_chart(fig_skills, use_container_width=True)

with col_right:
    salary_city = (
        filtered_df.groupby("ciudad")["salario_medio"]
        .mean().reset_index()
    )
    fig_salary = px.bar(
        salary_city, x="ciudad", y="salario_medio",
        title="Salario medio por ciudad"
    )
    st.plotly_chart(fig_salary, use_container_width=True)

# --------------------------------------------------
# TABLA

st.markdown("### Datos filtrados")
st.dataframe(filtered_df, use_container_width=True)

st.markdown("---")

# ══════════════════════════════════════════════════════════════
# ANÁLISIS ESTADÍSTICO — ADRIANA (Analytics & Bias Reporter)
# ══════════════════════════════════════════════════════════════

st.markdown("## 📊 Análisis estadístico")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Mercado España",
    "💰 Análisis Salarial",
    "🎲 Probabilidad Condicional",
    "⚖️ Sesgos",
    "💘 TinderMatch — Mi CV"
])

# ── TAB 1 — MERCADO ESPAÑA ────────────────────────────────────
with tab1:

    st.markdown("### Demanda de perfiles tech en España")

    # Gráfico 1: Demanda por perfil / Demand by profile
    demanda = df['busqueda'].value_counts().reset_index()
    demanda.columns = ['Perfil', 'Ofertas']
    fig1 = px.bar(
        demanda, x='Ofertas', y='Perfil', orientation='h',
        title='Número de ofertas por perfil — Tecnoempleo España',
        color='Ofertas',
        color_continuous_scale=['#ffd6e0', TINDER_RED],
        text='Ofertas',
        labels={'Perfil': 'Perfil', 'Ofertas': 'Número de ofertas'}
    )
    fig1.update_layout(yaxis={'categoryorder': 'total ascending'},
                       coloraxis_showscale=False, height=580)
    fig1.update_traces(textposition='outside')
    st.plotly_chart(fig1, use_container_width=True)
    st.markdown("""
    > **📝 Interpretación:** Los perfiles con más demanda son data-scientist (84), programador
    y soporte-técnico (76 cada uno). Big-data (11) y dba (8) tienen muy poca presencia.
    DataTalent debe priorizar los 5 primeros perfiles en sus programas de reskilling.
    """)

    st.markdown("---")

    col_a, col_b = st.columns(2)

    # Gráfico 2: Top 20 skills / Top 20 skills
    with col_a:
        st.markdown("#### Top 20 skills más demandadas")
        skills_series = (
            df['skills'].dropna().astype(str)
            .str.split(',').explode().str.strip()
        )
        top_skills = skills_series.value_counts().head(20).reset_index()
        top_skills.columns = ['Skill', 'Frecuencia']
        fig2 = px.bar(
            top_skills, x='Frecuencia', y='Skill', orientation='h',
            title='Top 20 skills más demandadas — Tecnoempleo España',
            color='Frecuencia',
            color_continuous_scale=['#ffd6e0', TINDER_RED],
            text='Frecuencia',
            labels={'Skill': 'Tecnología', 'Frecuencia': 'Nº de ofertas'}
        )
        fig2.update_layout(yaxis={'categoryorder': 'total ascending'},
                           coloraxis_showscale=False, height=550)
        fig2.update_traces(textposition='outside')
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown("""
        > **📝 Interpretación:** Python (168), Java (159) y SQL (96) dominan el mercado.
        Cualquier programa de reskilling debe incluir estas tres tecnologías
        más al menos una plataforma cloud (Azure o AWS).
        """)

    # Gráfico 3: Modalidad / Modality
    with col_b:
        st.markdown("#### Distribución por modalidad de trabajo")
        if 'modalidad' in df.columns:
            modalidad_counts = df['modalidad'].value_counts().reset_index()
            modalidad_counts.columns = ['Modalidad', 'Ofertas']
            fig3 = px.pie(
                modalidad_counts, values='Ofertas', names='Modalidad',
                title='Distribución de ofertas por modalidad — Tecnoempleo España',
                color_discrete_sequence=COLORS
            )
            fig3.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig3, use_container_width=True)
            st.markdown("""
            > **📝 Interpretación:** Solo el 7% exige presencialidad.
            El 53% de las ofertas con modalidad definida son flexibles (híbrido o remoto).
            Los candidatos no necesitan estar en una gran ciudad para acceder al mercado.
            """)


# ── TAB 2 — ANÁLISIS SALARIAL ─────────────────────────────────
with tab2:

    st.markdown("### 💰 Análisis salarial — DS Salaries (referencia global)")
    st.info("Tecnoempleo publica salario en menos del 20% de las ofertas. "
            "Usamos DS Salaries como referencia global de mercado.")

    col_a, col_b = st.columns(2)

    # Gráfico 4: Histograma salarial + KDE / Salary histogram + KDE
    with col_a:
        st.markdown("#### Distribución salarial — Histograma")
        salarios = df_sal['salary_in_eur'].dropna()
        fig4 = px.histogram(
            df_sal, x='salary_in_eur', nbins=40,
            title='Distribución salarial — DS Salaries (global)',
            labels={'salary_in_eur': 'Salario anual (EUR)'},
            color_discrete_sequence=[TINDER_PINK],
            marginal='violin'
        )
        fig4.add_vline(x=salarios.median(), line_dash='dash', line_color='green',
                       annotation_text=f'Mediana: €{salarios.median():,.0f}')
        fig4.add_vline(x=salarios.mean(), line_dash='dash', line_color=TINDER_RED,
                       annotation_text=f'Media: €{salarios.mean():,.0f}')
        fig4.update_layout(height=420)
        st.plotly_chart(fig4, use_container_width=True)
        st.markdown("""
        > **📝 Interpretación:** Distribución asimétrica positiva — la media (€103.314)
        supera a la mediana (€93.444). Test Shapiro-Wilk confirma que NO sigue
        distribución normal (p<0.05). Siempre comunicar la **mediana** a los candidatos.
        """)

    # Gráfico 5: Salario por nivel / Salary by level
    with col_b:
        st.markdown("#### Salario mediano por nivel de experiencia")
        sal_nivel = (
            df_sal.groupby('experience_label')['salary_in_eur']
            .agg(mediana='median', media='mean', n='count')
            .reindex(orden_exp).reset_index()
        )
        fig5 = px.bar(
            sal_nivel, x='experience_label', y='mediana',
            title='Salario mediano por nivel de experiencia — DS Salaries',
            labels={'experience_label': 'Nivel', 'mediana': 'Salario mediano (EUR)'},
            color='mediana',
            color_continuous_scale=['#ffd6e0', TINDER_RED],
            text=sal_nivel['mediana'].apply(lambda x: f'€{x:,.0f}')
        )
        fig5.update_layout(coloraxis_showscale=False, height=420)
        fig5.update_traces(textposition='outside')
        st.plotly_chart(fig5, use_container_width=True)
        st.markdown("""
        > **📝 Interpretación:** Junior (€51.980) → Senior (€124.660): el mayor salto
        es entre Mid-senior y Senior (+76%). Un candidato que llegue a Senior
        puede casi triplicar su salario de entrada.
        """)

    st.markdown("---")

    col_c, col_d = st.columns(2)

    # Gráfico 6: Boxplot / Boxplot
    with col_c:
        st.markdown("#### Dispersión salarial por nivel — Boxplot")
        df_box = df_sal[df_sal['experience_label'].notna()].copy()
        p95 = df_box['salary_in_eur'].quantile(0.95)
        df_box = df_box[df_box['salary_in_eur'] <= p95]
        fig6 = px.box(
            df_box, x='experience_label', y='salary_in_eur',
            category_orders={'experience_label': orden_exp},
            title='Dispersión salarial por nivel de experiencia',
            labels={'experience_label': 'Nivel', 'salary_in_eur': 'Salario anual (EUR)'},
            color='experience_label',
            color_discrete_sequence=COLORS
        )
        fig6.update_layout(showlegend=False, height=420)
        st.plotly_chart(fig6, use_container_width=True)
        st.markdown("""
        > **📝 Interpretación:** La caja Junior es estrecha — el mercado paga
        homogéneamente en entrada. A partir de Senior, la especialización
        marca grandes diferencias salariales.
        """)

    # Gráfico 7: Pivot table / Pivot table
    with col_d:
        st.markdown("#### Salario mediano: experiencia × tamaño de empresa")
        pivot = pd.pivot_table(
            df_sal, values='salary_in_eur',
            index='experience_label', columns='company_size_label',
            aggfunc='median'
        ).reindex(index=orden_exp, columns=orden_size)
        fig7 = px.imshow(
            pivot, text_auto='.0f',
            title='Salario mediano (EUR) — experiencia × tamaño empresa',
            labels={'x': 'Tamaño de empresa', 'y': 'Nivel', 'color': 'Salario (EUR)'},
            color_continuous_scale=['#ffd6e0', TINDER_RED],
            aspect='auto'
        )
        fig7.update_layout(height=420)
        st.plotly_chart(fig7, use_container_width=True)
        st.markdown("""
        > **📝 Interpretación:** Empresas pequeñas pagan sorprendentemente bien a juniors (€55.200).
        A partir de Senior, las grandes siempre pagan más.
        Orienta juniors a pequeñas o grandes; seniors a medianas o grandes.
        """)

    st.markdown("---")

    # Gráfico 8: Scatter / Scatter
    st.markdown("#### Evolución salarial por año y nivel — Dispersión")
    df_scatter = df_sal.dropna(subset=['work_year', 'salary_in_eur']).copy()
    p95 = df_scatter['salary_in_eur'].quantile(0.95)
    df_scatter = df_scatter[df_scatter['salary_in_eur'] <= p95]
    fig8 = px.scatter(
        df_scatter, x='work_year', y='salary_in_eur',
        color='experience_label',
        category_orders={'experience_label': orden_exp},
        title='Evolución salarial por año y nivel — DS Salaries (global)',
        labels={'work_year': 'Año', 'salary_in_eur': 'Salario anual (EUR)',
                'experience_label': 'Nivel'},
        color_discrete_sequence=COLORS,
        trendline='ols',
        opacity=0.6
    )
    fig8.update_layout(height=450)
    st.plotly_chart(fig8, use_container_width=True)
    st.markdown("""
    > **📝 Interpretación:** Tendencia salarial positiva entre 2020 y 2022.
    El nivel de experiencia es mucho más determinante que el año.
    Invertir en reskilling ahora tiene más retorno que esperar.
    """)


# ── TAB 3 — PROBABILIDAD CONDICIONAL ─────────────────────────
with tab3:

    st.markdown("### 🎲 Probabilidad condicional P(A|B)")
    st.markdown("Respondemos preguntas de negocio concretas usando probabilidad condicional.")

    # Gráfico 9: Heatmap correlaciones / Correlation heatmap
    st.markdown("#### Heatmap de correlaciones — DS Salaries")
    df_corr = df_sal[['salary_in_eur', 'remote_ratio', 'work_year']].dropna()
    df_corr = df_corr.rename(columns={
        'salary_in_eur': 'Salario (EUR)',
        'remote_ratio':  'Ratio remoto (%)',
        'work_year':     'Año'
    })
    matriz = df_corr.corr().round(3)
    fig9 = px.imshow(
        matriz, text_auto=True,
        title='Matriz de correlaciones — DS Salaries (global)',
        color_continuous_scale=['#ffd6e0', TINDER_RED],
        zmin=-1, zmax=1, aspect='auto'
    )
    fig9.update_layout(height=380)
    st.plotly_chart(fig9, use_container_width=True)
    st.markdown("""
    > **📝 Interpretación:** Las tres correlaciones son positivas pero muy débiles (máx. 0.17).
    La modalidad de trabajo no determina el salario — el nivel de experiencia pesa mucho más.
    """)

    st.markdown("---")

    col_a, col_b = st.columns(2)

    # Gráfico 10: P(salario alto | nivel) / P(high salary | level)
    with col_a:
        st.markdown("#### P(Salario alto | Nivel de experiencia)")
        mediana_global = df_sal['salary_in_eur'].median()
        df_sal['salario_alto'] = df_sal['salary_in_eur'] > mediana_global
        prob_nivel = (
            df_sal.groupby('experience_label')['salario_alto']
            .agg(prob=lambda x: x.sum() / len(x), n='count')
            .reindex(orden_exp).reset_index()
        )
        prob_nivel['prob_pct'] = (prob_nivel['prob'] * 100).round(1)
        fig10 = px.bar(
            prob_nivel, x='experience_label', y='prob_pct',
            title=f'P(Salario > mediana €{mediana_global:,.0f} | Nivel)',
            labels={'experience_label': 'Nivel', 'prob_pct': 'Probabilidad (%)'},
            color='prob_pct',
            color_continuous_scale=['#ffd6e0', TINDER_RED],
            text=prob_nivel['prob_pct'].apply(lambda x: f'{x:.1f}%')
        )
        fig10.add_hline(y=50, line_dash='dash', line_color='gray',
                        annotation_text='50% referencia')
        fig10.update_layout(coloraxis_showscale=False, height=400)
        fig10.update_traces(textposition='outside')
        st.plotly_chart(fig10, use_container_width=True)
        st.markdown("""
        > **📝 Interpretación:** Junior: 11.4% de probabilidad de superar la mediana.
        Senior: 73.2%. El salto Mid-senior → Senior casi triplica la probabilidad.
        """)

    # Gráfico 11: P(remoto | empresa) / P(remote | company)
    with col_b:
        st.markdown("#### P(Trabajo remoto | Tamaño de empresa)")
        df_sal['es_remoto'] = df_sal['remote_ratio'] == 100
        prob_remoto = (
            df_sal.groupby('company_size_label')['es_remoto']
            .agg(prob=lambda x: x.sum() / len(x), n='count')
            .reindex(orden_size).reset_index()
        )
        prob_remoto['prob_pct'] = (prob_remoto['prob'] * 100).round(1)
        fig11 = px.bar(
            prob_remoto, x='company_size_label', y='prob_pct',
            title='P(Trabajo 100% remoto | Tamaño de empresa)',
            labels={'company_size_label': 'Tamaño', 'prob_pct': 'Probabilidad (%)'},
            color='prob_pct',
            color_continuous_scale=['#ffd6e0', TINDER_RED],
            text=prob_remoto['prob_pct'].apply(lambda x: f'{x:.1f}%')
        )
        fig11.add_hline(y=50, line_dash='dash', line_color='gray',
                        annotation_text='50% referencia')
        fig11.update_layout(coloraxis_showscale=False, height=400)
        fig11.update_traces(textposition='outside')
        st.plotly_chart(fig11, use_container_width=True)
        st.markdown("""
        > **📝 Interpretación:** Empresas medianas (69.3%) ofrecen más remoto que las grandes (53.5%).
        Candidatos que priorizan el remoto deben orientarse a empresas de 50-250 empleados.
        """)

    st.markdown("---")

    # Gráfico 12: P(flexible | ciudad) / P(flexible | city)
    st.markdown("#### P(Trabajo flexible | Ciudad) — Tecnoempleo España")
    if 'modalidad' in df.columns and 'ciudad' in df.columns:
        df_ciudad = df.dropna(subset=['ciudad', 'modalidad']).copy()
        df_ciudad['es_flexible'] = df_ciudad['modalidad'].isin(['Híbrido', 'En Remoto'])
        prob_ciudad = (
            df_ciudad.groupby('ciudad')['es_flexible']
            .agg(prob=lambda x: x.sum() / len(x), n='count')
            .query('n >= 5')
            .sort_values('prob', ascending=False)
            .head(15).reset_index()
        )
        prob_ciudad['prob_pct'] = (prob_ciudad['prob'] * 100).round(0)
        fig12 = px.bar(
            prob_ciudad, x='prob_pct', y='ciudad', orientation='h',
            title='P(Trabajo híbrido o remoto | Ciudad) — mín. 5 ofertas por ciudad',
            labels={'prob_pct': 'Probabilidad (%)', 'ciudad': 'Ciudad'},
            color='prob_pct',
            color_continuous_scale=['#ffd6e0', TINDER_RED],
            text=prob_ciudad['prob_pct'].apply(lambda x: f'{x:.0f}%')
        )
        fig12.add_vline(x=50, line_dash='dash', line_color='gray',
                        annotation_text='50% referencia')
        fig12.update_layout(yaxis={'categoryorder': 'total ascending'},
                            coloraxis_showscale=False, height=480)
        fig12.update_traces(textposition='outside')
        st.plotly_chart(fig12, use_container_width=True)
        st.markdown("""
        > **📝 Interpretación:** Alcobendas (86%) y Almería (76%) lideran la flexibilidad.
        Madrid (44%) y Barcelona (45%) tienen menos flexibilidad pese a concentrar más ofertas.
        Candidatos en Sevilla o Zaragoza deben orientarse a empresas de otras ciudades con remoto.
        """)


# ── TAB 4 — SESGOS ───────────────────────────────────────────
with tab4:

    st.markdown("### ⚖️ Informe de sesgos — Ética en los datos")

    # Tabla resumen / Summary table
    st.markdown("#### Resumen ejecutivo")
    sesgos_data = {
        'Sesgo': ['MNAR — Salarios ausentes', 'Sesgo de búsqueda',
                  'Subrepresentación España'],
        'Dataset': ['Tecnoempleo', 'Tecnoempleo', 'DS Salaries'],
        'Tipo': ['MNAR', 'Selección', 'Geográfico'],
        '% afectado': ['80.7% nulos', '24 términos fijos', '2.3% (14/607)'],
        'Impacto': [
            'No permite análisis salarial del mercado español',
            'Excluye perfiles no contemplados en el scraping',
            'Estadísticos de España no son fiables'
        ]
    }
    st.dataframe(pd.DataFrame(sesgos_data), use_container_width=True)

    st.markdown("---")

    col_a, col_b = st.columns(2)

    # Gráfico 13: Sesgo de búsqueda / Search bias
    with col_a:
        st.markdown("#### Sesgo de selección — Distribución por término")
        busqueda_counts = df['busqueda'].value_counts().reset_index()
        busqueda_counts.columns = ['Término', 'Ofertas']
        fig13 = px.bar(
            busqueda_counts, x='Ofertas', y='Término', orientation='h',
            title='Ofertas por término — solo 24 términos predefinidos',
            color='Ofertas',
            color_continuous_scale=['#ffd6e0', TINDER_RED],
            labels={'Término': 'Término de búsqueda', 'Ofertas': 'Nº de ofertas'}
        )
        fig13.update_layout(yaxis={'categoryorder': 'total ascending'},
                            coloraxis_showscale=False, height=550)
        st.plotly_chart(fig13, use_container_width=True)
        st.markdown("""
        > **📝 Interpretación:** El dataset solo contiene 24 perfiles predefinidos.
        Ofertas con otros títulos quedan excluidas, sesgando el análisis.
        """)

    # Gráfico 14: Subrepresentación geográfica / Geographic underrepresentation
    with col_b:
        st.markdown("#### Subrepresentación geográfica — DS Salaries")
        paises = df_sal['company_location'].value_counts().head(15).reset_index()
        paises.columns = ['País', 'Registros']
        fig14 = px.bar(
            paises, x='País', y='Registros',
            title='Registros por país — España (ES) en rojo',
            text='Registros',
            labels={'País': 'País (código ISO)', 'Registros': 'Nº de registros'},
            color=paises['País'].apply(lambda x: 'España' if x == 'ES' else 'Otros'),
            color_discrete_map={'España': TINDER_RED, 'Otros': TINDER_PINK}
        )
        fig14.update_layout(showlegend=False, height=550)
        fig14.update_traces(textposition='outside')
        st.plotly_chart(fig14, use_container_width=True)
        st.markdown("""
        > **📝 Interpretación:** España representa solo el 2.3% del dataset (14 registros).
        EEUU domina con 355 (58.5%). Los estadísticos españoles en DS Salaries no son fiables.
        """)

    st.markdown("---")

    # Recomendaciones / Recommendations
    st.markdown("#### 💡 Recomendaciones para DataTalent Solutions S.L.")
    recos = [
        "Comunicar siempre la **mediana** salarial (€93.444), nunca la media.",
        "No usar Tecnoempleo como fuente salarial — el 80.7% de nulos hace inviable el análisis.",
        "Ampliar los términos de búsqueda del scraper para reducir el sesgo de selección.",
        "Complementar con fuentes españolas (InfoJobs, LinkedIn España) para análisis salariales.",
        "No entrenar modelos de selección con estos datasets sin técnicas de debiasing previas.",
        "Comunicar la incertidumbre al equipo directivo: las cifras son orientativas."
    ]
    for i, r in enumerate(recos, 1):
        st.markdown(f"**{i}.** {r}")


# ══════════════════════════════════════════════════════════════
# TAB 5 — TINDERMATCH
# Analiza el CV del usuario y muestra las ofertas más compatibles
# Analyzes the user's CV and shows the most compatible offers
# ══════════════════════════════════════════════════════════════
with tab5:

    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #ff0a54, #ff477e);
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
        margin-bottom: 1.5rem;
    ">
        <h2 style="color:white;margin:0;font-size:2rem;">💘 TinderMatch</h2>
        <p style="color:white;margin-top:0.5rem;font-size:1rem;">
            Sube tu CV y te mostramos las ofertas más compatibles
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ── Función de extracción de skills del CV ────────────────
    # Skills conocidas para buscar en el CV / Known skills to search in CV
    SKILLS_CONOCIDAS = [
        # Lenguajes / Languages
        'python', 'java', 'javascript', 'typescript', 'sql', 'r', 'scala',
        'c#', 'c++', 'php', 'ruby', 'swift', 'kotlin', 'go', 'rust',
        # Frontend
        'react', 'angular', 'vue', 'html', 'css', 'bootstrap', 'tailwind',
        'jquery', 'next.js', 'nuxt',
        # Backend
        'node', 'django', 'flask', 'spring', 'fastapi', '.net', 'laravel',
        'express', 'rails',
        # Data / ML
        'pandas', 'numpy', 'scikit-learn', 'tensorflow', 'pytorch', 'keras',
        'spark', 'hadoop', 'kafka', 'airflow', 'dbt', 'mlflow',
        'machine learning', 'deep learning', 'nlp', 'computer vision',
        'data science', 'big data', 'etl', 'power bi', 'tableau', 'looker',
        'qlik', 'matplotlib', 'seaborn', 'plotly',
        # Cloud / DevOps
        'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform',
        'jenkins', 'github actions', 'ci/cd', 'devops', 'linux',
        'ansible', 'prometheus', 'grafana',
        # Bases de datos / Databases
        'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch',
        'oracle', 'sql server', 'sqlite', 'cassandra', 'dynamodb',
        # Otros / Others
        'git', 'agile', 'scrum', 'jira', 'rest', 'api', 'microservices',
        'ciberseguridad', 'networking', 'windows', 'vmware',
    ]

    def extraer_skills_cv(texto_cv: str) -> list:
        """
        Extrae skills del texto del CV buscando coincidencias con la lista conocida.
        Extracts skills from CV text by matching against the known skills list.
        """
        texto_lower = texto_cv.lower()
        skills_encontradas = []
        for skill in SKILLS_CONOCIDAS:
            # Busco la skill como palabra completa (no como substring)
            # I search for the skill as a whole word (not as a substring)
            import re
            patron = r'\b' + re.escape(skill) + r'\b'
            if re.search(patron, texto_lower):
                skills_encontradas.append(skill)
        return skills_encontradas

    def calcular_match(skills_cv: list, skills_oferta: str) -> float:
        """
        Calcula el porcentaje de match entre las skills del CV y las de una oferta.
        Calculates the match percentage between CV skills and a job offer's skills.
        """
        if not skills_cv or not isinstance(skills_oferta, str):
            return 0.0
        skills_oferta_list = [s.strip().lower() for s in skills_oferta.split(',')]
        if not skills_oferta_list:
            return 0.0
        # Cuántas skills de la oferta aparecen en el CV
        # How many offer skills appear in the CV
        matches = sum(1 for s in skills_oferta_list if s in skills_cv)
        return round(matches / len(skills_oferta_list) * 100, 1)

    def get_emoji_match(score: float) -> str:
        """Devuelve un emoji según el nivel de match. / Returns emoji based on match level."""
        if score >= 80: return "💘 Match perfecto"
        if score >= 60: return "❤️ Gran match"
        if score >= 40: return "🧡 Buen match"
        if score >= 20: return "💛 Match parcial"
        return "🤍 Bajo match"

    # ── Subida del CV / CV upload ─────────────────────────────
    # Función para extraer texto de PDF / Function to extract text from PDF
    def extraer_texto_pdf(archivo) -> str:
        """
        Extrae el texto de un PDF usando pdfplumber.
        Extracts text from a PDF using pdfplumber.
        """
        texto = ""
        with pdfplumber.open(io.BytesIO(archivo.read())) as pdf:
            for pagina in pdf.pages:
                texto_pagina = pagina.extract_text()
                if texto_pagina:
                    texto += texto_pagina + "\n"
        return texto

    col_input, col_info = st.columns([2, 1])

    with col_input:
        # Selector de método de entrada / Input method selector
        metodo = st.radio(
            "¿Cómo quieres subir tu CV?",
            ["📎 Subir PDF", "📝 Pegar texto"],
            horizontal=True,
            key="metodo_cv"
        )

        cv_texto = ""

        if metodo == "📎 Subir PDF":
            # Upload de PDF / PDF upload
            pdf_file = st.file_uploader(
                "Sube tu CV en PDF",
                type=["pdf"],
                key="cv_pdf",
                help="El texto se extrae automáticamente del PDF"
            )
            if pdf_file is not None:
                with st.spinner("Extrayendo texto del PDF..."):
                    try:
                        cv_texto = extraer_texto_pdf(pdf_file)
                        if cv_texto.strip():
                            st.success(f"✅ PDF cargado correctamente ({len(cv_texto)} caracteres extraídos)")
                            # Muestro un preview del texto extraído / I show a preview of extracted text
                            with st.expander("👁️ Ver texto extraído del PDF"):
                                st.text(cv_texto[:1000] + ("..." if len(cv_texto) > 1000 else ""))
                        else:
                            st.error("No se pudo extraer texto del PDF. "
                                     "Puede ser un PDF escaneado. Prueba a pegar el texto manualmente.")
                    except Exception as e:
                        st.error(f"Error al leer el PDF: {e}. Prueba a pegar el texto manualmente.")
        else:
            # Texto manual / Manual text
            cv_texto = st.text_area(
                "Copia y pega el contenido de tu CV aquí:",
                height=250,
                placeholder="Ej: Soy desarrollador con 3 años de experiencia en Python, SQL, "
                            "Django y AWS. He trabajado con Docker y tengo conocimientos de "
                            "machine learning con scikit-learn y pandas...",
                key="cv_input"
            )

        # Filtros adicionales para el match / Additional filters for match
        st.markdown("#### 🔍 Filtros adicionales (opcional)")
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            ciudad_match = st.selectbox(
                "Ciudad preferida",
                ["Cualquiera"] + sorted(df["ciudad"].dropna().unique().tolist()),
                key="ciudad_match"
            )
        with col_f2:
            modalidad_match = st.selectbox(
                "Modalidad preferida",
                ["Cualquiera"] + sorted(df["modalidad"].dropna().unique().tolist())
                if "modalidad" in df.columns else ["Cualquiera"],
                key="modalidad_match"
            )

        min_match = st.slider(
            "Match mínimo (%)",
            min_value=0, max_value=100, value=20, step=5,
            key="min_match"
        )

    with col_info:
        st.markdown("#### 💡 Cómo funciona")
        st.markdown("""
        1. **Sube tu CV** en PDF o pega el texto
        2. El sistema **extrae tus skills** automáticamente
        3. **Compara** con las skills de cada oferta
        4. Te muestra las ofertas ordenadas por **% de compatibilidad**

        ---
        **Skills detectadas** de forma automática:
        - Lenguajes (Python, Java, SQL...)
        - Frameworks (React, Django, Spring...)
        - Cloud (AWS, Azure, GCP...)
        - Data/ML (Pandas, TensorFlow...)
        - DevOps (Docker, Kubernetes...)
        - Bases de datos (MySQL, MongoDB...)

        ---
        ⚠️ **Si el PDF es escaneado** (imagen), el texto no se puede extraer automáticamente.
        En ese caso usa la opción de pegar el texto.
        """)

    # ── Botón de análisis / Analysis button ──────────────────
    st.markdown("<br>", unsafe_allow_html=True)

    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
    with col_btn2:
        analizar = st.button(
            "💘 Buscar mi match perfecto",
            use_container_width=True,
            type="primary",
            key="btn_match"
        )

    # ── Resultados / Results ──────────────────────────────────
    if analizar:
        if not cv_texto.strip():
            st.warning("⚠️ Por favor pega el texto de tu CV antes de buscar.")
        else:
            with st.spinner("Analizando tu CV y buscando matches... 💘"):

                # Extraigo skills del CV / I extract skills from CV
                skills_cv = extraer_skills_cv(cv_texto)

                if not skills_cv:
                    st.error("No he detectado ninguna skill técnica en el texto. "
                             "Asegúrate de incluir tecnologías concretas como Python, SQL, etc.")
                else:
                    # Muestro skills detectadas / I show detected skills
                    st.success(f"✅ He detectado **{len(skills_cv)} skills** en tu CV:")
                    skills_html = " ".join([
                        f'<span style="background:#fff0f5;color:#ff0a54;padding:4px 10px;'
                        f'border-radius:12px;font-size:0.85rem;margin:2px;display:inline-block;'
                        f'font-weight:600;border:1px solid #ff0a54">{s.title()}</span>'
                        for s in skills_cv
                    ])
                    st.markdown(f'<div style="margin:0.5rem 0 1rem 0">{skills_html}</div>',
                                unsafe_allow_html=True)

                    # Aplico filtros opcionales / I apply optional filters
                    df_match = df.copy()
                    if ciudad_match != "Cualquiera":
                        df_match = df_match[df_match["ciudad"] == ciudad_match]
                    if modalidad_match != "Cualquiera" and "modalidad" in df_match.columns:
                        df_match = df_match[df_match["modalidad"] == modalidad_match]

                    # Calculo el match para cada oferta / I calculate match for each offer
                    df_match = df_match.copy()
                    df_match['match_pct'] = df_match['skills'].apply(
                        lambda s: calcular_match(skills_cv, s)
                    )

                    # Filtro por match mínimo y ordeno / I filter by min match and sort
                    resultados = (
                        df_match[df_match['match_pct'] >= min_match]
                        .sort_values('match_pct', ascending=False)
                        .head(20)
                        .reset_index(drop=True)
                    )

                    if len(resultados) == 0:
                        st.warning(f"No hay ofertas con un match ≥ {min_match}%. "
                                   f"Prueba a bajar el mínimo o cambiar los filtros.")
                    else:
                        st.markdown(f"### 🎯 {len(resultados)} ofertas compatibles encontradas")

                        # Gráfico de distribución de matches / Match distribution chart
                        fig_match = px.histogram(
                            df_match[df_match['match_pct'] > 0],
                            x='match_pct', nbins=20,
                            title='Distribución del % de compatibilidad de tus ofertas',
                            labels={'match_pct': 'Match (%)'},
                            color_discrete_sequence=[TINDER_PINK]
                        )
                        fig_match.add_vline(
                            x=resultados['match_pct'].mean(),
                            line_dash='dash', line_color=TINDER_RED,
                            annotation_text=f"Media: {resultados['match_pct'].mean():.1f}%"
                        )
                        fig_match.update_layout(height=300)
                        st.plotly_chart(fig_match, use_container_width=True)

                        # Tarjetas de resultados / Result cards
                        st.markdown("### 💼 Tus mejores matches")

                        for i, row in resultados.iterrows():
                            score       = row['match_pct']
                            emoji       = get_emoji_match(score)
                            titulo      = str(row.get('titulo', 'Sin título')).title()
                            empresa     = str(row.get('empresa', 'Empresa desconocida')).title()
                            ciudad      = str(row.get('ciudad', '')).title()
                            modalidad_o = str(row.get('modalidad', '')) if 'modalidad' in row else ''
                            skills_o    = str(row.get('skills', ''))
                            # URL directa a la oferta en Tecnoempleo
                            # Direct URL to the offer on Tecnoempleo
                            url_oferta  = row['url'] if 'url' in row and pd.notna(row['url']) else None

                            # Skills que coinciden / Matching skills
                            skills_oferta_list = [s.strip().lower() for s in skills_o.split(',')]
                            skills_match = [s for s in skills_oferta_list if s in skills_cv]
                            skills_no_match = [s for s in skills_oferta_list if s not in skills_cv]

                            # Color de la barra según el score / Bar color based on score
                            if score >= 60:
                                color_bar = TINDER_RED
                            elif score >= 40:
                                color_bar = "#ff7096"
                            else:
                                color_bar = "#ffb3c6"

                            # Añado enlace si existe URL / I add link if URL exists
                            link_html = (
                                f'<div style="margin-top:0.5rem;">' +
                                f'<a href="{url_oferta}" target="_blank" ' +
                                f'style="color:{TINDER_RED};font-weight:600;font-size:0.85rem;text-decoration:none;">' +
                                f'🔗 Ver oferta en Tecnoempleo →</a></div>'
                            ) if url_oferta else ""

                            st.markdown(f"""
                            <div style="
                                background: white;
                                border-radius: 16px;
                                padding: 1.2rem 1.5rem;
                                margin-bottom: 1rem;
                                box-shadow: 0 4px 15px rgba(255,10,84,0.1);
                                border-left: 5px solid {color_bar};
                            ">
                                <div style="display:flex;justify-content:space-between;align-items:flex-start;">
                                    <div>
                                        <div style="font-size:1.1rem;font-weight:700;color:#1a1a2e">
                                            {titulo}
                                        </div>
                                        <div style="color:{TINDER_RED};font-weight:600;margin:2px 0">
                                            {empresa}
                                        </div>
                                        <div style="color:#666;font-size:0.85rem">
                                            📍 {ciudad} &nbsp;|&nbsp; 🏠 {modalidad_o}
                                        </div>
                                    </div>
                                    <div style="text-align:right;">
                                        <div style="font-size:2rem;font-weight:900;color:{color_bar}">
                                            {score:.0f}%
                                        </div>
                                        <div style="font-size:0.8rem;color:#888">{emoji}</div>
                                    </div>
                                </div>
                                <div style="margin-top:0.8rem;">
                                    <span style="font-size:0.75rem;color:#999;
                                                 text-transform:uppercase;letter-spacing:1px">
                                        ✅ Skills que tienes:
                                    </span><br>
                                    {''.join([
                                        f'<span style="background:#fff0f5;color:{TINDER_RED};'
                                        f'padding:2px 8px;border-radius:10px;font-size:0.75rem;'
                                        f'margin:2px;display:inline-block;font-weight:600">'
                                        f'{s.title()}</span>'
                                        for s in skills_match[:8]
                                    ]) if skills_match else
                                    '<span style="color:#aaa;font-size:0.8rem">Ninguna detectada</span>'}
                                </div>
                                {'<div style="margin-top:0.5rem;"><span style="font-size:0.75rem;color:#999;text-transform:uppercase;letter-spacing:1px">❌ Skills que te faltan:</span><br>' +
                                ''.join([
                                    f'<span style="background:#f5f5f5;color:#888;'
                                    f'padding:2px 8px;border-radius:10px;font-size:0.75rem;'
                                    f'margin:2px;display:inline-block">'
                                    f'{s.title()}</span>'
                                    for s in skills_no_match[:5]
                                ]) + '</div>' if skills_no_match else ''}
                                {link_html}
                            </div>
                            """, unsafe_allow_html=True)

                        # Tabla descargable / Downloadable table
                        st.markdown("---")
                        st.markdown("#### 📥 Exportar resultados")
                        cols_export = ['titulo', 'empresa', 'ciudad', 'skills', 'match_pct']
                        cols_export = [c for c in cols_export if c in resultados.columns]
                        csv = resultados[cols_export].to_csv(index=False).encode('utf-8')
                        st.download_button(
                            label="⬇️ Descargar mis matches en CSV",
                            data=csv,
                            file_name="mis_matches_tinderjob.csv",
                            mime="text/csv"
                        )
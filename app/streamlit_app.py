import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------------------------------------- CONFIGURATION -----------------------------------


st.set_page_config(
    page_title="TinderJobs",
    page_icon="💕",
    layout="wide"
)

# -------------------------------------------------- ESTILOS. ---------------


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
}

/* Subtítulo */
h2, h3 {
    color: #222222;
}

/* Metrics (KPIs) */
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
    background: #fff0f5;
}

/* Botones y selects */
.stSelectbox label {
    color: #ff0a54;
    font-weight: 600;
}

/* Dataframe */
.dataframe {
    border-radius: 12px;
}

</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# CARGA DE DATOS


@st.cache_data
def load_data():
    df = pd.read_csv("data/processed/clean_tecnoempleo_jobs.csv")

    # normalizar nombres
    df.columns = df.columns.str.strip().str.lower()

    return df

df = load_data()

# --------------------------------------------------
# LIMPIEZA


required_cols = ["ciudad", "skills", "salario_medio"]

missing = [c for c in required_cols if c not in df.columns]

if missing:
    st.error(f"Faltan columnas en el CSV: {missing}")
    st.stop()

df = df.dropna(subset=required_cols)

# --------------------------------------------------
# HEADER


st.markdown("<h1>TinderJobs</h1>", unsafe_allow_html=True)
st.markdown(
    "<h3>Descubre qué skills te acercan a tu próximo trabajo</h3>",
    unsafe_allow_html=True
)

# --------------------------------------------------
# SIDEBAR


st.sidebar.header("Filtros")

selected_city = st.sidebar.selectbox(
    "Ciudad",
    ["Todas"] + sorted(df["ciudad"].dropna().unique().tolist())
)

# Skills vienen como texto (probablemente listas separadas por comas)

all_skills = (
    df["skills"]
    .dropna()
    .astype(str)
    .str.split(",")
    .explode()
    .str.strip()
    .unique()
)

selected_skill = st.sidebar.selectbox(
    "Skill",
    ["Todas"] + sorted(all_skills)
)

filtered_df = df.copy()

if selected_city != "Todas":
    filtered_df = filtered_df[filtered_df["ciudad"] == selected_city]

if selected_skill != "Todas":
    filtered_df = filtered_df[
        filtered_df["skills"].astype(str).str.contains(selected_skill, na=False)
    ]

# --------------------------------------------------
# KPIs

avg_salary = int(filtered_df["salario_medio"].mean()) if len(filtered_df) else 0
offers = len(filtered_df)

top_city = filtered_df["ciudad"].mode()[0] if len(filtered_df) else "-"
top_skill = (
    filtered_df["skills"].mode()[0]
    if len(filtered_df)
    else "-"
)

col1, col2, col3 = st.columns(3)

col1.metric("💰 Salario medio", f"{avg_salary:,.0f} €")
col2.metric("📄 Ofertas", offers)
col3.metric("🏙️ Ciudad líder", top_city)

# --------------------------------------------------
# GRÁFICOS

col_left, col_right = st.columns(2)

with col_left:

    skills_count = (
        filtered_df["skills"]
        .dropna()
        .astype(str)
        .str.split(",")
        .explode()
        .str.strip()
        .value_counts()
        .reset_index()
    )

    skills_count.columns = ["Skill", "Count"]

    fig_skills = px.bar(
        skills_count,
        x="Skill",
        y="Count",
        title="Skills más demandadas"
    )

    st.plotly_chart(fig_skills, use_container_width=True)

with col_right:

    salary_city = (
        filtered_df
        .groupby("ciudad")["salario_medio"]
        .mean()
        .reset_index()
    )

    fig_salary = px.bar(
        salary_city,
        x="ciudad",
        y="salario_medio",
        title="Salario medio por ciudad"
    )

    st.plotly_chart(fig_salary, use_container_width=True)

# --------------------------------------------------
# TABLA

st.markdown("### Datos filtrados")

st.dataframe(filtered_df, use_container_width=True)
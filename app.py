import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

st.title("🔎 Painel de Logins")

# Aviso inicial
st.info("Carregue o arquivo CSV de logins para iniciar a análise.")

# Upload
uploaded_file = st.file_uploader("Carregue o arquivo CSV", type=["csv"])

# =========================
# FUNÇÃO DE LEITURA ROBUSTA
# =========================
@st.cache_data
def load_data(file):
    df = pd.read_csv(
        file,
        sep=";",
        encoding="latin1",
        engine="python",
        on_bad_lines="skip"
    )

    # ✅ Normaliza colunas (evita KeyError)
    df.columns = [col.strip().upper() for col in df.columns]

    # ✅ Validação obrigatória
    required_columns = ["DATA", "LOGIN"]

    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise ValueError(
            f"Colunas obrigatórias não encontradas: {missing}. "
            f"Colunas disponíveis: {list(df.columns)}"
        )

    # ✅ Tratamento
    df["DATA"] = pd.to_datetime(df["DATA"], dayfirst=True, errors="coerce")
    df["LOGIN"] = df["LOGIN"].astype(str).fillna("")

    # ✅ Remove inválidos
    df = df.dropna(subset=["DATA"])

    return df


# =========================
# FLUXO PRINCIPAL
# =========================
if uploaded_file is not None:

    st.warning("Linhas inválidas no CSV serão ignoradas automaticamente.")

    try:
        df = load_data(uploaded_file)

        if df.empty:
            st.error("O arquivo não possui dados válidos.")
            st.stop()

    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {e}")
        st.stop()

    # =========================
    # FILTROS
    # =========================

    login_input = st.text_input("Digite o login (ex: vitor.alcantara)")

    min_date = df["DATA"].min().date()
    max_date = df["DATA"].max().date()

    date_range = st.date_input(
        "Selecione o período",
        value=(min_date, max_date)
    )

    if isinstance(date_range, tuple):
        start_date, end_date = date_range
    else:
        start_date = end_date = date_range

    filtered_df = df[
        (df["DATA"].dt.date >= start_date) &
        (df["DATA"].dt.date <= end_date)
    ]

    if login_input:
        filtered_df = filtered_df[
            filtered_df["LOGIN"].str.contains(login_input, case=False, na=False)
        ]

    # =========================
    # RESULTADOS
    # =========================

    st.subheader("📋 Resultados Filtrados")

    display_df = filtered_df.copy()
    display_df["DATA"] = display_df["DATA"].dt.strftime("%d-%m-%Y")

    st.dataframe(display_df, use_container_width=True)

    # =========================
    # ESTATÍSTICAS
    # =========================

    st.subheader("📊 Estatísticas")
    st.write(f"Total de registros filtrados: {len(filtered_df)}")
    st.write(f"Logins distintos: {filtered_df['LOGIN'].nunique()}")

    # =========================
    # GRÁFICO
    # =========================

    st.subheader("📈 Gráfico de Logins por Data")

    if not filtered_df.empty:
        chart_data = (
            filtered_df
            .groupby(filtered_df["DATA"].dt.date)
            .size()
            .reset_index(name="contagem")
            .sort_values("DATA")
            .set_index("DATA")
        )

        st.bar_chart(chart_data)

    else:
        st.info("Nenhum registro para exibir no gráfico.")

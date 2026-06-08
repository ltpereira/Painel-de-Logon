import streamlit as st
import pandas as pd

st.title("🔎 Painel de Logins")

# Carregar CSV
uploaded_file = st.file_uploader("Carregue o arquivo CSV", type=["csv"])

if uploaded_file is not None:
    # Ler CSV
    df = pd.read_csv(
    uploaded_file,
    sep=";",
    encoding="latin1",         # <- mais tolerante que utf-8
    engine="python",           # <- parser mais robusto
    on_bad_lines="skip"        # <- ignora linhas quebradas
)
    
    # Garantir tipos corretos
    df["DATA"] = pd.to_datetime(df["DATA"], dayfirst=True, errors="coerce")
    df["LOGIN"] = df["LOGIN"].astype(str).fillna("")

    # Remover linhas sem DATA
    df = df.dropna(subset=["DATA"])

    # Filtro de login
    login_input = st.text_input("Digite o login (ex: vitor.alcantara)")

    # Filtro de datas
    min_date = df["DATA"].min().date()
    max_date = df["DATA"].max().date()

    start_date, end_date = st.date_input(
        "Selecione o período",
        [min_date, max_date]
    )

    # Aplicar filtros de data
    filtered_df = df[
        (df["DATA"].dt.date >= start_date) &
        (df["DATA"].dt.date <= end_date)
    ]

    # Aplicar filtro de login se preenchido
    if login_input:
        filtered_df = filtered_df[filtered_df["LOGIN"].str.contains(login_input, case=False)]

    # Mostrar resultados
    st.subheader("📋 Resultados Filtrados")
    st.dataframe(filtered_df)

    # Estatísticas simples
    st.subheader("📊 Estatísticas")
    st.write(f"Total de registros filtrados: {len(filtered_df)}")
    st.write("Logins distintos:", filtered_df["LOGIN"].nunique())

    # Gráfico de logins por data
    st.subheader("📈 Gráfico de Logins por Data")
    if not filtered_df.empty:
        chart_data = filtered_df.groupby(filtered_df["DATA"].dt.date).size().reset_index(name='contagem')
        chart_data = chart_data.set_index("DATA")
        st.bar_chart(chart_data)
    else:
        st.write("Nenhum registro para exibir no gráfico.")

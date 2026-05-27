import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from io import StringIO



#_______________________________________________________

st.set_page_config(
    page_title="Indicadores de Arquivo",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# PADRÃO VISUAL COCAL


st.markdown("""
<style>
* {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

body, .main {
    background-color: #f8f9fa;
}

h1 {
    color: #31515f;
    font-weight: 700;
    margin-bottom: 8px;
    letter-spacing: -0.5px;
}

h2, h3 {
    color: #31515f;
    font-weight: 600;
}

.metric-card {
    background: white;
    border-radius: 12px;
    padding: 24px;
    border: 1px solid #e5e7eb;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    transition: all 0.2s ease;
}

.metric-card:hover {
    box-shadow: 0 4px 12px rgba(49, 81, 95, 0.12);
}

.metric-label {
    color: #6b7280;
    font-size: 13px;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 8px;
}

.metric-value {
    color: #31515f;
    font-size: 32px;
    font-weight: 700;
    line-height: 1;
}

.metric-delta {
    color: #10b981;
    font-size: 14px;
    margin-top: 8px;
    font-weight: 500;
}

section[data-testid="stSidebar"] {
    background-color: white;
    border-right: 1px solid #e5e7eb;
}

.stFileUploader > div > div > button {
    background-color: #31515f !important;
    color: white !important;
}

.stFileUploader > div > div > button:hover {
    background-color: #1f3240 !important;
}

.progress-bar {
    background-color: #31515f !important;
}

.dataframe {
    font-size: 13px;
}

div[data-testid="stMetricDelta"] > div {
    color: #31515f !important;
}
</style>
""", unsafe_allow_html=True)


# SIDEBAR - UPLOAD


with st.sidebar:
    st.markdown("### Importar aquivo")

    arquivo = st.file_uploader(
        "Selecione CSV ou Excel",
        type=["csv", "xls", "xlsx"],
        help="Arquivo deve conter coluna 'Total de Itens'"
    )


# FUNÇÃO CARREGAR


def carregar_arquivo(arquivo):
    nome = arquivo.name.lower()

    if nome.endswith(".csv"):
        # Ler como texto primeiro
        arquivo.seek(0)
        conteudo = arquivo.read().decode("latin1")

        # Limpeza do ; extra no final das linhas
        linhas = conteudo.splitlines()
        linhas_limpa = [linha.strip().rstrip(';') for linha in linhas]

        texto_limpo = "\n".join(linhas_limpa)

        df = pd.read_csv(
            StringIO(texto_limpo),      # ← Correção aqui
            sep=";",
            encoding="latin1",
            skiprows=1,
            engine="python",
            on_bad_lines="warn",
            index_col=False
        )

    else:
        df = pd.read_excel(arquivo)

    # Limpeza final
    df = df.loc[:, ~df.columns.str.contains("^Unnamed")]
    df.columns = df.columns.str.strip()
    df = df.reset_index(drop=True)

    # Debug (opcional - pode remover depois)
    st.sidebar.success("Arquivo carregado!")
    st.sidebar.write("**Colunas detectadas:**", df.columns.tolist())

    return df

    # Limpeza final de colunas
    df = df.loc[:, ~df.columns.str.contains("^Unnamed")]
    df.columns = df.columns.str.strip()
    df = df.reset_index(drop=True)

    # Debug: mostrar colunas carregadas
    st.sidebar.write("✅ Colunas carregadas:", df.columns.tolist())

    return df


# CARREGAR DADOS


df = None

if arquivo is not None:
    try:
        df = carregar_arquivo(arquivo)
        st.sidebar.success("Arquivo carregado com sucesso!")
    except Exception as e:
        st.error(f"Erro ao carregar: {str(e)}")


# DADOS PADRÃO


if df is None:
    df = pd.DataFrame({
        "Código": [25, 30, 45, 50, 60, 70, 80, 90],
        "Endereço": ["RUA001", "RUA002", "RUA003", "RUA004", "RUA005", "RUA006", "RUA007", "RUA008"],
        "Total de Itens": [17, 0, 4, 0, 23, 0, 15, 0]
    })


# VALIDAÇÃO E PROCESSAMENTO


if "Total de Itens" not in df.columns:
    st.error("Coluna 'Total de Itens' não encontrada")
    st.write("Colunas disponíveis:", df.columns.tolist())
else:

    df["Total de Itens"] = pd.to_numeric(
        df["Total de Itens"], errors="coerce").fillna(0).astype(int)

    # CÁLCULOS
    total_caixas = len(df)
    caixas_vazias = len(df[df["Total de Itens"] == 0])
    caixas_ocupadas = total_caixas - caixas_vazias
    total_itens = int(df["Total de Itens"].sum())
    pct_ocupadas = (caixas_ocupadas / total_caixas *
                    100) if total_caixas > 0 else 0
    pct_vazias = (caixas_vazias / total_caixas *
                  100) if total_caixas > 0 else 0

    # CABEÇALHO

    col_logo, col_title = st.columns([1, 5])

    with col_logo:
        st.image("https://attachments.gupy.io/production/companies/2298/career/4729/images/2021-06-29_13-13_logo.png", width=80)

    with col_title:
        st.markdown("# Indicadores de arquivo")
        st.markdown("Monitoramento de ocupação de caixas armazenadas")

    st.markdown("---")

    # MÉTRICAS - CARDS

    st.markdown("### Indicadores principais")

    col1, col2, col3 = st.columns(3, gap="medium")

    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total de Caixas</div>
            <div class="metric-value">{total_caixas}</div>
            <div class="metric-delta">Unidades</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Caixas Ocupadas</div>
            <div class="metric-value">{caixas_ocupadas}</div>
            <div class="metric-delta">{pct_ocupadas:.0f}% do total</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Caixas Vazias</div>
            <div class="metric-value">{caixas_vazias}</div>
            <div class="metric-delta">{pct_vazias:.0f}% do total</div>
        </div>
        """, unsafe_allow_html=True)

    # SEGUNDO ROW
    col4, col5 = st.columns(2, gap="medium")

    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total de Itens</div>
            <div class="metric-value">{total_itens}</div>
            <div class="metric-delta">Documentos/Materiais</div>
        </div>
        """, unsafe_allow_html=True)

    with col5:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Ocupação Média</div>
            <div class="metric-value">{pct_ocupadas:.0f}%</div>
            <div class="metric-delta">Taxa geral do arquivo</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # GRÁFICO PIZZA

    st.markdown("### Distribuição de ocupação")

    col_chart, col_stats = st.columns([2, 1], gap="large")

    with col_chart:
        fig_pizza = go.Figure(data=[go.Pie(
            labels=["Ocupadas", "Vazias"],
            values=[caixas_ocupadas, caixas_vazias],
            marker=dict(colors=["#31515f", "#d1d5db"]),
            hovertemplate="<b>%{label}</b><br>Caixas: %{value}<br>%{percent}<extra></extra>",
            textposition="auto",
            textinfo="percent+label"
        )])

        fig_pizza.update_layout(
            height=350,
            margin=dict(l=0, r=0, t=0, b=0),
            font=dict(family="sans-serif", size=12, color="#31515f"),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )

        st.plotly_chart(fig_pizza, use_container_width=True,
                        config={"displayModeBar": False})

    with col_stats:
        media_caixa = (
            total_itens / caixas_ocupadas) if caixas_ocupadas > 0 else 0
        st.markdown(f"""
        #### Resumo
        
        **Situação**
        
        • **Ocupadas:** {caixas_ocupadas} ({pct_ocupadas:.0f}%)
        • **Vazias:** {caixas_vazias} ({pct_vazias:.0f}%)
        
        ---
        
        **Itens**
        
        • **Total:** {total_itens}
        • **Média/Caixa:** {media_caixa:.1f}
        """)

    st.markdown("---")

    # GRÁFICO BARRAS - TOP 10

    st.markdown("### Caixas com maior ocupação")

    df_top = df.nlargest(10, "Total de Itens")

    fig_barras = go.Figure(data=[go.Bar(
        x=df_top["Código"].astype(str),
        y=df_top["Total de Itens"],
        marker=dict(color="#31515f"),
        hovertemplate="<b>Caixa %{x}</b><br>Itens: %{y}<extra></extra>"
    )])

    fig_barras.update_layout(
        height=350,
        xaxis_title="Código da Caixa",
        yaxis_title="Quantidade de Itens",
        margin=dict(l=0, r=0, t=0, b=40),
        font=dict(family="sans-serif", size=11, color="#374151"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridwidth=1, gridcolor="#e5e7eb"),
        showlegend=False
    )

    st.plotly_chart(fig_barras, use_container_width=True,
                    config={"displayModeBar": False})

    st.markdown("---")

    # TABELA DETALHADA

    st.markdown("### Detalhamento completo")

    df_display = df.copy()
    df_display = df_display.sort_values(
        "Total de Itens", ascending=False).reset_index(drop=True)

    st.dataframe(
        df_display,
        use_container_width=True,
        height=500,
        column_config={
            "Código": st.column_config.NumberColumn(format="%d"),
            "Total de Itens": st.column_config.NumberColumn(format="%d")
        }
    )

    # RODAPÉ

    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #31515f; font-size: 12px; margin-top: 20px; ">
    Cocal Indicadores de Arquivo • Última atualização: {0}
    </div>
    """.format(pd.Timestamp.now().strftime("%d/%m/%Y %H:%M")), unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align: center; margin-top: 10px; font-size: 12px;">
    devBy: <a href="https://wa.me/5518997957724" target="_blank" style="color:#31515f; text-decoration:none;">
    Brunuo Pereira - dev235478
    </a>
    </div>
    """, unsafe_allow_html=True)

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from io import StringIO
import re

st.set_page_config(
    page_title="Indicadores de Arquivo",
    layout="wide",
    initial_sidebar_state="collapsed"
)

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
</style>
""", unsafe_allow_html=True)

# MAPEAMENTO DE COLUNAS
COLUMN_ALIASES = {
    'codigo': ['codigo', 'codigo do registro', 'caixa'],
    'caixa': ['caixa', 'codigo', 'codigo do registro'],
    'endereco': ['endereco', 'endereço', 'local', 'localizacao', 'localização'],
    'nome': ['nome', 'descricao', 'descrição', 'titulo', 'título'],
    'total_itens': ['total de itens', 'qtde. de arquivos', 'quantidade de arquivos', 'qtd arquivos', 'qtd. arquivos', 'total', 'quantidade', 'qtde'],
    'data_inicial': ['data inicial', 'data inicio', 'data de inicio', 'data de início', 'data_inicio', 'data_inicial'],
    'data_final': ['data final', 'data fim', 'data de fim', 'data de saida', 'data de saída', 'data_final', 'data_fim']
}

# REFERÊNCIA DE COLUNAS ESPERADAS
COLUNAS_REFERENCIA = set()
for aliases in COLUMN_ALIASES.values():
    COLUNAS_REFERENCIA.update(aliases)

def normalizar_coluna(nome):
    """Converte nome de coluna para padrão lowercase sem acentos."""
    nome = nome.lower().strip()
    nome = re.sub(r'[áàãâä]', 'a', nome)
    nome = re.sub(r'[éèêë]', 'e', nome)
    nome = re.sub(r'[íìîï]', 'i', nome)
    nome = re.sub(r'[óòôõö]', 'o', nome)
    nome = re.sub(r'[úùûü]', 'u', nome)
    nome = re.sub(r'[ç]', 'c', nome)
    return nome

def mapear_coluna(nome_original):
    """Encontra a coluna padrão correspondente a um nome original."""
    nome_norm = normalizar_coluna(nome_original)
    for coluna_padrao, aliases in COLUMN_ALIASES.items():
        for alias in aliases:
            if normalizar_coluna(alias) == nome_norm:
                return coluna_padrao
    return None

def detectar_cabecalho(linhas_raw):
    """Detecta qual linha contém o cabeçalho baseado em heurísticas."""
    melhor_linha = 0
    melhor_score = -1
    
    for idx, linha in enumerate(linhas_raw[:50]):
        if isinstance(linha, str):
            partes = [p.strip() for p in linha.split(';')]
        else:
            continue
        
        partes = [p for p in partes if p]
        if len(partes) < 2:
            continue
        
        score = 0
        for parte in partes:
            parte_norm = normalizar_coluna(parte)
            if parte_norm in COLUNAS_REFERENCIA:
                score += 2
            if len(parte) > 3 and not parte.isdigit():
                score += 1
        
        if score > melhor_score:
            melhor_score = score
            melhor_linha = idx
    
    return melhor_linha

def processar_arquivo_csv(arquivo):
    """Processa arquivo CSV com detecção automática de cabeçalho."""
    arquivo.seek(0)
    conteudo = arquivo.read().decode('latin1', errors='replace')
    linhas = conteudo.splitlines()
    linhas_limpa = [linha.strip().rstrip(';') for linha in linhas if linha.strip()]
    
    if not linhas_limpa:
        return None
    
    idx_cabecalho = detectar_cabecalho(linhas_limpa)
    
    linhas_para_df = linhas_limpa[idx_cabecalho:]
    texto_limpo = "\n".join(linhas_para_df)
    
    df = pd.read_csv(
        StringIO(texto_limpo),
        sep=';',
        encoding='latin1',
        engine='python',
        on_bad_lines='warn',
        index_col=False
    )
    
    return df

def processar_arquivo_excel(arquivo):
    """Processa arquivo Excel."""
    df = pd.read_excel(arquivo, header=None)
    
    melhor_linha = detectar_cabecalho_excel(df)
    
    if melhor_linha > 0:
        df = df.iloc[melhor_linha:].reset_index(drop=True)
    
    df.columns = df.iloc[0]
    df = df.iloc[1:].reset_index(drop=True)
    
    return df

def detectar_cabecalho_excel(df):
    """Detecta cabeçalho em arquivo Excel."""
    melhor_linha = 0
    melhor_score = -1
    
    for idx in range(min(20, len(df))):
        linha = df.iloc[idx]
        linha_str = [str(v).strip() for v in linha if pd.notna(v)]
        
        if len(linha_str) < 2:
            continue
        
        score = 0
        for valor in linha_str:
            valor_norm = normalizar_coluna(valor)
            if valor_norm in COLUNAS_REFERENCIA:
                score += 2
            if len(valor) > 3 and not valor.isdigit():
                score += 1
        
        if score > melhor_score:
            melhor_score = score
            melhor_linha = idx
    
    return melhor_linha

def limpar_dataframe(df):
    """Remove linhas vazias, linhas de lixo e normaliza colunas."""
    df = df.loc[:, ~df.columns.str.contains('^Unnamed', na=False)].copy()
    df.columns = df.columns.str.strip()
    df = df.dropna(how='all').reset_index(drop=True)
    
    mask = df.astype(str).apply(lambda x: x.str.len().sum(), axis=1) > 0
    df = df[mask].reset_index(drop=True)
    
    df_limpo = pd.DataFrame()
    for col in df.columns:
        mapeamento = mapear_coluna(col)
        if mapeamento:
            df_limpo[mapeamento] = df[col].values
    
    return df_limpo

def criar_dataframe_padrao(colunas_presentes):
    """Garante que o DataFrame contém as colunas mínimas."""
    colunas_minimas = ['codigo', 'caixa', 'endereco', 'nome', 'total_itens', 'data_inicial', 'data_final']
    
    for col in colunas_minimas:
        if col not in colunas_presentes.columns:
            colunas_presentes[col] = None
    
    return colunas_presentes

def carregar_arquivo(arquivo):
    """Carrega e processa arquivo com detecção automática."""
    nome = arquivo.name.lower()
    
    try:
        if nome.endswith('.csv'):
            df = processar_arquivo_csv(arquivo)
        else:
            df = processar_arquivo_excel(arquivo)
        
        if df is None or df.empty:
            st.error("Arquivo vazio ou inválido")
            return None
        
        df = limpar_dataframe(df)
        df = criar_dataframe_padrao(df)
        
        st.sidebar.success("Arquivo carregado com sucesso!")
        st.sidebar.write("Colunas detectadas:", [c for c in df.columns if df[c].notna().any()])
        
        return df
    
    except Exception as e:
        st.error(f"Erro ao carregar arquivo: {str(e)}")
        return None

# SIDEBAR
with st.sidebar:
    st.markdown("### Importar arquivo")
    arquivo = st.file_uploader(
        "Selecione CSV ou Excel",
        type=['csv', 'xls', 'xlsx'],
        help="Arquivo pode ter cabeçalho em qualquer posição"
    )

# CARREGAMENTO
df = None

if arquivo is not None:
    df = carregar_arquivo(arquivo)

if df is None:
    df = pd.DataFrame({
        'codigo': [0, 1, 25, 60],
        'endereco': ['60 RUA005', '25 RUA001', '30 RUA002', '45 RUA003'],
        'total_itens': [23, 17, 0, 4]
    })

# PROCESSAMENTO
if 'total_itens' not in df.columns:
    df['total_itens'] = 0

df['total_itens'] = pd.to_numeric(df['total_itens'], errors='coerce').fillna(0).astype(int)

total_caixas = len(df)
caixas_vazias = len(df[df['total_itens'] == 0])
caixas_ocupadas = total_caixas - caixas_vazias
total_itens = int(df['total_itens'].sum())
pct_ocupadas = (caixas_ocupadas / total_caixas * 100) if total_caixas > 0 else 0
pct_vazias = (caixas_vazias / total_caixas * 100) if total_caixas > 0 else 0

# CABEÇALHO
col_logo, col_title = st.columns([1, 5])
with col_logo:
    st.image("https://attachments.gupy.io/production/companies/2298/career/4729/images/2021-06-29_13-13_logo.png", width=80)

with col_title:
    st.markdown("# Indicadores de Arquivo")
    st.markdown("Monitoramento de ocupacao de caixas armazenadas")

st.markdown("---")

# MÉTRICAS
st.markdown("### Indicadores principais")
col1, col2, col3 = st.columns(3, gap='medium')

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Total de Caixas</div>
        <div class="metric-value">{total_caixas}</div>
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

col4, col5 = st.columns(2, gap='medium')
with col4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Total de Itens</div>
        <div class="metric-value">{total_itens}</div>
    </div>
    """, unsafe_allow_html=True)

with col5:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Ocupacao Media</div>
        <div class="metric-value">{pct_ocupadas:.0f}%</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# GRÁFICOS
st.markdown("### Distribuição de ocupação")
col_chart, col_stats = st.columns([2, 1], gap='large')

with col_chart:
    fig_pizza = go.Figure(data=[go.Pie(
        labels=['Ocupadas', 'Vazias'],
        values=[caixas_ocupadas, caixas_vazias],
        marker=dict(colors=['#31515f', '#d1d5db']),
        textinfo='percent+label'
    )])
    fig_pizza.update_layout(height=350, margin=dict(l=0,r=0,t=0,b=0))
    st.plotly_chart(fig_pizza, use_container_width=True, config={'displayModeBar': False})

with col_stats:
    media_caixa = total_itens / caixas_ocupadas if caixas_ocupadas > 0 else 0
    st.markdown(f"""
    #### Resumo
    **Situação**
    - **Ocupadas:** {caixas_ocupadas} ({pct_ocupadas:.0f}%)
    - **Vazias:** {caixas_vazias} ({pct_vazias:.0f}%)

    **Itens**
    - **Total:** {total_itens}
    - **Media/Caixa:** {media_caixa:.1f}
    """)

st.markdown("---")

st.markdown("### Caixas com maior ocupação")
df_top = df.nlargest(10, 'total_itens')
fig_barras = go.Figure(data=[go.Bar(
    x=df_top['codigo'].astype(str) if 'codigo' in df_top.columns else range(len(df_top)),
    y=df_top['total_itens'],
    marker=dict(color='#31515f')
)])
fig_barras.update_layout(height=350, xaxis_title='Codigo da Caixa', yaxis_title='Quantidade de Itens')
st.plotly_chart(fig_barras, use_container_width=True, config={'displayModeBar': False})

st.markdown("---")

# TABELA COM FILTRO
st.markdown("### Detalhamento completo")

busca = st.text_input(
    "Buscar por Código, Endereço ou quantidade",
    placeholder="Ex: RUA006, 19, 83...",
    help="Digite qualquer informação para filtrar"
)

df_display = df.copy()

if busca:
    busca = busca.lower()
    mask = pd.Series([False] * len(df_display), index=df_display.index)
    for col in ['codigo', 'endereco', 'total_itens']:
        if col in df_display.columns:
            mask = mask | (df_display[col].astype(str).str.lower().str.contains(busca, na=False))
    df_display = df_display[mask].reset_index(drop=True)

df_display = df_display.sort_values('total_itens', ascending=False).reset_index(drop=True)

st.dataframe(
    df_display,
    use_container_width=True,
    height=500,
    column_config={col: st.column_config.NumberColumn(format='%d') for col in ['codigo', 'total_itens'] if col in df_display.columns}
)

# RODAPÉ
st.markdown("---")
st.markdown(f"""
<div style="text-align: center; color: #31515f; font-size: 12px; margin-top: 20px;">
Cocal Indicadores de Arquivo | Atualizacao: {pd.Timestamp.now().strftime('%d/%m/%Y %H:%M')}
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="text-align: center; margin-top: 10px; font-size: 12px;">
devBy: <a href="https://wa.me/5518997957724" target="_blank" style="color:#31515f; text-decoration:none;">Bruno Pereira - dev235478</a>
</div>
""", unsafe_allow_html=True)

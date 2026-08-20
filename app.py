# -*- coding: utf-8 -*-
"""
Dashboard de Fracionamento — LCM Construção
Monitoramento de processos individuais abaixo do teto que, somados por
fornecedor no período, ultrapassam o limite financeiro.

Execução:
    streamlit run app.py
Modo demonstração (sem banco, dados sintéticos):
    DASH_DEMO=1 streamlit run app.py
"""

import os
import random
from contextlib import contextmanager
from datetime import date, timedelta

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from query import SQL_FRACIONAMENTO

MODO_DEMO = os.getenv("DASH_DEMO", "0") == "1"

# Valores fixos que antes estavam no menu de limites
TETO_PARCELA = 100_000.0
TETO_FORNECEDOR = 100_000.0

# -----------------------------------------------------------------------------
# 1. Configuração da página + design system
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Monitoramento de Processos | LCM",
    page_icon="🟢",
    layout="wide",
    initial_sidebar_state="collapsed",
)

VERDE = "#12A150"
VERDE_ESC = "#0B6B36"
VERDE_CLARO = "#E4F5EA"
TINTA = "#132A1E"
MUTED = "#7A8B81"
BORDA = "#E6EDE8"
ALERTA = "#D9534F"

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"], .stApp { font-family: 'Inter', -apple-system, sans-serif; }
#MainMenu, footer, header {visibility: hidden;}
.stApp { background: #F4F7F5; }
.block-container { padding-top: 1.6rem; padding-bottom: 4rem; max-width: 1500px; }

/* ---------- Cartões (containers nativos com key card_*) ---------- */
div[class*="st-key-card_"] {
    background:#FFFFFF !important; border:1px solid #E6EDE8 !important; border-radius:22px !important;
    padding: 18px 20px 10px 20px !important;
    box-shadow: 0 1px 2px rgba(16,40,28,.04), 0 12px 30px -18px rgba(16,40,28,.18);
}
div[class*="st-key-card_"] p.card-title { margin-bottom:0; }

/* ---------- Cartões estáticos (HTML puro) ---------- */
.card {
    background: #FFFFFF; border: 1px solid #E6EDE8; border-radius: 22px;
    padding: 20px 22px; box-shadow: 0 1px 2px rgba(16,40,28,.04), 0 12px 30px -18px rgba(16,40,28,.18);
    margin-bottom: 6px;
}
.card-title { font-size: .82rem; font-weight: 600; color: #7A8B81; letter-spacing:.02em; margin:0 0 2px 0; }
.card-sub { font-size: .72rem; color: #A6B4AC; margin: 0 0 14px 0; }
.kpi-value { font-size: 1.9rem; font-weight: 800; color: #132A1E; letter-spacing: -.02em; line-height: 1.15; }
.kpi-foot { font-size: .74rem; color: #7A8B81; margin-top: 6px; }

/* Cartão destaque (verde) */
.card-hero {
    background: linear-gradient(150deg, #10A251 0%, #0B7C3D 55%, #095F2F 100%);
    border: none; color: #fff;
    box-shadow: 0 18px 40px -22px rgba(9,95,47,.85);
}
.card-hero .card-title, .card-hero .card-sub { color: rgba(255,255,255,.72); }
.card-hero .kpi-value { color: #fff; font-size: 2.1rem; }
.card-hero .kpi-foot { color: rgba(255,255,255,.78); }

/* Pílulas */
.pill { display:inline-block; padding: 5px 12px; border-radius: 999px; font-size:.72rem; font-weight:600;
        background:#E4F5EA; color:#0B6B36; border:1px solid #CFEBDA; }
.pill-warn { background:#FDEBEA; color:#B23B37; border-color:#F6D5D3; }
.pill-ghost { background:#FFFFFF; color:#7A8B81; border:1px solid #E6EDE8; }

/* Styling customizado para o Popover parecer uma pílula */
div[data-testid="stPopover"] > button {
    background: #E4F5EA !important;
    color: #0B6B36 !important;
    border: 1px solid #CFEBDA !important;
    border-radius: 999px !important;
    font-size: .75rem !important;
    font-weight: 600 !important;
    padding: 2px 14px !important;
    min-height: 30px !important;
    height: auto !important;
}
div[data-testid="stPopover"] > button:hover {
    background: #D1EEDB !important;
    border-color: #BBE2CA !important;
    color: #0B6B36 !important;
}

/* Cabeçalho */
.hero-title { font-size: 1.75rem; font-weight: 800; color:#132A1E; letter-spacing:-.03em; margin:0; }
.hero-sub { color:#7A8B81; font-size:.9rem; margin: 4px 0 0 0; }

/* Métricas nativas dentro dos cartões */
[data-testid="stMetricValue"] { font-size: 1.55rem; font-weight: 700; color:#132A1E; }
[data-testid="stMetricLabel"] p { font-size: .78rem !important; color:#7A8B81 !important; font-weight:600; }

/* Tabelas */
[data-testid="stDataFrame"] { border-radius: 16px; overflow: hidden; border:1px solid #E6EDE8; }

/* Botões */
.stButton > button {
    border-radius: 12px; border:1px solid #E6EDE8; background:#fff; color:#132A1E;
    font-weight:600; font-size:.82rem; padding:.45rem .9rem; transition: all .15s ease;
}
.stButton > button:hover { border-color:#12A150; color:#0B6B36; background:#F3FBF6; }
.stButton > button p { white-space: nowrap; }
.stButton > button[kind="primary"] { background:#12A150; border-color:#12A150; color:#fff; }
.stButton > button[kind="primary"]:hover { background:#0B7C3D; color:#fff; }
.stDownloadButton > button { border-radius:12px; font-weight:600; }

/* Esconder sidebar caso o usuário tente abrir */
[data-testid="collapsedControl"] { display: none; }

/* Expanders */
[data-testid="stExpander"] { border:1px solid #E6EDE8 !important; border-radius:16px !important; background:#fff; }

/* Divisores */
hr { border-color:#E6EDE8; opacity:1; margin: 1.6rem 0; }

</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# 2. Utilidades
# -----------------------------------------------------------------------------
def brl(v, casas=2):
    try:
        s = f"{float(v):,.{casas}f}"
    except (TypeError, ValueError):
        return "R$ 0,00"
    return "R$ " + s.replace(",", "X").replace(".", ",").replace("X", ".")


def compacto(v):
    v = float(v or 0)
    for lim, suf in ((1_000_000_000, "bi"), (1_000_000, "mi"), (1_000, "mil")):
        if abs(v) >= lim:
            return f"R$ {v/lim:,.1f} {suf}".replace(".", ",")
    return brl(v, 0)


_CARD_SEQ = {"n": 0}


@contextmanager
def card(titulo=None, sub=None):
    _CARD_SEQ["n"] += 1
    with st.container(border=True, key=f"card_{_CARD_SEQ['n']}"):
        if titulo:
            st.markdown(
                f'<p class="card-title">{titulo}</p>'
                + (f'<p class="card-sub">{sub}</p>' if sub else '<div style="height:8px"></div>'),
                unsafe_allow_html=True,
            )
        yield


def kpi(titulo, valor, rodape="", hero=False):
    st.markdown(
        f"""<div class="card {'card-hero' if hero else ''}">
              <p class="card-title">{titulo}</p>
              <div class="kpi-value">{valor}</div>
              <div class="kpi-foot">{rodape}</div>
            </div>""",
        unsafe_allow_html=True,
    )


LAYOUT_BASE = dict(
    template="plotly_white",
    font=dict(family="Inter, sans-serif", size=12, color=TINTA),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=0, r=6, t=10, b=0),
    hoverlabel=dict(bgcolor="white", bordercolor=BORDA, font_size=12),
)


# -----------------------------------------------------------------------------
# 3. Dados
# -----------------------------------------------------------------------------
def _conn_str():
    cfg = st.secrets.get("banco", {}) if hasattr(st, "secrets") else {}
    return (
        "DRIVER={ODBC Driver 17 for SQL Server};"
        f"SERVER={cfg.get('server', os.getenv('DB_SERVER', '34.95.193.32'))};"
        f"DATABASE={cfg.get('database', os.getenv('DB_NAME', 'UAU'))};"
        f"UID={cfg.get('user', os.getenv('DB_USER', ''))};"
        f"PWD={cfg.get('password', os.getenv('DB_PASS', ''))};"
        "TrustServerCertificate=yes;"
    )


@st.cache_data(ttl=600, show_spinner="Analisando processos...")
def carregar_dados(dt_inicio, dt_fim, teto_parcela, teto_fornecedor):
    if MODO_DEMO:
        return _dados_demo(dt_inicio, dt_fim, teto_fornecedor)

    import pyodbc
    ini = dt_inicio.strftime("%Y%m%d")
    fim = dt_fim.strftime("%Y%m%d")
    with pyodbc.connect(_conn_str()) as conn:
        df = pd.read_sql(
            SQL_FRACIONAMENTO,
            conn,
            params=[ini, fim, ini, fim, float(teto_parcela), float(teto_fornecedor)],
        )
    return df


def _dados_demo(dt_inicio, dt_fim, teto_fornecedor):
    random.seed(7)
    fornecedores = [
        ("CONSTRUMAX MATERIAIS LTDA", "12.345.678/0001-90"),
        ("ALFA LOCACAO DE EQUIPAMENTOS", "98.765.432/0001-11"),
        ("SERVICOS ELETRICOS BETA ME", "45.678.912/0001-33"),
        ("TRANSPORTES GAMA EIRELI", "23.456.789/0001-55"),
        ("DELTA ENGENHARIA E MONTAGENS", "34.567.891/0001-77"),
        ("EPSILON ACABAMENTOS LTDA", "56.789.123/0001-22"),
    ]
    obras = ["RESIDENCIAL AURORA", "TORRE NORTE", "CENTRO LOGISTICO SUL", "VIADUTO LESTE"]
    empresas = ["LCM CONSTRUCAO S.A.", "LCM INFRAESTRUTURA LTDA"]
    dias = max((dt_fim - dt_inicio).days, 1)

    linhas = []
    for i, (nome, cnpj) in enumerate(fornecedores):
        n_proc = random.randint(3, 7)
        for p in range(n_proc):
            num_proc = 40000 + i * 137 + p
            obra = random.choice(obras)
            emp = random.choice(empresas)
            for parc in range(1, random.randint(2, 5)):
                valor = round(random.uniform(8_000, 89_000), 2)
                linhas.append(
                    {
                        "NomeFornecedor": nome,
                        "CnpjCpf": cnpj,
                        "CodForn_Proc": 1000 + i,
                        "Num_Proc": num_proc,
                        "NumParc_Proc": parc,
                        "Descr_obr": obra,
                        "Desc_emp": emp,
                        "NomeBanco": random.choice(["ITAU", "BRADESCO", "SANTANDER", "BB"]),
                        "Aprovado": random.choice(["1-Sim", "1-Sim", "0-Nao"]),
                        "DtPagParc_Proc": pd.Timestamp(dt_inicio) + pd.Timedelta(days=random.randint(0, dias)),
                        "Data_Proc": pd.Timestamp(dt_inicio) + pd.Timedelta(days=random.randint(0, dias)),
                        "ValorParc_Proc": valor,
                        "ValPagar": valor,
                        "Historico_Proc": f"MEDICAO {parc} - {obra}",
                    }
                )
    df = pd.DataFrame(linhas)
    df["ValorTotalFornecedor"] = df.groupby("CodForn_Proc")["ValPagar"].transform("sum")
    return df[df["ValorTotalFornecedor"] > teto_fornecedor].reset_index(drop=True)


# -----------------------------------------------------------------------------
# 4. Estado da Sessão & Filtros
# -----------------------------------------------------------------------------
hoje = date.today()
PRESETS = {"7d": 7, "30d": 30, "90d": 90, "12m": 365}

if "dt_ini" not in st.session_state:
    st.session_state.dt_ini = hoje - timedelta(days=30)
    st.session_state.dt_fim = hoje
if "busca" not in st.session_state:
    st.session_state.busca = ""
if "ordenar" not in st.session_state:
    st.session_state.ordenar = "Valor acumulado"
if "top_n" not in st.session_state:
    st.session_state.top_n = 10


# -----------------------------------------------------------------------------
# 5. Cabeçalho & Popover de Ajustes
# -----------------------------------------------------------------------------
h1, h2, h3 = st.columns([3.5, 1, 1.2])

with h1:
    st.markdown(
        '<p class="hero-title">Dashboard de Fracionamento</p>'
        '<p class="hero-sub">Processos abaixo do teto que, somados por fornecedor, ultrapassam o limite financeiro.</p>',
        unsafe_allow_html=True,
    )

with h2:
    st.write("")
    rotulo_data = f"📅 {st.session_state.dt_ini.strftime('%d/%m/%Y')} — {st.session_state.dt_fim.strftime('%d/%m/%Y')}"
    
    with st.popover(rotulo_data, use_container_width=True):
        st.markdown("**Período de vencimento**")
        cols = st.columns(4)
        for c, (rot, dias) in zip(cols, PRESETS.items()):
            if c.button(rot, use_container_width=True, key=f"preset_{dias}"):
                st.session_state.dt_ini = hoje - timedelta(days=dias)
                st.session_state.dt_fim = hoje
                st.rerun()

        c1, c2 = st.columns(2)
        st.session_state.dt_ini = c1.date_input("Início", st.session_state.dt_ini, format="DD/MM/YYYY")
        st.session_state.dt_fim = c2.date_input("Fim", st.session_state.dt_fim, format="DD/MM/YYYY")

        st.divider()
        st.session_state.busca = st.text_input("Buscar fornecedor", value=st.session_state.busca, placeholder="nome ou CNPJ")
        
        idx_ordenar = ["Valor acumulado", "Nº de parcelas", "Nº de processos"].index(st.session_state.ordenar)
        st.session_state.ordenar = st.selectbox("Ordenar ranking por", ["Valor acumulado", "Nº de parcelas", "Nº de processos"], index=idx_ordenar)
        st.session_state.top_n = st.slider("Fornecedores no gráfico", 5, 30, st.session_state.top_n)

        st.divider()
        if st.button("Aplicar Filtros", use_container_width=True, type="primary"):
            st.cache_data.clear()
            st.rerun()

with h3:
    st.write("")
    st.markdown(
        f'<div style="text-align:left;padding-top:4px;">'
        f'<span class="pill pill-ghost">Teto {compacto(TETO_FORNECEDOR)}</span></div>',
        unsafe_allow_html=True,
    )

st.write("")

# Recuperando valores do estado localmente para o uso no resto do script
data_inicio = st.session_state.dt_ini
data_termino = st.session_state.dt_fim
busca = st.session_state.busca
ordenar = st.session_state.ordenar
top_n = st.session_state.top_n


if data_inicio > data_termino:
    st.error("A data inicial não pode ser maior que a data final.")
    st.stop()

try:
    df = carregar_dados(data_inicio, data_termino, TETO_PARCELA, TETO_FORNECEDOR)
except Exception as exc: 
    st.error(f"Não foi possível conectar ao banco de dados: {exc}")
    st.stop()

if df.empty:
    st.info("Nenhum registro encontrado para os filtros selecionados.", icon="🔍")
    st.stop()

# Normalizações defensivas
df = df.copy()
df["ValPagar"] = pd.to_numeric(df.get("ValPagar", df.get("ValorParc_Proc")), errors="coerce").fillna(0)
df["DtPagParc_Proc"] = pd.to_datetime(df["DtPagParc_Proc"], errors="coerce")
df["NomeFornecedor"] = df["NomeFornecedor"].fillna("(sem fornecedor)").str.strip()
if "CnpjCpf" not in df:
    df["CnpjCpf"] = ""

if busca:
    alvo = busca.strip().lower()
    mask = df["NomeFornecedor"].str.lower().str.contains(alvo) | df["CnpjCpf"].astype(str).str.lower().str.contains(alvo)
    df = df[mask]
    if df.empty:
        st.info(f"Nenhum fornecedor encontrado para “{busca}”.", icon="🔍")
        st.stop()

# -----------------------------------------------------------------------------
# 6. Agregações
# -----------------------------------------------------------------------------
resumo = (
    df.groupby(["NomeFornecedor", "CnpjCpf"], dropna=False)
    .agg(
        ValorTotal=("ValPagar", "sum"),
        Parcelas=("ValPagar", "size"),
        Processos=("Num_Proc", "nunique"),
        MaiorParcela=("ValPagar", "max"),
        Ultimo=("DtPagParc_Proc", "max"),
    )
    .reset_index()
)
resumo["TicketMedio"] = resumo["ValorTotal"] / resumo["Parcelas"]
resumo["Excedente"] = resumo["ValorTotal"] - TETO_FORNECEDOR
chave_ord = {"Valor acumulado": "ValorTotal", "Nº de parcelas": "Parcelas", "Nº de processos": "Processos"}[ordenar]
resumo = resumo.sort_values(chave_ord, ascending=False).reset_index(drop=True)

total_geral = float(df["ValPagar"].sum())
top1 = resumo.iloc[0]
concentracao = top1["ValorTotal"] / total_geral * 100 if total_geral else 0

# -----------------------------------------------------------------------------
# 7. KPIs
# -----------------------------------------------------------------------------
k1, k2, k3, k4 = st.columns([1.25, 1, 1, 1])
with k1:
    kpi(
        "Volume financeiro exposto",
        brl(total_geral),
        f"{len(df)} parcelas · {df['Num_Proc'].nunique()} processos",
        hero=True,
    )
with k2:
    kpi("Fornecedores sinalizados", f"{len(resumo)}", f"acima de {compacto(TETO_FORNECEDOR)} no período")
with k3:
    kpi("Ticket médio por parcela", brl(df["ValPagar"].mean()), f"maior parcela: {brl(df['ValPagar'].max())}")
with k4:
    kpi(
        "Maior concentração",
        f"{concentracao:.1f}%",
        f"{top1['NomeFornecedor'][:26]}",
    )

st.write("")

# -----------------------------------------------------------------------------
# 8. Seleção de fornecedor (clique no ranking ou no gráfico)
# -----------------------------------------------------------------------------
if "forn_sel" not in st.session_state:
    st.session_state.forn_sel = None


def _nome_do_ponto(pt, base):
    cd = pt.get("customdata")
    if isinstance(cd, (list, tuple)):
        return cd[0] if cd else None
    if cd:
        return cd
    rotulo = pt.get("y")
    for nome in base["NomeFornecedor"]:
        if str(nome).startswith(str(rotulo)):
            return nome
    return None


def _registrar(candidato, slot):
    if st.session_state.get(slot) != candidato:
        st.session_state[slot] = candidato
        if candidato:
            st.session_state.forn_sel = candidato


c_esq, c_dir = st.columns([1.25, 1])

with c_esq, card("Ranking de fornecedores", "Clique em uma linha para abrir os processos detalhados."):
    tabela = resumo.assign(Fornecedor=resumo["NomeFornecedor"])[
        ["Fornecedor", "ValorTotal", "Processos", "Parcelas"]
    ]
    evento_tab = st.dataframe(
        tabela,
        use_container_width=True,
        hide_index=True,
        height=min(60 + 35 * len(tabela), 420),
        on_select="rerun",
        selection_mode="single-row",
        key="tab_rank",
        column_config={
            "Fornecedor": st.column_config.TextColumn("Fornecedor", width="medium"),
            "ValorTotal": st.column_config.ProgressColumn(
                "Acumulado no período",
                format="localized",
                width="medium",
                min_value=0,
                max_value=float(resumo["ValorTotal"].max()),
            ),
            "Processos": st.column_config.NumberColumn("Proc.", width="small", help="Processos distintos"),
            "Parcelas": st.column_config.NumberColumn("Parc.", width="small", help="Parcelas no período"),
        },
    )
    linhas_sel = evento_tab.selection.rows if evento_tab and evento_tab.selection else []
    _registrar(resumo.iloc[linhas_sel[0]]["NomeFornecedor"] if linhas_sel else None, "_prev_tab")

with c_dir, card("Exposição por fornecedor", f"Top {top_n} · clique na barra para detalhar"):
    top = resumo.head(top_n).sort_values("ValorTotal")
    sel_atual = st.session_state.forn_sel
    cores = [VERDE if (sel_atual is None or n == sel_atual) else "#CBE7D6" for n in top["NomeFornecedor"]]
    fig = go.Figure(
        go.Bar(
            x=top["ValorTotal"],
            y=[n[:28] for n in top["NomeFornecedor"]],
            customdata=top["NomeFornecedor"],
            orientation="h",
            marker=dict(color=cores, line=dict(width=0)),
            text=[compacto(v) for v in top["ValorTotal"]],
            textposition="outside",
            textfont=dict(size=11, color=MUTED),
            hovertemplate="<b>%{customdata}</b><br>%{x:,.2f}<extra></extra>",
        )
    )
    fig.add_vline(x=TETO_FORNECEDOR, line_dash="dot", line_color=ALERTA, line_width=1.5)
    fig.update_layout(
        **LAYOUT_BASE,
        height=max(260, 34 * len(top) + 60),
        bargap=0.42,
        xaxis=dict(visible=False, range=[0, float(top["ValorTotal"].max()) * 1.38]),
        yaxis=dict(showgrid=False, ticksuffix="  ", tickfont=dict(size=11, color=TINTA)),
        showlegend=False,
    )
    evento_bar = st.plotly_chart(
        fig, use_container_width=True, on_select="rerun", key="graf_rank",
        config={"displayModeBar": False},
    )
    pontos = evento_bar.selection.points if evento_bar and evento_bar.selection else []
    _registrar(_nome_do_ponto(pontos[0], top) if pontos else None, "_prev_bar")


# -----------------------------------------------------------------------------
# 10. Drill-down do fornecedor selecionado
# -----------------------------------------------------------------------------
st.write("")
sel = st.session_state.forn_sel

if not sel:
    st.markdown(
        '<div class="card" style="text-align:center;padding:38px 22px;">'
        '<div style="font-size:1.6rem;">👆</div>'
        '<div style="font-weight:700;color:#132A1E;margin-top:6px;">Selecione um fornecedor</div>'
        '<div style="color:#7A8B81;font-size:.85rem;margin-top:4px;">'
        'Clique em uma linha do ranking ou em uma barra do gráfico para ver os processos detalhados.</div></div>',
        unsafe_allow_html=True,
    )
    st.stop()

det = df[df["NomeFornecedor"] == sel].sort_values(["DtPagParc_Proc", "Num_Proc"])
info = resumo[resumo["NomeFornecedor"] == sel].iloc[0]

th1, th2 = st.columns([4, 1])
with th1:
    st.markdown(
        f'<div style="display:flex;align-items:center;gap:14px;">'
        f'<div style="width:46px;height:46px;border-radius:14px;background:{VERDE_CLARO};color:{VERDE_ESC};'
        f'display:flex;align-items:center;justify-content:center;font-weight:800;font-size:1.05rem;">'
        f'{sel[:2].upper()}</div>'
        f'<div><div style="font-size:1.25rem;font-weight:800;color:#132A1E;letter-spacing:-.02em;">{sel}</div>'
        f'<div style="color:#7A8B81;font-size:.82rem;">CNPJ/CPF {info["CnpjCpf"] or "—"} · '
        f'{int(info["Processos"])} processos · {int(info["Parcelas"])} parcelas</div></div></div>',
        unsafe_allow_html=True,
    )
with th2:
    st.write("")
    if st.button("Limpar seleção", use_container_width=True):
        for k in ("tab_rank", "graf_rank", "_prev_tab", "_prev_bar"):
            st.session_state.pop(k, None)
        st.session_state.forn_sel = None
        st.rerun()

st.write("")
d1, d2, d3, d4 = st.columns(4)
with d1:
    kpi("Acumulado no período", brl(info["ValorTotal"]), f"{info['ValorTotal']/TETO_FORNECEDOR*100:.0f}% do teto")
with d2:
    kpi("Excedente ao teto", brl(info["Excedente"]), "valor acima do limite")
with d3:
    kpi("Ticket médio", brl(info["TicketMedio"]), f"maior parcela: {brl(info['MaiorParcela'])}")
with d4:
    dias_span = (det["DtPagParc_Proc"].max() - det["DtPagParc_Proc"].min()).days + 1
    kpi("Janela de vencimentos", f"{dias_span} dias", f"até {info['Ultimo']:%d/%m/%Y}" if pd.notna(info["Ultimo"]) else "")

st.write("")
g1, g2 = st.columns([1.4, 1])

with g1, card("Acumulado no tempo × teto", "Momento em que a soma das parcelas ultrapassa o limite"):
    acum = det[["DtPagParc_Proc", "ValPagar", "Num_Proc"]].copy()
    acum["Acumulado"] = acum["ValPagar"].cumsum()
    fig_ac = go.Figure()
    fig_ac.add_trace(
        go.Bar(
            x=acum["DtPagParc_Proc"], y=acum["ValPagar"],
            marker_color="#BFE7CE", name="Parcela",
            hovertemplate="%{x|%d/%m/%Y}<br>Parcela: R$ %{y:,.2f}<extra></extra>",
        )
    )
    fig_ac.add_trace(
        go.Scatter(
            x=acum["DtPagParc_Proc"], y=acum["Acumulado"], mode="lines+markers",
            line=dict(color=VERDE_ESC, width=2.5), marker=dict(size=5), name="Acumulado",
            hovertemplate="%{x|%d/%m/%Y}<br>Acumulado: R$ %{y:,.2f}<extra></extra>",
        )
    )
    fig_ac.add_hline(
        y=TETO_FORNECEDOR, line_dash="dot", line_color=ALERTA,
        annotation_text=f"teto {compacto(TETO_FORNECEDOR)}", annotation_position="top left",
        annotation_font_color=ALERTA, annotation_font_size=11,
    )
    fig_ac.update_layout(
        **LAYOUT_BASE, height=300,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, font=dict(size=11)),
        xaxis=dict(showgrid=False, tickfont=dict(color=MUTED, size=11), tickformat="%d/%m"),
        yaxis=dict(gridcolor="#EEF3F0", zeroline=False, tickfont=dict(color=MUTED, size=11), tickprefix="R$ "),
        barmode="overlay",
    )
    st.plotly_chart(fig_ac, use_container_width=True, config={"displayModeBar": False})

with g2, card("Distribuição por obra", "Onde o valor está sendo lançado"):
    col_obra = "Descr_obr" if "Descr_obr" in det else "Num_Proc"
    por_obra = det.groupby(col_obra)["ValPagar"].sum().sort_values(ascending=False).head(6)
    paleta = ["#0B6B36", "#12A150", "#3FBE71", "#7AD79B", "#A9E6C1", "#D6F2E0"]
    fig_donut = go.Figure(
        go.Pie(
            labels=[str(i)[:26] for i in por_obra.index],
            values=por_obra.values,
            hole=0.66,
            marker=dict(colors=paleta[: len(por_obra)], line=dict(color="#fff", width=2)),
            textinfo="percent",
            textfont=dict(size=11, color="#fff"),
            hovertemplate="<b>%{label}</b><br>R$ %{value:,.2f}<extra></extra>",
        )
    )
    fig_donut.update_layout(
        **{**LAYOUT_BASE, "margin": dict(l=0, r=0, t=6, b=70)},
        height=310,
        showlegend=True,
        legend=dict(orientation="h", x=0, y=-0.08, font=dict(size=10, color=MUTED)),
        annotations=[
            dict(text=f"<b>{compacto(por_obra.sum())}</b><br><span style='font-size:10px;color:{MUTED}'>total</span>",
                 x=0.5, y=0.5, showarrow=False, font=dict(size=15, color=TINTA))
        ],
    )
    st.plotly_chart(fig_donut, use_container_width=True, config={"displayModeBar": False})

# ---- Processos detalhados ----
st.write("")
agrup = {"Valor": ("ValPagar", "sum"), "Parcelas": ("ValPagar", "size"), "Vencimento": ("DtPagParc_Proc", "min")}
if "Descr_obr" in det:
    agrup["Obra"] = ("Descr_obr", "first")
if "Desc_emp" in det:
    agrup["Empresa"] = ("Desc_emp", "first")
if "Aprovado" in det:
    agrup["Aprovado"] = ("Aprovado", "first")

procs = det.groupby("Num_Proc").agg(**agrup).reset_index().sort_values("Vencimento")

COLS_PARCELA = [c for c in [
    "NumParc_Proc", "DtPagParc_Proc", "ValorParc_Proc", "ValPagar", "Historico_Proc",
    "NomeBanco", "Aprovado", "Descr_obr", "Desc_emp",
] if c in det.columns]

with card("Processos detalhados", f"{len(procs)} processos deste fornecedor — expanda para ver as parcelas"):
    for _, p in procs.iterrows():
        obra = p.get("Obra", "—")
        aprov = str(p.get("Aprovado", "")) or "—"
        icone = "✅" if aprov.startswith("1") else "🕓"
        titulo = (
            f"{icone}  Processo **{int(p['Num_Proc'])}**  ·  {brl(p['Valor'])}  ·  "
            f"{int(p['Parcelas'])} parcela(s)  ·  {obra}  ·  1º venc. {p['Vencimento']:%d/%m/%Y}"
        )
        with st.expander(titulo):
            parcelas = det[det["Num_Proc"] == p["Num_Proc"]][COLS_PARCELA]
            st.dataframe(
                parcelas,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "NumParc_Proc": st.column_config.NumberColumn("Parcela", width="small"),
                    "DtPagParc_Proc": st.column_config.DateColumn("Vencimento", format="DD/MM/YYYY"),
                    "ValorParc_Proc": st.column_config.NumberColumn("Valor (R$)", format="localized"),
                    "ValPagar": st.column_config.NumberColumn("A pagar (R$)", format="localized"),
                    "Historico_Proc": st.column_config.TextColumn("Histórico", width="large"),
                    "NomeBanco": "Banco",
                    "Aprovado": "Aprovado",
                    "Descr_obr": "Obra",
                    "Desc_emp": "Empresa",
                },
            )

st.write("")
b1, b2 = st.columns([1, 4])
with b1:
    st.download_button(
        "⬇️ Exportar detalhamento (CSV)",
        det.to_csv(index=False, sep=";", decimal=",").encode("utf-8-sig"),
        file_name=f"fracionamento_{sel[:20].replace(' ', '_')}_{data_inicio:%Y%m%d}_{data_termino:%Y%m%d}.csv",
        mime="text/csv",
        use_container_width=True,
    )
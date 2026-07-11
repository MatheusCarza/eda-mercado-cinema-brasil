"""Dashboard interativo do mercado de cinema brasileiro (dados ANCINE, 2014-2026).

Roda inteiramente a partir dos CSVs agregados em outputs/processados/,
gerados por notebooks/analise.ipynb — não depende dos dados brutos.
"""

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Mercado de Cinema Brasileiro", page_icon="🎬", layout="wide")

# ═══════════════════════════════════════════════════════════════
# CONSTANTES (mesma paleta e nomes de mês do notebook, para
# manter a identidade visual entre notebook e dashboard)
# ═══════════════════════════════════════════════════════════════
CORES = {
    'nacional':    '#1f77b4',
    'estrangeiro': '#ff7f0e',
    'pandemia':    '#d62728',
    'destaque':    '#2ca02c',
    'neutro':      '#7f7f7f',
    'total':       '#17becf',
}
MESES_PT = {1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Abr', 5: 'Mai', 6: 'Jun',
            7: 'Jul', 8: 'Ago', 9: 'Set', 10: 'Out', 11: 'Nov', 12: 'Dez'}
ORDEM_MESES = list(MESES_PT.values())

DATA_DIR = Path(__file__).parent / "outputs" / "processados"

ARQUIVOS = {
    "market_share_anual": "market_share_anual.csv",
    "publico_anual": "publico_anual.csv",
    "publico_mensal": "publico_mensal.csv",
    "publico_por_uf": "publico_por_uf.csv",
    "queda_pandemia": "queda_pandemia.csv",
    "top_filmes": "top_filmes.csv",
    "ainda_estou_aqui_diario": "ainda_estou_aqui_diario.csv",
    "agente_secreto_diario": "agente_secreto_diario.csv",
    "resumo_dataset": "resumo_dataset.csv",
    "visao_geral_origem": "visao_geral_origem.csv",
    "publico_por_pais_estrangeiro": "publico_por_pais_estrangeiro.csv",
    "top_filmes_pos_reabertura": "top_filmes_pos_reabertura.csv",
    "filmes_premiados_geografico": "filmes_premiados_geografico.csv",
    "top_municipios": "top_municipios.csv",
    "sazonalidade_mensal": "sazonalidade_mensal.csv",
    "sazonalidade_por_origem": "sazonalidade_por_origem.csv",
}


# ═══════════════════════════════════════════════════════════════
# CARREGAMENTO DE DADOS
# ═══════════════════════════════════════════════════════════════
@st.cache_data
def load_data():
    dfs = {}
    for chave, nome in ARQUIVOS.items():
        caminho = DATA_DIR / nome
        if not caminho.exists():
            dfs[chave] = pd.DataFrame()
            continue
        dfs[chave] = pd.read_csv(caminho)

    if not dfs["publico_mensal"].empty:
        dfs["publico_mensal"]["DATA"] = pd.to_datetime(dfs["publico_mensal"]["ANO_MES"], format="%Y-%m")
        dfs["publico_mensal"]["ANO"] = dfs["publico_mensal"]["ANO_MES"].str[:4].astype(int)

    for chave in ("ainda_estou_aqui_diario", "agente_secreto_diario"):
        if not dfs[chave].empty:
            dfs[chave]["DATA_EXIBICAO"] = pd.to_datetime(dfs[chave]["DATA_EXIBICAO"])
            dfs[chave]["DIAS_DESDE_ESTREIA"] = (
                dfs[chave]["DATA_EXIBICAO"] - dfs[chave]["DATA_EXIBICAO"].min()
            ).dt.days

    return dfs


def arquivos_ausentes(dfs):
    return [ARQUIVOS[k] for k, v in dfs.items() if v.empty]


# ═══════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════
def formatar_num(valor):
    return f"{valor:,.0f}".replace(",", ".")


def caption_periodo_completo(extra=""):
    texto = "Período/base completa — não responde ao filtro de Ano"
    if extra:
        texto += f" ({extra})"
    st.caption(texto)


# ═══════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════
def build_sidebar(dfs):
    st.sidebar.header("Filtros")

    ano_ini, ano_fim = st.sidebar.slider("Período (Ano)", 2014, 2026, (2014, 2026), step=1)
    st.sidebar.caption("⚠️ 2026 contém dados parciais (jan–jun).")

    origens_disp = ["Nacional", "Estrangeiro"]
    origem_sel = st.sidebar.multiselect("Origem", origens_disp, default=origens_disp)
    if not origem_sel:
        st.sidebar.warning("Selecione ao menos uma origem — usando ambas.")
        origem_sel = origens_disp

    ufs_disp = sorted(dfs["publico_por_uf"]["UF"].unique()) if not dfs["publico_por_uf"].empty else []
    uf_sel = st.sidebar.multiselect("Estado (UF)", ufs_disp, default=ufs_disp)
    if not uf_sel:
        st.sidebar.warning("Selecione ao menos um estado — usando todos.")
        uf_sel = ufs_disp

    st.sidebar.markdown("---")
    st.sidebar.caption(
        "Nem todo gráfico responde a todos os filtros — quando um recorte "
        "representa o período/base completa, isso é indicado na legenda do gráfico."
    )

    faltando = arquivos_ausentes(dfs)
    if faltando:
        st.sidebar.markdown("---")
        st.sidebar.warning(
            "CSVs ausentes em `outputs/processados/` (rode o notebook para gerá-los):\n\n"
            + "\n".join(f"- {f}" for f in faltando)
        )

    return {"ano_ini": ano_ini, "ano_fim": ano_fim, "origem_sel": origem_sel, "uf_sel": uf_sel}


# ═══════════════════════════════════════════════════════════════
# ABA 1 — VISÃO GERAL
# ═══════════════════════════════════════════════════════════════
def tab_visao_geral(dfs, filtros):
    resumo = dfs["resumo_dataset"]
    if not resumo.empty:
        r = resumo.iloc[0]
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Público Total", formatar_num(r["Publico_Total"]))
        c2.metric("Filmes Únicos", formatar_num(r["Filmes_Unicos"]))
        c3.metric("Salas Únicas", formatar_num(r["Salas_Unicas"]))
        c4.metric("Estados Cobertos", int(r["Estados"]))
        caption_periodo_completo("métricas de todo o histórico 2014–2026")

    st.divider()

    mensal = dfs["publico_mensal"]
    if not mensal.empty:
        mensal_f = mensal[(mensal["ANO"] >= filtros["ano_ini"]) & (mensal["ANO"] <= filtros["ano_fim"])]
        fig = px.line(
            mensal_f, x="DATA", y="PUBLICO",
            color_discrete_sequence=[CORES["total"]],
            labels={"DATA": "Data", "PUBLICO": "Público"},
            title="Público Mensal ao Longo do Tempo",
        )
        fig.add_vrect(
            x0="2020-03-01", x1="2021-12-31",
            fillcolor=CORES["pandemia"], opacity=0.12, line_width=0,
            annotation_text="Pandemia", annotation_position="top left",
        )
        st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        anual = dfs["publico_anual"]
        if not anual.empty:
            anual_f = anual[(anual["ANO"] >= filtros["ano_ini"]) & (anual["ANO"] <= filtros["ano_fim"])].copy()
            anual_f["Período"] = anual_f["ANO"].apply(
                lambda a: "Pandemia" if a in (2020, 2021) else ("2026 (parcial)" if a == 2026 else "Normal")
            )
            fig = px.bar(
                anual_f, x="ANO", y="Publico_Total", color="Período",
                color_discrete_map={"Pandemia": CORES["pandemia"], "2026 (parcial)": CORES["neutro"], "Normal": CORES["total"]},
                labels={"Publico_Total": "Público Total", "ANO": "Ano"},
                title="Público por Ano",
            )
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        vg = dfs["visao_geral_origem"]
        if not vg.empty:
            vg_f = vg[vg["ORIGEM"].isin(filtros["origem_sel"])]
            fig = px.pie(
                vg_f, values="Total", names="ORIGEM", hole=0.4,
                color="ORIGEM",
                color_discrete_map={"Nacional": CORES["nacional"], "Estrangeiro": CORES["estrangeiro"]},
                title="Participação por Origem",
            )
            st.plotly_chart(fig, use_container_width=True)
            caption_periodo_completo()


# ═══════════════════════════════════════════════════════════════
# ABA 2 — PANDEMIA & RECUPERAÇÃO
# ═══════════════════════════════════════════════════════════════
def tab_pandemia(dfs, filtros):
    queda = dfs["queda_pandemia"]
    if not queda.empty:
        baseline = queda.loc[queda["ANO"] == 2019, "PUBLICO"]
        pior_ano = queda.loc[queda["VAR_PCT_VS_2019"].idxmin()]
        ultimo_ano = queda.iloc[-1]
        c1, c2, c3 = st.columns(3)
        c1.metric("Público 2019 (baseline)", formatar_num(baseline.iloc[0]) if not baseline.empty else "—")
        c2.metric(f"Maior Queda ({int(pior_ano['ANO'])})", f"{pior_ano['VAR_PCT_VS_2019']:.1f}%", delta_color="inverse")
        c3.metric(f"Variação em {int(ultimo_ano['ANO'])}", f"{ultimo_ano['VAR_PCT_VS_2019']:+.1f}%")

    st.divider()

    if not queda.empty:
        queda_f = queda[(queda["ANO"] >= filtros["ano_ini"]) & (queda["ANO"] <= filtros["ano_fim"])]
        if queda_f.empty:
            st.info("Ajuste o período (slider de Ano) para incluir 2019–2022 e ver este gráfico.")
        else:
            queda_f = queda_f.copy()
            queda_f["Sinal"] = queda_f["VAR_PCT_VS_2019"].apply(lambda v: "Queda" if v < 0 else "Alta")
            fig = px.bar(
                queda_f, x="ANO", y="VAR_PCT_VS_2019", color="Sinal",
                color_discrete_map={"Queda": CORES["pandemia"], "Alta": CORES["destaque"]},
                labels={"VAR_PCT_VS_2019": "% vs. 2019", "ANO": "Ano"},
                title="Variação do Público vs. Baseline 2019",
            )
            st.plotly_chart(fig, use_container_width=True)

    st.subheader("Top 10 Filmes Desde a Reabertura Plena (2022+)")
    caption_periodo_completo("recorte fixo 2022+, não filtra por Ano do slider")
    top_reab = dfs["top_filmes_pos_reabertura"]
    if not top_reab.empty:
        cols = st.columns(len(filtros["origem_sel"]) or 1)
        for col, origem in zip(cols, filtros["origem_sel"]):
            with col:
                sub = top_reab[top_reab["origem"] == origem].sort_values("Público", ascending=True)
                cor = CORES["nacional"] if origem == "Nacional" else CORES["estrangeiro"]
                fig = px.bar(
                    sub, x="Público", y="Título", orientation="h",
                    color_discrete_sequence=[cor],
                    title=f"{origem}",
                )
                st.plotly_chart(fig, use_container_width=True)


# ═══════════════════════════════════════════════════════════════
# ABA 3 — NACIONAL VS. ESTRANGEIRO
# ═══════════════════════════════════════════════════════════════
def tab_nacional_estrangeiro(dfs, filtros):
    ms = dfs["market_share_anual"]
    if not ms.empty:
        ms_f = ms[(ms["ANO"] >= filtros["ano_ini"]) & (ms["ANO"] <= filtros["ano_fim"])]
        if not ms_f.empty:
            ultimo = ms_f.iloc[-1]
            primeiro = ms_f.iloc[0]
            c1, c2 = st.columns(2)
            c1.metric(
                "% Nacional (último ano do período)", f"{ultimo['pct_nacional']:.1f}%",
                delta=f"{ultimo['pct_nacional'] - primeiro['pct_nacional']:+.1f}pp vs. início do período",
            )
            c2.metric(
                "% Estrangeiro (último ano do período)", f"{ultimo['pct_estrangeiro']:.1f}%",
                delta=f"{ultimo['pct_estrangeiro'] - primeiro['pct_estrangeiro']:+.1f}pp vs. início do período",
            )

    st.divider()

    if not ms.empty:
        ms_f = ms[(ms["ANO"] >= filtros["ano_ini"]) & (ms["ANO"] <= filtros["ano_fim"])]
        col_map = {"Nacional": "pct_nacional", "Estrangeiro": "pct_estrangeiro"}
        cores_map = {"pct_nacional": CORES["nacional"], "pct_estrangeiro": CORES["estrangeiro"]}
        ys = [col_map[o] for o in filtros["origem_sel"] if o in col_map]
        if ys:
            fig = px.bar(
                ms_f, x="ANO", y=ys, barmode="stack",
                color_discrete_map=cores_map,
                labels={"value": "% do Público", "variable": "Origem", "ANO": "Ano"},
                title="Market Share Anual (% do Público)",
            )
            st.plotly_chart(fig, use_container_width=True)

    st.subheader("Top 10 Filmes — Todo o Período (2014–2026)")
    caption_periodo_completo()
    top_filmes = dfs["top_filmes"]
    if not top_filmes.empty:
        cols = st.columns(len(filtros["origem_sel"]) or 1)
        for col, origem in zip(cols, filtros["origem_sel"]):
            with col:
                sub = top_filmes[top_filmes["origem"] == origem].sort_values("Público", ascending=True)
                cor = CORES["nacional"] if origem == "Nacional" else CORES["estrangeiro"]
                fig = px.bar(sub, x="Público", y="Título", orientation="h", color_discrete_sequence=[cor], title=origem)
                st.plotly_chart(fig, use_container_width=True)

    if "Estrangeiro" in filtros["origem_sel"]:
        st.subheader("Participação por País no Público Estrangeiro")
        caption_periodo_completo()
        paises = dfs["publico_por_pais_estrangeiro"]
        if not paises.empty:
            top_paises = paises.head(15).sort_values("Publico", ascending=True)
            fig = px.bar(
                top_paises, x="Publico", y="Pais", orientation="h",
                color_discrete_sequence=[CORES["estrangeiro"]],
                labels={"Publico": "Público", "Pais": "País"},
                title="Top 15 Países (Público Estrangeiro)",
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Filtro de Origem exclui filmes estrangeiros — ranking de países não exibido.")


# ═══════════════════════════════════════════════════════════════
# ABA 4 — FILMES PREMIADOS
# ═══════════════════════════════════════════════════════════════
def tab_filmes_premiados(dfs, filtros):
    aea = dfs["ainda_estou_aqui_diario"]
    oas = dfs["agente_secreto_diario"]

    caption_periodo_completo("curvas completas desde a estreia de cada filme; filtros de Ano/Origem não se aplicam")

    c1, c2 = st.columns(2)
    for col, df_filme, nome in ((c1, aea, "Ainda Estou Aqui"), (c2, oas, "O Agente Secreto")):
        with col:
            st.markdown(f"**{nome}**")
            if not df_filme.empty:
                sc1, sc2, sc3 = st.columns(3)
                sc1.metric("Público Total", formatar_num(df_filme["PUBLICO_ACUM"].max()))
                sc2.metric("Dias em Cartaz", int(df_filme["DIAS_DESDE_ESTREIA"].max()))
                sc3.metric("Pico Diário", formatar_num(df_filme["PUBLICO"].max()))

    st.divider()

    if not aea.empty and not oas.empty:
        combinado = pd.concat([
            aea[["DIAS_DESDE_ESTREIA", "PUBLICO_ACUM"]].assign(Filme="Ainda Estou Aqui"),
            oas[["DIAS_DESDE_ESTREIA", "PUBLICO_ACUM"]].assign(Filme="O Agente Secreto"),
        ])
        fig = px.line(
            combinado, x="DIAS_DESDE_ESTREIA", y="PUBLICO_ACUM", color="Filme",
            color_discrete_map={"Ainda Estou Aqui": CORES["destaque"], "O Agente Secreto": CORES["nacional"]},
            labels={"DIAS_DESDE_ESTREIA": "Dias desde a estreia", "PUBLICO_ACUM": "Público acumulado"},
            title="Público Acumulado — Comparação Alinhada pela Estreia",
        )
        st.plotly_chart(fig, use_container_width=True)

    geo = dfs["filmes_premiados_geografico"]
    if not geo.empty:
        geo_f = geo[geo["UF"].isin(filtros["uf_sel"])]
        fig = px.bar(
            geo_f, x="UF", y="Publico", color="Filme", barmode="group",
            color_discrete_map={"Ainda Estou Aqui": CORES["destaque"], "O Agente Secreto": CORES["nacional"]},
            labels={"Publico": "Público"},
            title="Distribuição por Estado",
        )
        st.plotly_chart(fig, use_container_width=True)
        caption_periodo_completo("filtro de UF se aplica; Ano/Origem não")


# ═══════════════════════════════════════════════════════════════
# ABA 5 — DISTRIBUIÇÃO GEOGRÁFICA
# ═══════════════════════════════════════════════════════════════
def tab_geografica(dfs, filtros):
    uf_df = dfs["publico_por_uf"]
    mun_df = dfs["top_municipios"]

    if not uf_df.empty:
        lider_uf = uf_df.loc[uf_df["PUBLICO"].idxmax()]
        c1, c2, c3 = st.columns(3)
        c1.metric("UF Líder", f"{lider_uf['UF']}", f"{lider_uf['PCT']:.1f}% do público")
        if not mun_df.empty:
            lider_mun = mun_df.iloc[0]
            c2.metric("Município Líder", lider_mun["LABEL"], f"{lider_mun['PCT']:.1f}% do público")
            c3.metric("Top 5 Municípios", f"{mun_df.head(5)['PCT'].sum():.1f}%", "do público total")

    st.divider()
    caption_periodo_completo("agregado do período completo; filtro de UF se aplica, Ano não")

    col1, col2 = st.columns(2)
    with col1:
        if not uf_df.empty:
            uf_f = uf_df[uf_df["UF"].isin(filtros["uf_sel"])].sort_values("PUBLICO", ascending=True)
            fig = px.bar(
                uf_f, x="PUBLICO", y="UF", orientation="h",
                color_discrete_sequence=[CORES["total"]],
                labels={"PUBLICO": "Público"},
                title="Público por Estado",
            )
            st.plotly_chart(fig, use_container_width=True)
    with col2:
        if not mun_df.empty:
            mun_f = mun_df[mun_df["UF_SALA_COMPLEXO"].isin(filtros["uf_sel"])].sort_values("PUBLICO", ascending=True)
            fig = px.bar(
                mun_f, x="PUBLICO", y="LABEL", orientation="h",
                color_discrete_sequence=[CORES["destaque"]],
                labels={"PUBLICO": "Público", "LABEL": "Município"},
                title="Top Municípios",
            )
            st.plotly_chart(fig, use_container_width=True)


# ═══════════════════════════════════════════════════════════════
# ABA 6 — SAZONALIDADE
# ═══════════════════════════════════════════════════════════════
def tab_sazonalidade(dfs, filtros):
    saz = dfs["sazonalidade_mensal"]
    if not saz.empty:
        pico = saz.loc[saz["PUBLICO"].idxmax()]
        vale = saz.loc[saz["PUBLICO"].idxmin()]
        c1, c2 = st.columns(2)
        c1.metric("Mês de Pico", pico["MES_NOME"], formatar_num(pico["PUBLICO"]))
        c2.metric("Mês de Vale", vale["MES_NOME"], formatar_num(vale["PUBLICO"]))

    st.divider()
    caption_periodo_completo("média histórica excluindo 2020/2021 (pandemia) e 2026 (parcial)")

    if not saz.empty:
        fig = px.bar(
            saz, x="MES_NOME", y="PUBLICO",
            category_orders={"MES_NOME": ORDEM_MESES},
            color_discrete_sequence=[CORES["total"]],
            labels={"MES_NOME": "Mês", "PUBLICO": "Público Médio"},
            title="Sazonalidade Mensal",
        )
        st.plotly_chart(fig, use_container_width=True)

    saz_origem = dfs["sazonalidade_por_origem"]
    if not saz_origem.empty:
        saz_origem_f = saz_origem[saz_origem["ORIGEM"].isin(filtros["origem_sel"])].copy()
        saz_origem_f["MES_NOME"] = saz_origem_f["MES"].map(MESES_PT)
        fig = px.bar(
            saz_origem_f, x="MES_NOME", y="PUBLICO", color="ORIGEM", barmode="group",
            category_orders={"MES_NOME": ORDEM_MESES},
            color_discrete_map={"Nacional": CORES["nacional"], "Estrangeiro": CORES["estrangeiro"]},
            labels={"MES_NOME": "Mês", "PUBLICO": "Público Médio", "ORIGEM": "Origem"},
            title="Sazonalidade por Origem",
        )
        st.plotly_chart(fig, use_container_width=True)


# ═══════════════════════════════════════════════════════════════
# APP PRINCIPAL
# ═══════════════════════════════════════════════════════════════
dfs = load_data()
filtros = build_sidebar(dfs)

st.title("🎬 Mercado de Cinema Brasileiro")
st.caption("Dados ANCINE, janeiro de 2014 a junho de 2026 (2026 parcial)")

tabs = st.tabs([
    "📊 Visão Geral",
    "🦠 Pandemia & Recuperação",
    "🎬 Nacional vs. Estrangeiro",
    "🏆 Filmes Premiados",
    "🗺️ Distribuição Geográfica",
    "📅 Sazonalidade",
])

with tabs[0]:
    tab_visao_geral(dfs, filtros)
with tabs[1]:
    tab_pandemia(dfs, filtros)
with tabs[2]:
    tab_nacional_estrangeiro(dfs, filtros)
with tabs[3]:
    tab_filmes_premiados(dfs, filtros)
with tabs[4]:
    tab_geografica(dfs, filtros)
with tabs[5]:
    tab_sazonalidade(dfs, filtros)

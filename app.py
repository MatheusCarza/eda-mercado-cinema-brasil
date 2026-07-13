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
ORIGENS = ["Nacional", "Estrangeiro"]

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

    for chave in ("top_filmes", "top_filmes_pos_reabertura"):
        if not dfs[chave].empty:
            dfs[chave]["Estreia"] = pd.to_datetime(dfs[chave]["Estreia"])

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


def leitura(texto):
    """Legenda descritiva: o que o gráfico mostra."""
    st.caption(f"📖 {texto}")


def comentario(texto):
    """Comentário analítico: um insight calculado a partir dos dados exibidos."""
    st.markdown(f"💡 *{texto}*")


def origens_na_ordem(origem_sel):
    """Mantém a ordem fixa Nacional → Estrangeiro, em vez da ordem de seleção do multiselect."""
    return [o for o in ORIGENS if o in origem_sel]


def rotulo_com_data(titulo, data):
    return f"{titulo.title()} ({MESES_PT[data.month].lower()}/{data.year})"


# ═══════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════
def build_sidebar(dfs):
    st.sidebar.header("Filtros")

    ano_ini, ano_fim = st.sidebar.slider("Período (Ano)", 2014, 2026, (2014, 2026), step=1)
    st.sidebar.caption("⚠️ 2026 contém dados parciais (jan–jun).")

    origem_sel = st.sidebar.multiselect("Origem", ORIGENS, default=ORIGENS)
    if not origem_sel:
        st.sidebar.warning("Selecione ao menos uma origem — usando ambas.")
        origem_sel = ORIGENS

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
    vg_full = dfs["visao_geral_origem"]

    if not resumo.empty:
        r = resumo.iloc[0]
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Público Total", formatar_num(r["Publico_Total"]))
        c2.metric("Filmes Únicos", formatar_num(r["Filmes_Unicos"]))
        c3.metric("Salas Únicas", formatar_num(r["Salas_Unicas"]))
        c4.metric("Estados Cobertos", int(r["Estados"]))
        caption_periodo_completo("métricas de todo o histórico 2014–2026")

        if not vg_full.empty and {"Nacional", "Estrangeiro"}.issubset(set(vg_full["ORIGEM"])):
            nac = vg_full[vg_full["ORIGEM"] == "Nacional"].iloc[0]
            est = vg_full[vg_full["ORIGEM"] == "Estrangeiro"].iloc[0]
            media_nac = nac["Total"] / nac["Titulos_Unicos"]
            media_est = est["Total"] / est["Titulos_Unicos"]
            razao = media_est / media_nac
            comentario(
                f"Em média, um filme estrangeiro atrai {razao:.1f}x mais público que um nacional por "
                f"título lançado ({formatar_num(media_est)} vs. {formatar_num(media_nac)} espectadores/filme)."
            )

    st.divider()

    mensal = dfs["publico_mensal"]
    if not mensal.empty:
        mensal_f = mensal[(mensal["ANO"] >= filtros["ano_ini"]) & (mensal["ANO"] <= filtros["ano_fim"])]
        leitura("Série mensal completa de público, com o fechamento das salas durante a pandemia destacado em vermelho.")
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
        if not mensal_f.empty:
            min_row = mensal_f.loc[mensal_f["PUBLICO"].idxmin()]
            max_row = mensal_f.loc[mensal_f["PUBLICO"].idxmax()]
            texto = (
                f"No período selecionado, o pico foi em {max_row['DATA']:%m/%Y} "
                f"({formatar_num(max_row['PUBLICO'])} espectadores) e o menor volume em "
                f"{min_row['DATA']:%m/%Y} ({formatar_num(min_row['PUBLICO'])})."
            )
            if min_row["ANO"] in (2020, 2021):
                texto += " O vale coincide com o fechamento das salas durante a pandemia."
            comentario(texto)

    col1, col2 = st.columns(2)
    with col1:
        anual = dfs["publico_anual"]
        if not anual.empty:
            anual_f = anual[(anual["ANO"] >= filtros["ano_ini"]) & (anual["ANO"] <= filtros["ano_fim"])].copy()
            leitura("Totais anuais, com pandemia e 2026 (parcial) destacados em cores diferentes.")
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
            if not anual_f.empty:
                ultimo = anual_f.iloc[-1]
                if pd.notna(ultimo["Var_Pct_YoY"]):
                    comentario(f"Em {int(ultimo['ANO'])}, o público variou {ultimo['Var_Pct_YoY']:+.1f}% frente ao ano anterior.")
                else:
                    comentario(f"{int(ultimo['ANO'])} é o primeiro ano da série — sem ano anterior para comparar.")

    with col2:
        vg = dfs["visao_geral_origem"]
        if not vg.empty:
            vg_f = vg[vg["ORIGEM"].isin(filtros["origem_sel"])]
            leitura("Participação de público por origem, no período completo (2014–2026).")
            fig = px.pie(
                vg_f, values="Total", names="ORIGEM", hole=0.4,
                color="ORIGEM",
                color_discrete_map={"Nacional": CORES["nacional"], "Estrangeiro": CORES["estrangeiro"]},
                title="Participação por Origem",
            )
            st.plotly_chart(fig, use_container_width=True)
            if len(vg_f) == 2:
                maior = vg_f.loc[vg_f["Pct_Publico"].idxmax()]
                comentario(f"{maior['ORIGEM']} concentra {maior['Pct_Publico']:.1f}% do público total.")
            elif len(vg_f) == 1:
                comentario(f"Mostrando só {vg_f.iloc[0]['ORIGEM']} — selecione as duas origens no filtro para comparar.")
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
        c2.metric(f"Maior Queda ({int(pior_ano['ANO'])})", f"{pior_ano['VAR_PCT_VS_2019']:.1f}%")
        c3.metric(f"Variação em {int(ultimo_ano['ANO'])}", f"{ultimo_ano['VAR_PCT_VS_2019']:+.1f}%")
        caption_periodo_completo("baseline fixo em 2019, independente do slider de Ano")
        comentario(
            f"A pandemia derrubou o público em {abs(pior_ano['VAR_PCT_VS_2019']):.0f}% em "
            f"{int(pior_ano['ANO'])} frente a 2019; em {int(ultimo_ano['ANO'])}, a diferença já "
            f"era de {ultimo_ano['VAR_PCT_VS_2019']:+.1f}%."
        )

    st.divider()

    if not queda.empty:
        queda_f = queda[(queda["ANO"] >= filtros["ano_ini"]) & (queda["ANO"] <= filtros["ano_fim"])]
        if queda_f.empty:
            st.info("Ajuste o período (slider de Ano) para incluir 2019–2022 e ver este gráfico.")
        else:
            leitura("Variação percentual do público de cada ano frente ao baseline de 2019 (pré-pandemia).")
            queda_f = queda_f.copy()
            queda_f["Sinal"] = queda_f["VAR_PCT_VS_2019"].apply(lambda v: "Queda" if v < 0 else "Alta")
            fig = px.bar(
                queda_f, x="ANO", y="VAR_PCT_VS_2019", color="Sinal",
                color_discrete_map={"Queda": CORES["pandemia"], "Alta": CORES["destaque"]},
                labels={"VAR_PCT_VS_2019": "% vs. 2019", "ANO": "Ano"},
                title="Variação do Público vs. Baseline 2019",
            )
            st.plotly_chart(fig, use_container_width=True)
            if len(queda_f) > 1:
                primeiro, ultimo = queda_f.iloc[0], queda_f.iloc[-1]
                tendencia = "recuperação" if ultimo["VAR_PCT_VS_2019"] > primeiro["VAR_PCT_VS_2019"] else "piora"
                comentario(
                    f"Entre {int(primeiro['ANO'])} e {int(ultimo['ANO'])}, a variação foi de "
                    f"{primeiro['VAR_PCT_VS_2019']:+.1f}% para {ultimo['VAR_PCT_VS_2019']:+.1f}% — "
                    f"tendência de {tendencia} no período selecionado."
                )
            else:
                comentario(f"Único ano no período selecionado: {int(queda_f.iloc[0]['ANO'])}.")

    st.subheader("Top 10 Filmes Desde a Reabertura Plena (2022+)")
    leitura("Ranking dos filmes nacionais e estrangeiros de maior público considerando só 2022 em diante.")
    caption_periodo_completo("recorte fixo 2022+, não filtra por Ano do slider")
    top_reab = dfs["top_filmes_pos_reabertura"]
    if not top_reab.empty:
        origens_ord = origens_na_ordem(filtros["origem_sel"])
        cols = st.columns(len(origens_ord))
        for col, origem in zip(cols, origens_ord):
            with col:
                sub = top_reab[top_reab["origem"] == origem].sort_values("Público", ascending=True).copy()
                sub["Label"] = [rotulo_com_data(t, d) for t, d in zip(sub["Título"], sub["Estreia"])]
                cor = CORES["nacional"] if origem == "Nacional" else CORES["estrangeiro"]
                fig = px.bar(
                    sub, x="Público", y="Label", orientation="h",
                    color_discrete_sequence=[cor],
                    labels={"Label": "Filme"},
                    title=f"{origem}",
                )
                st.plotly_chart(fig, use_container_width=True)
                if not sub.empty:
                    lider = sub.iloc[-1]
                    comentario(
                        f"{rotulo_com_data(lider['Título'], lider['Estreia'])} lidera com "
                        f"{formatar_num(lider['Público'])} espectadores desde 2022."
                    )


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
        origens_ord = origens_na_ordem(filtros["origem_sel"])
        ys = [col_map[o] for o in origens_ord]
        if ys:
            leitura("Evolução do market share (% do público) do cinema nacional e estrangeiro, ano a ano.")
            fig = px.bar(
                ms_f, x="ANO", y=ys, barmode="stack",
                color_discrete_map=cores_map,
                labels={"value": "% do Público", "variable": "Origem", "ANO": "Ano"},
                title="Market Share Anual (% do Público)",
            )
            st.plotly_chart(fig, use_container_width=True)
            if "Nacional" in origens_ord and not ms_f.empty:
                melhor = ms_f.loc[ms_f["pct_nacional"].idxmax()]
                texto = (
                    f"O melhor ano em participação do cinema nacional no período foi {int(melhor['ANO'])}, "
                    f"com {melhor['pct_nacional']:.1f}%."
                )
                if int(melhor["ANO"]) in (2020, 2021):
                    texto += (
                        " Mas isso reflete a pandemia — o mercado total despencou e blockbusters "
                        "estrangeiros foram adiados, não um ano forte para o cinema nacional em termos absolutos."
                    )
                comentario(texto)

    st.subheader("Top 10 Filmes — Todo o Período (2014–2026)")
    leitura("Ranking histórico completo dos filmes nacionais e estrangeiros de maior público.")
    caption_periodo_completo()
    top_filmes = dfs["top_filmes"]
    if not top_filmes.empty:
        origens_ord = origens_na_ordem(filtros["origem_sel"])
        cols = st.columns(len(origens_ord))
        for col, origem in zip(cols, origens_ord):
            with col:
                sub = top_filmes[top_filmes["origem"] == origem].sort_values("Público", ascending=True).copy()
                sub["Label"] = [rotulo_com_data(t, d) for t, d in zip(sub["Título"], sub["Estreia"])]
                cor = CORES["nacional"] if origem == "Nacional" else CORES["estrangeiro"]
                fig = px.bar(sub, x="Público", y="Label", orientation="h", color_discrete_sequence=[cor],
                             labels={"Label": "Filme"}, title=origem)
                st.plotly_chart(fig, use_container_width=True)
                if not sub.empty:
                    concentracao = sub["Público"].max() / sub["Público"].sum() * 100
                    lider = sub.iloc[-1]
                    comentario(
                        f"{rotulo_com_data(lider['Título'], lider['Estreia'])} sozinho concentra "
                        f"{concentracao:.0f}% do público somado dos 10 mais assistidos do período analisado (2014–2026)."
                    )

    if "Estrangeiro" in filtros["origem_sel"]:
        st.subheader("Participação por País no Público Estrangeiro")
        leitura("Distribuição do público de filmes estrangeiros entre os principais países de origem.")
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
            lider = paises.iloc[0]
            comentario(f"{lider['Pais'].title()} sozinho concentra {lider['Pct']:.1f}% de todo o público estrangeiro.")
    else:
        st.info("Filtro de Origem exclui filmes estrangeiros — ranking de países não exibido.")


# ═══════════════════════════════════════════════════════════════
# ABA 4 — FILMES PREMIADOS
# ═══════════════════════════════════════════════════════════════
def tab_filmes_premiados(dfs, filtros):
    aea = dfs["ainda_estou_aqui_diario"]
    oas = dfs["agente_secreto_diario"]

    caption_periodo_completo("curvas completas desde a estreia de cada filme; filtros de Ano/Origem não se aplicam")

    nomes = {"Ainda Estou Aqui": "Ainda Estou Aqui", "O Agente Secreto": "O Agente Secreto"}
    if not aea.empty:
        nomes["Ainda Estou Aqui"] = rotulo_com_data("Ainda Estou Aqui", aea["DATA_EXIBICAO"].min())
    if not oas.empty:
        nomes["O Agente Secreto"] = rotulo_com_data("O Agente Secreto", oas["DATA_EXIBICAO"].min())

    c1, c2 = st.columns(2)
    for col, df_filme, nome in ((c1, aea, nomes["Ainda Estou Aqui"]), (c2, oas, nomes["O Agente Secreto"])):
        with col:
            st.markdown(f"**{nome}**")
            if not df_filme.empty:
                sc1, sc2, sc3 = st.columns(3)
                sc1.metric("Público Total", formatar_num(df_filme["PUBLICO_ACUM"].max()))
                sc2.metric("Dias em Cartaz", int(df_filme["DIAS_DESDE_ESTREIA"].max()))
                sc3.metric("Pico Diário", formatar_num(df_filme["PUBLICO"].max()))

    if not aea.empty and not oas.empty:
        razao = aea["PUBLICO_ACUM"].max() / oas["PUBLICO_ACUM"].max()
        comentario(f"Ainda Estou Aqui vendeu {razao:.1f}x mais ingressos que O Agente Secreto, até agora.")

    st.divider()

    if not aea.empty and not oas.empty:
        leitura("Comparação do público acumulado dos dois filmes, alinhado pelos dias desde a estreia de cada um.")
        combinado = pd.concat([
            aea[["DIAS_DESDE_ESTREIA", "PUBLICO_ACUM"]].assign(Filme=nomes["Ainda Estou Aqui"]),
            oas[["DIAS_DESDE_ESTREIA", "PUBLICO_ACUM"]].assign(Filme=nomes["O Agente Secreto"]),
        ])
        fig = px.line(
            combinado, x="DIAS_DESDE_ESTREIA", y="PUBLICO_ACUM", color="Filme",
            color_discrete_map={nomes["Ainda Estou Aqui"]: CORES["destaque"], nomes["O Agente Secreto"]: CORES["nacional"]},
            labels={"DIAS_DESDE_ESTREIA": "Dias desde a estreia", "PUBLICO_ACUM": "Público acumulado"},
            title="Público Acumulado — Comparação Alinhada pela Estreia",
        )
        st.plotly_chart(fig, use_container_width=True)

        def dias_ate_90pct(df):
            alvo = df["PUBLICO_ACUM"].max() * 0.9
            return int(df.loc[df["PUBLICO_ACUM"] >= alvo, "DIAS_DESDE_ESTREIA"].min())

        d90_aea = dias_ate_90pct(aea)
        d90_oas = dias_ate_90pct(oas)
        mais_rapido = "Ainda Estou Aqui" if d90_aea < d90_oas else "O Agente Secreto"
        comentario(
            f"Ainda Estou Aqui atingiu 90% do seu público total em {d90_aea} dias, contra {d90_oas} "
            f"de O Agente Secreto — {mais_rapido} teve o público mais concentrado no início da exibição."
        )

    geo = dfs["filmes_premiados_geografico"]
    if not geo.empty:
        leitura("Distribuição do público de cada filme premiado entre os estados.")
        geo_f = geo[geo["UF"].isin(filtros["uf_sel"])]
        if not geo_f.empty:
            fig = px.bar(
                geo_f, x="UF", y="Publico", color="Filme", barmode="group",
                color_discrete_map={"Ainda Estou Aqui": CORES["destaque"], "O Agente Secreto": CORES["nacional"]},
                labels={"Publico": "Público"},
                title="Distribuição por Estado",
            )
            st.plotly_chart(fig, use_container_width=True)
            caption_periodo_completo("filtro de UF se aplica; Ano/Origem não")

            geo_aea = geo_f[geo_f["Filme"] == "Ainda Estou Aqui"]
            geo_oas = geo_f[geo_f["Filme"] == "O Agente Secreto"]
            if not geo_aea.empty and not geo_oas.empty:
                conc_aea = geo_aea["Publico"].max() / geo_aea["Publico"].sum() * 100
                conc_oas = geo_oas["Publico"].max() / geo_oas["Publico"].sum() * 100
                mais_concentrado = "Ainda Estou Aqui" if conc_aea > conc_oas else "O Agente Secreto"
                comentario(
                    f"Dentro dos estados selecionados, o estado líder concentra {conc_aea:.0f}% do público de "
                    f"Ainda Estou Aqui e {conc_oas:.0f}% do de O Agente Secreto — {mais_concentrado} tem "
                    f"alcance geográfico mais concentrado num único estado."
                )
        else:
            st.info("Nenhum dos estados selecionados tem dados para estes filmes.")


# ═══════════════════════════════════════════════════════════════
# ABA 5 — DISTRIBUIÇÃO GEOGRÁFICA
# ═══════════════════════════════════════════════════════════════
def tab_geografica(dfs, filtros):
    uf_df = dfs["publico_por_uf"]
    mun_df = dfs["top_municipios"]

    uf_f_kpi = uf_df[uf_df["UF"].isin(filtros["uf_sel"])] if not uf_df.empty else uf_df
    mun_f_kpi = mun_df[mun_df["UF_SALA_COMPLEXO"].isin(filtros["uf_sel"])] if not mun_df.empty else mun_df

    if not uf_df.empty:
        c1, c2, c3 = st.columns(3)
        if not uf_f_kpi.empty:
            lider_uf = uf_f_kpi.loc[uf_f_kpi["PUBLICO"].idxmax()]
            c1.metric("UF Líder (na seleção)", f"{lider_uf['UF']}", f"{lider_uf['PCT']:.1f}% do público nacional")
        else:
            c1.metric("UF Líder (na seleção)", "—")

        if not mun_f_kpi.empty:
            lider_mun = mun_f_kpi.loc[mun_f_kpi["PUBLICO"].idxmax()]
            c2.metric("Município Líder (na seleção)", lider_mun["LABEL"], f"{lider_mun['PCT']:.1f}% do público nacional")
            c3.metric("Municípios na Seleção (Top 10)", f"{mun_f_kpi['PCT'].sum():.1f}%", "do público nacional")
        else:
            c2.metric("Município Líder (na seleção)", "—")
            c3.metric("Municípios na Seleção (Top 10)", "—")
            st.info("Nenhum dos 10 municípios de maior público está nos estados selecionados.")

    st.divider()
    caption_periodo_completo("agregado do período completo; filtro de UF se aplica, Ano não")

    col1, col2 = st.columns(2)
    with col1:
        if not uf_df.empty:
            leitura("Público total por estado, em todo o período.")
            uf_f = uf_df[uf_df["UF"].isin(filtros["uf_sel"])].sort_values("PUBLICO", ascending=True)
            fig = px.bar(
                uf_f, x="PUBLICO", y="UF", orientation="h",
                color_discrete_sequence=[CORES["total"]],
                labels={"PUBLICO": "Público"},
                title="Público por Estado",
            )
            st.plotly_chart(fig, use_container_width=True)
            top5_pct = uf_df.nlargest(5, "PUBLICO")["PCT"].sum()
            comentario(
                f"Os 5 estados líderes do país concentram {top5_pct:.0f}% de todo o público nacional "
                f"(métrica sobre todos os estados, independente da seleção de UF)."
            )
    with col2:
        if not mun_df.empty:
            leitura("Top 10 municípios de maior público total.")
            mun_f = mun_df[mun_df["UF_SALA_COMPLEXO"].isin(filtros["uf_sel"])].sort_values("PUBLICO", ascending=True)
            if not mun_f.empty:
                fig = px.bar(
                    mun_f, x="PUBLICO", y="LABEL", orientation="h",
                    color_discrete_sequence=[CORES["destaque"]],
                    labels={"PUBLICO": "Público", "LABEL": "Município"},
                    title="Top Municípios",
                )
                st.plotly_chart(fig, use_container_width=True)
                top5_mun_pct = mun_df.head(5)["PCT"].sum()
                top5_uf_pct = uf_df.nlargest(5, "PUBLICO")["PCT"].sum() if not uf_df.empty else None
                texto = f"Os 5 municípios líderes do país concentram {top5_mun_pct:.1f}% do público nacional"
                if top5_uf_pct is not None:
                    texto += (
                        f" — mais concentrado ainda do que os 5 estados líderes ({top5_uf_pct:.0f}%), sinal de "
                        f"que a bilheteria se concentra em grandes cidades específicas, não no estado como um todo"
                    )
                texto += " (métrica sobre todo o país, independente da seleção de UF)."
                comentario(texto)
            else:
                st.info("Nenhum dos 10 municípios de maior público está nos estados selecionados.")


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
        caption_periodo_completo("média histórica excluindo 2020/2021 (pandemia) e 2026 (parcial)")
        razao = pico["PUBLICO"] / vale["PUBLICO"]
        comentario(f"{pico['MES_NOME']} tem, em média, {razao:.1f}x mais público que {vale['MES_NOME']}, o mês mais fraco do ano.")

    st.divider()

    if not saz.empty:
        leitura("Padrão sazonal médio de público por mês do ano.")
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
        leitura("Sazonalidade mensal comparando cinema nacional e estrangeiro.")
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

        if {"Nacional", "Estrangeiro"}.issubset(set(saz_origem_f["ORIGEM"])):
            nac_sub = saz_origem_f[saz_origem_f["ORIGEM"] == "Nacional"]
            est_sub = saz_origem_f[saz_origem_f["ORIGEM"] == "Estrangeiro"]
            mes_pico_nac = nac_sub.loc[nac_sub["PUBLICO"].idxmax(), "MES_NOME"]
            mes_pico_est = est_sub.loc[est_sub["PUBLICO"].idxmax(), "MES_NOME"]
            if mes_pico_nac == mes_pico_est:
                comentario(f"Nacional e estrangeiro têm o mesmo mês de pico: {mes_pico_nac}.")
            else:
                comentario(
                    f"O pico do cinema nacional é em {mes_pico_nac}, enquanto o do estrangeiro é em "
                    f"{mes_pico_est} — calendários de lançamento diferentes entre os dois segmentos."
                )


# ═══════════════════════════════════════════════════════════════
# ABA 7 — CONCLUSÕES
# ═══════════════════════════════════════════════════════════════
def tab_conclusoes(dfs):
    st.caption(
        "Síntese da análise completa, respondendo às perguntas centrais do projeto — "
        "não responde aos filtros da barra lateral."
    )

    anual = dfs["publico_anual"]
    queda = dfs["queda_pandemia"]
    ms = dfs["market_share_anual"]
    top_filmes = dfs["top_filmes"]
    aea = dfs["ainda_estou_aqui_diario"]
    oas = dfs["agente_secreto_diario"]
    paises = dfs["publico_por_pais_estrangeiro"]
    saz = dfs["sazonalidade_mensal"]
    uf_df = dfs["publico_por_uf"]
    mun_df = dfs["top_municipios"]

    st.subheader("1. Impacto da pandemia")
    if not queda.empty:
        pior_ano = queda.loc[queda["VAR_PCT_VS_2019"].idxmin()]
        st.write(
            f"Queda de {abs(pior_ano['VAR_PCT_VS_2019']):.0f}% em {int(pior_ano['ANO'])} frente a 2019 — "
            "salas praticamente fechadas entre mar/2020 e ago/2020."
        )
    else:
        st.info("Dados de queda_pandemia.csv indisponíveis.")

    st.subheader("2. Recuperação")
    if not anual.empty:
        completos = anual[anual["ANO"] != 2026]
        ultimo_completo = completos["ANO"].max()
        anual_idx = anual.set_index("ANO")
        pub_ultimo = anual_idx.loc[ultimo_completo, "Publico_Total"]
        pub_2019 = anual_idx.loc[2019, "Publico_Total"] if 2019 in anual_idx.index else None
        if pub_2019:
            pct_recuperacao = pub_ultimo / pub_2019 * 100
            status = "recuperado" if pct_recuperacao >= 100 else f"{100 - pct_recuperacao:.0f}pp abaixo do nível pré-pandemia"
            st.write(
                f"Em {int(ultimo_completo)} (último ano completo), o público está em "
                f"{pct_recuperacao:.0f}% do nível de 2019 — {status}."
            )
    else:
        st.info("Dados de publico_anual.csv indisponíveis.")

    st.subheader("3. Filmes premiados")
    if not aea.empty and not oas.empty:
        total_aea = aea["PUBLICO"].sum()
        total_oas = oas["PUBLICO"].sum()
        texto_aea = f"Ainda Estou Aqui: {formatar_num(total_aea)} espectadores"
        if not top_filmes.empty:
            nacionais = top_filmes[top_filmes["origem"] == "Nacional"].sort_values("Público", ascending=False).reset_index(drop=True)
            pos = nacionais.index[nacionais["Título"].str.upper() == "AINDA ESTOU AQUI"].tolist()
            if pos:
                texto_aea += f", o {pos[0] + 1}º filme nacional mais visto do período analisado (2014–2026)"
        st.write(texto_aea + ".")
        st.write(f"O Agente Secreto: {formatar_num(total_oas)} espectadores — impacto mais autoral que popular.")
    else:
        st.info("Dados diários de Ainda Estou Aqui / O Agente Secreto indisponíveis.")

    st.subheader("4. Nacional vs. estrangeiro")
    if not ms.empty:
        media_nacional = ms["pct_nacional"].mean()
        texto = f"O cinema nacional respondeu, em média, por {media_nacional:.0f}% do público no período"
        if not paises.empty:
            lider_pais = paises.iloc[0]
            texto += f" — o estrangeiro domina de forma consistente, puxado majoritariamente pelos EUA ({lider_pais['Pct']:.0f}% do público estrangeiro)"
        st.write(texto + ".")
    else:
        st.info("Dados de market_share_anual.csv indisponíveis.")

    st.subheader("5. Sazonalidade")
    if not saz.empty:
        pico = saz.loc[saz["PUBLICO"].idxmax()]
        vale = saz.loc[saz["PUBLICO"].idxmin()]
        razao = pico["PUBLICO"] / vale["PUBLICO"]
        st.write(
            f"{pico['MES_NOME']} é o mês de pico e {vale['MES_NOME']} o de vale — "
            f"{razao:.1f}x mais público no melhor mês."
        )
    else:
        st.info("Dados de sazonalidade_mensal.csv indisponíveis.")

    st.subheader("6. Distribuição geográfica")
    if not uf_df.empty and not mun_df.empty:
        top5_pct = uf_df.nlargest(5, "PUBLICO")["PCT"].sum()
        top5_mun_pct = mun_df.head(5)["PCT"].sum()
        st.write(
            f"Os 5 estados líderes concentram {top5_pct:.0f}% do público nacional, e os 5 municípios "
            f"líderes sozinhos já concentram {top5_mun_pct:.1f}% — a bilheteria é ainda mais concentrada "
            "em cidades específicas do que em estados inteiros."
        )
    else:
        st.info("Dados de publico_por_uf.csv / top_municipios.csv indisponíveis.")


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
    "🧾 Conclusões",
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
with tabs[6]:
    tab_conclusoes(dfs)

import sqlite3
import pandas as pd
import plotly.express as px
import streamlit as st

# Configuração da página (Modo Wide e título profissional)
st.set_page_config(
    page_title="Painel Executivo | ODS 13 - Ação Climática",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Estilização CSS Avançada para dar o "tchan" profissional (Ideal para TV/Telão)
st.markdown("""
    <style>
    /* Fundo geral e fontes */
    .main {
        background-color: #0b0f19;
        color: #f3f4f6;
    }
    h1, h2, h3 {
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        letter-spacing: -0.5px;
    }
    
    /* Cartões e métricas personalizados */
    div[data-testid="stMetric"] {
        background-color: #111827;
        border: 1px solid #1f2937;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    div[data-testid="stMetric"] label {
        color: #9ca3af !important;
        font-weight: 600;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: #10b981 !important;
        font-size: 2rem !important;
    }

    /* Botões estilizados */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        font-weight: 600;
        background-color: #059669;
        color: white;
        border: none;
        padding: 0.6rem 1rem;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #047857;
        box-shadow: 0 0 15px rgba(5, 150, 105, 0.4);
    }

    /* Alertas e caixas de texto */
    .stAlert {
        background-color: #111827;
        border: 1px solid #1f2937;
        color: #e5e7eb;
    }
    </style>
""", unsafe_allow_html=True)

# Banco de dados
DB_NAME = "pesquisa_ods13.db"


def init_db():
  conn = sqlite3.connect(DB_NAME)
  cursor = conn.cursor()
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS respostas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sessao TEXT,
            pergunta_id TEXT,
            opcao TEXT,
            data_hora DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
  conn.commit()
  conn.close()


init_db()

# Dicionário com as 5 perguntas principais e suas explicações
perguntas_dict = {
    "P1": {
        "titulo": "P1: O Objetivo Principal",
        "enunciado": (
            "Qual é o foco principal da ODS 13 (Ação Contra a Mudança Global do"
            " Clima)?"
        ),
        "opcoes": {
            "A": (
                "Acabar com a fome e a pobreza extrema em países em"
                " desenvolvimento."
            ),
            "B": (
                "Adotar medidas urgentes para combater a mudança climática e"
                " seus impactos reais."
            ),
            "C": (
                "Garantir Wi-Fi gratuito e de alta velocidade em todas as"
                " escolas públicas."
            ),
        },
        "explicacao": (
            "A ODS 13 é o compromisso global da ONU focado exclusivamente em"
            " enfrentar as mudanças climáticas e minimizar os desastres"
            " naturais decorrentes do aquecimento global."
        ),
    },
    "P2": {
        "titulo": "P2: Os Vilões do Clima",
        "enunciado": (
            "O que é apontado como a principal causa do aumento acelerado dos"
            " gases de efeito estufa na atmosfera?"
        ),
        "opcoes": {
            "A": (
                "A queima contínua de combustíveis fósseis (como petróleo,"
                " carvão e gás natural)."
            ),
            "B": (
                "O excesso de plantio de árvores frutíferas em áreas urbanas."
            ),
            "C": "O uso de energia solar e eólica em residências.",
        },
        "explicacao": (
            "A queima de combustíveis fósseis (usados em carros, indústrias e"
            " termoelétricas) libera toneladas de dióxido de carbono ($CO_2$),"
            " prendendo o calor na atmosfera como se fosse uma estufa."
        ),
    },
    "P3": {
        "titulo": "P3: A Solução Energética",
        "enunciado": (
            "Qual das alternativas abaixo representa uma fonte de energia limpa"
            " e renovável fundamental para o futuro?"
        ),
        "opcoes": {
            "A": "Carvão mineral.",
            "B": "Energia solar e dos ventos (eólica).",
            "C": "Gasolina aditivada.",
        },
        "explicacao": (
            "Fontes renováveis como a solar e a eólica aproveitam recursos"
            " naturais inesgotáveis sem emitir gases poluentes que destroem o"
            " clima."
        ),
    },
    "P4": {
        "titulo": "P4: O Poder da Natureza",
        "enunciado": (
            "Por que florestas densas, matas ciliares e mangues são considerados"
            " verdadeiros 'heróis' contra a crise climática?"
        ),
        "opcoes": {
            "A": (
                "Porque eles servem como sumidouros naturais que absorvem e"
                " armazenam o gás carbônico ($CO_2$)."
            ),
            "B": (
                "Porque eles impedem completamente a ocorrência de terremotos"
                " e tsunamis."
            ),
            "C": (
                "Porque eles atraem animais silvestres para dentro das grandes"
                " cidades."
            ),
        },
        "explicacao": (
            "As plantas e os oceanos absorvem grande parte do carbono da"
            " atmosfera pela fotossíntese, ajudando a resfriar o planeta e"
            " regular o ciclo das chuvas."
        ),
    },
    "P5": {
        "titulo": "P5: Ação Local",
        "enunciado": (
            "O que significa na prática reduzir a 'pegada de carbono' no seu dia"
            " a dia?"
        ),
        "opcoes": {
            "A": (
                "Deixar todas as luzes da casa acesas o dia todo para espantar"
                " o frio."
            ),
            "B": "Desperdiçar alimentos comprados em supermercados.",
            "C": (
                "Consumir com mais consciência, reciclar, evitar o desperdício"
                " e priorizar o transporte coletivo ou limpo."
            ),
        },
        "explicacao": (
            "Cada pequena escolha cotidiana — como economizar energia,"
            " reciclar e repensar o transporte — diminui a quantidade de"
            " recursos consumidos e poluição gerada."
        ),
    },
}

# Menu lateral de controle
st.sidebar.title("🎛️ Painel de Controle")
modo = st.sidebar.radio(
    "Navegação:", ["🌍 Pesquisa (Público)", "📊 Painel Executivo (Telão)"]
)

# --- MODO 1: PÚBLICO ---
if modo == "🌍 Pesquisa (Público)":
  st.markdown("# 🌍 Pesquisa Interativa: ODS 13")
  st.markdown(
      "### *Contribua com os dados regionais respondendo às questões abaixo:*"
  )
  st.markdown("---")

  sessao_evento = "Show_Principal"

  with st.form("form_pesquisa_completa"):
    respostas_usuario = {}

    for p_id, p_info in perguntas_dict.items():
      st.markdown(f"#### {p_info['titulo']}")
      st.write(p_info["enunciado"])

      escolha = st.radio(
          "Selecione uma alternativa:",
          options=list(p_info["opcoes"].keys()),
          format_func=lambda x, pi=p_id: (
              f"({x}) {perguntas_dict[pi]['opcoes'][x]}"
          ),
          key=f"radio_{p_id}",
      )
      respostas_usuario[p_id] = escolha
      st.markdown("---")

    enviar_tudo = st.form_submit_button("🚀 Enviar Respostas da Pesquisa")

    if enviar_tudo:
      conn = sqlite3.connect(DB_NAME)
      cursor = conn.cursor()
      for p_id, opcao_escolhida in respostas_usuario.items():
        cursor.execute(
            "INSERT INTO respostas (sessao, pergunta_id, opcao) VALUES (?, ?,"
            " ?)",
            (sessao_evento, p_id, opcao_escolhida),
        )
      conn.commit()
      conn.close()
      st.success(
          "🌟 Respostas registradas com sucesso no banco de dados regional!"
      )

# --- MODO 2: PAINEL EXECUTIVO / TELÃO ---
elif modo == "📊 Painel Executivo (Telão)":
  st.markdown("# 📊 Painel de Insights & Impacto — ODS 13")
  st.write(
      "Monitoramento em tempo real das respostas coletadas para apresentação"
      " executiva."
  )
  st.markdown("---")

  conn = sqlite3.connect(DB_NAME)
  df = pd.read_sql_query("SELECT * FROM respostas", conn)
  conn.close()

  if df.empty:
    st.warning(
        "⚠️ Nenhum dado registrado no banco ainda. Faça simulações na aba de"
        " público para testar!"
    )
  else:
    # Abas limpas para o apresentador gerenciar a exibição na TV
    tab_geral, tab_detalhada = st.tabs([
        "📈 Dashboard Geral (Visão Coletiva)",
        "🔍 Aprofundamento por Pergunta",
    ])

    with tab_geral:
      st.markdown("### 🌐 Panorama Integrado das 5 Questões")

      # Organiza os gráficos em grade de 2 colunas para exibição bonita na TV
      col1, col2 = st.columns(2)
      toggle_col = True

      for p_id, p_info in perguntas_dict.items():
        df_p = df[df["pergunta_id"] == p_id]
        if df_p.empty:
          continue

        contagem = (
            df_p["opcao"]
            .value_counts()
            .reset_index()
            .rename(columns={"opcao": "Alternativa", "count": "Votos"})
        )
        todas_alternativas = list(p_info["opcoes"].keys())
        contagem = (
            pd.DataFrame({"Alternativa": todas_alternativas})
            .merge(contagem, on="Alternativa", how="left")
            .fillna(0)
        )
        contagem["Texto_Alternativa"] = contagem["Alternativa"].map(
            lambda x: f"Opção {x}"
        )

        # Plotly com tema escuro e visual polido para TV
        fig = px.bar(
            contagem,
            x="Texto_Alternativa",
            y="Votos",
            color="Alternativa",
            text="Votos",
            title=p_info["titulo"],
            template="plotly_dark",
            height=320,
        )
        fig.update_layout(
            showlegend=False,
            xaxis_title="",
            yaxis_title="Respostas",
            paper_bgcolor="#111827",
            plot_bgcolor="#111827",
            font=dict(color="#f3f4f6"),
            margin=dict(l=20, r=20, t=40, b=20),
        )
        fig.update_traces(textfont_size=12, textangle=0, textposition="outside")

        if toggle_col:
          with col1:
            st.plotly_chart(fig, use_container_width=True)
        else:
          with col2:
            st.plotly_chart(fig, use_container_width=True)
        toggle_col = not toggle_col

    with tab_detalhada:
      pergunta_selecionada = st.selectbox(
          "Selecione o Tópico para Debate Detalhado:",
          options=list(perguntas_dict.keys()),
          format_func=lambda x: perguntas_dict[x]["titulo"],
      )

      p_info = perguntas_dict[pergunta_selecionada]

      st.markdown(f"### 📌 {p_info['titulo']}")
      st.info(f"**Questão:** {p_info['enunciado']}")

      df_filtrado = df[df["pergunta_id"] == pergunta_selecionada]

      if df_filtrado.empty:
        st.warning(
            "Nenhum registro encontrado para esta questão específica ainda."
        )
      else:
        contagem = (
            df_filtrado["opcao"]
            .value_counts()
            .reset_index()
            .rename(columns={"opcao": "Alternativa", "count": "Votos"})
        )
        todas_alternativas = list(p_info["opcoes"].keys())
        contagem = (
            pd.DataFrame({"Alternativa": todas_alternativas})
            .merge(contagem, on="Alternativa", how="left")
            .fillna(0)
        )
        contagem["Texto_Alternativa"] = contagem["Alternativa"].map(
            lambda x: f"Opção {x}"
        )

        col_grafico, col_metricas = st.columns([2.5, 1])

        with col_grafico:
          fig = px.bar(
              contagem,
              x="Texto_Alternativa",
              y="Votos",
              color="Alternativa",
              text="Votos",
              title=f"Distribuição Detalhada — {p_info['titulo']}",
              template="plotly_dark",
              height=400,
          )
          fig.update_layout(
              showlegend=False,
              xaxis_title="",
              yaxis_title="Total",
              paper_bgcolor="#111827",
              plot_bgcolor="#111827",
              font=dict(color="#f3f4f6"),
          )
          st.plotly_chart(fig, use_container_width=True)

        with col_metricas:
          st.markdown("### 📊 Status")
          st.metric(
              label="Amostras Coletadas", value=int(contagem["Votos"].sum())
          )

        st.markdown("---")
        st.markdown("### 💡 Discussão Pedagógica & Causa/Consequência:")
        st.success(p_info["explicacao"])

    # Seção de Exportação dos Dados para Análise Formal
    st.markdown("---")
    st.markdown("### 💾 Exportar Dataset Oficial")
    st.download_button(
        label="📥 Baixar Dados Coletados em Formato CSV",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="dados_oficiais_ods13.csv",
        mime="text/csv",
    )
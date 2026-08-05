import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, date, time
from weasyprint import HTML
import base64
import os

# -----------------------------------------------------------------------------
# 1. CONFIGURAÇÃO DA PÁGINA E CSS
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="PMCE - Registro de Ocorrência",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilo visual personalizado da Polícia Militar do Ceará
st.markdown("""
<style>
    .main-header {
        background-color: #1b4332;
        color: white;
        padding: 18px 25px;
        border-radius: 8px;
        text-align: center;
        margin-bottom: 25px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .main-header h1 {
        color: white !important;
        margin: 0;
        font-size: 26px;
        font-weight: 700;
        letter-spacing: 1px;
    }
    .main-header p {
        margin: 5px 0 0 0;
        font-size: 14px;
        opacity: 0.9;
    }
    .section-header {
        border-left: 5px solid #1b4332;
        padding-left: 10px;
        color: #1b4332;
        font-weight: bold;
        margin-top: 20px;
        margin-bottom: 15px;
    }
    .stButton>button {
        background-color: #1b4332;
        color: white;
        font-weight: bold;
        border: none;
        border-radius: 5px;
        padding: 10px 24px;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #2d6a4f;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. BANCO DE DADOS (SQLITE)
# -----------------------------------------------------------------------------
DB_FILE = "relatorio_pmce.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS ocorrencias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero_ocorrencia TEXT,
            data_ocorrencia TEXT,
            hora_ocorrencia TEXT,
            opm TEXT,
            viatura TEXT,
            cidade TEXT,
            bairro TEXT,
            endereco TEXT,
            natureza TEXT,
            composicao TEXT,
            envolvidos TEXT,
            materiais TEXT,
            historico TEXT,
            providencias TEXT,
            data_registro TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

def salvar_ocorrencia(num, data_oc, hora_oc, opm, viatura, cidade, bairro, endereco, natureza, composicao, envolvidos, materiais, historico, providencias):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        INSERT INTO ocorrencias (
            numero_ocorrencia, data_ocorrencia, hora_ocorrencia, opm, viatura,
            cidade, bairro, endereco, natureza, composicao, envolvidos,
            materiais, historico, providencias, data_registro
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        num, str(data_oc), str(hora_oc), opm, viatura, cidade, bairro,
        endereco, natureza, composicao, envolvidos, materiais, historico,
        providencias, datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))
    conn.commit()
    rec_id = c.lastrowid
    conn.close()
    return rec_id

# -----------------------------------------------------------------------------
# 3. IMAGENS BASE64 & GERADOR PDF (WEASYPRINT)
# -----------------------------------------------------------------------------
def get_image_base64(filepath):
    if os.path.exists(filepath):
        with open(filepath, "rb") as f:
            encoded = base64.b64encode(f.read()).decode()
            ext = filepath.split(".")[-1].lower()
            mime = "png" if ext == "png" else "jpeg"
            return f"data:image/{mime};base64,{encoded}"
    return ""

def gerar_pdf_relatorio(dados):
    logo_ceara = get_image_base64("logo_ceara.png")
    logo_pmce = get_image_base64("logo_pmce.png")

    img_ceara_html = f'<img src="{logo_ceara}">' if logo_ceara else '<b>GOVERNO DO CEARÁ</b>'
    img_pmce_html = f'<img src="{logo_pmce}">' if logo_pmce else '<b>PMCE</b>'

    html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <style>
        @page {{
            size: A4;
            margin: 15mm 12mm;
        }}
        body {{
            font-family: Arial, sans-serif;
            font-size: 10pt;
            line-height: 1.4;
            color: #222222;
            margin: 0;
            padding: 0;
        }}
        .header-table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 15px;
            border-bottom: 2px solid #1b4332;
            padding-bottom: 8px;
        }}
        .header-table td {{
            vertical-align: middle;
        }}
        .logo-cell {{
            width: 15%;
            text-align: center;
        }}
        .logo-cell img {{
            max-width: 70px;
            height: auto;
        }}
        .title-cell {{
            width: 70%;
            text-align: center;
        }}
        .title-cell h2 {{
            margin: 0;
            font-size: 13pt;
            color: #1b4332;
            text-transform: uppercase;
        }}
        .title-cell h3 {{
            margin: 3px 0 0 0;
            font-size: 10pt;
            color: #444;
            font-weight: normal;
        }}
        .title-cell p {{
            margin: 2px 0 0 0;
            font-size: 8pt;
            color: #666;
        }}
        .section-title {{
            background-color: #1b4332;
            color: #ffffff;
            font-size: 10pt;
            font-weight: bold;
            padding: 5px 8px;
            margin-top: 12px;
            margin-bottom: 6px;
            border-radius: 2px;
            text-transform: uppercase;
        }}
        .field-table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 8px;
        }}
        .field-table td {{
            border: 1px solid #cccccc;
            padding: 5px 8px;
            vertical-align: top;
            font-size: 9.5pt;
        }}
        .label {{
            font-weight: bold;
            color: #1b4332;
            font-size: 8.5pt;
            text-transform: uppercase;
            display: block;
            margin-bottom: 2px;
        }}
        .box-text {{
            border: 1px solid #cccccc;
            padding: 8px;
            min-height: 45px;
            background-color: #fafafa;
            font-size: 9.5pt;
            white-space: pre-wrap;
        }}
        .footer {{
            margin-top: 30px;
            width: 100%;
            text-align: center;
        }}
        .signature-line {{
            border-top: 1px solid #333333;
            width: 60%;
            margin: 40px auto 5px auto;
        }}
    </style>
</head>
<body>

    <table class="header-table">
        <tr>
            <td class="logo-cell">
                {img_ceara_html}
            </td>
            <td class="title-cell">
                <h2>Governo do Estado do Ceará</h2>
                <h3>Secretaria da Segurança Pública e Defesa Social</h3>
                <p><b>POLÍCIA MILITAR DO CEARÁ - PMCE</b></p>
                <p style="font-weight: bold; font-size: 11pt; margin-top: 5px; color: #1b4332;">
                    RELATÓRIO DE OCORRÊNCIA POLICIAL Nº {dados.get('numero_ocorrencia', 'N/A')}
                </p>
            </td>
            <td class="logo-cell">
                {img_pmce_html}
            </td>
        </tr>
    </table>

    <div class="section-title">1. Dados Gerais da Ocorrência</div>
    <table class="field-table">
        <tr>
            <td style="width: 25%;"><span class="label">Nº Ocorrência</span>{dados.get('numero_ocorrencia', '')}</td>
            <td style="width: 25%;"><span class="label">Data</span>{dados.get('data_ocorrencia', '')}</td>
            <td style="width: 25%;"><span class="label">Hora</span>{dados.get('hora_ocorrencia', '')}</td>
            <td style="width: 25%;"><span class="label">Viatura / Prefixo</span>{dados.get('viatura', '')}</td>
        </tr>
        <tr>
            <td colspan="2"><span class="label">Unidade / OPM</span>{dados.get('opm', '')}</td>
            <td colspan="2"><span class="label">Natureza da Ocorrência</span>{dados.get('natureza', '')}</td>
        </tr>
        <tr>
            <td colspan="2"><span class="label">Município</span>{dados.get('cidade', '')}</td>
            <td><span class="label">Bairro</span>{dados.get('bairro', '')}</td>
            <td><span class="label">Endereço</span>{dados.get('endereco', '')}</td>
        </tr>
    </table>

    <div class="section-title">2. Composição da Equipe</div>
    <div class="box-text">{dados.get('composicao', 'Nenhuma informação registrada.')}</div>

    <div class="section-title">3. Pessoas Envolvidas (Vítimas / Conduzidos / Testemunhas)</div>
    <div class="box-text">{dados.get('envolvidos', 'Nenhuma informação registrada.')}</div>

    <div class="section-title">4. Material Apreendido / Recuperado</div>
    <div class="box-text">{dados.get('materiais', 'Nenhum material registrado.')}</div>

    <div class="section-title">5. Histórico da Ocorrência</div>
    <div class="box-text">{dados.get('historico', 'Nenhum histórico registrado.')}</div>

    <div class="section-title">6. Providências Adotadas</div>
    <div class="box-text">{dados.get('providencias', 'Nenhuma providência registrada.')}</div>

    <div class="footer">
        <div class="signature-line"></div>
        <p style="font-size: 9pt; font-weight: bold; margin: 0;">Comandante da Composição / Relator</p>
        <p style="font-size: 8pt; color: #555; margin-top: 3px;">Documento gerado em {datetime.now().strftime("%d/%m/%Y às %H:%M")}</p>
    </div>

</body>
</html>"""

    pdf_bytes = HTML(string=html_content).write_pdf()
    return pdf_bytes

# -----------------------------------------------------------------------------
# 4. INTERFACE DO USUÁRIO (STREAMLIT)
# -----------------------------------------------------------------------------

st.markdown("""
<div class="main-header">
    <h1>POLÍCIA MILITAR DO CEARÁ</h1>
    <p>Sistema de Registro e Geração de Relatório de Ocorrência Policial</p>
</div>
""", unsafe_allow_html=True)

aba_registro, aba_historico = st.tabs(["📝 Novo Registro", "📋 Registros Salvos"])

with aba_registro:
    st.markdown("<h3 class='section-header'>1. DADOS GERAIS DA OCORRÊNCIA</h3>", unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        numero_ocorrencia = st.text_input("Nº Ocorrência / CIOPS*", value=f"PMCE-{datetime.now().strftime('%Y%m%d-%H%M')}")
    with col2:
        data_ocorrencia = st.date_input("Data da Ocorrência*", value=date.today())
    with col3:
        hora_ocorrencia = st.time_input("Hora da Ocorrência*", value=datetime.now().time())
    with col4:
        viatura = st.text_input("Viatura / Prefixo*", placeholder="Ex: RD-1234")

    col5, col6 = st.columns(2)
    with col5:
        opm = st.text_input("OPM / Batalhão*", placeholder="Ex: 1º BPM / 3ª CIA")
    with col6:
        natureza = st.text_input("Natureza da Ocorrência*", placeholder="Ex: Roubo a Pessoa / Porte Ilegal de Arma")

    col7, col8, col9 = st.columns([1, 1, 2])
    with col7:
        cidade = st.text_input("Município*", value="Fortaleza")
    with col8:
        bairro = st.text_input("Bairro*", placeholder="Ex: Aldeota")
    with col9:
        endereco = st.text_input("Endereço / Ponto de Referência*", placeholder="Ex: Av. Santos Dumont, nº 1000")

    st.markdown("<h3 class='section-header'>2. INTEGRANTES E ENVOLVIDOS</h3>", unsafe_allow_html=True)
    
    composicao = st.text_area(
        "13 - COMPOSIÇÃO (INTEGRANTES DA EQUIPE)*",
        placeholder="Ex:\n- Comandante: 1º Sgt PM 12345 Silva\n- Motorista: Cb PM 67890 Santos\n- Patrulheiro: Sd PM 54321 Oliveira",
        height=130
    )

    envolvidos = st.text_area(
        "14 - PESSOAS ENVOLVIDAS (VÍTIMAS / ACUSADOS / TESTEMUNHAS)",
        placeholder="Ex:\n- Vítima: João da Silva, CPF: 000.000.000-00\n- Acusado: Pedro Alves, RG: 1234567-SSP/CE",
        height=130
    )

    st.markdown("<h3 class='section-header'>3. DETALHES E MATERIAIS</h3>", unsafe_allow_html=True)

    materiais = st.text_area(
        "15 - MATERIAIS APREENDIDOS / RECUPERADOS",
        placeholder="Ex:\n- 01 Revólver Calibre 38, Marca Taurus, nº 12345\n- 06 Munições intactas\n- 01 Aparelho Celular Samsung",
        height=110
    )

    historico = st.text_area(
        "16 - HISTÓRICO DA OCORRÊNCIA (NARRATIVA COMPLETA)*",
        placeholder="Descreva detalhadamente a dinâmica dos fatos ocorridos durante o serviço...",
        height=160
    )

    providencias = st.text_area(
        "17 - PROVIDÊNCIAS ADOTADAS",
        placeholder="Ex: Ocorrência apresentada no 2º Distrito Policial ao delegado de plantão para procedimentos cabíveis.",
        height=110
    )

    st.markdown("---")
    
    col_btn1, col_btn2 = st.columns(2)
    
    with col_btn1:
        if st.button("💾 SALVAR NO BANCO DE DADOS"):
            if not numero_ocorrencia or not composicao or not historico:
                st.error("Por favor, preencha os campos obrigatórios (Nº Ocorrência, Composição e Histórico).")
            else:
                rec_id = salvar_ocorrencia(
                    numero_ocorrencia, data_ocorrencia, hora_ocorrencia, opm, viatura,
                    cidade, bairro, endereco, natureza, composicao, envolvidos,
                    materiais, historico, providencias
                )
                st.success(f"Ocorrência registrada com sucesso! (ID: {rec_id})")

    with col_btn2:
        dados_pdf = {
            "numero_ocorrencia": numero_ocorrencia,
            "data_ocorrencia": data_ocorrencia.strftime("%d/%m/%Y") if data_ocorrencia else "",
            "hora_ocorrencia": hora_ocorrencia.strftime("%H:%M") if hora_ocorrencia else "",
            "opm": opm,
            "viatura": viatura,
            "cidade": cidade,
            "bairro": bairro,
            "endereco": endereco,
            "natureza": natureza,
            "composicao": composicao,
            "envolvidos": envolvidos,
            "materiais": materiais,
            "historico": historico,
            "providencias": providencias
        }
        
        try:
            pdf_data = gerar_pdf_relatorio(dados_pdf)
            st.download_button(
                label="📄 GERAR E BAIXAR RELATÓRIO PDF",
                data=pdf_data,
                file_name=f"Relatorio_{numero_ocorrencia.replace('/', '_')}.pdf",
                mime="application/pdf"
            )
        except Exception as e:
            st.error(f"Erro ao preparar arquivo PDF: {e}")

with aba_historico:
    st.markdown("<h3 class='section-header'>OCORRÊNCIAS REGISTRADAS NO SISTEMA</h3>", unsafe_allow_html=True)
    
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT id, numero_ocorrencia, data_ocorrencia, hora_ocorrencia, opm, viatura, natureza, cidade, data_registro FROM ocorrencias ORDER BY id DESC", conn)
    conn.close()

    if df.empty:
        st.info("Nenhuma ocorrência salva até o momento.")
    else:
        st.dataframe(df, use_container_width=True)

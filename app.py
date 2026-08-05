import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, time
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

if "hora_inicial_default" not in st.session_state:
    st.session_state["hora_inicial_default"] = datetime.now().time()
if "data_default" not in st.session_state:
    st.session_state["data_default"] = datetime.now().date()

def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as image_file:
            encoded = base64.b64encode(image_file.read()).decode()
            return f"data:image/png;base64,{encoded}"
    return ""

img_pmce = get_image_base64("logo_pmce.png")
img_ceara = get_image_base64("logo_ceara.png")

st.markdown("""
<style>
    :root {
        --verde-oliva: #1B4D3E;
        --azul-marinho: #002B49;
        --dourado: #DAA520;
    }
    
    .stApp {
        background-color: #FFFFFF !important;
    }
    
    .stApp, .stApp p, .stApp label, .stApp span, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6, .stMarkdown {
        color: #111111 !important;
    }
    
    .header-oficial {
        text-align: left;
        padding-bottom: 5px;
    }
    .header-oficial .unidade {
        font-weight: bold;
        font-size: 1rem;
        color: #333333;
        margin: 0;
    }
    .header-oficial .endereco {
        font-size: 0.85rem;
        color: #666666;
        margin: 2px 0;
    }
    .header-oficial .lema {
        font-style: italic;
        font-weight: bold;
        font-size: 0.9rem;
        color: #333333;
        margin-top: 4px;
    }
    
    .faixa-gov {
        height: 8px;
        width: 100%;
        background: linear-gradient(to right, #00A859 25%, #0088CE 25% 50%, #FDC82F 50% 75%, #F37021 75%);
        margin: 10px 0 20px 0;
        border-radius: 2px;
    }

    button[data-baseweb="tab"] {
        background-color: #F0F4F1 !important;
        border-radius: 6px 6px 0 0 !important;
        padding: 10px 20px !important;
        margin-right: 5px !important;
    }
    
    button[data-baseweb="tab"] p {
        color: #1B4D3E !important;
        font-weight: bold !important;
    }
    
    button[aria-selected="true"] {
        background-color: var(--verde-oliva) !important;
    }
    
    button[aria-selected="true"] p {
        color: #FFFFFF !important;
    }

    .stButton > button {
        background-color: var(--verde-oliva) !important;
        color: #FFFFFF !important;
        font-weight: bold !important;
        border: none !important;
        padding: 12px 24px !important;
        border-radius: 6px !important;
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. BANCO DE DADOS
# -----------------------------------------------------------------------------
DB_FILE = "ocorrencias_pmce.db"

def init_db():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ocorrências (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            unidade TEXT, data_fato TEXT, hora_inicial TEXT, hora_final TEXT,
            natureza TEXT, vtr TEXT, ht TEXT, ciops TEXT, turno TEXT,
            delegacia TEXT, delegado TEXT, procedimentos TEXT, composicao TEXT,
            condutor TEXT, testemunhas_policiais TEXT, local_ocorrencia TEXT,
            local_abordagem TEXT, acusado TEXT, vitimas TEXT, armas TEXT,
            municao TEXT, drogas TEXT, veiculos TEXT, quantia_recuperada TEXT,
            quantia_apreendida TEXT, testemunhas_povo TEXT, objetos_recuperados TEXT,
            objetos_apreendidos TEXT, ficaram_preso TEXT, suspeitos_menores TEXT,
            narrativa TEXT, data_registro TEXT, equipe TEXT
        )
    ''')
    try:
        cursor.execute("ALTER TABLE ocorrências ADD COLUMN equipe TEXT DEFAULT 'Equipe Alfa'")
    except sqlite3.OperationalError:
        pass
    conn.commit()
    return conn

conn = init_db()

# -----------------------------------------------------------------------------
# 3. GERADORES DE PDF
# -----------------------------------------------------------------------------
def gerar_pdf_ocorrencia(d):
    html_content = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <style>
            @page {{ size: A4; margin: 12mm 10mm; }}
            body {{ font-family: Arial, sans-serif; font-size: 8.5pt; color: #111; line-height: 1.2; }}
            
            .unidade-header {{ font-size: 9pt; font-weight: bold; color: #222; text-transform: uppercase; }}
            .end-header {{ font-size: 7.5pt; color: #555; margin-top: 2px; }}
            .lema-header {{ font-size: 8pt; font-style: italic; font-weight: bold; margin-top: 3px; color: #111; }}
            
            .faixa-ceara {{
                height: 5px;
                width: 100%;
                background: linear-gradient(to right, #00A859 25%, #0088CE 25% 50%, #FDC82F 50% 75%, #F37021 75%);
                margin: 6px 0 12px 0;
            }}
            
            .logos-block {{ text-align: center; margin-bottom: 12px; }}
            .logos-block img {{ height: 55px; margin: 0 15px; vertical-align: middle; }}
            
            .doc-title {{ text-align: center; background-color: #1B4D3E; color: #FFF; font-weight: bold; font-size: 10pt; padding: 5px; margin-bottom: 10px; border-radius: 3px; }}
            
            .sec-title {{ background-color: #002B49; color: #FFF; font-weight: bold; font-size: 8pt; padding: 3px 6px; margin-top: 8px; margin-bottom: 4px; border-left: 3px solid #DAA520; text-transform: uppercase; }}
            table {{ width: 100%; border-collapse: collapse; margin-bottom: 4px; }}
            td {{ border: 1px solid #CCC; padding: 4px 5px; vertical-align: top; }}
            .lbl {{ font-weight: bold; color: #1B4D3E; font-size: 7pt; text-transform: uppercase; display: block; }}
            .val {{ font-size: 8pt; color: #111; word-break: break-word; }}
            .bg {{ background-color: #F0F4F1; }}
            .box-narrativa {{ border: 1px solid #CCC; padding: 6px; min-height: 120px; font-size: 8pt; text-align: justify; white-space: pre-wrap; margin-top: 4px; }}
            .footer {{ margin-top: 25px; text-align: center; }}
            .sig {{ display: inline-block; width: 45%; margin: 0 2%; border-top: 1px solid #000; padding-top: 3px; font-size: 7.5pt; }}
        </style>
    </head>
    <body>
        <div>
            <div class="unidade-header">1ª COMPANHIA / 18º BATALHÃO POLICIAL MILITAR</div>
            <div class="end-header">Rua Prof. Armando Farias, s/nº - Pici (IPDI / UFC) - Fortaleza-CE - CEP: 60.440-552</div>
            <div class="end-header">Telefone: (85) 98485-2398 - E-mail: 18bpm@policiamilitar.ce.gov.br</div>
            <div class="lema-header">"RAÇA DE FORTES, POVO DE BRAVOS"</div>
        </div>

        <div class="faixa-ceara"></div>

        <div class="logos-block">
            {"<img src='" + img_pmce + "'>" if img_pmce else ""}
            {"<img src='" + img_ceara + "'>" if img_ceara else ""}
        </div>

        <div class="doc-title">RELATÓRIO DE OCORRÊNCIA POLICIAL Nº {d['id']:06d}</div>

        <div class="sec-title">01. IDENTIFICAÇÃO E DADOS GERAIS</div>
        <table>
            <tr>
                <td width="35%" class="bg"><span class="lbl">01 - UNIDADE (CIA/BTL)</span><span class="val">{d['unidade']}</span></td>
                <td width="20%"><span class="lbl">02 - DATA</span><span class="val">{d['data_fato']}</span></td>
                <td width="22.5%"><span class="lbl">03 - HORA INICIAL</span><span class="val">{d['hora_inicial']}</span></td>
                <td width="22.5%"><span class="lbl">04 - HORA FINAL</span><span class="val">{d['hora_final']}</span></td>
            </tr>
            <tr>
                <td colspan="2"><span class="lbl">05 - NATUREZA DA OCORRÊNCIA</span><span class="val">{d['natureza']}</span></td>
                <td class="bg"><span class="lbl">06 - FRAÇÃO / PREFIXO VTR</span><span class="val">{d['vtr']}</span></td>
                <td><span class="lbl">07 - DESIGNAÇÃO DA EQUIPE</span><span class="val"><strong>{d.get('equipe', 'N/I')}</strong></span></td>
            </tr>
            <tr>
                <td class="bg"><span class="lbl">08 - FICHA CIOPS / Nº COPOM</span><span class="val">{d['ciops']}</span></td>
                <td><span class="lbl">09 - TURNO</span><span class="val">{d['turno']}</span></td>
                <td colspan="2"><span class="lbl">10 - DELEGACIA DE DESTINO</span><span class="val">{d['delegacia']}</span></td>
            </tr>
            <tr>
                <td colspan="2"><span class="lbl">11 - DELEGADO(A) PLANTONISTA</span><span class="val">{d['delegado']}</span></td>
                <td colspan="2" class="bg"><span class="lbl">12 - N°(S) DOS PROCEDIMENTO(S)</span><span class="val">{d['procedimentos']}</span></td>
            </tr>
        </table>

        <div class="sec-title">02. COMPOSIÇÃO POLICIAL E LOCALIZADORES</div>
        <table>
            <tr>
                <td width="50%"><span class="lbl">13 - COMPOSIÇÃO</span><span class="val">{d['composicao']}</span></td>
                <td width="50%" class="bg"><span class="lbl">14 - CONDUTOR DA OCORRÊNCIA</span><span class="val">{d['condutor']}</span></td>
            </tr>
            <tr>
                <td colspan="2"><span class="lbl">15 - TESTEMUNHAS POLICIAIS</span><span class="val">{d['testemunhas_policiais']}</span></td>
            </tr>
            <tr>
                <td width="50%" class="bg"><span class="lbl">16 - LOCAL DA OCORRÊNCIA</span><span class="val">{d['local_ocorrencia']}</span></td>
                <td width="50%"><span class="lbl">17 - LOCAL DA ABORDAGEM</span><span class="val">{d['local_abordagem']}</span></td>
            </tr>
        </table>

        <div class="sec-title">03. ENVOLVIDOS</div>
        <table>
            <tr>
                <td width="50%" class="bg"><span class="lbl">18 - ACUSADO(S)</span><span class="val">{d['acusado']}</span></td>
                <td width="50%"><span class="lbl">19 - VÍTIMA(S)</span><span class="val">{d['vitimas']}</span></td>
            </tr>
            <tr>
                <td width="50%"><span class="lbl">26 - TESTEMUNHAS DO POVO</span><span class="val">{d['testemunhas_povo']}</span></td>
                <td width="25%" class="bg"><span class="lbl">29 - FICARAM PRESO?</span><span class="val"><strong>{d['ficaram_preso']}</strong></span></td>
                <td width="25%"><span class="lbl">30 - SUSPEITOS MENORES?</span><span class="val">{d['suspeitos_menores']}</span></td>
            </tr>
        </table>

        <div class="sec-title">04. APREENSÕES E BENS RECUPERADOS</div>
        <table>
            <tr>
                <td width="50%"><span class="lbl">20 - ARMA(S) APREENDIDA(S)</span><span class="val">{d['armas']}</span></td>
                <td width="50%" class="bg"><span class="lbl">21 - MUNIÇÃO APREENDIDA</span><span class="val">{d['municao']}</span></td>
            </tr>
            <tr>
                <td width="50%" class="bg"><span class="lbl">22 - DROGA(S) APREENDIDA(S)</span><span class="val">{d['drogas']}</span></td>
                <td width="50%"><span class="lbl">23 - VEÍCULO(S) RECUPERADO(S)</span><span class="val">{d['veiculos']}</span></td>
            </tr>
            <tr>
                <td width="50%"><span class="lbl">24 - QUANTIA RECUPERADA</span><span class="val">{d['quantia_recuperada']}</span></td>
                <td width="50%" class="bg"><span class="lbl">25 - QUANTIA APREENDIDA</span><span class="val">{d['quantia_apreendida']}</span></td>
            </tr>
            <tr>
                <td width="50%" class="bg"><span class="lbl">27 - OBJETO(S) RECUPERADO(S)</span><span class="val">{d['objetos_recuperados']}</span></td>
                <td width="50%"><span class="lbl">28 - OBJETO(S) APREENDIDO(S)</span><span class="val">{d['objetos_apreendidos']}</span></td>
            </tr>
        </table>

        <div class="sec-title">05. NARRATIVA SUCINTA DA OCORRÊNCIA</div>
        <div class="box-narrativa">31 - NARRATIVA:<br>{d['narrativa']}</div>

        <div class="footer">
            <div class="sig"><strong>{d['condutor']}</strong><br>Condutor da Ocorrência</div>
            <div class="sig"><strong>{d['delegado']}</strong><br>Delegado(a) / Autoridade Policial</div>
        </div>
    </body>
    </html>
    """
    return HTML(string=html_content).write_pdf()

def gerar_pdf_ranking(df_ranking):
    data_atual = datetime.now().strftime("%d/%m/%Y %H:%M")
    
    rows_html = ""
    for idx, row in df_ranking.iterrows():
        pos = idx + 1
        medalha = "🥇" if pos == 1 else ("🥈" if pos == 2 else ("🥉" if pos == 3 else f"{pos}º"))
        rows_html += f"""
        <tr>
            <td style="text-align:center; font-weight:bold; font-size:10pt;">{medalha}</td>
            <td style="font-weight:bold;">{row['Equipe']}</td>
            <td style="text-align:center;">{row['Total de Ocorrências']}</td>
            <td style="text-align:center;">{row['Tráfico de Drogas']}</td>
            <td style="text-align:center;">{row['Armas Apreendidas']}</td>
            <td style="text-align:center;">{row['Mandados Cump.']}</td>
            <td style="text-align:center; font-weight:bold; color:#1B4D3E;">{row['Pontuação Total']}</td>
        </tr>
        """

    html_content = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <style>
            @page {{ size: A4; margin: 12mm 10mm; }}
            body {{ font-family: Arial, sans-serif; font-size: 9pt; color: #111; line-height: 1.3; }}
            .unidade-header {{ font-size: 9pt; font-weight: bold; color: #222; text-transform: uppercase; }}
            .end-header {{ font-size: 7.5pt; color: #555; margin-top: 2px; }}
            .lema-header {{ font-size: 8pt; font-style: italic; font-weight: bold; margin-top: 3px; color: #111; }}
            .faixa-ceara {{
                height: 5px; width: 100%;
                background: linear-gradient(to right, #00A859 25%, #0088CE 25% 50%, #FDC82F 50% 75%, #F37021 75%);
                margin: 6px 0 12px 0;
            }}
            .logos-block {{ text-align: center; margin-bottom: 12px; }}
            .logos-block img {{ height: 50px; margin: 0 15px; vertical-align: middle; }}
            .doc-title {{ text-align: center; background-color: #002B49; color: #FFF; font-weight: bold; font-size: 11pt; padding: 6px; margin-bottom: 15px; border-radius: 3px; border-bottom: 3px solid #DAA520; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
            th {{ background-color: #1B4D3E; color: white; padding: 6px; font-size: 8pt; text-transform: uppercase; border: 1px solid #1B4D3E; }}
            td {{ border: 1px solid #CCC; padding: 6px; font-size: 8.5pt; }}
            tr:nth-child(even) {{ background-color: #F9F9F9; }}
            .footer {{ margin-top: 30px; font-size: 8pt; color: #666; text-align: right; border-top: 1px solid #EEE; padding-top: 5px; }}
        </style>
    </head>
    <body>
        <div>
            <div class="unidade-header">1ª COMPANHIA / 18º BATALHÃO POLICIAL MILITAR</div>
            <div class="end-header">Rua Prof. Armando Farias, s/nº - Pici (IPDI / UFC) - Fortaleza-CE - CEP: 60.440-552</div>
            <div class="lema-header">"RAÇA DE FORTES, POVO DE BRAVOS"</div>
        </div>
        <div class="faixa-ceara"></div>
        <div class="logos-block">
            {"<img src='" + img_pmce + "'>" if img_pmce else ""}
            {"<img src='" + img_ceara + "'>" if img_ceara else ""}
        </div>
        <div class="doc-title">RELATÓRIO ESTATÍSTICO DE DESEMPENHO E RANKING DAS EQUIPES</div>
        
        <p><strong>Data de Emissão:</strong> {data_atual}</p>
        
        <table>
            <thead>
                <tr>
                    <th width="8%">POS</th>
                    <th width="28%">EQUIPE</th>
                    <th width="14%">OCORRÊNCIAS</th>
                    <th width="13%">TRÁFICO</th>
                    <th width="13%">ARMAS</th>
                    <th width="12%">MANDADOS</th>
                    <th width="12%">PONTUAÇÃO</th>
                </tr>
            </thead>
            <tbody>
                {rows_html}
            </tbody>
        </table>
        
        <div class="footer">
            Sistema Eletrônico ROP PMCE • Documento Gerado Automaticamente
        </div>
    </body>
    </html>
    """
    return HTML(string=html_content).write_pdf()

# -----------------------------------------------------------------------------
# 4. EXIBIÇÃO NO APLICATIVO
# -----------------------------------------------------------------------------
st.markdown("""
<div class="header-oficial">
    <div class="unidade">1ª COMPANHIA / 18º BATALHÃO POLICIAL MILITAR</div>
    <div class="endereco">Rua Prof. Armando Farias, s/nº – Pici (Campus do Pici - UFC) – Fortaleza-CE – CEP: 60.440-552</div>
    <div class="endereco">Telefone: (85) 98485-2398 – E-mail: 18bpm@policiamilitar.ce.gov.br</div>
    <div class="lema">"RAÇA DE FORTES, POVO DE BRAVOS"</div>
</div>
<div class="faixa-gov"></div>
""", unsafe_allow_html=True)

if img_pmce or img_ceara:
    col_l1, col_l2 = st.columns(2)
    if img_pmce:
        col_l1.markdown(f'<div style="text-align: right;"><img src="{img_pmce}" style="height:80px;"></div>', unsafe_allow_html=True)
    if img_ceara:
        col_l2.markdown(f'<div style="text-align: left;"><img src="{img_ceara}" style="height:80px;"></div>', unsafe_allow_html=True)

tab_registro, tab_admin = st.tabs(["📝 Novo Registro", "🔒 Painel de Controle - Comando"])

with tab_registro:
    st.subheader("Formulário de Cadastramento de Ocorrência")
    
    with st.form("form_ocorrencia", clear_on_submit=True):
        st.markdown("##### 🔹 Seção A - Dados Gerais da Ocorrência")
        
        equipe = st.selectbox("DESIGNAÇÃO DA EQUIPE*", ["Equipe Alfa", "Equipe Bravo", "Equipe Charlie", "Equipe Delta"], key="f_equipe")
        unidade = st.text_input("01 - UNIDADE (CIA/BTL)*", value="1º BPM / 1ª CIA", key="f_unidade")
        data_fato = st.date_input("02 - DATA*", value=st.session_state["data_default"], key="f_data").strftime("%d/%m/%Y")
        
        c_h1, c_h2 = st.columns(2)
        hora_inicial = c_h1.time_input("03 - HORA INICIAL*", value=st.session_state["hora_inicial_default"], key="f_h_ini").strftime("%H:%M")
        hora_final = c_h2.time_input("04 - HORA FINAL*", value=time(0, 30), key="f_h_fim").strftime("%H:%M")
        
        natureza = st.text_input("05 - NATUREZA DA OCORRÊNCIA (TIPO/ART.)*", key="f_natureza", placeholder="Ex: Art. 33 da Lei 11.343/06 (Tráfico de Drogas)")
        vtr = st.text_input("06 - FRAÇÃO (PREFIXO VTR)*", key="f_vtr", placeholder="Ex: CP-10112")
        ht = st.text_input("07 - Nº DO HT", key="f_ht", placeholder="Ex: HT-8842")
        ciops = st.text_input("08 - FICHA CIOPS/Nº COPOM", key="f_ciops", placeholder="Ex: 2026-00482")
        
        turno = st.selectbox("09 - TURNO", ["1º Turno (Matutino)", "2º Turno (Vespertino)", "3º Turno (Noturno)", "Extra / Especial"], key="f_turno")
        delegacia = st.text_input("10 - DELEGACIA DE DESTINO", key="f_delegacia", placeholder="Ex: Delegacia Regional")
        delegado = st.text_input("11 - DELEGADO(A)", key="f_delegado", placeholder="Nome do Delegado(a)")
        procedimentos = st.text_input("12 - N°(S) DOS PROCEDIMENTO(S)", key="f_procedimentos", placeholder="Ex: IP 452/2026, Mandado de P

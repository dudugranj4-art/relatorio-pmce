import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, time
from weasyprint import HTML
import base64
import os

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
    
    .btn-excluir > button {
        background-color: #B22222 !important;
    }
    .btn-excluir > button:hover {
        background-color: #8B0000 !important;
    }
</style>
""", unsafe_allow_html=True)

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

def gerar_pdf_ocorrencia(d):
    equipe_val = d.get('equipe', 'N/I')
    img_pmce_html = f"<img src='{img_pmce}'>" if img_pmce else ""
    img_ceara_html = f"<img src='{img_ceara}'>" if img_ceara else ""

    html_content = f"""<!DOCTYPE html>
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
        {img_pmce_html}
        {img_ceara_html}
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
            <td colspan="2"><span class="lbl">05 - NATUREZA DA OCORRÊNCIA</span><span class="val"><strong>{d['natureza']}</strong></span></td>
            <td class="bg"><span class="lbl">06 - FRAÇÃO / PREFIXO VTR</span><span class="val">{d['vtr']}</span></td>
            <td><span class="lbl">07 - DESIGNAÇÃO DA EQUIPE</span><span class="val"><strong>{equipe_val}</strong></span></td>
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
    img_pmce_html = f"<img src='{img_pmce}'>" if img_pmce else ""
    img_ceara_html = f"<img src='{img_ceara}'>" if img_ceara else ""
    
    rows_html = ""
    for idx, row in df_ranking.iterrows():
        pos = idx + 1
        if pos == 1:
            medalha = "1º"
        elif pos == 2:
            medalha = "2º"
        elif pos == 3:
            medalha = "3º"
        else:
            medalha = f"{pos}º"

        rows_html += f"""
        <tr>
            <td style="text-align:center; font-weight:bold; font-size:10pt;">{medalha}</td>
            <td style="font-weight:bold;">{row['Equipe']}</td>
            <td style="text-align:center;">{row['Total de Ocorrências']}</td>
            <td style="text-align:center;">{row['Tráfico']}</td>
            <td style="text-align:center;">{row['Apreensão de Arma']}</td>
            <td style="text-align:center;">{row['Mandado']}</td>
            <td style="text-align:center;">{row['Outros']}</td>
            <td style="text-align:center; font-weight:bold; color:#1B4D3E;">{row['Pontuação Total']}</td>
        </tr>
        """

    html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <style>
        @page {{ size: A4; margin: 12mm 10mm; }}
        body {{ font-family: Arial, sans-serif; font-size: 8.5pt; color: #111; line-height: 1.3; }}
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
        th {{ background-color: #1B4D3E; color: white; padding: 5px; font-size: 7.5pt; text-transform: uppercase; border: 1px solid #1B4D3E; }}
        td {{ border: 1px solid #CCC; padding: 5px; font-size: 8pt; }}
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
        {img_pmce_html}
        {img_ceara_html}
    </div>
    <div class="doc-title">RELATÓRIO ESTATÍSTICO DE DESEMPENHO E RANKING DAS EQUIPES</div>
    
    <p><strong>Data de Emissão:</strong> {data_atual}</p>
    
    <table>
        <thead>
            <tr>
                <th width="6%">POS</th>
                <th width="22%">EQUIPE</th>
                <th width="12%">OCORRÊNCIAS</th>
                <th width="10%">TRÁFICO</th>
                <th width="12%">ARMAS</th>
                <th width="10%">MANDADOS</th>
                <th width="8%">OUTROS</th>
                <th width="10%">PONTUAÇÃO</th>
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

opcoes_natureza = ["Tráfico", "Apreensão de arma", "Mandado", "Intervenção", "Outros"]

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
        
        natureza = st.selectbox("05 - NATUREZA DA OCORRÊNCIA*", opcoes_natureza, key="f_natureza")
        
        vtr = st.text_input("06 - FRAÇÃO (PREFIXO VTR)*", key="f_vtr", placeholder="Ex: CP-10112")
        ht = st.text_input("07 - Nº DO HT", key="f_ht", placeholder="Ex: HT-8842")
        ciops = st.text_input("08 - FICHA CIOPS/Nº COPOM", key="f_ciops", placeholder="Ex: 2026-00482")
        
        turno = st.selectbox("09 - TURNO", ["1º Turno (Matutino)", "2º Turno (Vespertino)", "3º Turno (Noturno)", "Extra / Especial"], key="f_turno")
        delegacia = st.text_input("10 - DELEGACIA DE DESTINO", key="f_delegacia", placeholder="Ex: Delegacia Regional")
        delegado = st.text_input("11 - DELEGADO(A)", key="f_delegado", placeholder="Nome do Delegado(a)")
        procedimentos = st.text_input("12 - N°(S) DOS PROCEDIMENTO(S)", key="f_procedimentos", placeholder="Ex: IP 452/2026, Mandado de Prisão")
        
        st.markdown("##### 🔹 Seção B - Equipe Policial")
        composicao = st.text_area("13 - COMPOSIÇÃO (INTEGRANTES DA EQUIPE)*", key="f_composicao", placeholder="Ex: 3º SGT PM Silva, CB PM Costa, SD PM Lima", height=80)
        condutor = st.text_input("14 - CONDUTOR (POSTO/GRAD, NOME E MATRÍCULA)*", key="f_condutor", placeholder="Ex: 3º SGT PM 18.234 Silva (Mat: 123.456-1-X)")
        testemunhas_policiais = st.text_input("15 - TESTEMUNHAS POLICIAIS", key="f_test_pol", placeholder="Ex: CB PM 25.109 Costa; SD PM 31.882 Lima")
        
        st.markdown("##### 🔹 Seção C - Localização e Envolvidos")
        local_ocorrencia = st.text_input("16 - LOCAL DA OCORRÊNCIA*", key="f_loc_oco", placeholder="Endereco completo ou referencia")
        local_abordagem = st.text_input("17 - LOCAL DA ABORDAGEM*", key="f_loc_abo", placeholder="Endereco exato da abordagem")
        acusado = st.text_input("18 - ACUSADO*", key="f_acusado", placeholder="Nome completo do acusado ou A apurar")
        vitimas = st.text_input("19 - VÍTIMAS*", key="f_vitimas", placeholder="Nome da vitima ou A Sociedade")
        testemunhas_povo = st.text_input("26 - TESTEMUNHAS DO POVO", value="Não identificadas no local", key="f_test_povo")
        
        c_r1, c_r2 = st.columns(2)
        ficaram_preso = c_r1.radio("29 - FICARAM PRESO?*", ["Sim", "Não"], horizontal=True, key="f_preso")
        suspeitos_menores = c_r2.radio("30 - SUSPEITOS MENORES?*", ["Não", "Sim"], horizontal=True, key="f_menor")
        
        st.markdown("##### 🔹 Seção D - Apreensões e Bens Recuperados")
        armas = st.text_input("20 - ARMA(S) APREENDIDA(S)", value="Nenhuma", key="f_armas")
        municao = st.text_input("21 - MUNIÇÃO APREENDIDA", value="Nenhuma", key="f_municao")
        drogas = st.text_input("22 - DROGA(S) APREENDIDA(S)", value="Nenhuma", key="f_drogas")
        veiculos = st.text_input("23 - VEÍCULO(S) RECUPERADO(S)", value="Nenhum", key="f_veiculos")
        quantia_recuperada = st.text_input("24 - QUANTIA RECUPERADA", value="R$ 0,00", key="f_qnt_rec")
        quantia_apreendida = st.text_input("25 - QUANTIA APREENDIDA", value="R$ 0,00", key="f_qnt_apr")
        objetos_recuperados = st.text_input("27 - OBJETO(S) RECUPERADO(S)", value="Nenhum", key="f_obj_rec")
        objetos_apreendidos = st.text_input("28 - OBJETO(S) APREENDIDO(S)", value="Nenhum", key="f_obj_apr")
        
        st.markdown("##### 🔹 Seção E - Histórico da Ocorrência")
        narrativa = st.text_area("31 - NARRATIVA SUCINTA DA OCORRÊNCIA*", height=160, key="f_narrativa", placeholder="Resumo claro, cronologico e impessoal do patrulhamento, abordagem, constatacao da infracao, apreensoes e conducao...")
        
        btn_submit = st.form_submit_button("🚨 SALVAR E REGISTRAR OCORRÊNCIA")
        
        if btn_submit:
            if not (unidade and natureza and vtr and composicao and condutor and local_ocorrencia and acusado and narrativa):
                st.error("Por favor, preencha todos os campos obrigatórios marcados com (*).")
            else:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO ocorrências (
                        unidade, data_fato, hora_inicial, hora_final, natureza, vtr, ht, ciops, turno,
                        delegacia, delegado, procedimentos, composicao, condutor, testemunhas_policiais,
                        local_ocorrencia, local_abordagem, acusado, vitimas, armas, municao, drogas,
                        veiculos, quantia_recuperada, quantia_apreendida, testemunhas_povo,
                        objetos_recuperados, objetos_apreendidos, ficaram_preso, suspeitos_menores,
                        narrativa, data_registro, equipe
                    ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                ''', (
                    unidade, data_fato, hora_inicial, hora_final, natureza, vtr, ht, ciops, turno,
                    delegacia, delegado, procedimentos, composicao, condutor, testemunhas_policiais,
                    local_ocorrencia, local_abordagem, acusado, vitimas, armas, municao, drogas,
                    veiculos, quantia_recuperada, quantia_apreendida, testemunhas_povo,
                    objetos_recuperados, objetos_apreendidos, ficaram_preso, suspeitos_menores,
                    narrativa, datetime.now().strftime("%d/%m/%Y %H:%M"), equipe
                ))
                conn.commit()
                st.success(f"✅ Ocorrência cadastrada com sucesso pela **{equipe}**! Protocolo gerado: Nº {cursor.lastrowid:06d}")

with tab_admin:
    st.subheader("Acesso Restrito ao Comando")
    
    with st.form("form_login_comando"):
        senha = st.text_input("Insira a Senha de Acesso Administrador", type="password", key="f_senha_adm")
        btn_entrar = st.form_submit_button("🔓 ENTRAR NO PAINEL")
    
    if btn_entrar:
        if senha == "comando2026":
            st.session_state["autenticado"] = True
        else:
            st.error("Senha incorreta. Acesso negado.")
            st.session_state["autenticado"] = False

    if st.session_state.get("autenticado", False):
        st.success("Autenticação realizada com sucesso!")
        df = pd.read_sql_query("SELECT * FROM ocorrências ORDER BY id DESC", conn)
        
        if 'equipe' not in df.columns:
            df['equipe'] = 'Equipe Alfa'
        df['equipe'] = df['equipe'].fillna('Equipe Alfa')
        
        st.markdown("---")
        st.markdown("## 🏆 Painel Geral de Desempenho e Ranking das Equipes")
        
        equipes_list = ["Equipe Alfa", "Equipe Bravo", "Equipe Charlie", "Equipe Delta"]
        stats = []

        for eq in equipes_list:
            df_eq = df[df['equipe'] == eq]
            tot_ocorr = len(df_eq)
            
            trafico = df_eq[df_eq['natureza'] == 'Tráfico'].shape[0]
            armas = df_eq[df_eq['natureza'] == 'Apreensão de arma'].shape[0]
            mandados = df_eq[df_eq['natureza'] == 'Mandado'].shape[0]
            intervencao = df_eq[df_eq['natureza'] == 'Intervenção'].shape[0]
            outros = df_eq[df_eq['natureza'] == 'Outros'].shape[0]
            
            pontos = (tot_ocorr * 1) + (trafico * 3) + (armas * 3) + (mandados * 2)
            
            stats.append({
                "Equipe": eq,
                "Total de Ocorrências": tot_ocorr,
                "Tráfico": trafico,
                "Apreensão de Arma": armas,
                "Mandado": mandados,
                "Intervenção": intervencao,
                "Outros": outros,
                "Pontuação Total": pontos
            })

        df_ranking = pd.DataFrame(stats).sort_values(by="Pontuação Total", ascending=False).reset_index(drop=True)
        
        c1, c2, c3, c4 = st.columns(4)
        cols = [c1, c2, c3, c4]
        for idx, row in df_ranking.iterrows():
            with cols[idx]:
                if idx == 0:
                    pos_str = "🥇 1º Lugar"
                elif idx == 1:
                    pos_str = "🥈 2º Lugar"
                elif idx == 2:
                    pos_str = "🥉 3º Lugar"
                else:
                    pos_str = "4º Lugar"
                
                st.metric(label=f"{pos_str} • {row['Equipe']}", value=f"{row['Pontuação Total']} pts", delta=f"{row['Total de Ocorrências']} Ocorrências")

        st.markdown("### 📊 Gráfico Comparativo por Natureza da Ocorrência")
        chart_data = df_ranking.set_index("Equipe")[["Tráfico", "Apreensão de Arma", "Mandado", "Intervenção", "Outros"]]
        st.bar_chart(chart_data)

        st.markdown("### 📋 Tabela Detalhada do Ranking")
        st.dataframe(df_ranking, use_container_width=True)

        pdf_ranking_bytes = gerar_pdf_ranking(df_ranking)
        st.download_button(
            label="📄 BAIXAR RELATÓRIO ESTATÍSTICO DE RANKING EM PDF",
            data=pdf_ranking_bytes,
            file_name=f"Ranking_Equipes_PMCE_{datetime.now().strftime('%d_%m_%Y')}.pdf",
            mime="application/pdf",
            use_container_width=True,
            key="btn_pdf_ranking"
        )
        
        st.markdown("---")
        if not df.empty:
            st.markdown("### 🔍 Pesquisa e Filtros de Ocorrências")
            c_f1, c_f2, c_f3 = st.columns(3)
            filtro_vtr = c_f1.text_input("Filtrar por Viatura (VTR)", key="f_filt_vtr")
            filtro_acusado = c_f2.text_input("Filtrar por Acusado", key="f_filt_acu")
            filtro_equipe = c_f3.selectbox("Filtrar por Equipe", ["Todas"] + equipes_list, key="f_filt_eq")
            
            df_filtered = df.copy()
            if filtro_vtr:
                df_filtered = df_filtered[df_filtered['vtr'].str.contains(filtro_vtr, case=False, na=False)]
            if filtro_acusado:
                df_filtered = df_filtered[df_filtered['acusado'].str.contains(filtro_acusado, case=False, na=False)]
            if filtro_equipe != "Todas":
                df_filtered = df_filtered[df_filtered['equipe'] == filtro_equipe]
                
            st.dataframe(
                df_filtered[['id', 'data_fato', 'equipe', 'unidade', 'vtr', 'natureza', 'acusado', 'ficaram_preso']],
                use_container_width=True
            )
            
            st.markdown("---")
            st.markdown("### ✏️ Gerenciar Ocorrência Específica")
            id_selecionado = st.number_input("Informe o Número do Protocolo (ID)", min_value=1, max_value=int(df['id'].max()), step=1, key="f_id_sel")
            ocorrencia_row = df[df['id'] == id_selecionado]
            
            if not ocorrencia_row.empty:
                d = ocorrencia_row.iloc[0].to_dict()
                col_btn1, col_btn2, col_btn3 = st.columns(3)
                
                with col_btn1:
                    pdf_data = gerar_pdf_ocorrencia(d)
                    st.download_button(
                        label="📄 BAIXAR RELATÓRIO OFICIAL EM PDF",
                        data=pdf_data,
                        file_name=f"Relatorio_PMCE_{d['id']:06d}.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                        key="f_btn_pdf"
                    )
                
                with col_btn2:
                    st.info(f"Ocorrência Selecionada: Protocolo #{d['id']:06d} ({d.get('equipe', 'Equipe Alfa')})")
                
                with col_btn3:
                    with st.expander("⚠️ Excluir ocorrência", expanded=False):
                        st.warning("Essa ação é **irreversível**. Deseja realmente excluir?")
                        if st.button("🗑️ CONFIRMAR EXCLUSÃO", key="btn_excluir", use_container_width=True):
                            cursor = conn.cursor()
                            cursor.execute("DELETE FROM ocorrências WHERE id = ?", (id_selecionado,))
                            conn.commit()
                            st.success(f"Ocorrência #{id_selecionado:06d} excluída permanentemente.")
                            st.rerun()
                
                with st.expander("🛠️ Clique para EDITAR os campos desta ocorrência"):
                    with st.form("edit_form"):
                        e_equipe = st.selectbox("Equipe", equipes_list, index=equipes_list.index(d.get('equipe', 'Equipe Alfa')), key="e_eq")
                        e_unidade = st.text_input("Unidade", value=d['unidade'], key="e_uni")
                        
                        idx_nat = opcoes_natureza.index(d['natureza']) if d['natureza'] in opcoes_natureza else 4
                        e_natureza = st.selectbox("Natureza da Ocorrência", opcoes_natureza, index=idx_nat, key="e_nat")
                        
                        e_procedimentos = st.text_input("Procedimentos", value=d['procedimentos'], key="e_proc")
                        e_acusado = st.text_input("Acusado", value=d['acusado'], key="e_acu")
                        e_narrativa = st.text_area("Narrativa", value=d['narrativa'], height=120, key="e_nar")
                        
                        btn_salvar_edicao = st.form_submit_button("Salvar Alterações no Banco de Dados")
                        if btn_salvar_edicao:
                            cursor = conn.cursor()
                            cursor.execute('''
                                UPDATE ocorrências 
                                SET equipe=?, unidade=?, natureza=?, procedimentos=?, acusado=?, narrativa=? 
                                WHERE id=?
                            ''', (e_equipe, e_unidade, e_natureza, e_procedimentos, e_acusado, e_narrativa, id_selecionado))
                            conn.commit()
                            st.success("Ocorrência alterada com sucesso!")
                            st.rerun()
            else:
                st.info("Nenhuma ocorrência encontrada com este ID.")
        else:
            st.info("Nenhuma ocorrência registrada até o momento.")

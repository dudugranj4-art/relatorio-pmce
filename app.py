import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
from weasyprint import HTML
import io

# -----------------------------------------------------------------------------
# 1. CONFIGURAÇÃO DA PÁGINA E CSS PERSONALIZADO (IDENTIDADE PMCE)
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="PMCE - Registro de Ocorrência",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    /* Cores Institucionais PMCE */
    :root {
        --verde-oliva: #1B4D3E;
        --azul-marinho: #002B49;
        --dourado: #DAA520;
        --fundo-cinza: #F4F6F7;
    }
    
    .stApp {
        background-color: var(--fundo-cinza);
    }
    
    .pmce-header {
        background-color: var(--verde-oliva);
        color: white;
        padding: 20px;
        border-radius: 8px;
        text-align: center;
        border-bottom: 5px solid var(--dourado);
        margin-bottom: 25px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .pmce-header h3 {
        color: var(--dourado);
        margin: 0;
        font-size: 1.1rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .pmce-header h1 {
        margin: 5px 0;
        font-size: 1.8rem;
        font-weight: 800;
    }
    
    .pmce-header p {
        margin: 0;
        font-size: 0.95rem;
        opacity: 0.9;
    }
    
    .section-box {
        background-color: white;
        padding: 20px;
        border-radius: 8px;
        border-left: 5px solid var(--azul-marinho);
        margin-bottom: 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    .stButton > button {
        background-color: var(--verde-oliva);
        color: white;
        font-weight: bold;
        border: none;
        padding: 10px 24px;
        border-radius: 5px;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background-color: var(--azul-marinho);
        color: var(--dourado);
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. CAMADA DE BANCO DE DADOS (SQLITE)
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
            narrativa TEXT, data_registro TEXT
        )
    ''')
    conn.commit()
    return conn

conn = init_db()

# -----------------------------------------------------------------------------
# 3. GERADOR DE PDF FORMATADO (WEASYPRINT)
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
            .header {{ border-bottom: 3px solid #1B4D3E; padding-bottom: 6px; text-align: center; margin-bottom: 10px; }}
            .header-title {{ font-size: 10pt; font-weight: bold; color: #1B4D3E; text-transform: uppercase; }}
            .header-subtitle {{ font-size: 8.5pt; color: #333; font-weight: bold; margin: 2px 0; }}
            .header-doc {{ display: inline-block; background-color: #1B4D3E; color: #FFF; font-weight: bold; padding: 4px 12px; font-size: 9.5pt; margin-top: 4px; border-radius: 3px; }}
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
        <div class="header">
            <div class="header-title">GOVERNO DO ESTADO DO CEARÁ</div>
            <div class="header-subtitle">SECRETARIA DA SEGURANÇA PÚBLICA E DEFESA SOCIAL</div>
            <div class="header-subtitle">POLÍCIA MILITAR DO CEARÁ - PMCE</div>
            <div class="header-doc">RELATÓRIO DE OCORRÊNCIA POLICIAL Nº {d['id']:06d}</div>
        </div>

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
                <td><span class="lbl">07 - Nº DO HT</span><span class="val">{d['ht']}</span></td>
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
        <div class="box-narrativa">31 - NARRATIVA:\n{d['narrativa']}</div>

        <div class="footer">
            <div class="sig"><strong>{d['condutor']}</strong><br>Condutor da Ocorrência</div>
            <div class="sig"><strong>{d['delegado']}</strong><br>Delegado(a) / Autoridade Policial</div>
        </div>
    </body>
    </html>
    """
    return HTML(string=html_content).write_pdf()

# -----------------------------------------------------------------------------
# 4. INTERFACE DO USUÁRIO
# -----------------------------------------------------------------------------

# Cabeçalho Institucional
st.markdown("""
<div class="pmce-header">
    <h3>Governo do Estado do Ceará • SSPDS</h3>
    <h1>POLÍCIA MILITAR DO CEARÁ</h1>
    <p>Sistema Eletrônico de Registro de Ocorrência Policial (ROP)</p>
</div>
""", unsafe_allow_html=True)

tab_registro, tab_admin = st.tabs(["📝 Novo Registro", "🔒 Painel de Controle - Comando"])

# -----------------------------------------------------------------------------
# ABA 1: NOVO REGISTRO (FORMULÁRIO PÚBLICO COM OS 31 CAMPOS)
# -----------------------------------------------------------------------------
with tab_registro:
    st.subheader("Formulário de Cadastramento de Ocorrência")
    
    with st.form("form_ocorrencia", clear_on_submit=True):
        st.markdown("##### 🔹 Seção A - Dados Gerais da Ocorrência")
        c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
        unidade = c1.text_input("01 - UNIDADE (CIA/BTL)*", placeholder="Ex: 1º BPM / 1ª CIA - Russas")
        data_fato = c2.date_input("02 - DATA*", datetime.now()).strftime("%d/%m/%Y")
        hora_inicial = c3.time_input("03 - HORA INICIAL*", value=datetime.now().time()).strftime("%H:%M")
        hora_final = c4.time_input("04 - HORA FINAL*", value=datetime.now().time()).strftime("%H:%M")
        
        c5, c6, c7, c8 = st.columns([2, 1, 1, 1])
        natureza = c5.text_input("05 - NATUREZA DA OCORRÊNCIA (TIPO/ART.)*", placeholder="Ex: Art. 33 da Lei 11.343/06")
        vtr = c6.text_input("06 - FRAÇÃO (PREFIXO VTR)*", placeholder="Ex: CP-10112")
        ht = c7.text_input("07 - Nº DO HT", placeholder="Ex: HT-8842")
        ciops = c8.text_input("08 - FICHA CIOPS/Nº COPOM", placeholder="Ex: 2026-00482")
        
        c9, c10, c11, c12 = st.columns(4)
        turno = c9.selectbox("09 - TURNO", ["1º Turno (Matutino)", "2º Turno (Vespertino)", "3º Turno (Noturno)", "Extra / Especial"])
        delegacia = c10.text_input("10 - DELEGACIA DE DESTINO", placeholder="Ex: Delegacia Regional")
        delegado = c11.text_input("11 - DELEGADO(A)", placeholder="Nome do Delegado(a)")
        procedimentos = c12.text_input("12 - N°(S) DOS PROCEDIMENTO(S)", placeholder="Ex: IP 452/2026, APFD 882/2026")
        
        st.markdown("##### 🔹 Seção B - Equipe Policial")
        composicao = st.text_area("13 - COMPOSIÇÃO (INTEGRANTES DA EQUIPE)*", placeholder="Ex: 3º SGT PM Silva, CB PM Costa, SD PM Lima", height=70)
        
        c13, c14 = st.columns(2)
        condutor = c13.text_input("14 - CONDUTOR (POSTO/GRAD, NOME E MATRÍCULA)*", placeholder="Ex: 3º SGT PM 18.234 Silva (Mat: 123.456-1-X)")
        testemunhas_policiais = c14.text_input("15 - TESTEMUNHAS POLICIAIS", placeholder="Ex: CB PM 25.109 Costa; SD PM 31.882 Lima")
        
        st.markdown("##### 🔹 Seção C - Localização e Envolvidos")
        c15, c16 = st.columns(2)
        local_ocorrencia = c15.text_input("16 - LOCAL DA OCORRÊNCIA*", placeholder="Endereço completo ou referência")
        local_abordagem = c16.text_input("17 - LOCAL DA ABORDAGEM*", placeholder="Endereço exato da abordagem")
        
        c17, c18 = st.columns(2)
        acusado = c17.text_input("18 - ACUSADO*", placeholder="Nome completo do acusado ou 'A apurar'")
        vitimas = c18.text_input("19 - VÍTIMAS*", placeholder="Nome da vítima ou 'A Sociedade'")
        
        c19, c20, c21 = st.columns([2, 1, 1])
        testemunhas_povo = c19.text_input("26 - TESTEMUNHAS DO POVO", value="Não identificadas no local")
        ficaram_preso = c20.radio("29 - FICARAM PRESO?*", ["Sim", "Não"], horizontal=True)
        suspeitos_menores = c21.radio("30 - SUSPEITOS MENORES?*", ["Não", "Sim"], horizontal=True)
        
        st.markdown("##### 🔹 Seção D - Apreensões e Bens Recuperados")
        c22, c23 = st.columns(2)
        armas = c22.text_input("20 - ARMA(S) APREENDIDA(S)", value="Nenhuma")
        municao = c23.text_input("21 - MUNIÇÃO APREENDIDA", value="Nenhuma")
        
        c24, c25 = st.columns(2)
        drogas = c24.text_input("22 - DROGA(S) APREENDIDA(S)", value="Nenhuma")
        veiculos = c25.text_input("23 - VEÍCULO(S) RECUPERADO(S)", value="Nenhum")
        
        c26, c27 = st.columns(2)
        quantia_recuperada = c26.text_input("24 - QUANTIA RECUPERADA", value="R$ 0,00")
        quantia_apreendida = c27.text_input("25 - QUANTIA APREENDIDA", value="R$ 0,00")
        
        c28, c29 = st.columns(2)
        objetos_recuperados = c28.text_input("27 - OBJETO(S) RECUPERADO(S)", value="Nenhum")
        objetos_apreendidos = c29.text_input("28 - OBJETO(S) APREENDIDO(S)", value="Nenhum")
        
        st.markdown("##### 🔹 Seção E - Histórico da Ocorrência")
        narrativa = st.text_area("31 - NARRATIVA SUCINTA DA OCORRÊNCIA*", height=160, placeholder="Resumo claro, cronológico e impessoal do patrulhamento, abordagem, constatação da infração, apreensões e condução...")
        
        btn_submit = st.form_submit_button("🚨 SALVAR E REGISTRAR OCORRÊNCIA", use_container_width=True)
        
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
                        narrativa, data_registro
                    ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                ''', (
                    unidade, data_fato, hora_inicial, hora_final, natureza, vtr, ht, ciops, turno,
                    delegacia, delegado, procedimentos, composicao, condutor, testemunhas_policiais,
                    local_ocorrencia, local_abordagem, acusado, vitimas, armas, municao, drogas,
                    veiculos, quantia_recuperada, quantia_apreendida, testemunhas_povo,
                    objetos_recuperados, objetos_apreendidos, ficaram_preso, suspeitos_menores,
                    narrativa, datetime.now().strftime("%d/%m/%Y %H:%M")
                ))
                conn.commit()
                st.success(f"✅ Ocorrência cadastrada com sucesso! Protocolo gerado: Nº {cursor.lastrowid:06d}")

# -----------------------------------------------------------------------------
# ABA 2: PAINEL DE CONTROLE DO COMANDO (CONSULTA, EDIÇÃO E PDF)
# -----------------------------------------------------------------------------
with tab_admin:
    st.subheader("Acesso Restrito ao Comando")
    
    senha = st.text_input("Insira a Senha de Acesso Administrador", type="password")
    
    if senha == "comando2026":  # Defina a senha desejada aqui
        st.success("Autenticação realizada com sucesso!")
        
        df = pd.read_sql_query("SELECT * FROM ocorrências ORDER BY id DESC", conn)
        
        if not df.empty:
            st.markdown("### 🔍 Pesquisa e Filtros")
            c_f1, c_f2, c_f3 = st.columns(3)
            filtro_vtr = c_f1.text_input("Filtrar por Viatura (VTR)")
            filtro_acusado = c_f2.text_input("Filtrar por Acusado")
            filtro_unidade = c_f3.text_input("Filtrar por Unidade")
            
            df_filtered = df.copy()
            if filtro_vtr:
                df_filtered = df_filtered[df_filtered['vtr'].str.contains(filtro_vtr, case=False, na=False)]
            if filtro_acusado:
                df_filtered = df_filtered[df_filtered['acusado'].str.contains(filtro_acusado, case=False, na=False)]
            if filtro_unidade:
                df_filtered = df_filtered[df_filtered['unidade'].str.contains(filtro_unidade, case=False, na=False)]
                
            st.dataframe(
                df_filtered[['id', 'data_fato', 'unidade', 'vtr', 'natureza', 'acusado', 'ficaram_preso']],
                use_container_width=True
            )
            
            st.markdown("---")
            st.markdown("### ✏️ Gerenciar Ocorrência Específica")
            
            id_selecionado = st.number_input("Informe o Número do Protocolo (ID)", min_value=1, max_value=int(df['id'].max()), step=1)
            
            ocorrencia_row = df[df['id'] == id_selecionado]
            
            if not ocorrencia_row.empty:
            d = ocorrencia_row.iloc[0].to_dict()
            

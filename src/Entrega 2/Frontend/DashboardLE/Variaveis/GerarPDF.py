from fpdf import FPDF
import io
import plotly.io as pio


def gerar_pdf_relatorio_estilizado(nome_grupo, mentor, integrantes, total_kg, df_dados, figs=None):
    """
    figs: Lista de objetos figure do Plotly [fig_evolucao, fig_distribuicao]
    """
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # --- CABEÇALHO ---
    # Logo (posicionado de forma fixa para não sobrepor)
    try:
        pdf.image("./assets/liderancas_logo.png", x=10, y=10, w=30)
    except:
        pdf.set_xy(10, 10)
        pdf.set_font("Helvetica", 'B', 12)
        pdf.cell(30, 10, "LOGO", border=1, align="C")

    # Título do Relatório (Deslocado para a direita do logo)
    pdf.set_xy(45, 15)
    pdf.set_font("Helvetica", 'B', 18)
    pdf.set_text_color(31, 119, 180)  # Azul
    pdf.cell(0, 10, "RELATÓRIO DE ARRECADAÇÃO", ln=True, align="L")

    pdf.set_xy(45, 23)
    pdf.set_font("Helvetica", '', 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 10, "Programa Lideranças Empáticas - Gestão de Impacto Social", ln=True, align="L")

    pdf.ln(15)  # Espaço após cabeçalho
    pdf.set_draw_color(31, 119, 180)
    pdf.line(10, 40, 200, 40)  # Linha divisória horizontal

    # --- INFO DO GRUPO (BOX ESTILIZADO) ---
    pdf.set_fill_color(245, 245, 245)
    pdf.rect(10, 45, 190, 35, 'F')  # Fundo cinza claro

    pdf.set_xy(15, 48)
    pdf.set_font("Helvetica", 'B', 12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 7, f"Equipe: {nome_grupo}", ln=True)

    pdf.set_font("Helvetica", '', 11)
    pdf.cell(0, 7, f"Mentor Responsável: {mentor}", ln=True)

    integrantes_str = ", ".join(integrantes)
    pdf.multi_cell(0, 7, f"Integrantes: {integrantes_str}")

    # --- TOTAL ARRECADADO (DESTAQUE) ---
    # Alinhado à direita dentro do box ou logo abaixo
    pdf.set_xy(140, 48)
    pdf.set_font("Helvetica", 'B', 14)
    pdf.set_text_color(31, 119, 180)
    pdf.cell(55, 10, f"TOTAL: {total_kg:.2f} kg", border=0, align="R")

    pdf.ln(25)

    # --- GRÁFICOS (Se fornecidos) ---
    if figs:
        pdf.set_font("Helvetica", 'B', 12)
        pdf.set_text_color(31, 119, 180)
        pdf.cell(0, 10, "Análise Visual de Dados", ln=True)
        pdf.ln(2)

        y_atual = pdf.get_y()
        for i, fig in enumerate(figs):
            # Converte Plotly para imagem PNG em memória
            img_bytes = pio.to_image(fig, format="png", width=600, height=350)
            img_io = io.BytesIO(img_bytes)

            # Posiciona dois gráficos lado a lado (ou um embaixo do outro)
            if i == 0:
                pdf.image(img_io, x=10, y=y_atual, w=90)
            else:
                pdf.image(img_io, x=105, y=y_atual, w=90)

        pdf.set_y(y_atual + 55)  # Pula o espaço ocupado pelas imagens
        pdf.ln(10)

    # --- TABELA DE DADOS ---
    pdf.set_font("Helvetica", 'B', 11)
    pdf.set_text_color(31, 119, 180)
    pdf.cell(0, 10, "Detalhamento das Coletas", ln=True)

    # Cabeçalho da Tabela
    pdf.set_font("Helvetica", 'B', 10)
    pdf.set_fill_color(31, 119, 180)
    pdf.set_text_color(255, 255, 255)

    cols = [50, 40, 20, 25, 55]
    headers = ["Alimento", "Marca", "Qtd", "Peso", "Data/Hora"]

    for i, h in enumerate(headers):
        pdf.cell(cols[i], 10, h, border=0, align="C", fill=True)
    pdf.ln()

    # Linhas da Tabela
    pdf.set_font("Helvetica", '', 9)
    pdf.set_text_color(0, 0, 0)
    fill = False

    for _, row in df_dados.iterrows():
        # Zebra striping (fundo alternado)
        if fill:
            pdf.set_fill_color(240, 248, 255)
        else:
            pdf.set_fill_color(255, 255, 255)

        pdf.cell(cols[0], 8, str(row.get('nome', row.get('Alimento', '')))[:28], border="B", fill=True)
        pdf.cell(cols[1], 8, str(row.get('marca', row.get('Marca', '')))[:20], border="B", fill=True)
        pdf.cell(cols[2], 8, str(row.get('quantidade', row.get('Qtd', ''))), border="B", align="C", fill=True)
        pdf.cell(cols[3], 8, f"{row.get('peso', row.get('Peso (kg)', ''))}kg", border="B", align="C", fill=True)

        data_str = str(row.get('dataHora', row.get('Data e Hora', '')))[:16]
        pdf.cell(cols[4], 8, data_str, border="B", align="C", fill=True)

        pdf.ln()
        fill = not fill  # Alterna a cor

    return bytes(pdf.output())
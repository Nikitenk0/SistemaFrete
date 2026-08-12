from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from datetime import datetime


def gerar_orcamento_pdf(dados, caminho):
    """
    Gera um PDF com os dados do orçamento.

    Parâmetros:
        dados: dicionário contendo os dados do orçamento.
        caminho: caminho onde o PDF será salvo.
    """

    pdf = canvas.Canvas(
        caminho,
        pagesize=A4
    )

    largura, altura = A4

    # ==========================================================
    # TÍTULO
    # ==========================================================

    pdf.setFont(
        "Helvetica-Bold",
        20
    )

    pdf.drawCentredString(
        largura / 2,
        altura - 3 * cm,
        "ORÇAMENTO"
    )

    # ==========================================================
    # DATA
    # ==========================================================

    pdf.setFont(
        "Helvetica",
        10
    )

    data = datetime.now().strftime(
        "%d/%m/%Y %H:%M"
    )

    pdf.drawRightString(
        largura - 2 * cm,
        altura - 4 * cm,
        f"Data: {data}"
    )

    # ==========================================================
    # LINHA
    # ==========================================================

    pdf.line(
        2 * cm,
        altura - 4.5 * cm,
        largura - 2 * cm,
        altura - 4.5 * cm
    )

    # ==========================================================
    # DADOS DO ORÇAMENTO
    # ==========================================================

    y = altura - 6 * cm

    # ---------- Origem ----------

    pdf.setFont(
        "Helvetica-Bold",
        12
    )

    pdf.drawString(
        3 * cm,
        y,
        "Origem:"
    )

    pdf.setFont(
        "Helvetica",
        12
    )

    pdf.drawString(
        7 * cm,
        y,
        dados["origem"]
    )

    # ---------- Destino ----------

    y -= 1 * cm

    pdf.setFont(
        "Helvetica-Bold",
        12
    )

    pdf.drawString(
        3 * cm,
        y,
        "Destino:"
    )

    pdf.setFont(
        "Helvetica",
        12
    )

    pdf.drawString(
        7 * cm,
        y,
        dados["destino"]
    )

    # ---------- Distância ----------

    y -= 1 * cm

    pdf.setFont(
        "Helvetica-Bold",
        12
    )

    pdf.drawString(
        3 * cm,
        y,
        "Distância:"
    )

    pdf.setFont(
        "Helvetica",
        12
    )

    pdf.drawString(
        7 * cm,
        y,
        dados["distancia"]
    )

    # ---------- Pedágio ----------

    y -= 1 * cm

    pdf.setFont(
        "Helvetica-Bold",
        12
    )

    pdf.drawString(
        3 * cm,
        y,
        "Pedágio:"
    )

    pdf.setFont(
        "Helvetica",
        12
    )

    pdf.drawString(
        7 * cm,
        y,
        dados["pedagio"]
    )

    # ==========================================================
    # VALOR GERAL
    # ==========================================================

    y -= 2 * cm

    pdf.line(
        3 * cm,
        y + 0.5 * cm,
        largura - 3 * cm,
        y + 0.5 * cm
    )

    pdf.setFont(
        "Helvetica-Bold",
        14
    )

    pdf.drawString(
        3 * cm,
        y,
        "VALOR GERAL:"
    )

    pdf.drawString(
        7 * cm,
        y,
        dados["geral"]
    )

    # ==========================================================
    # FINALIZA
    # ==========================================================

    pdf.save()
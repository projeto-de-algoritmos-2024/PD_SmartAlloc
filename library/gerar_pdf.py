import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime
import flet as ft


class PDF:
    def __init__(self, resultado, diretorio):
        self.resultado = resultado
        self.diretorio = diretorio
        self.data_atual = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    def criar_pdf(self):
        if not os.path.exists(self.diretorio + "/pdfs"):
            os.makedirs(self.diretorio + "/pdfs")

        caminho_pdf = self.diretorio + "/pdfs/resultado-processamento-" + self.data_atual + ".pdf"

        c = canvas.Canvas(caminho_pdf, pagesize=letter)
        c.setFont("Helvetica", 12)
        
        imagem = self.diretorio + "/assets/header_pdf.png"

        c.drawImage(imagem, 0, 730, width=614.4, height=44.8)
        c.drawString(100, 680, "Resultado do processamento:")
        y = 650
        for linha in self.resultado.split("\n"):
            c.drawString(100, y, linha)
            y -= 20
        
        c.save()

        return caminho_pdf

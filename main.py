import flet as ft
from library.gerar_pdf import PDF
import os

diretorio_atual = os.path.dirname(os.path.abspath(__file__))

def encontrar_p(j, trabalhos):
    for i in range(j - 1, -1, -1):
        if trabalhos[i][2] <= trabalhos[j][1]:
            return i
    return -1

def calcular_weighted_interval_scheduling(trabalhos):
    trabalhos_processados = []
    for trabalho in trabalhos:
        try:
            servico, inicio, fim, valor_servico = trabalho.split(",")
            inicio_h, inicio_m = map(int, inicio.strip().split(":"))
            fim_h, fim_m = map(int, fim.strip().split(":"))
            valor_servico = float(valor_servico.strip())
            trabalhos_processados.append((servico.strip(), inicio_h * 60 + inicio_m, fim_h * 60 + fim_m, valor_servico))
        except ValueError:
            return "Erro de Entrada: Formato inválido!"
    
    trabalhos_processados.sort(key=lambda x: x[2])
    n = len(trabalhos_processados)
    p = [encontrar_p(j, trabalhos_processados) for j in range(n)]
    
    M = [0] * (n + 1)
    for j in range(1, n + 1):
        M[j] = max(trabalhos_processados[j - 1][3] + M[p[j - 1] + 1], M[j - 1])
    
    selecionadas = []
    j = n
    while j > 0:
        if trabalhos_processados[j - 1][3] + M[p[j - 1] + 1] > M[j - 1]:
            selecionadas.append(trabalhos_processados[j - 1])
            j = p[j - 1] + 1
        else:
            j -= 1
    
    selecionadas.reverse()

    total_valor = sum(trabalho[3] for trabalho in selecionadas)

    resultado = "\n".join([f"{trabalho[0]} ({trabalho[1]//60:02}:{trabalho[1]%60:02} - {trabalho[2]//60:02}:{trabalho[2]%60:02}, Valor: R$ {trabalho[3]:.2f})" for trabalho in selecionadas])
    resultado += f"\n\nValor total dos serviços selecionados: R$ {total_valor:.2f}"

    return resultado if resultado else "Nenhum trabalho selecionado."


def main(page: ft.Page):
    page.title = "SmartAlloc"
    page.scroll = "adaptive"
    page.padding = ft.Padding(left=70, top=10, right=0, bottom=10)

    def gerar_pdf(resultado):
        pdf = PDF(resultado, diretorio_atual)
        caminho_pdf = pdf.criar_pdf()

        if(caminho_pdf):
            alerta = ft.AlertDialog(
                title=ft.Text("PDF Gerado"),
                content=ft.Text(f"O PDF foi gerado com sucesso em: {caminho_pdf}"),
            )
            page.dialog = alerta
            alerta.open = True
            page.update()


    def voltar_home(e):
        page.clean()
        page.add(header, elementos_home)
        page.update()


    header = ft.Row([
        ft.Image(src=diretorio_atual + "/assets/logoPD.png", width=100, height=100),
        ft.Text("SmartAlloc", size=44, weight="bold"),
    ], alignment="center")
    
    def mostrar_intervalo_peso(e):
        page.clean()
        page.add(header, ft.ElevatedButton("Voltar", on_click=voltar_home))
        interval_elementos = ft.Column()
        input_area = ft.TextField(label="Descrição, hora início, hora fim, valor", multiline=True, height=150, width=600)
        
        def calcular_inter(e):
            trabalhos = input_area.value.strip().split("\n")
            resultado = calcular_weighted_interval_scheduling(trabalhos)
            interval_elementos.controls.clear()
            resultado_txt = ft.Text("Resultado", size=30, weight="bold")
        
            gerar_pdf_btn = ft.ElevatedButton("Gerar PDF", on_click=lambda e: gerar_pdf(resultado))

            if(resultado != 'Erro de Entrada: Formato inválido!'):
                interval_elementos.controls.append(resultado_txt)
                interval_elementos.controls.append(gerar_pdf_btn)

            interval_elementos.controls.append(ft.Text(resultado))


            page.update()
        
        intervalo_controles = ft.Column([
            ft.Text("Agendamento de intervalo com peso", size=30, weight="bold"),
            ft.Text("\nInsira um trabalho por linha no formato: Descrição, hora início, hora fim, valor\nEx: Instalar luz da Fernanda Torres, 08:00, 11:00, 30.99\n\n"),
            input_area,
            ft.ElevatedButton("Calcular", on_click=calcular_inter),
            ft.Text("\n"),
            interval_elementos
        ])
        
        page.add(intervalo_controles)
        page.update()
    
    elementos_home = ft.Column([
        ft.Text("COLOCAR AQUI O TEXTO DE APRESENTAÇÃO"),
        ft.ElevatedButton("Agendamento de trabalhos", on_click=mostrar_intervalo_peso),
        ft.Text("\n\n\n")
    ],
    )
    
    page.add(header, elementos_home)

ft.app(target=main)
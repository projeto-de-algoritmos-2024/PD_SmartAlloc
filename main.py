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

def veiculo_entrega(capacidade, itens):
    n = len(itens)
    M = [[0] * (int(capacidade * 10) + 1) for _ in range(n + 1)]
    
    for i in range(1, n + 1):
        nome, peso, lucro = itens[i - 1]
        peso = int(peso * 10)
        for w in range(int(capacidade * 10) + 1):
            if peso > w:
                M[i][w] = M[i - 1][w]
            else:
                M[i][w] = max(M[i - 1][w], lucro + M[i - 1][w - peso])
    
    selecionados = []
    w = int(capacidade * 10)
    for i in range(n, 0, -1):
        if M[i][w] != M[i - 1][w]:
            selecionados.append(itens[i - 1])
            w -= int(itens[i - 1][1] * 10)
    
    return M[n][int(capacidade * 10)], selecionados


def main(page: ft.Page):
    page.title = "SmartAlloc"
    page.scroll = "adaptive"
    page.padding = ft.Padding(left=70, top=10, right=70, bottom=10)

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
        page.padding = ft.Padding(left=70, top=10, right=0, bottom=10)
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
    
    def mostrar_veiculo_entrega(e):
        page.padding = ft.Padding(left=70, top=10, right=0, bottom=10)
        page.clean()
        page.add(header, ft.ElevatedButton("Voltar", on_click=voltar_home))
        veiculo_elementos = ft.Column()
        capacidade_input = ft.TextField(label="Capacidade do Veículo (em kg)", width=600)
        itens_input = ft.TextField(label="Insira um item por linha (Nome, Peso, Lucro)", multiline=True, height=150, width=600)
        resultado_text = ft.Text("", selectable=True)
        
        def calcular_veiculo_entrega_action(e):
            try:
                capacidade = float(capacidade_input.value)
                itens_brutos = itens_input.value.strip().split("\n")
                itens = []
                
                for item in itens_brutos:
                    nome, peso, lucro = item.split(",")
                    itens.append((nome.strip(), float(peso.strip()), float(lucro.strip())))
                
                lucro_maximo, selecionados = veiculo_entrega(capacidade, itens)
                
                resultado = f"Lucro máximo: {lucro_maximo}\nItens selecionados:\n"
                for nome, peso, lucro in selecionados:
                    resultado += f"{nome} (Peso: {peso}, Lucro: {lucro})\n"
                
                resultado_text.value = resultado.strip()
                
                gerar_pdf_btn = ft.ElevatedButton("Gerar PDF", on_click=lambda e: gerar_pdf(resultado))
                veiculo_elementos.controls.append(gerar_pdf_btn)

                page.update()
            except ValueError:
                resultado_text.value = "Erro de Entrada: Formato inválido!"
                page.update()
        
        def gerar_pdf_veiculo_action(e):
            gerar_pdf(resultado_text.value)
        
        veiculo_controles = ft.Column([
            ft.Text("Veículo de Entrega - Maximização de Lucro", size=30, weight="bold"),
            ft.Text("\nInsira a capacidade do veículo e os itens no formato: Nome, Peso, Lucro\nEx: Item1, 10.5, 99.99\n\n"),
            capacidade_input,
            itens_input,
            ft.ElevatedButton("Calcular", on_click=calcular_veiculo_entrega_action),
            ft.Text("\n"),
            resultado_text,
        ])
        
        page.add(veiculo_controles)
        page.update()

    
    elementos_home = ft.Column([
        ft.Text("Este projeto oferece duas opções para resolver problemas práticos de alocação de tempo e recursos, com o objetivo de maximizar o lucro:\n✅ Weighted Interval Scheduling: Organiza seu dia para realizar os trabalhos com maior retorno financeiro dentro de um intervalo específico. O usuário insere horários de início, fim e o valor do trabalho, e o algoritmo determina o melhor conjunto de tarefas para maximizar o lucro.\n✅ Knapsack Problem: Organiza a alocação de itens para veículos de entrega. O usuário insere a capacidade do veículo, itens, peso e lucro de cada item, e o algoritmo seleciona os melhores itens para maximizar o uso da capacidade do veículo e o lucro obtido."),
        ft.ElevatedButton("Agendamento de trabalhos", on_click=mostrar_intervalo_peso),
        ft.ElevatedButton("Veículo de Entrega", on_click=mostrar_veiculo_entrega),
        ft.Text("\n\n\n")
    ],
    )
    
    page.add(header, elementos_home)

ft.app(target=main)
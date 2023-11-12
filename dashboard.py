#!/usr/bin/env python
# encoding: utf-8
#
#  ------------------------------------------------------------------------------
#  Name: dashboard.py
#  Version: 0.0.1
#  Summary: Gastos do Município de Capelinha/MG
#           Aplicativo web para visualização dos gastos do município de Capelinha/MG.
#
#  Author: Alexsander Lopes Camargos
#  Author-email: alcamargos@vivaldi.net
#
#  License: MIT
#  ------------------------------------------------------------------------------

"""
Gastos do Município de Capelinha/MG - Aplicativo Web

Este módulo contém um aplicativo web desenvolvido usando a biblioteca Streamlit
para visualização dos gastos do município de Capelinha/MG em 2022. O aplicativo
apresenta gráficos mensais, métricas e informações sobre os pagamentos realizados.
"""

# Importando as bibliotecas
import locale

import pandas as pd  # Biblioteca para manipulação e análise de dados.
import plotly.express as px  # Biblioteca para visualização de dados.
import plotly.graph_objects as go  # Biblioteca para visualização de dados.
import streamlit as st  # Biblioteca para criação de aplicativos web.

# Set the locale to the current system's default.
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')


# GLOBAL VARIABLES
# Set the seed for the random number generator.
RANDOM_SEED = 42

# Default data directory.
DATA_PATH = r'data/dadosabertos/2022/'

# Informações referentes aos Pagamentos realizados pelos órgãos municipais.
PAYMENT = f'{DATA_PATH}2022.3112307.despesa.pagamento.csv'

# Informações referentes aos órgãos municipais.
AGENCY = f'{DATA_PATH}2022.3112307.orgao.orgao.csv'

# Informações referentes aos Responsáveis pelos Órgãos.
RESPONSIBLE = f'{DATA_PATH}2022.3112307.orgao.orgaoResp.csv'

# Informações referentes as Unidades Orçamentárias dos órgãos municipais.
UNIT = f'{DATA_PATH}2022.3112307.orgao.orgaoUnidade.csv'

# Criando um objeto DatetimeIndex com os meses do ano.
MONTHS = pd.date_range(start='2022-01-01',
                       end='2022-12-01',
                       freq='MS').strftime('%B').str.lower()


def page_header() -> None:
    """Adiciona um cabeçalho à página contendo o título,
    uma imagem representativa e informações sobre o município.

    Returns:
    - None: A função não retorna nenhum valor.
    """

    text = '''[Capelinha](https://pt.wikipedia.org/wiki/Capelinha), é um município brasileiro situado no interior do
    estado de Minas Gerais, Região Sudeste do país. Localiza-se na microrregião denominada Vale do Jequitinhonha.
    Conforme o censo de 2022, a cidade tem uma população de 39.624 habitantes. Este município exerce uma influência
    significativa nos campos econômico, educacional, cultural,empresarial e esportivo nos municípios vizinhos,
    tornando-se a região mais densamente povoada do Vale do Jequitinhonha. A história de Capelinha remonta a 1812,
    quando a construção da Igreja Matriz deNossa Senhora da Graça por Feliciano Luiz Pego marcou o início de sua
    povoação.
    '''

    st.title('Gastos do Município de Capelinha/MG')
    st.image('assets/capelinha_mg_overview.jpg')
    st.markdown(text, unsafe_allow_html=True)
    st.markdown(
        '''> "Sem dados você é apenas mais uma pessoa com uma opinião." - W. Edwards Deming''')
    st.markdown('''***''')


def page_footer() -> None:
    """Adiciona um rodapé à página contendo informações sobre
    o criador e o ano de criação.

    Returns:
    - None: A função não retorna nenhum valor.
    """

    text = '''<div style="text-align: center;">
        <hr>
        Criado por <a href="https://github.com/alexcamargos">Alexsander Camargos</a> | (c) 2023
        </div>
        '''

    st.markdown(text, unsafe_allow_html=True, )


def load_and_process_data() -> pd.DataFrame:
    """Carrega os dados de pagamento de um arquivo CSV,
    realiza o pré-processamento e retorna um DataFrame processado.

    Returns:
    - pd.DataFrame: Um DataFrame contendo os dados de pagamento após
      o pré-processamento.
    """

    # Carregando os dados e realizando o pré-processamento diretamente.
    payment_df = pd.read_csv(PAYMENT,
                             sep=';',
                             encoding='utf-8',
                             dtype={'nom_credor': 'string'})

    # Convertendo as colunas que armazenam datas para o tipo 'datetime'.
    date_columns = ['dat_empenho', 'dat_liquidacao', 'dat_pagamento']
    payment_df[date_columns] = payment_df[date_columns].apply(pd.to_datetime,
                                                              format='%d/%m/%Y')

    # Trocando os valores na coluna 'nom_credor'.
    payment_df['nom_credor'] = payment_df['nom_credor'].replace(
        {'NAO INFORMADO': 'FOLHA DE PAGAMENTO DOS SERVIDORES(AS) MUNICIPAIS',
         'TRIBUNAL REGIONAL DO TRABALHO DA 03ª REGIAO VARA DO TRABALHO DE GUANHAES':
         'FOLHA DE PAGAMENTO DOS SERVIDORES(AS) DA CÂMARA DE VEREADORES'}
    )

    return payment_df


def generate_monthly_plot(month: int, data: pd.DataFrame) -> go.Figure:
    """Gera um gráfico de barras mostrando os valores pagos diariamente
    para um determinado mês.

    Parameters:
    - month (int): O número do mês para o qual o gráfico será gerado (1 a 12).
    - data (pd.DataFrame): O DataFrame contendo os dados de pagamento.

    Returns:
    - plotly.graph_objects.Figure: O gráfico de barras gerado para
    o mês especificado.
    """

    # Agrupar os dados por dia e calcular a soma total para cada dia
    daily_totals = data.query(f'dat_pagamento.dt.month == {month}').groupby(
        data['dat_pagamento'].dt.day)['vlr_pag_fonte'].sum()

    # Criar o gráfico de barra
    fig = go.Figure()
    fig.add_trace(go.Bar(x=daily_totals.index, y=daily_totals.values))
    fig.update_layout(title_text=f'{MONTHS[month - 1].capitalize()}',
                      xaxis_title='Dia do Mês',
                      yaxis_title='Valor pago (R$)',
                      showlegend=False)
    fig.update_xaxes(tickmode='array', tickvals=list(range(1, 32, 3)))

    return fig


def display_monthly_payments_chart(data) -> None:
    """Exibe um gráfico de barras representando os pagamentos
    realizados mensalmente em 2022.

    Parameters:
    - data (pd.DataFrame): Um DataFrame contendo os dados de pagamento.

    Returns:
    - None: A função não retorna nenhum valor. O gráfico é exibido
    diretamente na interface.
    """

    fig_payment_month = px.bar(data,
                               x=data['dat_pagamento'].dt.strftime('%B'),
                               y='vlr_pag_fonte',
                               barmode='group',
                               color_continuous_scale='Bluered_r',
                               color='seq_orgao',
                               hover_data=['vlr_pag_fonte',
                                           'vlr_ret_fonte',
                                           'vlr_ant_fonte',
                                           'vlr_anu_fonte'])

    # Adicionar título ao gráfico.
    fig_payment_month.update_layout(title_text='Pagamentos realizados por mês em 2022',
                                    title_x=0.5,
                                    xaxis_title='Mês',
                                    yaxis_title='Valor pago (R$)',
                                    hovermode='closest')

    st.plotly_chart(fig_payment_month,
                    use_container_width=True)


def display_individual_monthly_plots(data: pd.DataFrame) -> None:
    """Exibe gráficos individuais para cada mês,
    organizados em um layout de 3 colunas por linha.

    Parameters:
    - data (pd.DataFrame): Um DataFrame contendo os dados de pagamento.

    Returns:
    - None: A função não retorna nenhum valor. Os gráficos são exibidos
    diretamente na interface.
    """

    # Configurar o layout para exibir 3 gráficos por linha.
    columns = [st.columns(3) for _ in range(4)]

    # Iterar sobre todos os meses.
    for col_index, month in enumerate(range(1, 13), start=1):
        # Gerar o gráfico individual para o mês.
        monthly_plot = generate_monthly_plot(month, data)

        # Calcular o índice da coluna e linha no layout.
        column_index = (col_index - 1) % 3
        row_index = (col_index - 1) // 3

        # Adicionar o gráfico ao layout.
        columns[row_index][column_index].plotly_chart(monthly_plot,
                                                      use_container_width=True)


def display_total_expenses(data: pd.DataFrame) -> None:
    """Mostra o gasto total por mês no aplicativo.

    Parameters:
    - payment_df (pd.DataFrame): O DataFrame contendo os dados de pagamento.

    Returns:
    - None: A função não retorna nenhum valor.
    """

    st.markdown('''***''')

    st.header('Pagamentos totais em 2022')

    total_expenses = data['vlr_pag_fonte'].sum()
    total_expenses_formatted = locale.format_string('%.2f',
                                                    total_expenses,
                                                    grouping=True)

    st.metric(label='Gasto total em 2022',
              value=f'R$ {total_expenses_formatted}')


def display_monthly_payments_and_differences(data: pd.DataFrame) -> None:
    """Exibe os pagamentos mensais e as diferenças em relação à média.

    Parameters:
    - payment_df (pd.DataFrame): O DataFrame contendo os dados de pagamento.

    Returns:
    - None: A função não retorna nenhum valor.
    """

    st.markdown('''***''')

    st.header('Pagamentos mensais e diferenças em relação à média')

    # Agrupando os pagamentos por mês e somando os valores pagos.
    payment_month = (
        (data.groupby(data['dat_pagamento'].dt.strftime('%B')).agg({'vlr_pag_fonte': 'sum',
                                                                    'vlr_ret_fonte': 'sum',
                                                                    'vlr_ant_fonte': 'sum',
                                                                    'vlr_anu_fonte': 'sum'}
                                                                   ).sort_index()).reindex(MONTHS))

    # Calculando a média dos pagamentos mensais.
    payment_month_mean = payment_month['vlr_pag_fonte'].mean()

    # Configurar o layout para exibir 3 métricas por linha.
    columns = [st.columns(3) for _ in range(4)]

    # Lista para armazenar as métricas.
    metrics_list = []

    # Para cada mês, adicione a métrica à lista.
    for index, row in payment_month.iterrows():
        value_formatted = locale.format_string(
            '%.2f', row['vlr_pag_fonte'], grouping=True)
        difference = row['vlr_pag_fonte'] - payment_month_mean
        difference_formatted = locale.format_string(
            '%.2f', abs(difference), grouping=True)

        # Determina se o delta deve ser positivo ou negativo com base na comparação com a média.
        delta_sign = '+' if difference >= 0 else '-'

        # Adiciona a métrica à lista.
        metric = {
            'label': index.capitalize(),
            'value': f'R$ {value_formatted}',
            'delta': f'{delta_sign}R$ {difference_formatted}'
        }
        metrics_list.append(metric)

    # Exibe as métricas em uma grade de colunas de 4x3.
    for col_index, metrics_row in enumerate(metrics_list, start=1):
        # Calcular o índice da coluna e linha no layout.
        column_index = (col_index - 1) % 3
        row_index = (col_index - 1) // 3

        columns[row_index][column_index].metric(**metrics_row)


def main() -> None:
    """
    Função principal que gera a página principal do aplicativo,
    incluindo cabeçalho, gráficos mensais e rodapé.

    Returns:
    - None: A função não retorna nenhum valor.
    """

    # Show the page header.
    page_header()

    # Load and process the data.
    payment_df = load_and_process_data()

    # Create and display the monthly payments bar chart.
    display_monthly_payments_chart(payment_df)

    # Create and display the individual monthly plots.
    display_individual_monthly_plots(payment_df)

    # Show the total expenses.
    display_total_expenses(payment_df)

    # Display monthly payments and differences.
    display_monthly_payments_and_differences(payment_df)

    # Show the page footer.
    page_footer()


if __name__ == '__main__':
    # Initial page config
    st.set_page_config(
        page_title='Gastos do Município de Capelinha/MG',
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Run the app.
    main()

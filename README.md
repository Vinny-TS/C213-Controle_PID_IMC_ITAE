# Controle PID - Trabalho C213

Aplicação em Python com interface gráfica para identificação de sistemas e sintonia de controle PID. O projeto permite carregar arquivos `.mat`, comparar modelos identificados com a resposta real e calcular a sintonia dos controladores IMC e ITAE.

## Funcionalidades

- Login inicial da aplicação.
- Leitura de dados de entrada e saída a partir de arquivos `.mat`.
- Identificação do sistema pelos métodos de Smith e Sundaresan.
- Sintonização PID pelos métodos IMC e ITAE.
- Visualização de gráficos e exportação das imagens geradas.

## Estrutura

- `trabalhoPID-interface.py`: interface gráfica principal do projeto.
- `trabalhoPID_logica.py`: lógica de identificação, cálculo e simulação.
- `requirements.txt`: dependências do ambiente Python.

## Requisitos

- Python 3.12 ou superior.
- Dependências listadas em `requirements.txt`.
- Um arquivo `.mat` com as variáveis `dados_entrada` e `dados_saida`.

## Instalação

```bash
pip install -r requirements.txt
```

## Como executar

```bash
python "trabalhoPID-interface.py"
```

## Formato do arquivo `.mat`

O arquivo carregado pela aplicação deve conter:

- `dados_entrada`: matriz com pelo menos duas colunas, onde a primeira representa o tempo e a segunda o degrau aplicado.
- `dados_saida`: matriz com pelo menos duas colunas, onde a segunda representa a temperatura medida.

## Credenciais de acesso

Credenciais padrão usadas na tela de login:

- E-mail: `admin@admin.com`
- Senha: `admin`

## Observações

- Os gráficos podem ser exportados pela própria interface.
- O projeto não inclui testes automatizados nesta versão.

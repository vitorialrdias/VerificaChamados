# Documentação — Automação Sinal de Tickets Abertos

> Solução automatizada para monitoramento de tickets em aberto na área de Power BI, permitindo que a equipe de dados acompanhe demandas de forma ágil, centralizada e proativa, reduzindo a necessidade de interação manual e aumentando a eficiência no tratamento dos chamados.

---

## Índice

- [Sobre o Projeto](#sobre-o-projeto)
- [Arquitetura do Projeto](#arquitetura-do-projeto)
- [Fluxograma](#fluxograma)
- [Power Automate Cloud](#power-automate-cloud)
- [Tecnologias Utilizadas](#tecnologias-utilizadas)
- [Variáveis de Ambiente](#variáveis-de-ambiente)
- [Como Executar esse Projeto](#como-executar-esse-projeto)
- [Versões dos Pacotes](#versões-dos-pacotes)
- [Responsáveis pelo Projeto](#responsáveis-pelo-projeto)

---

## Sobre o Projeto

O projeto surgiu para resolver uma necessidade operacional real: a consulta manual de tickets em aberto e suas respectivas prioridades no ambiente corporativo.

Para otimizar esse processo, foi desenvolvida uma solução automatizada utilizando **Selenium** para navegação e extração de informações relevantes dos chamados, com integração para envio automatizado de notificações por **e-mail** (via Outlook/win32com) e **Microsoft Teams** (via Power Automate Cloud).

---

## Arquitetura do Projeto

A arquitetura está estruturada em torno do arquivo principal `main.py`, responsável por iniciar o processamento de navegação através do script `pages/navegador.py`. Após verificar a existência de novos chamados, o arquivo é extraído e a função `tratarExcel` realiza a normalização e extração dos dados pertinentes:

| Campo extraído   | Descrição                             |
|------------------|---------------------------------------|
| Número do chamado | Identificador único do ticket        |
| Descrição        | Resumo do chamado                     |
| Prioridade       | Nível de urgência do ticket           |
| Solicitante      | Usuário que abriu o chamado           |

Após a extração, o script `utils/envio_email.py` envia um e-mail via Outlook para a conta principal da equipe de Power BI com as informações do processo. Em seguida, o **Power Automate Cloud** identifica o novo e-mail na caixa de entrada e notifica o grupo via **Microsoft Teams**.

---

## Fluxograma

```
┌─────────────┐
│   main.py   │
└──────┬──────┘
       │
       ▼
┌────────────────────────────────────────┐      │
│  site = Navegador(url=url_site)        │
│  site.openPage()                       │
│  existe_chamado = site.searchChamado() │
└──────────────┬─────────────────────────┘
               │
       ┌───────┴────────┐
       │                │
   [Sim: existe]    [Não: encerra]
       │
       ▼
┌──────────────────┐
│  tratarExcel()   │
│  Normaliza o     │
│  arquivo e       │
│  extrai dados    │
│  do chamado      │
└───────┬──────────┘
        │
        ▼
┌───────────────────────────────────────┐
│  email = EnvioEmail(destinatario=...) │
│  header_html, linha_html =            │
│  email.gerarTabelaHTML(chamados)      │
│  html_corpo = email.htmlEmail(...)    │
│  email.enviarEmail(html_corpo)        │
└───────────────────┬───────────────────┘
                    │
                    ▼
     ┌──────────────────────────────┐
     │   Outlook (win32com.client)  │
     │  E-mail enviado para a conta │
     │  principal do time Power BI  │
     └──────────────┬───────────────┘
                    │
                    ▼
     ┌──────────────────────────────┐
     │     Power Automate Cloud     │
     │  Detecta novo e-mail na      │
     │  caixa de entrada do Outlook │
     │  e dispara notificação no    │
     │  Microsoft Teams             │
     └──────────────────────────────┘
```

---

## Power Automate Cloud

O Power Automate Cloud atua como a camada de notificação final do fluxo. Após o envio do e-mail pelo script Python, o seguinte fluxo automatizado é executado:

### Gatilho
- **Quando um novo e-mail chega (Outlook):** O fluxo é acionado ao detectar um novo e-mail na caixa de entrada da conta da equipe de Power BI. Pode-se filtrar pelo assunto do e-mail para garantir que apenas mensagens geradas pela automação disparem o fluxo.

### Ações do Fluxo

| Etapa | Ação no Power Automate        | Descrição                                                                 |
|-------|-------------------------------|---------------------------------------------------------------------------|
| 1     | **Gatilho:** Quando um e-mail chega (Outlook 365) | Monitora a caixa de entrada e inicia o fluxo ao receber um e-mail com o assunto definido. |
| 2     | **Obter corpo do e-mail**     | Extrai o conteúdo HTML do e-mail recebido, contendo a tabela com os chamados. |
| 3     | **Postar mensagem no Teams**  | Envia o corpo do e-mail como mensagem no canal do grupo da equipe de dados no Microsoft Teams. |

> **Observação:** O fluxo utiliza o conector do **Microsoft Outlook 365** para leitura do e-mail e o conector do **Microsoft Teams** para envio da notificação ao canal da equipe.

---

## Tecnologias Utilizadas

### Python
Linguagem central do projeto, responsável por estruturar toda a lógica de processamento, consultas, manipulação de dados e automação de navegação. Escolhida pela versatilidade, sintaxe acessível e amplo ecossistema de bibliotecas.

### Selenium
Biblioteca utilizada para automação de navegação web. Permite controlar o browser de forma programática para acessar o sistema de tickets, realizar buscas e extrair os arquivos de chamados sem necessidade de interação manual.

### win32com.client (pywin32)
Biblioteca que fornece acesso às APIs do Windows via COM (Component Object Model). Utilizada neste projeto para controlar o Microsoft Outlook e realizar o envio automatizado de e-mails com o relatório de tickets em HTML.

### pandas
Biblioteca de análise e manipulação de dados. Utilizada para leitura e tratamento do arquivo Excel exportado pelo sistema de tickets, realizando a normalização, filtragem e extração dos dados relevantes de cada chamado.

### python-dotenv
Biblioteca utilizada para gerenciamento de variáveis de ambiente. Carrega as configurações sensíveis (credenciais, URLs, e-mails) a partir de um arquivo `.env`, evitando a exposição de dados sensíveis no código-fonte.

### os, glob, time, shutil (bibliotecas nativas)
Módulos nativos do Python utilizados para manipulação do sistema de arquivos:

| Módulo   | Uso no projeto                                                   |
|----------|------------------------------------------------------------------|
| `os`     | Gerenciamento de caminhos e variáveis de ambiente                |
| `glob`   | Busca de arquivos por padrão no diretório de downloads           |
| `time`   | Controle de delays para aguardar carregamentos do browser        |
| `shutil` | Movimentação e cópia de arquivos extraídos                       |

---

## Variáveis de Ambiente

As credenciais e configurações sensíveis do projeto são armazenadas em um arquivo `.env` na raiz do projeto, carregado via **python-dotenv**. Este arquivo **não deve ser versionado** (inclua-o no `.gitignore`).

### Exemplo de `.env`

```env

# E-mail destinatário
EMAIL_DESTINATARIO=email@abc.com

# URL do site
URL_SITE=www.site.com.br

# Seletores/botões da página (XPath, ID ou seletor CSS)
# Armazenados no .env por boas práticas de segurança, centralizando
# elementos da interface que podem mudar sem necessidade de alterar o código-fonte
BTN_LOGIN="botaologin"
BTN_CHAMADOS="botaochamados"

# Nome original do arquivo Excel exportado
FILE_NAME="ExcelChamados"
```

### Exemplo de uso no código

```python
from dotenv import load_dotenv
import os

load_dotenv()

url_site = os.getenv("URL_SITE")
email    = os.getenv("EMAIL_DESTINATARIO")
```
---

## Como Executar esse Projeto

### 1. Instalar o Python

- Acesse o site oficial: [https://www.python.org/downloads/](https://www.python.org/downloads/)
- Baixe a versão recomendada para o seu sistema operacional.
- Durante a instalação no **Windows**, marque a opção **"Add Python to PATH"**.
- Conclua a instalação usando as opções padrão.

### 2. Instalar as Dependências

Na pasta do projeto, execute:

```bash
pip install selenium pandas pywin32 python-dotenv
```

### 3. Configurar o Arquivo `.env`

Crie um arquivo `.env` na raiz do projeto com base no modelo da seção [Variáveis de Ambiente](#variáveis-de-ambiente).

### 4. Navegar até o Projeto e Executar

**Via Terminal (Prompt de Comando):**

```bash
# Navegue até a pasta do projeto
cd C:\Documentos\Caminho\Para\Projeto

# Execute o arquivo principal
python main.py
```

**Via VSCode:**

Abra a pasta do projeto em **File → Open Folder...** e, no terminal integrado:

```bash
python main.py
```

---

## Versões dos Pacotes

| Pacote            | Versão        | Observação                                      |
|-------------------|---------------|-------------------------------------------------|
| **Python**        | 3.13.5        | Versão utilizada no desenvolvimento             |
| **selenium**      | 4.44.0        | Última versão estável (mai/2026)                |
| **pywin32**       | 311           | Última versão estável (jul/2025)                |
| **pandas**        | 3.0.0         | Última versão estável (jan/2026)                |
| **python-dotenv** | 1.2.2         | Última versão estável (mar/2026)                |
| **os**            | nativa        | Módulo nativo do Python                         |
| **glob**          | nativa        | Módulo nativo do Python                         |
| **time**          | nativa        | Módulo nativo do Python                         |
| **shutil**        | nativa        | Módulo nativo do Python                         |

Para instalar todas as dependências de uma vez, utilize o arquivo `requirements.txt`:

```text
selenium==4.44.0
pandas==3.0.0
pywin32==311
python-dotenv==1.2.2
```

```bash
pip install -r requirements.txt
```

---

## Responsáveis pelo Projeto

### Autora

**Vitoria Leticia Ribeiro Dias**  
Assistente Power BI  
Folha / Arquitetura e Sustentação Power BI
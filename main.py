import os,glob,time,shutil
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
import logging

# Importando os módulos do projeto
try:
    from source.config.logging import setup_logging
    from source.pages.navegador import Navegador
    from source.utils.envio_email import EnvioEmail
except ImportError as e:
    logging.info(f"Erro ao importar módulos internos: {e}")


load_dotenv()
setup_logging()

    
def tratarExcel() -> str:
    """Função para formatar o nome do arquivo e retornar o dados pertinentes"""
    logging.info("Iniciando leitura do excel")
    
    # Recupera o nome do usuário do sistema operacional
    usuario = os.getlogin()

    # Concatena o nome do usuário com o caminho da pasta desejada
    caminho_pasta = os.path.join("C:\\Users", usuario, "Downloads")
    texto_especifico = os.getenv("FILE_NAME")

    # Listando todos os arquivos .excel que começam com o texto específico
    arquivos = glob.glob(f"{caminho_pasta}\\{texto_especifico}*.xlsx")

    # Verificando se existem arquivos encontrados
    if not arquivos:
        logging.info("Nenhum arquivo novo encontrado.")
        return

    # Verificando qual é o arquivo mais recente
    arquivo_mais_recente = max(arquivos, key=os.path.getctime)
    logging.info(f"Arquivo mais recente encontrado: {arquivo_mais_recente}")
    logging.info(f"Verificando se o arquivo existe: {os.path.exists(arquivo_mais_recente)}")

    # Defina a pasta de destino
    caminho_destino = r'C:\CHAMADOS'

    data_atual = datetime.now().strftime('%d-%m-%Y')

    novo_nome_arquivo = f"CHAMADOS_{data_atual}.xlsx"
    logging.info(f"Novo nome do arquivo: {novo_nome_arquivo}")

    # Construindo o novo caminho completo (pasta de destino + novo nome)
    novo_caminho_arquivo = os.path.join(caminho_destino, novo_nome_arquivo)
    novo_caminho_arquivo = os.path.normpath(novo_caminho_arquivo)  # Normaliza o caminho
    
    time.sleep(3)


    # Movendo o arquivo e retornando os dados desejados
    try:
        shutil.move(arquivo_mais_recente, novo_caminho_arquivo)
        texto = pd.read_excel(novo_caminho_arquivo)
        quantidade_chamados = texto.shape[0]
        if quantidade_chamados == 0:
            logging.info("Nenhum chamado para ser atendido.") 
            return None
        chamados = []

        for _, row in texto.iterrows():
            chamados.append({
                "n_chamado": row["N°"],
                "descricao": str(row["DESCRIÇÃO"]).split("\n")[0].strip()[:80],
                "prioridade": row["PRIORIDADE"],
                "solicitante": row["USUÁRIO DE ABERTURA"]
            })

        return chamados
    except Exception as e:
        logging.error(f"Erro ao mover o arquivo: {e}")
        return None


def main():
    """Processo principal"""
    inicio = datetime.now().strftime('%H:%M')
    email = os.getenv("EMAIL_DESTINATARIO")
    url_site= os.getenv("URL_SITE")
    
    try:
        
        # Conexão com a pagina do GPS Amigo
        site = Navegador(url=url_site)
        site.openPage()
        existe_chamado = site.searchChamado()

        if existe_chamado:

            chamados = tratarExcel()
            email = EnvioEmail(destinatario=email)
            header_html, linha_html = email.gerarTabelaHTML(chamados)
            html_corpo = email.htmlEmail(header_html, linha_html)
            envio_email = email.enviarEmail(html_corpo)

        final = datetime.now().strftime('%H:%M')
        logging.info(f'Processamento iniciado: {inicio} e finalizado: {final}')

    except Exception as e:
        logging.error(f"Erro no processo principal: {e}")

if __name__ == "__main__":
        main()
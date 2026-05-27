import os,logging
from datetime import datetime
from dotenv import load_dotenv


# Importando os módulos do projeto
try:
    from source.config.logging import setup_logging
    from source.pages.navegador import Navegador
    from source.utils.envio_email import EnvioEmail
    from source.utils.tratar_excel import tratarExcel
except ImportError as e:
    logging.info(f"Erro ao importar módulos internos: {e}")


load_dotenv()
setup_logging()

    
def main():
    """Processo principal"""
    
    logging.info("="*100)
    logging.info("Iniciando automação...")
    
    inicio = datetime.now().strftime('%H:%M')
    
    email_destino = os.getenv("EMAIL_DESTINATARIO")
    EMAIL_REMETENTE = os.getenv("EMAIL_REMETENTE")
    url_site= os.getenv("URL_SITE")
    
    try:
        
        # Conexão com a pagina do GPS Amigo
        site = Navegador(url=url_site)
        site.openPage()
        existe_chamado = site.searchChamado()

        # Se existir chamado inicia o processo de extração dos dados e envio do e-mail
        if existe_chamado:

            chamados = tratarExcel()
            
            if chamados:
            
                email = EnvioEmail(destinatario=email_destino, conta_envio=EMAIL_REMETENTE)
                header_html, linha_html = email.gerarTabelaHTML(chamados)
                html_corpo = email.htmlEmail(header_html, linha_html)
                envio_email = email.enviarEmail(html_corpo)

        final = datetime.now().strftime('%H:%M')
        logging.info(f'Processamento iniciado: {inicio} e finalizado: {final}')

    except Exception as e:
        logging.error(f"Erro no processo principal: {e}")

if __name__ == "__main__":
        main()
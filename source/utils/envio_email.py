import win32com.client
import os, logging


def limpar_emails(lista):
    # Garante que emails válidos sejam separados por ponto e vírgula
    if isinstance(lista, str):
        lista = lista.split(';')  # Transforma string separada por ; em lista
    return ";".join(email.strip().strip(';') for email in lista if email and email.strip())


class EnvioEmail:
    def __init__(
        self,
        caminho_anexo=None,
        destinatario=None,
        conta_envio=None
        
          # 
    ):
        self.destinatarios = limpar_emails(destinatario)
        self.assunto = "Relatório - Chamados GPS Amigo"
        self.caminho_anexo = caminho_anexo
        self.conta_envio = conta_envio

    def gerarTabelaHTML(self, chamados):
        try:
            colunas = ["Nº Chamado", "  Data  ", "Resumo Descricao", "Prioridade", "Solicitante", "Status"]

            header_html = (
                "<tr>" +
                "".join(f"<th style='width:100px;'>{col}</th>" for col in colunas) +
                "</tr>"
            )

            linhas_html = ""

            for c in chamados:
                linhas_html += (
                    "<tr>"
                    f"<td>{c['n_chamado']}</td>"
                    f"<td>{c['data']}</td>"
                    f"<td>{c['descricao']}</td>"
                    f"<td>{c['prioridade']}</td>"
                    f"<td>{c['solicitante']}</td>"
                    f"<td>{c['status']}</td>"
                    "</tr>"
                )

            return header_html, linhas_html

        except Exception as e:
            logging.info(f'Erro ao criar tabela HTML: {e}')
            return "", ""

    def htmlEmail(self, header_html, linha_html):
        try:
            html_corpo = f"""
            <html>
            <head>
            <meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1">
            </head>
            <body>
            
            <style>
            table {{
                font-family: Century Gothic, Helvetica, Arial;
                border-collapse: collapse;
                width: 100%;
                font-size: 13px;
            }}
            th {{
                text-align: left;
                background-color: #0f1e63;
                color: white;
            }}
            td {{
                border: 1px solid #ddd;
                background-color: #F0F8FF;
            }}
            .tit_grande {{
                font-family: Helvetica;
                font-size: 26px;
                color: #0f1e63;
            }}
            </style>
            <div class="tit_grande"><b>Chamados Power BI - GPS Amigo</b></div>
            <br><br>
            <p>Chamados:</p>
            <table>
                {header_html}
                {linha_html}
            </table>
            </body>
            </html>
            """
            return html_corpo
        except Exception as e:
            logging.info(f'Erro ao criar HTML: {e}')
            return None

    def enviarEmail(self, html_corpo):
        try:
            outlook = win32com.client.Dispatch("Outlook.Application")
            namespace = outlook.GetNamespace("MAPI")
            mail = outlook.CreateItem(0)

            mail.To = self.destinatarios
            mail.Subject = self.assunto
            mail.HTMLBody = html_corpo

            # Define a conta de envio usando o método funcional via COM
            for account in namespace.Accounts:
                if account.SmtpAddress.lower() == self.conta_envio.lower():
                    mail._oleobj_.Invoke(*(64209, 0, 8, 0, account))
                    break
            else:
                return 'Erro'

            mail.Send()
            logging.info("Email enviado com sucesso.")
            return 'Sucesso'
        except Exception as e:
            logging.info(f'Erro no envio do e-mail: {e}')
            return 'Erro'
import os,glob,time,shutil,logging,re, html
from datetime import datetime
import pandas as pd



def limpar_descricao(texto: str) -> str:
    # 1. Decodificar HTML entities (&lt;br&gt; → <br>, &#039; → ', etc.)
    texto = html.unescape(texto)

    # 2. Remover tags HTML (<br>, <ul>, <li>, <em>, etc.)
    texto = re.sub(r'<[^>]+>', ' ', texto)

    # 3. Remover linhas que são SOMENTE saudação/fechamento/separador
    saudacoes_linha = re.compile(
        r'^\s*('
        r'bom\s+dia'
        r'|boa\s+tarde'
        r'|boa\s+noite'
        r'|por\s+gentileza'
        r'|ol[aá][\s,!.]*(\s*tudo\s+bem[?!.]*)?'
        r'|prezados?\s*(,|!|\(a\))?'
        r'|pessoal\s*[,!.]?'
        r'|por\s+favor\s*[,!.]?'
        r'|aguardamos\s+retorno.*'
        r'|qualquer\s+d[uú]vida.*'
        r'|fico\s+[aà]\s+disposi[çc][aã]o.*'
        r'|podem\s+me\s+acionar.*'
        r'|-{3,}'
        r')\s*$',
        flags=re.IGNORECASE | re.MULTILINE
    )
    texto = saudacoes_linha.sub('', texto)

    # 4. Remover saudação colada ao início do conteúdo real
    #    Ex: "Boa tarde! Solicito..." → "Solicito..."
    texto = re.sub(
        r'^[\s\n]*'
        r'(bom\s+dia'
        r'|boa\s+tarde'
        r'|boa\s+noite'
        r'|ol[aá]'
        r'|prezados?\s*(\(a\))?'
        r'|pessoal'
        r'|por\s+gentileza)'
        r'[\s!,.:–-]+'
        r'(?=\S)',
        '',
        texto,
        flags=re.IGNORECASE
    )

    # 5. Normalizar: colapsar múltiplos espaços/newlines, strip
    texto = re.sub(r'\n{3,}', '\n\n', texto)   # máx 2 quebras seguidas
    texto = re.sub(r'[ \t]{2,}', ' ', texto)    # espaços duplos
    texto = texto.strip()

    return texto

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
                "data": datetime.strptime(
                    row["DATA ABERTURA"],
                    "%Y-%m-%d %H:%M:%S"
                ).strftime("%d/%m"),
                "descricao": limpar_descricao(str(row["DESCRIÇÃO"]))[:100],
                "prioridade": row["PRIORIDADE"],
                "solicitante": row["USUÁRIO DE ABERTURA"],
                "status": row["STATUS"]
            })

        return chamados
    except Exception as e:
        logging.error(f"Erro ao mover o arquivo: {e}")
        return None
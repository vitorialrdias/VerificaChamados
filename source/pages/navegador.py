from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time, os, logging, subprocess
from dotenv import load_dotenv
import logging
load_dotenv()
class Navegador:
    def __init__(self, url=None):
        self.url = url
        self.driver = None

    def openPage(self):
        # Fecha a janela do Edge para não ocorrer interferencia
        subprocess.run(["taskkill", "/f", "/im", "msedge.exe"], capture_output=True)
        
        user = os.getlogin()
        edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

        options = Options()
        options.binary_location = edge_path

        # MODO HIDDEN 
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")

        self.driver = webdriver.Edge(options=options)
        self.driver.maximize_window()

        if self.url:
            self.driver.get(self.url)

        logging.info("Navegador iniciado (Selenium).")
        return self.driver

    def searchChamado(self) -> bool:
        try:
            wait = WebDriverWait(self.driver, 20)
            time.sleep(2)
            
            # Input login
            input_login = wait.until(
                EC.element_to_be_clickable((By.ID, os.getenv("INPUT_LOGIN")))
            )
            input_login.send_keys(os.getenv("USER"))
            
            # Input pass
            input_pass = wait.until(
                EC.element_to_be_clickable((By.ID, os.getenv("INPUT_PASS")))
            )
            input_pass.send_keys(os.getenv("PASS"))
            
            # Botão Entrar
            btn_entrar = wait.until(
                EC.element_to_be_clickable((By.ID, os.getenv("BTN_LOGIN")))
            )
            btn_entrar.click()

            time.sleep(5)

            # Botão acessar area dos chamados
            btn_amigo = wait.until(
                EC.element_to_be_clickable((By.ID, os.getenv("BTN_CHAMADOS")))
            )
            btn_amigo.click()

            time.sleep(8)
            self.driver.switch_to.window(self.driver.window_handles[-1])
            wait = WebDriverWait(self.driver, 30)
            
            # Entra no iframe dos chamados
            iframe = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.ID, "iframeMain"))
            )
            self.driver.switch_to.frame(iframe)
            
            # espera tabela carregar
            wait.until(
                EC.presence_of_element_located((By.ID, "table_my_queued"))
            )

            time.sleep(10)
            # verifica linhas do tbody
            linhas = self.driver.find_elements(
                By.CSS_SELECTOR,
                "#table_my_queued tbody tr"
            )
            
            if "Nenhum registro encontrado" not in linhas[0].text:

                # Clica para exportar os dados dos chamados em aberto
                self.driver.execute_script("document.querySelector(\"button[aria-controls='table_my_queued']\").click()")
                
                time.sleep(5)
                return True
            else:
                logging.info("Não há novos chamados para serem atendidos.")
                return None


        except Exception as e:
            logging.info(f"Falha ao interagir com a página: {e}")
            raise
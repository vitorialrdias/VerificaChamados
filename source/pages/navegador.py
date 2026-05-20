import time, os, logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class Navegador:
    def __init__(self, url=None):
        self.url = url
        self.driver = None

    def openPage(self):
        user = os.getlogin()
        edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

        options = Options()
        options.binary_location = edge_path
        # As opções de options abaixo possibilita o login pelo usuário profissional
        options.add_argument(f"--user-data-dir=C:/Users/{user}/AppData/Local/Microsoft/Edge/User Data")
        options.add_argument(r"--profile-directory=Default")
        
        # MODO HIDDEN 
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")

        self.driver = webdriver.Edge(options=options)

        if self.url:
            self.driver.get(self.url)

        logging.info("Navegador iniciado (Selenium).")
        return self.driver

    def searchChamado(self) -> bool:
        try:
            wait = WebDriverWait(self.driver, 20)
            time.sleep(1)

            # 🔹 Botão Entrar
            btn_entrar = wait.until(
                EC.element_to_be_clickable((By.ID, "btnLogin"))
            )
            btn_entrar.click()

            time.sleep(3)

            # 🔹 Botão GPS Amigo
            btn_amigo = wait.until(
                EC.element_to_be_clickable((By.ID, "gpsamigo"))
            )
            btn_amigo.click()

            time.sleep(2)
            self.driver.switch_to.window(self.driver.window_handles[-1])
            wait = WebDriverWait(self.driver, 30)
            
            time.sleep(5)
            # Entra no iframe
            iframe = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.ID, "iframeMain"))
            )
            self.driver.switch_to.frame(iframe)
            
            linhas = self.driver.find_elements(By.CSS_SELECTOR, "#table_my_queued tbody tr")
            
            if linhas:

                # Agora clica no botão dentro do iframe
                self.driver.execute_script("document.querySelector(\"button[aria-controls='table_my_queued']\").click()")
                
                time.sleep(5)
                return True
            else:
                logging.info("Não há novos chamados para serem atendidos.")
                return None


        except Exception as e:
            logging.info(f"Falha ao interagir com a página: {e}")
            raise
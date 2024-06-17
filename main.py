import sqlite3
from tkinter import *
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import logging

logging.basicConfig(filename='logdosistema.log', level=logging.ERROR,
                    format='%(asctime)s:%(levelname)s:%(message)s')

def extrair_dados_tabela(driver, conn, nome_tabela):
    c = conn.cursor()
    divs = driver.find_elements(By.XPATH, '//div[@role="listitem" and @class="v-list-item theme--light"]')
    
    if not divs:
        raise ValueError(f"Não foram encontrados dados para {nome_tabela}")

    for div in divs:
        try:
            title_div = div.find_element(By.CLASS_NAME, 'v-list-item__title')
            horario = title_div.text.strip()
            
            try:
                action_text = div.find_element(By.CLASS_NAME, 'v-list-item__action-text')
                status = "Horário Reservado" if "Horário Reservado" in action_text.text else "Disponível"
            except:
                status = "Disponível"
            
            c.execute(f'INSERT INTO {nome_tabela} (horario, status) VALUES (?, ?)', (horario, status))
        except Exception as e:
            logging.error(f"Erro ao processar a div: {e}")

def extrair_dados():
    driver = None
    conn = None
    try:
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        url = "https://gripo.app/reservar/padel-park-academy-cruz-alta-rs"
        driver.get(url)
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.XPATH, '//div[@role="listitem" and @class="v-list-item theme--light"]')))

        conn = sqlite3.connect('horarios.db')
        c = conn.cursor()

        c.execute('''
            CREATE TABLE IF NOT EXISTS quadra_central (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                horario TEXT,
                status TEXT
            )
        ''')

        c.execute('''
            CREATE TABLE IF NOT EXISTS quadra_lateral (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                horario TEXT,
                status TEXT
            )
        ''')

    
        extrair_dados_tabela(driver, conn, 'quadra_central')
        botao_quadra2 = wait.until(EC.element_to_be_clickable((By.XPATH, '//div[@role="tab" and .//span[text()="Lateral"]]')))
        botao_quadra2.click()
        wait.until(EC.presence_of_element_located((By.XPATH, '//div[@role="listitem" and @class="v-list-item theme--light"]')))
        extrair_dados_tabela(driver, conn, 'quadra_lateral')
        conn.commit()
        print("Dados armazenados no banco de dados com sucesso.")
    
    except ValueError as ve:
        logging.error(f"Erro específico de dados: {ve}")
        print(f"Erro específico de dados: {ve}")
    except Exception as e:
        logging.error(f"Erro durante a extração de dados: {e}")
        print("Erro durante a extração de dados. Verifique o log para mais detalhes.")
    
    finally:
        if conn:
            conn.close()
        if driver:
            driver.quit()
def main():
    root = Tk()
    root.title("Extração de Dados")
    root.geometry("400x200")
    botaoextrair = Button(root, text="Extrair Dados", command=extrair_dados)
    botaoextrair.pack(pady=24)
    root.mainloop()

if __name__ == "__main__":
    main()

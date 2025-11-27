import time
import re
from playwright.async_api import Page
from src.scripts.base import BaseScraper, ScraperResult

class LocPeticoes(BaseScraper):
    async def run(self, page: Page) -> ScraperResult:
        start_time = time.time()
        self.logger.info("Executando a extração dos processos do localizador PETIÇÕES.")

        try:
            # Navega para a home
            await self.navigate_to_home(page)

            # Realiza o login
            await self.login(page)

            # --- NAVEGAÇÃO ESPECÍFICA ---
            self.logger.info("Navegando para 'Processos com Localizador PETIÇÃO'...")
            
            # Tenta clicar usando regex robusto e ANCORADO (^) para não pegar "PETIÇÃO INICIAL"
            # O usuário informou: Processos com Localizador  "PETIÇÃO"
            try:
                await page.get_by_role("cell", name=re.compile(r"^Processos\s+com\s+Localizador\s+[\"']?PETIÇÃO[\"']?$", re.IGNORECASE)).click()
            except Exception as e:
                self.logger.warning(f"Clique por role falhou ({e}), tentando por texto genérico...")
                # Fallback: clica em qualquer elemento que tenha o texto chave
                await page.locator("text=Processos com Localizador").first.click()
            
            # Aguarda a tabela carregar (networkidle pode ser muito estrito)
            try:
                await page.wait_for_load_state("domcontentloaded", timeout=10000)
                # Dá um tempinho extra para scripts dinâmicos
                await page.wait_for_timeout(2000) 
            except Exception:
                self.logger.warning("Timeout esperando load state, prosseguindo...")
            
            processos_encontrados = []
            pagina_atual = 1
            
            while True:
                self.logger.info(f"Processando página {pagina_atual}...")
                
                # Extrai números de processo da página atual
                # Restringe a busca à tabela de resultados para evitar pegar processos do menu/sidebar
                # Tenta encontrar a tabela principal (geralmente tem id 'infraAreaDados' ou similar, ou é a maior tabela)
                # Aqui tentamos pegar o texto apenas das tabelas visíveis
                texto_pagina = ""
                tabelas = await page.locator("table").all()
                for tabela in tabelas:
                    if await tabela.is_visible():
                        texto_pagina += await tabela.inner_text() + "\n"
                
                # Se não achar tabelas, usa o content como fallback (mas é arriscado)
                if not texto_pagina.strip():
                    texto_pagina = await page.content()

                # Regex para capturar formato NNNNNNN-NN.NNNN.N.NN.NNNN
                matches = re.findall(r"\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}", texto_pagina)
                
                # Remove duplicatas da página atual e adiciona à lista geral
                novos_processos = list(set(matches))
                self.logger.info(f"Encontrados {len(novos_processos)} processos nesta página.")
                processos_encontrados.extend(novos_processos)
                
                # --- PAGINAÇÃO ---
                # Verifica se o botão de próxima página está desabilitado pelo ID do container (li)
                # Log do erro mostrou: id="lnkInfraProximaPaginaSuperior" class="page-item disabled"
                next_page_li = page.locator("#lnkInfraProximaPaginaSuperior")
                
                if await next_page_li.is_visible():
                    class_attr = await next_page_li.get_attribute("class")
                    if class_attr and "disabled" in class_attr:
                        self.logger.info("Fim da paginação (botão desabilitado).")
                        break
                    
                    # Se não estiver desabilitado, clica no link dentro dele
                    self.logger.info("Indo para a próxima página...")
                    await next_page_li.locator("a").click()
                    
                    # Aguarda carregamento
                    try:
                        await page.wait_for_load_state("domcontentloaded", timeout=10000)
                        await page.wait_for_timeout(1000) 
                    except Exception:
                        self.logger.warning("Timeout na paginação, tentando seguir...")
                    
                    pagina_atual += 1
                else:
                    # Fallback para o seletor genérico se o ID específico não existir
                    proxima_pagina_btn = page.locator("a[title='Próxima Página'], a:has-text('Próxima >')").first
                    if await proxima_pagina_btn.is_visible():
                         await proxima_pagina_btn.click()
                         # ... (logica de espera)
                         pagina_atual += 1
                    else:
                        self.logger.info("Fim da paginação (botão não encontrado).")
                        break

            # Remove duplicatas finais (caso o mesmo processo apareça em múltiplas páginas)
            processos_unicos = list(set(processos_encontrados))
            self.logger.info(f"Total de processos únicos extraídos: {len(processos_unicos)}")

            execution_time = time.time() - start_time
            return ScraperResult(
                success=True,
                data={"processos": processos_unicos, "total": len(processos_unicos)},
                message="Extração concluída com sucesso",
                execution_time=execution_time
            )

        except Exception as e:
            self.logger.error(f"Erro durante a execução: {e}")
            return ScraperResult(
                success=False,
                data=None,
                message=str(e),
                execution_time=time.time() - start_time
            )

# Função auxiliar para manter compatibilidade ou facilitar instanciacao se necessario
# Mas a ideia é que o main.py instancie a classe.

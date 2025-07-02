# agente_coletor_dados.py - Agente Coletor de Dados Simplificado

import json
import re
from typing import Dict, Any, List, Optional
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain

class AgenteColetorDados:
    """
    Agente responsável por coletar, validar e estruturar os dados de entrada
    para geração de petições iniciais.
    """
    
    def __init__(self, openai_api_key: str):
        self.llm = ChatOpenAI(
            model="gpt-4o", 
            openai_api_key=openai_api_key, 
            temperature=0.1
        )
        
        # Template para análise e estruturação dos dados
        self.prompt_estruturacao = PromptTemplate(
            input_variables=["dados_brutos"],
            template="""
            Você é um assistente jurídico especializado em organizar dados para petições iniciais.
            
            DADOS RECEBIDOS:
            {dados_brutos}
            
            TAREFA: Analise os dados e organize-os em uma estrutura padronizada para petição inicial.
            
            ESTRUTURA ESPERADA (retorne em JSON válido):
            {{
                "tipo_acao": "string - tipo da ação jurídica",
                "competencia": "string - vara/foro competente",
                "valor_causa": "string - valor da causa",
                "autor": {{
                    "nome": "string",
                    "tipo_pessoa": "fisica|juridica",
                    "cpf_cnpj": "string",
                    "endereco": "string",
                    "telefone": "string",
                    "email": "string",
                    "profissao": "string (se pessoa física)",
                    "estado_civil": "string (se pessoa física)"
                }},
                "reu": {{
                    "nome": "string",
                    "tipo_pessoa": "fisica|juridica", 
                    "cpf_cnpj": "string",
                    "endereco": "string",
                    "telefone": "string",
                    "email": "string"
                }},
                "fatos": {{
                    "resumo": "string - resumo dos fatos principais",
                    "cronologia": ["lista de eventos em ordem cronológica"],
                    "documentos": ["lista de documentos mencionados"],
                    "valores": ["lista de valores envolvidos"]
                }},
                "fundamentos_juridicos": {{
                    "areas_direito": ["lista de áreas do direito aplicáveis"],
                    "leis_aplicaveis": ["lista de leis que podem ser aplicáveis"],
                    "temas_pesquisa": ["lista de temas para pesquisa jurídica"]
                }},
                "pedidos": {{
                    "principais": ["lista de pedidos principais"],
                    "alternativos": ["lista de pedidos alternativos"],
                    "cautelares": ["lista de pedidos cautelares se houver"]
                }},
                "urgencia": "boolean - se há urgência no caso",
                "observacoes": "string - observações adicionais importantes"
            }}
            
            REGRAS:
            1. Se alguma informação não estiver disponível, use null ou string vazia
            2. Seja preciso na classificação do tipo de ação
            3. Identifique corretamente se as partes são pessoas físicas ou jurídicas
            4. Extraia todos os fatos relevantes de forma organizada
            5. Sugira áreas do direito e leis aplicáveis baseado nos fatos
            6. Organize os pedidos por ordem de importância
            
            RESPOSTA: Apenas o JSON estruturado, sem texto adicional.
            """
        )
        
        self.chain_estruturacao = LLMChain(llm=self.llm, prompt=self.prompt_estruturacao)
    
    def coletar_e_processar(self, dados_brutos: Dict[str, Any]) -> Dict[str, Any]:
        """
        Método principal para coletar e processar dados de entrada.
        
        Args:
            dados_brutos: Dados recebidos do n8n ou outro sistema
            
        Returns:
            Dict com dados estruturados e validados
        """
        try:
            print("📊 Iniciando coleta e processamento de dados...")
            
            # Etapa 1: Validação básica
            dados_validados = self._validar_dados_basicos(dados_brutos)
            
            # Etapa 2: Estruturação via LLM
            dados_estruturados = self._estruturar_dados_llm(dados_validados)
            
            # Etapa 3: Validação final e enriquecimento
            dados_finais = self._validar_e_enriquecer(dados_estruturados)
            
            print("✅ Dados coletados e processados com sucesso")
            return {
                "status": "sucesso",
                "dados_estruturados": dados_finais,
                "dados_originais": dados_brutos
            }
            
        except Exception as e:
            print(f"❌ Erro na coleta de dados: {e}")
            return {
                "status": "erro",
                "mensagem": f"Erro no processamento dos dados: {str(e)}",
                "dados_originais": dados_brutos
            }
    
    def _validar_dados_basicos(self, dados: Dict[str, Any]) -> Dict[str, Any]:
        """Validação básica dos dados de entrada."""
        dados_validados = dados.copy()
        
        # Garantir campos mínimos
        campos_obrigatorios = ['tipo_acao', 'autor', 'reu', 'fatos']
        for campo in campos_obrigatorios:
            if campo not in dados_validados or not dados_validados[campo]:
                if campo == 'tipo_acao':
                    dados_validados[campo] = "Ação não especificada"
                elif campo in ['autor', 'reu']:
                    dados_validados[campo] = {"nome": "Não informado"}
                elif campo == 'fatos':
                    dados_validados[campo] = "Fatos não especificados"
        
        # Normalizar estruturas de autor e réu
        for parte in ['autor', 'reu']:
            if isinstance(dados_validados.get(parte), str):
                dados_validados[parte] = {"nome": dados_validados[parte]}
            elif not isinstance(dados_validados.get(parte), dict):
                dados_validados[parte] = {"nome": "Não informado"}
        
        return dados_validados
    
    def _estruturar_dados_llm(self, dados: Dict[str, Any]) -> Dict[str, Any]:
        """Estrutura os dados usando LLM."""
        try:
            dados_formatados = json.dumps(dados, indent=2, ensure_ascii=False)
            resposta = self.chain_estruturacao.run(dados_brutos=dados_formatados)
            
            # Tentar parsear como JSON
            try:
                dados_estruturados = json.loads(resposta)
                return dados_estruturados
            except json.JSONDecodeError:
                print("⚠️ Resposta do LLM não é JSON válido, usando estrutura básica")
                return self._criar_estrutura_basica(dados)
                
        except Exception as e:
            print(f"⚠️ Erro na estruturação via LLM: {e}")
            return self._criar_estrutura_basica(dados)
    
    def _criar_estrutura_basica(self, dados: Dict[str, Any]) -> Dict[str, Any]:
        """Cria estrutura básica quando o LLM falha."""
        return {
            "tipo_acao": dados.get("tipo_acao", "Ação não especificada"),
            "competencia": dados.get("competencia", "Foro competente"),
            "valor_causa": dados.get("valor_causa", "A ser arbitrado"),
            "autor": self._estruturar_parte(dados.get("autor", {})),
            "reu": self._estruturar_parte(dados.get("reu", {})),
            "fatos": {
                "resumo": dados.get("fatos", "Fatos não especificados"),
                "cronologia": dados.get("cronologia", []),
                "documentos": dados.get("documentos", []),
                "valores": dados.get("valores", [])
            },
            "fundamentos_juridicos": {
                "areas_direito": self._extrair_areas_direito(dados),
                "leis_aplicaveis": dados.get("leis_aplicaveis", []),
                "temas_pesquisa": self._extrair_temas_pesquisa(dados)
            },
            "pedidos": {
                "principais": dados.get("pedidos", ["Pedido não especificado"]) if isinstance(dados.get("pedidos"), list) else [dados.get("pedidos", "Pedido não especificado")],
                "alternativos": dados.get("pedidos_alternativos", []),
                "cautelares": dados.get("pedidos_cautelares", [])
            },
            "urgencia": dados.get("urgencia", False),
            "observacoes": dados.get("observacoes", "")
        }
    
    def _estruturar_parte(self, parte_dados: Dict[str, Any]) -> Dict[str, Any]:
        """Estrutura dados de uma parte (autor ou réu)."""
        if isinstance(parte_dados, str):
            parte_dados = {"nome": parte_dados}
        
        return {
            "nome": parte_dados.get("nome", "Não informado"),
            "tipo_pessoa": self._detectar_tipo_pessoa(parte_dados),
            "cpf_cnpj": parte_dados.get("cpf", parte_dados.get("cnpj", parte_dados.get("cpf_cnpj", ""))),
            "endereco": parte_dados.get("endereco", ""),
            "telefone": parte_dados.get("telefone", ""),
            "email": parte_dados.get("email", ""),
            "profissao": parte_dados.get("profissao", "") if self._detectar_tipo_pessoa(parte_dados) == "fisica" else "",
            "estado_civil": parte_dados.get("estado_civil", "") if self._detectar_tipo_pessoa(parte_dados) == "fisica" else ""
        }
    
    def _detectar_tipo_pessoa(self, dados: Dict[str, Any]) -> str:
        """Detecta se é pessoa física ou jurídica."""
        # Verificar se tem CNPJ
        cnpj = dados.get("cnpj", "")
        if cnpj and (len(cnpj.replace(".", "").replace("/", "").replace("-", "")) == 14):
            return "juridica"
        
        # Verificar se tem CPF
        cpf = dados.get("cpf", "")
        if cpf and (len(cpf.replace(".", "").replace("-", "")) == 11):
            return "fisica"
        
        # Verificar campo tipo_pessoa explícito
        tipo = dados.get("tipo_pessoa", "").lower()
        if tipo in ["juridica", "pj", "empresa"]:
            return "juridica"
        elif tipo in ["fisica", "pf", "pessoa"]:
            return "fisica"
        
        # Verificar por palavras-chave no nome
        nome = dados.get("nome", "").lower()
        palavras_pj = ["ltda", "s.a.", "s/a", "eireli", "mei", "empresa", "comercio", "industria"]
        if any(palavra in nome for palavra in palavras_pj):
            return "juridica"
        
        # Default para pessoa física
        return "fisica"
    
    def _extrair_areas_direito(self, dados: Dict[str, Any]) -> List[str]:
        """Extrai áreas do direito baseado no tipo de ação e fatos."""
        areas = []
        
        tipo_acao = dados.get("tipo_acao", "").lower()
        fatos = str(dados.get("fatos", "")).lower()
        
        # Mapeamento de palavras-chave para áreas do direito
        mapeamento = {
            "direito civil": ["civil", "contrato", "responsabilidade", "danos", "indenização"],
            "direito do consumidor": ["consumidor", "produto", "serviço", "fornecedor", "cdc"],
            "direito trabalhista": ["trabalho", "trabalhista", "emprego", "salário", "rescisão"],
            "direito tributário": ["tributo", "imposto", "taxa", "contribuição", "fiscal"],
            "direito administrativo": ["administrativo", "servidor", "público", "licitação"],
            "direito penal": ["penal", "crime", "delito", "contravenção"],
            "direito comercial": ["comercial", "empresarial", "sociedade", "falência"],
            "direito de família": ["família", "divórcio", "alimentos", "guarda", "união"]
        }
        
        texto_completo = f"{tipo_acao} {fatos}".lower()
        
        for area, palavras_chave in mapeamento.items():
            if any(palavra in texto_completo for palavra in palavras_chave):
                areas.append(area)
        
        # Se não encontrou nenhuma área, adicionar direito civil como padrão
        if not areas:
            areas.append("direito civil")
        
        return areas
    
    def _extrair_temas_pesquisa(self, dados: Dict[str, Any]) -> List[str]:
        """Extrai temas específicos para pesquisa jurídica."""
        temas = []
        
        tipo_acao = dados.get("tipo_acao", "")
        areas = self._extrair_areas_direito(dados)
        
        # Adicionar tipo de ação como tema
        if tipo_acao:
            temas.append(tipo_acao.lower())
        
        # Adicionar áreas do direito
        temas.extend(areas)
        
        # Adicionar temas específicos baseados no conteúdo
        fatos = str(dados.get("fatos", "")).lower()
        
        temas_especificos = {
            "danos morais": ["dano moral", "danos morais", "constrangimento", "humilhação"],
            "juros e correção": ["juros", "correção monetária", "atualização"],
            "tutela antecipada": ["urgência", "tutela", "liminar", "antecipação"],
            "honorários advocatícios": ["honorários", "advocatícios", "sucumbência"],
            "código de processo civil": ["processo", "procedimento", "cpc"],
            "código civil": ["civil", "obrigação", "contrato"]
        }
        
        for tema, palavras in temas_especificos.items():
            if any(palavra in fatos for palavra in palavras):
                temas.append(tema)
        
        return list(set(temas))  # Remover duplicatas
    
    def _validar_e_enriquecer(self, dados: Dict[str, Any]) -> Dict[str, Any]:
        """Validação final e enriquecimento dos dados."""
        # Validar CPF/CNPJ
        for parte in ['autor', 'reu']:
            if parte in dados:
                cpf_cnpj = dados[parte].get('cpf_cnpj', '')
                if cpf_cnpj:
                    dados[parte]['cpf_cnpj'] = self._formatar_cpf_cnpj(cpf_cnpj)
        
        # Garantir que listas não estejam vazias
        if not dados.get('fundamentos_juridicos', {}).get('temas_pesquisa'):
            dados['fundamentos_juridicos']['temas_pesquisa'] = ['direito civil', 'código de processo civil']
        
        if not dados.get('pedidos', {}).get('principais'):
            dados['pedidos']['principais'] = ['Pedido não especificado']
        
        return dados
    
    def _formatar_cpf_cnpj(self, documento: str) -> str:
        """Formata CPF ou CNPJ."""
        # Remove caracteres não numéricos
        numeros = re.sub(r'\D', '', documento)
        
        if len(numeros) == 11:  # CPF
            return f"{numeros[:3]}.{numeros[3:6]}.{numeros[6:9]}-{numeros[9:]}"
        elif len(numeros) == 14:  # CNPJ
            return f"{numeros[:2]}.{numeros[2:5]}.{numeros[5:8]}/{numeros[8:12]}-{numeros[12:]}"
        else:
            return documento  # Retorna original se não for CPF nem CNPJ válido


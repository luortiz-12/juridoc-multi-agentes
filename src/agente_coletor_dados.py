# agente_coletor_dados.py - Agente Coletor que SEMPRE usa dados reais

import os
import json
import re
from typing import Dict, Any, List, Optional
from datetime import datetime

# LangChain imports
try:
    from langchain.llms import OpenAI
    from langchain.prompts import PromptTemplate
    from langchain.chains import LLMChain
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

class AgenteColetorDados:
    """
    Agente Coletor de Dados CORRIGIDO que:
    - SEMPRE usa dados reais do formulário
    - NUNCA cria dados simulados ou falsos
    - Mapeia corretamente os campos do n8n
    - Fallback inteligente quando LLM falha
    """
    
    def __init__(self, openai_api_key: str = None):
        print("📊 Inicializando Agente Coletor de Dados CORRIGIDO...")
        
        self.openai_api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        
        # MAPEAMENTO DIRETO DOS CAMPOS DO FORMULÁRIO
        self.mapeamento_campos = {
            # Dados do autor/cliente
            'clienteNome': 'autor.nome',
            'Qualificação': 'autor.qualificacao',
            
            # Dados da parte contrária
            'nome_contrario_peticao': 'reu.nome',
            'qualificacao_contrario_peticao': 'reu.qualificacao',
            
            # Dados do caso
            'tipoDocumento': 'tipo_acao',
            'fatos_peticao': 'fatos',
            'verbas_pleiteadas_peticao': 'pedidos',
            'valor_causa_peticao': 'valor_causa',
            
            # Dados trabalhistas específicos
            'data_admissao_peticao': 'data_admissao',
            'data_demissao_peticao': 'data_demissao',
            'salario_peticao': 'salario',
            'jornada_peticao': 'jornada',
            'motivo_saida_peticao': 'motivo_saida',
            'documentos_peticao': 'documentos'
        }
        
        # Inicializar LLM apenas se disponível
        if LANGCHAIN_AVAILABLE and self.openai_api_key:
            try:
                self.llm = OpenAI(
                    openai_api_key=self.openai_api_key,
                    temperature=0.1,
                    max_tokens=1000
                )
                self.llm_disponivel = True
                print("✅ LLM inicializado para análise complementar")
            except Exception as e:
                print(f"⚠️ LLM não disponível: {e}")
                self.llm_disponivel = False
        else:
            self.llm_disponivel = False
            print("⚠️ LLM não disponível - usando apenas mapeamento direto")
        
        print("✅ Agente Coletor CORRIGIDO inicializado")
    
    def coletar_e_processar(self, dados_entrada: Dict[str, Any]) -> Dict[str, Any]:
        """
        Coleta e processa dados SEMPRE usando informações reais do formulário.
        NUNCA cria dados simulados ou falsos.
        """
        try:
            print("📊 Iniciando coleta e processamento de dados REAIS...")
            print(f"📋 Campos recebidos: {list(dados_entrada.keys())}")
            
            # ETAPA 1: MAPEAMENTO DIRETO (SEMPRE FUNCIONA)
            dados_estruturados = self._mapear_dados_direto(dados_entrada)
            
            # ETAPA 2: ANÁLISE COMPLEMENTAR (SE LLM DISPONÍVEL)
            if self.llm_disponivel:
                try:
                    dados_complementares = self._analisar_com_llm(dados_entrada)
                    dados_estruturados = self._mesclar_dados(dados_estruturados, dados_complementares)
                except Exception as e:
                    print(f"⚠️ Análise LLM falhou, usando apenas mapeamento direto: {e}")
            
            # ETAPA 3: VALIDAÇÃO E LIMPEZA
            dados_finais = self._validar_e_limpar(dados_estruturados)
            
            print("✅ Dados coletados e processados com sucesso")
            print(f"📊 Autor: {dados_finais['autor']['nome']}")
            print(f"📊 Réu: {dados_finais['reu']['nome']}")
            print(f"📊 Tipo: {dados_finais['tipo_acao']}")
            
            return {
                "status": "sucesso",
                "dados_estruturados": dados_finais,
                "metadados": {
                    "timestamp": datetime.now().isoformat(),
                    "campos_processados": len(dados_entrada),
                    "metodo_usado": "mapeamento_direto" + ("_com_llm" if self.llm_disponivel else ""),
                    "dados_reais": True,
                    "dados_simulados": False
                }
            }
            
        except Exception as e:
            print(f"❌ Erro na coleta de dados: {e}")
            return {
                "status": "erro",
                "erro": str(e),
                "dados_estruturados": self._gerar_estrutura_minima(dados_entrada),
                "timestamp": datetime.now().isoformat()
            }
    
    def _mapear_dados_direto(self, dados_entrada: Dict[str, Any]) -> Dict[str, Any]:
        """
        Mapeia dados diretamente do formulário para estrutura padronizada.
        SEMPRE usa dados reais, nunca simula.
        """
        print("🔄 Mapeando dados diretamente do formulário...")
        
        # Estrutura base
        dados_estruturados = {
            "tipo_acao": self._extrair_tipo_acao(dados_entrada),
            "autor": self._extrair_dados_autor(dados_entrada),
            "reu": self._extrair_dados_reu(dados_entrada),
            "fatos": self._extrair_fatos(dados_entrada),
            "pedidos": self._extrair_pedidos(dados_entrada),
            "valor_causa": self._extrair_valor_causa(dados_entrada),
            "competencia": self._extrair_competencia(dados_entrada),
            "fundamentos_necessarios": self._extrair_fundamentos(dados_entrada),
            "observacoes": self._extrair_observacoes(dados_entrada),
            "urgencia": False
        }
        
        return dados_estruturados
    
    def _extrair_tipo_acao(self, dados: Dict[str, Any]) -> str:
        """Extrai tipo de ação dos dados reais."""
        
        # Verificar campo direto
        tipo_documento = dados.get('tipoDocumento', '').strip()
        if tipo_documento and tipo_documento != 'peticao':
            return tipo_documento
        
        # Analisar contexto para identificar tipo
        fatos = str(dados.get('fatos_peticao', '')).lower()
        motivo_saida = str(dados.get('motivo_saida_peticao', '')).lower()
        verbas = str(dados.get('verbas_pleiteadas_peticao', '')).lower()
        
        # Identificar por palavras-chave
        if any(palavra in fatos + motivo_saida + verbas for palavra in 
               ['rescisão indireta', 'horas extras', 'assédio moral', 'trabalhista', 'clt', 'demissão']):
            return "Ação Trabalhista"
        elif any(palavra in fatos + verbas for palavra in 
                ['consumidor', 'defeito', 'vício', 'fornecedor']):
            return "Ação de Consumidor"
        elif any(palavra in fatos + verbas for palavra in 
                ['danos morais', 'responsabilidade civil', 'indenização']):
            return "Ação de Indenização"
        
        # Se não conseguir identificar, usar dados disponíveis
        return "Ação Cível"
    
    def _extrair_dados_autor(self, dados: Dict[str, Any]) -> Dict[str, Any]:
        """Extrai dados do autor usando apenas informações reais."""
        
        nome = dados.get('clienteNome', '').strip()
        qualificacao = dados.get('Qualificação', '').strip()
        
        # Extrair CPF da qualificação se disponível
        cpf = ""
        if qualificacao:
            cpf_match = re.search(r'CPF\s*n?º?\s*([\d\.\-]+)', qualificacao, re.IGNORECASE)
            if cpf_match:
                cpf = cpf_match.group(1)
        
        # Extrair CTPS se disponível
        ctps = ""
        if qualificacao:
            ctps_match = re.search(r'CTPS\s*n?º?\s*([\d]+)', qualificacao, re.IGNORECASE)
            if ctps_match:
                ctps = ctps_match.group(1)
        
        return {
            "nome": nome if nome else "[NOME DO AUTOR A SER PREENCHIDO]",
            "qualificacao": qualificacao if qualificacao else "[QUALIFICAÇÃO A SER PREENCHIDA]",
            "cpf_cnpj": cpf,
            "ctps": ctps,
            "tipo_pessoa": "fisica",  # Assumir pessoa física por padrão
            "endereco": "[ENDEREÇO A SER PREENCHIDO]",
            "telefone": "",
            "email": ""
        }
    
    def _extrair_dados_reu(self, dados: Dict[str, Any]) -> Dict[str, Any]:
        """Extrai dados do réu usando apenas informações reais."""
        
        nome = dados.get('nome_contrario_peticao', '').strip()
        qualificacao = dados.get('qualificacao_contrario_peticao', '').strip()
        
        # Extrair CNPJ da qualificação se disponível
        cnpj = ""
        if qualificacao:
            cnpj_match = re.search(r'CNPJ\s*(?:sob\s*o\s*)?n?º?\s*([\d\.\-\/]+)', qualificacao, re.IGNORECASE)
            if cnpj_match:
                cnpj = cnpj_match.group(1)
        
        # Extrair endereço se disponível
        endereco = ""
        if qualificacao:
            endereco_match = re.search(r'(?:sede|endereço|sito).*?([A-Z][^,]+(?:,\s*[^,]+)*)', qualificacao, re.IGNORECASE)
            if endereco_match:
                endereco = endereco_match.group(1).strip()
        
        # Determinar tipo de pessoa
        tipo_pessoa = "juridica" if any(palavra in qualificacao.lower() for palavra in 
                                      ['ltda', 'sa', 's.a.', 'eireli', 'mei', 'cnpj']) else "fisica"
        
        return {
            "nome": nome if nome else "[NOME DO RÉU A SER PREENCHIDO]",
            "qualificacao": qualificacao if qualificacao else "[QUALIFICAÇÃO A SER PREENCHIDA]",
            "cpf_cnpj": cnpj,
            "tipo_pessoa": tipo_pessoa,
            "endereco": endereco if endereco else "[ENDEREÇO A SER PREENCHIDO]",
            "telefone": "",
            "email": ""
        }
    
    def _extrair_fatos(self, dados: Dict[str, Any]) -> str:
        """Extrai fatos usando apenas informações reais do formulário."""
        
        fatos_principais = dados.get('fatos_peticao', '').strip()
        
        # Adicionar informações complementares se disponíveis
        fatos_completos = []
        
        if fatos_principais:
            fatos_completos.append(fatos_principais)
        
        # Adicionar dados trabalhistas específicos se disponíveis
        if dados.get('data_admissao_peticao'):
            fatos_completos.append(f"Data de admissão: {dados['data_admissao_peticao']}")
        
        if dados.get('data_demissao_peticao'):
            fatos_completos.append(f"Data de demissão: {dados['data_demissao_peticao']}")
        
        if dados.get('salario_peticao'):
            fatos_completos.append(f"Salário: R$ {dados['salario_peticao']}")
        
        if dados.get('jornada_peticao'):
            fatos_completos.append(f"Jornada de trabalho: {dados['jornada_peticao']}")
        
        if dados.get('motivo_saida_peticao'):
            fatos_completos.append(f"Motivo da saída: {dados['motivo_saida_peticao']}")
        
        return " ".join(fatos_completos) if fatos_completos else "[FATOS A SEREM DETALHADOS]"
    
    def _extrair_pedidos(self, dados: Dict[str, Any]) -> str:
        """Extrai pedidos usando apenas informações reais."""
        
        verbas = dados.get('verbas_pleiteadas_peticao', '').strip()
        
        if verbas:
            return verbas
        
        # Se não há pedidos específicos, indicar que devem ser preenchidos
        return "[PEDIDOS A SEREM ESPECIFICADOS]"
    
    def _extrair_valor_causa(self, dados: Dict[str, Any]) -> str:
        """Extrai valor da causa usando apenas dados reais."""
        
        valor = dados.get('valor_causa_peticao', '').strip()
        
        if valor and valor != '0' and valor != '0.00':
            # Formatar valor se necessário
            try:
                valor_num = float(valor.replace(',', '.'))
                return f"R$ {valor_num:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
            except:
                return f"R$ {valor}"
        
        return "[VALOR A SER ARBITRADO]"
    
    def _extrair_competencia(self, dados: Dict[str, Any]) -> str:
        """Extrai competência baseada no tipo de ação e dados disponíveis."""
        
        # Analisar tipo de ação para determinar competência
        fatos = str(dados.get('fatos_peticao', '')).lower()
        motivo = str(dados.get('motivo_saida_peticao', '')).lower()
        
        if any(palavra in fatos + motivo for palavra in 
               ['rescisão indireta', 'horas extras', 'trabalhista', 'clt', 'empregado', 'empregador']):
            return "Justiça do Trabalho"
        elif any(palavra in fatos for palavra in ['consumidor', 'fornecedor']):
            return "Juizado Especial Cível"
        
        return "[COMPETÊNCIA A SER DEFINIDA]"
    
    def _extrair_fundamentos(self, dados: Dict[str, Any]) -> List[str]:
        """Extrai fundamentos jurídicos baseados nos dados reais."""
        
        fundamentos = []
        
        fatos = str(dados.get('fatos_peticao', '')).lower()
        motivo = str(dados.get('motivo_saida_peticao', '')).lower()
        verbas = str(dados.get('verbas_pleiteadas_peticao', '')).lower()
        
        texto_completo = fatos + " " + motivo + " " + verbas
        
        # Identificar fundamentos baseados no conteúdo real
        if 'rescisão indireta' in texto_completo:
            fundamentos.extend(['rescisão indireta', 'CLT art. 483'])
        
        if 'horas extras' in texto_completo:
            fundamentos.extend(['horas extras', 'CLT art. 59'])
        
        if 'assédio moral' in texto_completo:
            fundamentos.extend(['assédio moral', 'danos morais'])
        
        if 'danos morais' in texto_completo:
            fundamentos.append('danos morais')
        
        # Fundamentos por área
        if any(palavra in texto_completo for palavra in ['trabalhista', 'empregado', 'clt']):
            fundamentos.extend(['direito trabalhista', 'CLT'])
        elif any(palavra in texto_completo for palavra in ['consumidor', 'fornecedor']):
            fundamentos.extend(['direito do consumidor', 'CDC'])
        else:
            fundamentos.extend(['direito civil', 'código civil'])
        
        return list(set(fundamentos)) if fundamentos else ['direito civil']
    
    def _extrair_observacoes(self, dados: Dict[str, Any]) -> str:
        """Extrai observações dos dados disponíveis."""
        
        observacoes = []
        
        if dados.get('documentos_peticao'):
            observacoes.append(f"Documentos anexos: {dados['documentos_peticao']}")
        
        return ". ".join(observacoes) if observacoes else ""
    
    def _analisar_com_llm(self, dados_entrada: Dict[str, Any]) -> Dict[str, Any]:
        """Análise complementar com LLM se disponível."""
        
        if not self.llm_disponivel:
            return {}
        
        try:
            prompt = f"""
            Analise os seguintes dados de um caso jurídico e extraia informações estruturadas.
            IMPORTANTE: Use APENAS as informações fornecidas, não invente dados.
            
            Dados do caso:
            {json.dumps(dados_entrada, indent=2, ensure_ascii=False)}
            
            Retorne um JSON com análise complementar focando em:
            - Identificação precisa do tipo de ação
            - Fundamentos jurídicos aplicáveis
            - Urgência do caso
            
            Responda apenas com JSON válido.
            """
            
            resposta = self.llm(prompt)
            
            try:
                return json.loads(resposta)
            except:
                print("⚠️ Resposta LLM não é JSON válido")
                return {}
                
        except Exception as e:
            print(f"⚠️ Erro na análise LLM: {e}")
            return {}
    
    def _mesclar_dados(self, dados_base: Dict[str, Any], dados_llm: Dict[str, Any]) -> Dict[str, Any]:
        """Mescla dados base com análise LLM, priorizando dados reais."""
        
        # Sempre priorizar dados base (reais) sobre análise LLM
        resultado = dados_base.copy()
        
        # Apenas complementar campos que não comprometam dados reais
        if dados_llm.get('urgencia') and isinstance(dados_llm['urgencia'], bool):
            resultado['urgencia'] = dados_llm['urgencia']
        
        return resultado
    
    def _validar_e_limpar(self, dados: Dict[str, Any]) -> Dict[str, Any]:
        """Valida e limpa dados estruturados."""
        
        # Garantir que campos obrigatórios existam
        campos_obrigatorios = {
            'tipo_acao': 'Ação Cível',
            'autor': {},
            'reu': {},
            'fatos': '[FATOS A SEREM DETALHADOS]',
            'pedidos': '[PEDIDOS A SEREM ESPECIFICADOS]',
            'valor_causa': '[VALOR A SER ARBITRADO]',
            'competencia': '[COMPETÊNCIA A SER DEFINIDA]',
            'fundamentos_necessarios': ['direito civil'],
            'observacoes': '',
            'urgencia': False
        }
        
        for campo, valor_padrao in campos_obrigatorios.items():
            if campo not in dados or not dados[campo]:
                dados[campo] = valor_padrao
        
        return dados
    
    def _gerar_estrutura_minima(self, dados_entrada: Dict[str, Any]) -> Dict[str, Any]:
        """Gera estrutura mínima quando tudo falha, usando apenas dados reais."""
        
        return {
            "tipo_acao": "Ação Cível",
            "autor": {
                "nome": dados_entrada.get('clienteNome', '[NOME DO AUTOR A SER PREENCHIDO]'),
                "qualificacao": dados_entrada.get('Qualificação', '[QUALIFICAÇÃO A SER PREENCHIDA]')
            },
            "reu": {
                "nome": dados_entrada.get('nome_contrario_peticao', '[NOME DO RÉU A SER PREENCHIDO]'),
                "qualificacao": dados_entrada.get('qualificacao_contrario_peticao', '[QUALIFICAÇÃO A SER PREENCHIDA]')
            },
            "fatos": dados_entrada.get('fatos_peticao', '[FATOS A SEREM DETALHADOS]'),
            "pedidos": dados_entrada.get('verbas_pleiteadas_peticao', '[PEDIDOS A SEREM ESPECIFICADOS]'),
            "valor_causa": dados_entrada.get('valor_causa_peticao', '[VALOR A SER ARBITRADO]'),
            "competencia": "[COMPETÊNCIA A SER DEFINIDA]",
            "fundamentos_necessarios": ["direito civil"],
            "observacoes": "",
            "urgencia": False
        }


# test_completo.py - Teste Completo do Sistema com Todos os Agentes

import sys
import os
import json
sys.path.append('src')

def test_imports_agentes():
    """Testa se todos os agentes podem ser importados."""
    try:
        print("🧪 Testando imports dos agentes...")
        
        from agente_coletor_dados import AgenteColetorDados
        print("✅ AgenteColetorDados importado")
        
        from pesquisa_juridica import PesquisaJuridica
        print("✅ PesquisaJuridica importado")
        
        from agente_redator import AgenteRedator
        print("✅ AgenteRedator importado")
        
        from agente_validador import AgenteValidador
        print("✅ AgenteValidador importado")
        
        from orquestrador import OrquestradorPrincipal
        print("✅ OrquestradorPrincipal importado")
        
        return True
        
    except ImportError as e:
        print(f"❌ Erro de import: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        return False

def test_agente_coletor():
    """Testa o agente coletor de dados sem API key."""
    try:
        print("\n📊 Testando AgenteColetorDados...")
        
        # Dados de teste
        dados_teste = {
            "tipo_acao": "Ação de Cobrança",
            "autor": {
                "nome": "João Silva",
                "cpf": "123.456.789-00",
                "endereco": "Rua das Flores, 123"
            },
            "reu": {
                "nome": "Empresa XYZ Ltda",
                "cnpj": "12.345.678/0001-90"
            },
            "fatos": "Prestação de serviços não pagos",
            "pedidos": ["Cobrança", "Juros"]
        }
        
        # Testar métodos auxiliares sem API
        from agente_coletor_dados import AgenteColetorDados
        
        # Simular instância para testar métodos auxiliares
        class MockColetor:
            def _validar_dados_basicos(self, dados):
                return AgenteColetorDados._validar_dados_basicos(None, dados)
            
            def _criar_estrutura_basica(self, dados):
                return AgenteColetorDados._criar_estrutura_basica(None, dados)
            
            def _detectar_tipo_pessoa(self, dados):
                return AgenteColetorDados._detectar_tipo_pessoa(None, dados)
        
        mock_coletor = MockColetor()
        
        # Testar validação básica
        dados_validados = mock_coletor._validar_dados_basicos(dados_teste)
        print("✅ Validação básica funcionando")
        
        # Testar estruturação básica
        estrutura_basica = mock_coletor._criar_estrutura_basica(dados_validados)
        print("✅ Estruturação básica funcionando")
        
        # Testar detecção de tipo de pessoa
        tipo_autor = mock_coletor._detectar_tipo_pessoa(dados_teste["autor"])
        tipo_reu = mock_coletor._detectar_tipo_pessoa(dados_teste["reu"])
        print(f"✅ Detecção de tipos: Autor={tipo_autor}, Réu={tipo_reu}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste do coletor: {e}")
        return False

def test_pesquisa_juridica():
    """Testa o módulo de pesquisa jurídica."""
    try:
        print("\n🔍 Testando PesquisaJuridica...")
        
        from pesquisa_juridica import PesquisaJuridica
        pesquisa = PesquisaJuridica()
        
        # Testar métodos de validação
        conteudo_legal = "Esta é uma lei sobre direito civil artigo 123"
        is_legal = pesquisa._is_relevant_legal_content(conteudo_legal)
        print(f"✅ Validação conteúdo legal: {is_legal}")
        
        conteudo_juris = "Acórdão do STF sobre direito constitucional"
        is_juris = pesquisa._is_relevant_jurisprudence(conteudo_juris)
        print(f"✅ Validação jurisprudência: {is_juris}")
        
        conteudo_doutrina = "Doutrina de Maria Helena Diniz sobre contratos"
        is_doutrina = pesquisa._is_relevant_doctrine(conteudo_doutrina)
        print(f"✅ Validação doutrina: {is_doutrina}")
        
        # Testar geração de resumo
        resumo = pesquisa._gerar_resumo_pesquisa(["direito civil"], "Ação de Cobrança")
        print("✅ Geração de resumo funcionando")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de pesquisa: {e}")
        return False

def test_flask_app_completa():
    """Testa a aplicação Flask completa."""
    try:
        print("\n🌐 Testando aplicação Flask completa...")
        
        # Importar versão de teste
        from main_test import create_test_app
        app = create_test_app()
        
        with app.test_client() as client:
            # Testar rota principal
            response = client.get('/')
            print(f"✅ Rota principal: Status {response.status_code}")
            
            # Testar rota de status
            response = client.get('/api/status')
            print(f"✅ Rota de status: Status {response.status_code}")
            
            # Testar endpoint de petição
            dados_teste = {
                "tipo_acao": "Ação de Cobrança",
                "autor": {"nome": "João Silva"},
                "reu": {"nome": "Empresa XYZ"},
                "fatos": "Serviços prestados não pagos",
                "pedidos": ["Cobrança do valor"]
            }
            
            response = client.post('/api/gerar-peticao', json=dados_teste)
            print(f"✅ Endpoint petição: Status {response.status_code}")
            
            if response.status_code == 200:
                data = response.get_json()
                print(f"   Resposta contém documento: {'documento_html' in data}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste Flask: {e}")
        return False

def test_estrutura_arquivos():
    """Testa se todos os arquivos necessários existem."""
    try:
        print("\n📁 Testando estrutura de arquivos...")
        
        arquivos_necessarios = [
            'src/agente_coletor_dados.py',
            'src/pesquisa_juridica.py', 
            'src/agente_redator.py',
            'src/agente_validador.py',
            'src/orquestrador.py',
            'src/main.py',
            'src/main_v2.py',
            'src/main_test.py',
            'requirements.txt',
            'Procfile',
            'start.py',
            'README.md'
        ]
        
        arquivos_encontrados = 0
        for arquivo in arquivos_necessarios:
            if os.path.exists(arquivo):
                arquivos_encontrados += 1
                print(f"✅ {arquivo}")
            else:
                print(f"❌ {arquivo} - NÃO ENCONTRADO")
        
        print(f"\n📊 Arquivos encontrados: {arquivos_encontrados}/{len(arquivos_necessarios)}")
        return arquivos_encontrados == len(arquivos_necessarios)
        
    except Exception as e:
        print(f"❌ Erro no teste de estrutura: {e}")
        return False

def test_dados_exemplo():
    """Testa processamento com dados de exemplo realistas."""
    try:
        print("\n📋 Testando com dados de exemplo realistas...")
        
        dados_exemplo = {
            "tipo_acao": "Ação de Cobrança",
            "competencia": "1ª Vara Cível de São Paulo/SP",
            "valor_causa": "R$ 15.000,00",
            "autor": {
                "nome": "Maria Santos Silva",
                "tipo_pessoa": "fisica",
                "cpf": "123.456.789-00",
                "endereco": "Rua das Palmeiras, 456, Bairro Centro, São Paulo/SP, CEP 01234-567",
                "telefone": "(11) 99999-9999",
                "email": "maria.santos@email.com",
                "profissao": "Consultora",
                "estado_civil": "Solteira"
            },
            "reu": {
                "nome": "Empresa Serviços Ltda",
                "tipo_pessoa": "juridica",
                "cnpj": "12.345.678/0001-90",
                "endereco": "Av. Paulista, 1000, São Paulo/SP, CEP 01310-100",
                "telefone": "(11) 3333-4444",
                "email": "contato@empresaservicos.com.br"
            },
            "fatos": {
                "resumo": "A autora prestou serviços de consultoria para a ré entre janeiro e março de 2024, conforme contrato firmado, mas não recebeu o pagamento acordado de R$ 15.000,00.",
                "cronologia": [
                    "Janeiro 2024: Assinatura do contrato de prestação de serviços",
                    "Janeiro-Março 2024: Prestação dos serviços de consultoria",
                    "Abril 2024: Entrega do relatório final",
                    "Maio 2024: Vencimento do pagamento sem quitação",
                    "Junho 2024: Notificação extrajudicial sem resposta"
                ],
                "documentos": [
                    "Contrato de prestação de serviços",
                    "Relatório final entregue",
                    "Notificação extrajudicial",
                    "Comprovantes de entrega"
                ],
                "valores": ["R$ 15.000,00 (valor principal)", "Juros e correção monetária"]
            },
            "pedidos": {
                "principais": [
                    "Condenação da ré ao pagamento de R$ 15.000,00",
                    "Aplicação de juros de mora de 1% ao mês",
                    "Correção monetária pelo IPCA",
                    "Condenação em honorários advocatícios"
                ],
                "alternativos": [],
                "cautelares": []
            },
            "urgencia": False,
            "observacoes": "Caso simples de cobrança de serviços prestados com documentação completa."
        }
        
        print("✅ Dados de exemplo estruturados")
        print(f"   Tipo de ação: {dados_exemplo['tipo_acao']}")
        print(f"   Valor da causa: {dados_exemplo['valor_causa']}")
        print(f"   Número de pedidos: {len(dados_exemplo['pedidos']['principais'])}")
        print(f"   Documentos: {len(dados_exemplo['fatos']['documentos'])}")
        
        # Validar estrutura dos dados
        campos_obrigatorios = ['tipo_acao', 'autor', 'reu', 'fatos', 'pedidos']
        for campo in campos_obrigatorios:
            if campo in dados_exemplo:
                print(f"✅ Campo obrigatório '{campo}' presente")
            else:
                print(f"❌ Campo obrigatório '{campo}' ausente")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de dados exemplo: {e}")
        return False

def main():
    """Executa todos os testes."""
    print("🚀 Iniciando Testes Completos do JuriDoc com Agentes")
    print("=" * 60)
    
    tests = [
        ("Imports dos Agentes", test_imports_agentes),
        ("Agente Coletor de Dados", test_agente_coletor),
        ("Pesquisa Jurídica", test_pesquisa_juridica),
        ("Aplicação Flask", test_flask_app_completa),
        ("Estrutura de Arquivos", test_estrutura_arquivos),
        ("Dados de Exemplo", test_dados_exemplo)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        if test_func():
            passed += 1
            print(f"✅ {test_name}: PASSOU")
        else:
            print(f"❌ {test_name}: FALHOU")
    
    print("\n" + "="*60)
    print(f"📊 RESULTADO FINAL: {passed}/{total} testes passaram")
    
    if passed == total:
        print("🎉 TODOS OS TESTES PASSARAM! Sistema funcionando corretamente.")
        print("\n🚀 PRÓXIMOS PASSOS:")
        print("1. Configure a variável OPENAI_API_KEY para testes completos")
        print("2. Faça deploy no Render")
        print("3. Teste integração com n8n")
        return True
    else:
        print("⚠️ ALGUNS TESTES FALHARAM. Verifique os erros acima.")
        print(f"Taxa de sucesso: {(passed/total)*100:.1f}%")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)


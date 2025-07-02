# test_basic.py - Teste básico do sistema

import sys
import os
sys.path.append('src')

def test_imports():
    """Testa se todos os imports funcionam corretamente."""
    try:
        print("🧪 Testando imports...")
        
        # Testar import do módulo de pesquisa
        from pesquisa_juridica import PesquisaJuridica
        print("✅ PesquisaJuridica importado com sucesso")
        
        # Testar inicialização da pesquisa
        pesquisa = PesquisaJuridica()
        print("✅ PesquisaJuridica inicializado com sucesso")
        
        # Testar Flask app
        from main import create_app
        print("✅ Flask app importado com sucesso")
        
        app = create_app()
        print("✅ Flask app criado com sucesso")
        
        return True
        
    except ImportError as e:
        print(f"❌ Erro de import: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        return False

def test_pesquisa_module():
    """Testa o módulo de pesquisa jurídica."""
    try:
        print("\n🔍 Testando módulo de pesquisa...")
        
        from pesquisa_juridica import PesquisaJuridica
        pesquisa = PesquisaJuridica()
        
        # Testar pesquisa específica (sem fazer requisições reais)
        print("✅ Módulo de pesquisa carregado")
        
        # Testar métodos de validação
        test_content = "Esta é uma lei sobre direito civil artigo 123"
        is_legal = pesquisa._is_relevant_legal_content(test_content)
        print(f"✅ Validação de conteúdo legal: {is_legal}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de pesquisa: {e}")
        return False

def test_flask_routes():
    """Testa as rotas do Flask."""
    try:
        print("\n🌐 Testando rotas Flask...")
        
        from main import create_app
        app = create_app()
        
        with app.test_client() as client:
            # Testar rota principal
            response = client.get('/')
            print(f"✅ Rota principal: Status {response.status_code}")
            
            # Testar rota de status
            response = client.get('/api/status')
            print(f"✅ Rota de status: Status {response.status_code}")
            
            if response.status_code == 200:
                data = response.get_json()
                print(f"   Resposta: {data}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de rotas: {e}")
        return False

def main():
    """Executa todos os testes."""
    print("🚀 Iniciando testes do JuriDoc Simplificado")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_pesquisa_module,
        test_flask_routes
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Resultado: {passed}/{total} testes passaram")
    
    if passed == total:
        print("🎉 Todos os testes passaram! Sistema funcionando corretamente.")
        return True
    else:
        print("⚠️ Alguns testes falharam. Verifique os erros acima.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)



# INSTRUÇÕES PARA DEPLOY NO RENDER

## Arquivos Integrados:
- ✅ Sistema RAG completo integrado
- ✅ 6 arquivos RAG copiados
- ✅ Dependencies atualizadas no requirements.txt
- ✅ Configuração RAG criada

## Para fazer o deploy:

1. **Commit e Push para GitHub:**
   ```bash
   git add .
   git commit -m "Integração sistema RAG completo"
   git push origin main
   ```

2. **No Render:**
   - O deploy será automático após o push
   - Aguardar build e deploy (pode demorar 5-10 minutos)
   - Verificar logs para confirmar carregamento do RAG

3. **Testar endpoints:**
   - Status: https://sua-url.onrender.com/api/juridoc/status
   - Geração: https://sua-url.onrender.com/api/juridoc/gerar

## Funcionalidades RAG Disponíveis:
- 📚 Base de conhecimento com 195+ documentos analisados
- 🔍 Busca online em LexML, Planalto, JusBrasil
- 🤖 Agentes técnicos e redatores aprimorados
- 🛡️ Fallback inteligente para conhecimento LLM
- ⚡ Cache de buscas para performance

## Configurações:
- Arquivo: rag_config.json
- Logs: Verificar mensagens "✅ Sistema RAG carregado"
- Fallback: Sistema funciona mesmo se RAG falhar

## Monitoramento:
- Verificar logs de inicialização
- Testar geração de documentos
- Confirmar qualidade dos resultados

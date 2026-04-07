# ⚠️ Limitações Conhecidas

Lista de limitações atuais do projeto e possíveis soluções futuras.

> **Escopo:** Este projeto foi desenhado para análise heurística de currículos técnicos da área de TI. O dicionário de palavras-chave e as regras de estrutura são otimizados para esse contexto.

---

## Processamento de PDF

### 1. Sem OCR

**Limitação:** PDFs que são imagens escaneadas não têm texto extraído.

**Impacto:** Score será 0 para currículos escaneados ou impressos e digitalizados.

**Sintoma:**
```json
{
  "extracted_text": "",
  "final_score": 0
}
```

**Solução futura:** Integrar Tesseract OCR.

**Workaround atual:** Usar PDFs com texto selecionável (criados digitalmente, não escaneados).

---

### 2. Limite de 16MB

**Limitação:** Arquivos maiores que 16MB são rejeitados.

**Impacto:** Currículos muito elaborados com muitas imagens podem exceder.

**Sintoma:**
```
413 Request Entity Too Large
```

**Solução futura:** Aumentar limite ou comprimir antes de processar.

**Workaround atual:** Comprimir PDF antes de enviar.

---

### 3. Apenas PDF

**Limitação:** Não aceita .docx, .doc, .txt, etc.

**Impacto:** Usuários com currículo em Word precisam converter.

**Solução futura:** Suporte a múltiplos formatos com python-docx.

**Workaround atual:** Converter para PDF antes de enviar.

---

## Análise ATS

### 4. Sem Integração com ATS Real

**Limitação:** A análise é uma simulação heurística, não uma validação oficial.

**Impacto:** Score pode diferir de ATS reais do mercado (Greenhouse, Lever, etc.).

**Clarificação:** Este projeto **simula** comportamento de ATS para fins educacionais. Não substitui validação em sistemas reais.

---

### 5. Dicionário de Keywords Técnicas

**Limitação:** ~200 keywords técnicas mapeadas, focadas em TI (infraestrutura, DevOps, desenvolvimento).

**Impacto:** Currículos de áreas fora de TI não terão análise adequada. Este é um recorte de escopo, não uma limitação técnica.

**Solução futura:** Permitir upload de vaga para comparação dinâmica de keywords.

---

### 6. Apenas Português

**Limitação:** NLP otimizado para português brasileiro.

**Impacto:** Currículos em inglês/espanhol terão análise degradada.

**Solução futura:** Detecção de idioma e stemmer apropriado.

---

## Segurança e Privacidade

### 7. Sem Autenticação

**Limitação:** Qualquer pessoa com acesso à URL pode usar.

**Impacto:** Adequado apenas para uso local ou demonstração.

**Solução futura:** Implementar auth (OAuth, JWT).

---

### 8. Logs Contêm Dados Sensíveis

**Limitação:** Logs salvam texto extraído do currículo.

**Impacto:** Dados pessoais podem vazar se logs forem expostos.

**Mitigação atual:** `.gitignore` ignora pasta `logs/`.

**Solução futura:** Logs estruturados sem PII.

---

## Infraestrutura

### 9. Sem Persistência

**Limitação:** Análises não são salvas em banco de dados.

**Impacto:** Não há histórico de análises.

**Solução futura:** PostgreSQL/SQLite para persistência.

---

### 10. Logs Locais

**Limitação:** Logs apenas em arquivo local.

**Impacto:** Difícil debugging em produção distribuída.

**Solução futura:** CloudWatch Logs na AWS.

---

### 11. Sem Cache

**Limitação:** PDFs são reprocessados a cada envio.

**Impacto:** Mesmo PDF enviado 2x = 2 processamentos.

**Solução futura:** Hash do PDF + Redis cache.

---

### 12. Sem Rate Limiting

**Limitação:** Não há limite de requests.

**Impacto:** Possível abuso ou DoS.

**Solução futura:** Rate limiting no Nginx ou middleware Flask.

---

## Performance

### 13. Processamento Síncrono

**Limitação:** Análise é feita na mesma thread do request.

**Impacto:** Request pode demorar para PDFs grandes.

**Solução futura:** Celery para processamento assíncrono.

---

### 14. Sem Métricas

**Limitação:** Não há coleta de métricas de performance.

**Impacto:** Difícil identificar gargalos.

**Solução futura:** Prometheus + Grafana ou CloudWatch.

---

## Comparativo: Atual vs Futuro

| Limitação | Estado Atual | Roadmap |
|-----------|--------------|---------|
| OCR | ❌ | Fase 7 (Tesseract) |
| Múltiplos formatos | ❌ | Fase 7 |
| Auth | ❌ | Fase 6 |
| Persistência | ❌ | Fase 6 |
| Cache | ❌ | Fase 6 |
| Rate limiting | ❌ | Fase 5 (Nginx) |
| Logs centralizados | ❌ | Fase 5 (CloudWatch) |
| Métricas | ❌ | Fase 6 |
| Multi-idioma | ❌ | Fase 7 |

---

## Por que Essas Limitações São Aceitáveis?

1. **Escopo do projeto:** Análise heurística de currículos técnicos, não produto genérico
2. **Foco:** Demonstrar empacotamento e operação de aplicação Python containerizada
3. **Recorte intencional:** Área de TI como público-alvo, não todas as profissões
4. **Evolução planejada:** Roadmap documenta como endereçar cada limitação
5. **Transparência:** Documentar limitações é melhor que escondê-las

---

## Como Contribuir

Se quiser ajudar a resolver alguma limitação:

1. Abrir issue no GitHub descrevendo a solução proposta
2. Discutir abordagem antes de implementar
3. Submeter PR com testes

Ver [ROADMAP.md](ROADMAP.md) para prioridades.

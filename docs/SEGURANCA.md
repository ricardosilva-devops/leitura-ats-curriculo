# 🔐 Segurança e Privacidade

Política de tratamento de dados sensíveis no projeto Leitura ATS.

---

## ⚠️ Dados Sensíveis

**Currículos contêm informações pessoais sensíveis:**
- Nome completo
- E-mail e telefone
- Endereço
- CPF (em alguns casos)
- Histórico profissional
- Formação acadêmica

---

## Política de Tratamento de Dados

### 1. Uploads

| Aspecto | Comportamento |
|---------|---------------|
| Persistência | **Não persiste** - arquivo processado em memória |
| Armazenamento | Arquivo **não é salvo** no servidor |
| Transmissão | HTTP local (HTTPS em produção) |

### 2. Logs de Análise

**Atenção:** O sistema gera logs detalhados em `aplicacao/logs/`.

Esses logs **podem conter**:
- Texto extraído do currículo
- Dados estruturados (nome, experiências, etc.)
- Keywords identificadas

**Recomendações:**
- ❌ Não usar currículos reais em ambiente público
- ❌ Não commitar pasta `logs/` no Git (já ignorada)
- ✅ Usar currículos fictícios para demonstração
- ✅ Limpar logs regularmente

### 3. Git e Repositório

O `.gitignore` já ignora:
```
logs/
*.pdf
aplicacao/uploads/
.env
```

**Nunca commitar:**
- Currículos reais
- Logs com dados extraídos
- Variáveis de ambiente com secrets

---

## Boas Práticas

### Para Demonstração

Use o currículo de exemplo fictício incluído:
```
exemplos/curriculo_exemplo.pdf
```

Este arquivo contém dados **inventados** e pode ser usado livremente.

### Para Desenvolvimento

1. Criar currículos de teste com dados fictícios
2. Usar nomes como "João da Silva Teste"
3. Não usar dados reais próprios ou de terceiros

### Para Produção (Futuro)

Quando o projeto for para produção:

1. **HTTPS obrigatório** - nunca HTTP em produção
2. **Logs sem PII** - remover dados pessoais dos logs
3. **Retention policy** - logs por tempo limitado
4. **Criptografia** - dados em repouso criptografados
5. **LGPD compliance** - termo de consentimento

---

## Limpeza de Dados

### Limpar Logs Manualmente

```bash
rm -rf aplicacao/logs/*
```

### Script de Limpeza

```bash
./scripts/cleanup.sh
```

### Limpeza Automática (Cron)

```bash
# Remover logs com mais de 7 dias
0 0 * * * find /path/to/aplicacao/logs -name "*.txt" -mtime +7 -delete
```

---

## Configurações de Segurança

### SECRET_KEY

**Nunca use a chave padrão em produção!**

```bash
# Gerar chave segura
python -c "import secrets; print(secrets.token_hex(32))"

# Usar via variável de ambiente
export SECRET_KEY="sua-chave-segura-aqui"
```

### Limite de Upload

Configurado em `app.py`:
```python
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB
```

### Debug Mode

**Sempre desabilitar em produção:**
```python
# Desenvolvimento
app.run(debug=True)

# Produção (via Gunicorn)
# debug é automaticamente False
```

---

## Modelo de Ameaças Simplificado

| Ameaça | Mitigação |
|--------|-----------|
| Upload malicioso | Validação de tipo, limite de tamanho |
| Injeção de código | PDF é apenas lido, não executado |
| Vazamento de dados | Logs ignorados no Git, limpeza periódica |
| Acesso não autorizado | Não há autenticação (local only) |
| MITM | HTTPS em produção |

---

## Responsabilidades

### Desenvolvedor
- Não commitar dados sensíveis
- Usar dados fictícios para testes
- Manter `.gitignore` atualizado

### Operador (Produção Futura)
- Configurar HTTPS
- Implementar logs sem PII
- Definir retention policy
- Compliance LGPD

### Usuário
- Não enviar currículos reais em ambiente de demonstração
- Entender que dados são processados localmente
- Usar currículo de exemplo para testar

---

## Checklist de Segurança

Antes de publicar ou compartilhar:

- [ ] Pasta `logs/` está vazia ou ignorada
- [ ] Nenhum PDF real no repositório
- [ ] `.env` não está commitado
- [ ] SECRET_KEY não é a padrão
- [ ] Currículo de exemplo usa dados fictícios

---

## Contato

Para reportar vulnerabilidades ou preocupações de segurança:
- Abrir issue privada no GitHub
- Ou contato direto com o mantenedor

---

**Nota:** Este é um projeto de portfólio/demonstração. Em ambiente de produção real, implementar compliance LGPD completo, auditorias de segurança, e políticas de privacidade formais.

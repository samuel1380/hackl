# 🔒 Sistema de Monitoramento Remoto

Sistema de monitoramento remoto com transmissão de câmera e tela em tempo real via WebRTC e SocketIO.

## 📋 Funcionalidades

- ✅ Geração de links temporários de acesso
- ✅ Controle de usos máximos por link
- ✅ Notas e metadados nos links
- 📹 Transmissão de câmera em tempo real (Web e App Nativo)
- 🖥️ Transmissão de tela em tempo real (App Nativo)
- 📊 Dashboard com histórico de acessos
- 🔌 **API RESTful v1** completa
- 🔐 Rate limiting para proteção contra abuso
- 📝 Sistema de logging estruturado
- ⚙️ Configuração via variáveis de ambiente
- 🔄 Heartbeat e limpeza automática de conexões
- 📈 Estatísticas em tempo real

## 🚀 Instalação

### 1. Clonar o repositório
```bash
git clone <seu-repositorio>
cd app
```

### 2. Instalar dependências
```bash
pip install -r requirements.txt
```

### 3. Configurar variáveis de ambiente
Copie o arquivo `.env.example` para `.env` e ajuste os valores:

```bash
cp .env.example .env
```

**⚠️ IMPORTANTE**: Altere a `SECRET_KEY` no arquivo `.env` para uma chave aleatória segura!

```bash
# Gerar uma SECRET_KEY segura (Python)
python -c "import secrets; print(secrets.token_hex(32))"
```

### 4. Iniciar o servidor
```bash
python app.py
```

O servidor estará disponível em `http://localhost:5000`

## 📁 Estrutura do Projeto

```
app/
├── app.py                      # Servidor Flask principal
├── models.py                   # Modelos do banco de dados
├── config.py                   # Configurações centralizadas
├── requirements.txt            # Dependências Python
├── .env                        # Variáveis de ambiente (NÃO COMMITAR)
├── .env.example                # Exemplo de variáveis de ambiente
├── .gitignore                  # Arquivos ignorados pelo Git
│
├── templates/
│   ├── dashboard.html          # Painel administrativo
│   └── client.html             # Interface do cliente (web)
│
├── static/
│   ├── manifest.json           # Manifesto PWA
│   └── sw.js                   # Service Worker
│
└── cliente_app/
    └── monitor_cliente.py      # Cliente nativo (executável)
```

## ⚙️ Configuração

### Variáveis de Ambiente (.env)

| Variável | Descrição | Padrão |
|----------|-----------|--------|
| `SECRET_KEY` | Chave secreta do Flask | ⚠️ Alterar obrigatoriamente |
| `FLASK_ENV` | Ambiente (development/production) | `production` |
| `DATABASE_URL` | URL do banco de dados | `sqlite:///dashboard.db` |
| `SERVER_URL` | URL pública do servidor | `https://hackl.onrender.com` |
| `PORT` | Porta do servidor | `5000` |
| `MAX_LINK_EXPIRY_MINUTES` | Expiração máxima de links | `1440` (24h) |
| `RATE_LIMIT_LINKS` | Limite de criação de links | `5 per minute` |
| `RATE_LIMIT_ACCESS` | Limite de registros de acesso | `10 per minute` |
| `CAMERA_FPS` | FPS da câmera | `6` |
| `SCREEN_FPS` | FPS da tela | `2` |
| `JPEG_QUALITY_CAMERA` | Qualidade JPEG câmera (1-100) | `25` |
| `JPEG_QUALITY_SCREEN` | Qualidade JPEG tela (1-100) | `20` |

## 🔐 Segurança

### Implementações de Segurança

1. **✅ Variáveis de Ambiente**: Dados sensíveis não ficam no código
2. **✅ Rate Limiting**: Proteção contra spam e DDoS
3. **✅ Validação de Input**: Todos os inputs são validados
4. **✅ Logging Estruturado**: Rastreamento de todas as ações
5. **✅ Tratamento de Erros**: Erros específicos sem expor informações sensíveis

### Recomendações Adicionais

- 🔒 Use HTTPS em produção
- 🔑 Altere a `SECRET_KEY` regularmente
- 📊 Monitore os logs em `app.log`
- 🚫 Nunca commite o arquivo `.env`
- 🔐 Configure firewall para limitar acesso ao servidor

## 📊 Uso

### Dashboard (Admin)

1. Acesse `http://seu-servidor:5000/`
2. Gere um novo link com tempo de expiração
3. Compartilhe o link com o cliente
4. Monitore as transmissões em tempo real

### Cliente Web

1. Acesse o link fornecido
2. Autorize o acesso à câmera
3. A transmissão iniciará automaticamente

### Cliente Nativo (Executável)

1. Configure o `.env` com a URL do servidor
2. Execute `monitor_cliente.py` ou o `.exe` compilado
3. Transmissão de câmera e tela iniciará automaticamente

### API RESTful v1

A API permite integração com outros sistemas. Veja o [Guia Completo da API](API_GUIDE.md).

**Endpoints principais**:
- `GET /api/v1/links` - Listar links
- `GET /api/v1/links/<code>` - Detalhes de um link
- `DELETE /api/v1/links/<code>` - Desativar link
- `PATCH /api/v1/links/<code>` - Atualizar link
- `GET /api/v1/logs` - Listar logs
- `GET /api/v1/stats` - Estatísticas

**Exemplo**:
```bash
# Obter estatísticas
curl http://localhost:5000/api/v1/stats

# Desativar link
curl -X DELETE http://localhost:5000/api/v1/links/abc123
```

## 🔧 Cliente Nativo - Build

Para compilar o cliente nativo em executável:

```bash
cd cliente_app
python build_exe.py
```

O executável estará em `cliente_app/dist/MonitoramentoSeguro.exe`

## 📝 Logs

### Servidor
Logs são salvos em `app.log` com o formato:
```
2026-01-08 19:50:00 - __main__ - INFO - ✅ Link criado: abc123 (expira em 60min)
```

### Cliente Nativo
Logs são salvos em `monitor_cliente.log`

## 🐛 Troubleshooting

### Erro: "SECRET_KEY padrão detectada"
**Solução**: Altere a `SECRET_KEY` no arquivo `.env`

### Erro: "Rate limit exceeded"
**Solução**: Aguarde alguns minutos ou ajuste os limites no `.env`

### Câmera não funciona no cliente nativo
**Solução**: Verifique se a câmera não está em uso por outro aplicativo

### Erro de conexão SocketIO
**Solução**: Verifique se o `SERVER_URL` está correto no `.env`

## 📦 Deploy

### Render.com

1. Crie um novo Web Service
2. Conecte seu repositório GitHub
3. Configure as variáveis de ambiente no painel do Render
4. Deploy automático será feito a cada push

### Heroku

```bash
heroku create seu-app
heroku config:set SECRET_KEY=sua_chave_aqui
git push heroku main
```

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📄 Licença

Este projeto é privado e confidencial.

## ⚠️ Avisos Legais

Este sistema deve ser usado apenas com consentimento explícito dos usuários monitorados. O uso indevido pode violar leis de privacidade e vigilância.

---

**Desenvolvido com ❤️ para monitoramento seguro e transparente**

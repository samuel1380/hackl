# 🔌 Guia de Uso da API v1

## Base URL
```
http://localhost:5000/api/v1
```

## Autenticação
Atualmente a API não requer autenticação (você optou por não ter senha).

---

## 📋 Endpoints

### 1. Listar Links

**GET** `/api/v1/links`

**Query Parameters**:
- `page` (int, default: 1) - Número da página
- `per_page` (int, default: 20) - Itens por página
- `active` (boolean) - Filtrar apenas links ativos

**Exemplo**:
```bash
curl "http://localhost:5000/api/v1/links?page=1&per_page=10&active=true"
```

**Resposta**:
```json
{
  "links": [
    {
      "id": 1,
      "code": "abc123...",
      "expires_at": "2026-01-09T20:00:00",
      "created_at": "2026-01-08T19:00:00",
      "is_active": true,
      "is_expired": false,
      "max_uses": 5,
      "current_uses": 2,
      "remaining_uses": 3,
      "notes": "Cliente VIP",
      "created_by": "admin",
      "last_accessed": "2026-01-08T19:30:00",
      "total_logs": 2
    }
  ],
  "total": 15,
  "page": 1,
  "per_page": 10,
  "pages": 2
}
```

---

### 2. Obter Link Específico

**GET** `/api/v1/links/<code>`

**Exemplo**:
```bash
curl "http://localhost:5000/api/v1/links/abc123..."
```

**Resposta**:
```json
{
  "id": 1,
  "code": "abc123...",
  "expires_at": "2026-01-09T20:00:00",
  "is_active": true,
  "max_uses": 5,
  "current_uses": 2,
  "remaining_uses": 3,
  "notes": "Cliente VIP"
}
```

---

### 3. Desativar Link

**DELETE** `/api/v1/links/<code>`

**Exemplo**:
```bash
curl -X DELETE "http://localhost:5000/api/v1/links/abc123..."
```

**Resposta**:
```json
{
  "message": "Link desativado com sucesso"
}
```

---

### 4. Atualizar Link

**PATCH** `/api/v1/links/<code>`

**Body** (JSON):
```json
{
  "notes": "Cliente Premium - Renovado",
  "max_uses": 10,
  "is_active": true
}
```

**Exemplo**:
```bash
curl -X PATCH "http://localhost:5000/api/v1/links/abc123..." \
  -H "Content-Type: application/json" \
  -d '{"notes": "Cliente Premium", "max_uses": 10}'
```

**Resposta**:
```json
{
  "id": 1,
  "code": "abc123...",
  "notes": "Cliente Premium",
  "max_uses": 10,
  "current_uses": 2
}
```

---

### 5. Listar Logs

**GET** `/api/v1/logs`

**Query Parameters**:
- `page` (int) - Número da página
- `per_page` (int) - Itens por página
- `link_code` (string) - Filtrar por código do link
- `ip` (string) - Filtrar por IP

**Exemplo**:
```bash
curl "http://localhost:5000/api/v1/logs?link_code=abc123&page=1"
```

**Resposta**:
```json
{
  "logs": [
    {
      "id": 1,
      "link_code": "abc123...",
      "ip_address": "192.168.1.1",
      "browser": "Chrome",
      "os": "Windows",
      "email": "user@example.com",
      "timestamp": "2026-01-08T19:30:00",
      "user_agent": "Mozilla/5.0...",
      "country": "Brazil",
      "city": "São Paulo",
      "session_duration": 120
    }
  ],
  "total": 48,
  "page": 1,
  "per_page": 50,
  "pages": 1
}
```

---

### 6. Estatísticas

**GET** `/api/v1/stats`

**Exemplo**:
```bash
curl "http://localhost:5000/api/v1/stats"
```

**Resposta**:
```json
{
  "total_links": 15,
  "active_links": 12,
  "total_logs": 48,
  "links_created_today": 3,
  "accesses_today": 12
}
```

---

### 7. Health Check

**GET** `/api/v1/health`

**Exemplo**:
```bash
curl "http://localhost:5000/api/v1/health"
```

**Resposta**:
```json
{
  "status": "healthy",
  "timestamp": "2026-01-08T20:00:00",
  "version": "1.0.0"
}
```

---

## 🐍 Exemplos em Python

### Listar Links
```python
import requests

response = requests.get('http://localhost:5000/api/v1/links')
data = response.json()

for link in data['links']:
    print(f"Link: {link['code']}")
    print(f"Usos: {link['current_uses']}/{link['max_uses']}")
    print(f"Notas: {link['notes']}")
    print("---")
```

### Desativar Link
```python
import requests

code = "abc123..."
response = requests.delete(f'http://localhost:5000/api/v1/links/{code}')

if response.status_code == 200:
    print("Link desativado!")
else:
    print(f"Erro: {response.json()}")
```

### Atualizar Notas
```python
import requests

code = "abc123..."
data = {"notes": "Cliente Premium - Renovado"}

response = requests.patch(
    f'http://localhost:5000/api/v1/links/{code}',
    json=data
)

print(response.json())
```

### Obter Estatísticas
```python
import requests

response = requests.get('http://localhost:5000/api/v1/stats')
stats = response.json()

print(f"Total de links: {stats['total_links']}")
print(f"Links ativos: {stats['active_links']}")
print(f"Acessos hoje: {stats['accesses_today']}")
```

---

## 📱 Exemplos em JavaScript

### Fetch API
```javascript
// Listar links
fetch('http://localhost:5000/api/v1/links')
  .then(res => res.json())
  .then(data => {
    console.log('Total de links:', data.total);
    data.links.forEach(link => {
      console.log(`${link.code}: ${link.notes}`);
    });
  });

// Desativar link
fetch('http://localhost:5000/api/v1/links/abc123', {
  method: 'DELETE'
})
  .then(res => res.json())
  .then(data => console.log(data.message));

// Atualizar link
fetch('http://localhost:5000/api/v1/links/abc123', {
  method: 'PATCH',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    notes: 'Cliente Premium',
    max_uses: 10
  })
})
  .then(res => res.json())
  .then(data => console.log('Atualizado:', data));
```

---

## 🔒 Códigos de Status HTTP

| Código | Significado |
|--------|-------------|
| 200 | Sucesso |
| 400 | Requisição inválida |
| 404 | Recurso não encontrado |
| 500 | Erro interno do servidor |

---

## 📊 Paginação

Todas as listagens suportam paginação:

```bash
# Página 1, 20 itens
/api/v1/links?page=1&per_page=20

# Página 2, 50 itens
/api/v1/logs?page=2&per_page=50
```

Resposta inclui:
- `total` - Total de itens
- `page` - Página atual
- `per_page` - Itens por página
- `pages` - Total de páginas

---

## 🎯 Casos de Uso

### Dashboard Customizado
Crie seu próprio dashboard consumindo a API:
```javascript
// Atualizar estatísticas a cada 10s
setInterval(async () => {
  const stats = await fetch('/api/v1/stats').then(r => r.json());
  document.getElementById('total-links').textContent = stats.total_links;
  document.getElementById('accesses-today').textContent = stats.accesses_today;
}, 10000);
```

### Integração com CRM
```python
# Criar link para cliente e salvar no CRM
import requests

# Criar link via dashboard (POST /generate_link)
# Depois obter detalhes via API
link_code = "abc123..."
link_data = requests.get(f'/api/v1/links/{link_code}').json()

# Salvar no CRM
crm.create_customer_link(
    customer_id=123,
    link_url=f"https://seu-dominio.com/v/{link_code}",
    expires_at=link_data['expires_at'],
    max_uses=link_data['max_uses']
)
```

### Monitoramento
```python
# Script de monitoramento
import requests
import time

while True:
    health = requests.get('/api/v1/health').json()
    if health['status'] != 'healthy':
        send_alert("Sistema fora do ar!")
    
    time.sleep(60)  # Verificar a cada minuto
```

---

## 🚀 Próximas Versões

Planejado para v2:
- Autenticação com API Keys
- Rate limiting por API key
- Webhooks para eventos
- Filtros avançados
- Exportação CSV/JSON
- GraphQL endpoint

---

**Versão**: 1.0.0  
**Última atualização**: 2026-01-08

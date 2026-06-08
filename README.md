# 🌱 EcoTech — Data Capture

> API para captação e visualização de dados de **umidade do solo** em tempo real.

---

## 📋 Sobre o Projeto

O **data-capture** é o backend do **Projeto EcoTech**, uma solução de monitoramento ambiental que expõe uma API REST em Flask para receber, armazenar e consultar leituras de umidade do solo enviadas por sensores (ou simuladas via script). Os dados ficam persistidos em CSV e podem ser visualizados através de um dashboard HTML embutido no próprio repositório.

---

## 🗂️ Estrutura do Repositório

```
data-capture/
├── main.py            # API Flask — endpoints REST
├── popular_dados.py   # Script para simular envio de leituras
├── index.html         # Dashboard web (gráfico + exportação)
├── umidade.csv        # Arquivo de persistência dos dados
└── LICENSE
```

---

## ⚙️ Tecnologias

- **Python 3** + **Flask** + **Flask-CORS**
- **CSV** para persistência leve dos dados
- **HTML / JavaScript** no dashboard (sem framework externo)
- **jsPDF + autoTable** para exportação em PDF direto no navegador

---

## 🚀 Como Executar

### 1. Clone o repositório

```bash
git clone https://github.com/paivagpg77/data-capture.git
cd data-capture
```

### 2. Instale as dependências

```bash
pip install flask flask-cors
```

### 3. Inicie a API

```bash
python main.py
```

A API ficará disponível em `http://0.0.0.0:5000`.

---

## 📡 Endpoints da API

| Método | Rota        | Descrição                                   |
|--------|-------------|---------------------------------------------|
| `GET`  | `/receber`  | Recebe uma leitura de umidade via query param |
| `GET`  | `/dados`    | Retorna todas as leituras armazenadas (JSON) |
| `GET`  | `/ultima`   | Retorna a leitura mais recente (JSON)        |

### Exemplo de envio de leitura

```
GET /receber?umidade=65
```

**Resposta:** `Dados salvos com sucesso` (HTTP 200)

### Exemplo de retorno de `/ultima`

```json
{
  "data_hora": "2025-06-01 14:32:10",
  "umidade": "65"
}
```

---

## 🧪 Simulando Dados com `popular_dados.py`

Para testar a API sem um sensor físico, utilize o script de população:

```bash
python popular_dados.py
```

O script envia **20 leituras aleatórias** (entre 30% e 90%) para a API com intervalo de 2 segundos entre cada envio. Antes de rodar, certifique-se de que o endereço `API_URL` no arquivo aponta para o IP correto da sua máquina.

```python
# popular_dados.py — ajuste conforme necessário
API_URL = "http://192.168.0.110:5000"
```

---

## 🖥️ Dashboard Web

Abra o arquivo `index.html` no navegador para visualizar o dashboard. Ele se conecta automaticamente à API e atualiza os dados a cada **5 segundos**.

**Funcionalidades do dashboard:**
- Leitura atual de umidade em destaque
- Histórico das últimas 10 leituras em tabela
- Campo para configurar o endereço da API dinamicamente
- Exportação dos dados em **PDF** (gerado no próprio navegador via jsPDF)
- Download direto em **CSV** (com suporte a acentos no Excel/Google Sheets)
- Integração com **Google Sheets** via Service Account

> **Atenção:** o campo de endereço da API no dashboard vem preenchido com `http://192.168.0.110:5000` por padrão. Altere para o IP da sua máquina na rede local antes de usar.

---

## 📤 Exportação para Google Sheets

Para enviar os dados diretamente para uma planilha do Google:

1. Acesse o [Google Cloud Console](https://console.cloud.google.com) e crie um projeto
2. Ative a **Google Sheets API**
3. Crie uma **Service Account** e baixe o JSON de credenciais
4. Compartilhe sua planilha com o e-mail da Service Account
5. No dashboard, clique em **🔗 Google Sheets**, cole o ID da planilha e o JSON de credenciais

---

## 📄 Licença

Distribuído sob a licença **MIT**. Veja o arquivo [LICENSE](./LICENSE) para mais detalhes.

---

> Projeto desenvolvido como parte do **Projeto EcoTech** 🌍

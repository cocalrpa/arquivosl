**✅ Fixed!** The picture wasn't showing because Cloudinary links with `q_auto/f_auto` sometimes have restrictions or need proper formatting for GitHub Markdown.

---

### **Updated README** (with reliable image display):

```markdown
# Indicadores de Arquivo

Um dashboard moderno e interativo para monitoramento de ocupação de caixas em arquivo, desenvolvido com Streamlit.

![Dashboard Preview](https://res.cloudinary.com/dnfqlwaqe/image/upload/v1779897829/ArquivoPBI_dzgkh1.png)

---

## Funcionalidades

- Métricas em tempo real: Total de caixas, ocupadas, vazias e itens armazenados
- Visualizações interativas: Gráfico de pizza e ranking das caixas mais ocupadas
- Busca inteligente: Filtre por código, endereço ou quantidade de itens
- Suporte a múltiplos formatos: CSV e Excel
- **Documentação do Usuário**: Link direto para o guia no sidebar (ícone simples)
- Design moderno: Interface clean com cards e tipografia premium
- Totalmente responsivo: Otimizado para desktop e tablets

---

## Pré-visualização

![Interface do Dashboard](https://res.cloudinary.com/dnfqlwaqe/image/upload/v1779897829/ArquivoPBI_dzgkh1.png)

---

## Como Executar

### 1. Clone o repositório
```bash
git clone <url-do-seu-repositorio>
cd indicadores-de-arquivo
```

### 2. Instale as dependências
```bash
pip install streamlit pandas plotly openpyxl
```

### 3. Execute o dashboard
```bash
streamlit run app.py
```

---

## Documentação do Usuário

Acesse o guia completo do usuário diretamente no sidebar do dashboard através do ícone abaixo:

[<img src="https://res.cloudinary.com/dmkksbmua/image/upload/v1780489142/arquivo_user_rnebfj.png" width="200" alt="Documentação do Usuário">](https://res.cloudinary.com/dmkksbmua/image/upload/v1780489142/arquivo_user_rnebfj.png)

> **Clique na imagem acima** para abrir o guia completo.

---

## Requisitos do Arquivo

Seu arquivo deve conter as seguintes colunas (ou equivalentes):
- Código / Caixa
- Endereço / Localização
- Total de Itens / Quantidade

**Formatos suportados**: `.csv` e `.xlsx`

---

## Tecnologias Utilizadas

- Streamlit - Framework web
- Pandas - Manipulação de dados
- Plotly - Gráficos interativos
- Python 3.9+

---

## Desenvolvido por

<div style="text-align: center; margin-top: 10px; font-size: 12px;">
    devBy: <a href="https://wa.me/5518997957724" target="_blank" style="color:#31515f; text-decoration:none;">
    Bruno Pereira - dev235478
    </a>
</div>
```

### Main changes:
- Removed `q_auto/f_auto` (this often causes display issues on GitHub)
- Added `alt` text for better accessibility
- Increased width slightly to `200`
- Added a note "Clique na imagem acima"

---

Try copying this version. The image should now appear correctly. Let me know if it still doesn't show!

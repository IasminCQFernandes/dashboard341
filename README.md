# Dashboard de Fracionamento — LCM

Monitoramento de processos individuais abaixo do teto que, somados por fornecedor
no período, ultrapassam o limite financeiro.

## Estrutura

```
app.py                        # interface e visualizações
query.py                      # consulta SQL (parametrizada)
requirements.txt
.streamlit/config.toml        # tema (verde/claro)
.streamlit/secrets.toml       # credenciais do banco (criar a partir do .example)
```

## Como rodar

```bash
pip install -r requirements.txt
cp .streamlit/secrets.toml.example .streamlit/secrets.toml   # preencha a senha
streamlit run app.py
```

Modo demonstração (dados sintéticos, sem banco e sem driver ODBC):

```bash
DASH_DEMO=1 streamlit run app.py
```

## O que mudou em relação à versão anterior

**Design**

- Tema claro premium (cartões brancos arredondados, sombra suave, verde de destaque),
  no lugar do `plotly_dark`.
- Cartão-destaque em gradiente verde com o volume financeiro exposto + 3 KPIs de apoio.
- Tipografia Inter, espaçamentos e hierarquia consistentes; gráficos sem grade pesada,
  eixos discretos e rótulos em R$ compacto.
- Sidebar como painel de controle: atalhos de período (7d/30d/90d/12m), limites
  configuráveis, busca, ordenação e Top N.

**Interatividade**

- **Clique no fornecedor abre o detalhamento**: tanto na linha do ranking
  (`st.dataframe` com `on_select`) quanto na barra do gráfico
  (`st.plotly_chart` com `on_select`). A barra selecionada fica destacada e as demais esmaecidas.
- Painel do fornecedor: KPIs próprios (acumulado, excedente ao teto, ticket médio,
  janela de vencimentos), curva **acumulada x linha do teto** (mostra em que momento
  o fornecedor estoura o limite), distribuição por obra e lista de processos —
  cada processo em um expander com suas parcelas.
- Exportação do detalhamento em CSV (`;` e vírgula decimal, pronto para Excel PT-BR).
- Botão "Limpar seleção" e estado vazio orientando o clique.

**Correções e robustez**

- Credenciais saíram do código-fonte: agora vêm de `st.secrets` (ou variáveis de
  ambiente `DB_SERVER`, `DB_NAME`, `DB_USER`, `DB_PASS`).
- KPIs passaram a usar `ValPagar` (valor + acréscimo − desconto), coerente com a
  regra de agrupamento da própria consulta, em vez de `ValorParc_Proc`.
- Contagem de processos usa `nunique` de `Num_Proc` (antes contava parcelas como
  se fossem processos).
- Os tetos de R$ 100.000 viraram parâmetros da query (`?`) controlados pela sidebar.
- Conexão fechada via context manager; `NotImplementedError` órfão removido;
  validação de intervalo de datas; formatação monetária em padrão brasileiro.

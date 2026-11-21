# Roteiro — reconciliar a amostra dos específicos do cargo 523 (137 contra 187) (ato do proprietário e da Zapia)

**Natureza:** passo a passo para **você** pedir à Zapia e **comparar**; **a sessão não consulta o TEC, não recebe números e não decide a reconciliação**. Origem: S16 (regra P7) e `docs/canonicos/plataformas/AUDITORIA_TECCONCURSOS_UFMS_523_324_20261116_EDITADA.md`. **Estado:** os específicos do 523 estão **não definitivos**; enquanto isso `top10_materia.py` recusa a lista com `PENDENCIA_ABERTA` para essas matérias. **Nada aqui versiona número de amostra** (S16, P6): a Zapia traz a amostra a cada plano.

## O que se sabe e o que não se sabe

- **Sabido (relato da Zapia, não verificado aqui):** o caderno 523 salvo tinha **137 questões**; a consulta atual da mesma seleção devolveu **187**. A divergência **não foi reconciliada**.
- **Não sabido:** **por quê** (a causa não foi observada). Hipóteses possíveis, **sem nenhuma confirmada**: filtros diferentes entre o caderno salvo e a consulta; o acervo do TEC mudou entre as datas; o caderno salvo não foi atualizado (o controle de atualizar questões foi **observado e não acionado**); questões anuladas ou em branco contadas de modo diferente. **Não escolha uma delas por estimativa.**

## Passo a passo

1. **Escolher uma única consulta de referência:** cargo 523, **filtro exclusivo da FAPEC** (modalidade 1), **mesmos filtros** do pedido original (matéria, banca, ano, cargo, órgão, dificuldade, tipo, situação), anotados por escrito antes de começar.
2. **Pedir à Zapia** (ela está liberada para o TEC, somente leitura, sem alterar cadernos; D-27). Texto sugerido, para você encaminhar:
   > Consulta de reconciliação, só leitura. No TEC, na sua sessão, reproduza **uma vez** a consulta do cargo 523 com filtro exclusivo FAPEC e **estes filtros**: <liste>. Informe, **sem alterar nenhum caderno**: (a) data e hora da consulta; (b) os filtros **realmente aplicados**, como a tela os mostra; (c) o **total de questões** que o TEC mostra; (d) o total de **cada matéria** do TEC; (e) se o caderno 523 **salvo** foi aberto, quantas questões ele mostra **agora** e a data dele; (f) o que o TEC exibiu de aviso. **Não interprete, não estime e não complete o que faltar:** diga "não vi". Entregue só números e rótulos, **sem texto de questão**, sem arquivo bruto e sem credencial.
3. **Repetir a consulta uma segunda vez**, em **outro dia**, com os **mesmos filtros**. Duas consultas iguais em dias diferentes mostram se o número é estável; uma só não mostra.
4. **Comparar você mesmo**, lado a lado, **só os números que a Zapia relatou**: 137 (salvo), 187 (atual) e as duas consultas novas. Anote, para cada total, a **data** e os **filtros**.
5. **Decidir** (decisão **sua**, não da sessão):
   - **Os totais das duas consultas coincidem e a causa é explicada** (por exemplo, o caderno salvo estava desatualizado): você declara o conjunto **definitivo** daquela consulta e diz qual total vale.
   - **Os totais coincidem e a causa não é explicada:** você pode declarar definitivo **a consulta atual**, registrando que a causa da diferença para o caderno salvo **segue desconhecida**.
   - **Os totais não coincidem entre as consultas novas:** o conjunto **continua não definitivo**; **não** use média nem escolha o maior.
6. **Relatar à sessão, só com números e rótulos:** a sessão então registra a decisão no estado (sem versionar os números das amostras) e a Zapia traz a amostra definitiva **a cada plano**, como já está decidido.

**O que NÃO fazer:** escolher 137 ou 187 por conveniência; somar as duas; ajustar percentual para fechar; tratar o relato da Zapia como prova independente; mandar print ou arquivo bruto ao repositório.

## Frases literais

- Pedido à Zapia: o texto do passo 2, com os filtros preenchidos.
- Decisão à sessão: `523: declaro definitivo o conjunto da consulta de <data> (filtros: <resumo>); causa da diferença: <explicada: ... | desconhecida>.` ou `523: segue não definitivo.`

## O que isto destrava e o que não destrava

Se você declarar definitivo, a próxima consulta pode gerar o top 10 dos específicos do 523 (T2) com lista final. **Não** altera o 324 (amostra pequena, marcada **instável**: P7), **não** prova que os números são os do TEC e **não** muda cargos, edital nem plano. O estado do conjunto fica **não definitivo** até a sua declaração.

## Limites

Os números vêm do **autorrelato da Zapia** (confiança C). A reconciliação é **julgamento seu** sobre relatos, não auditoria do TEC. As retificações do edital continuam **não conferidas** (`retificacoes_verificadas=false`).

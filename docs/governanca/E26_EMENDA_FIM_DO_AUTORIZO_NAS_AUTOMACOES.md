# E26: emenda, fim do `AUTORIZO` por mensagem nas automações entre agentes, Zapia, TEC e Gemini (23/11/2026)

**Natureza:** emenda **aditiva**, no padrão da E2: o texto antigo das especificações **permanece** e a seção "Emenda do AUTORIZO (E26)" no **fim** de cada uma **vale onde divergir**. **Decisão do proprietário (23/11/2026):** "o fluxo de automação entre os agentes com a Zapia, o TEC e o Gemini [deve ser] livre de interferência humana ou pedido de aprovação". **Entra em vigor com o merge deste PR**, que ele faz com o pedido expresso citando PR e head: esse merge é a **autorização permanente** descrita abaixo. Não altera `AGENTS.md` (a seção "ROTINA_AUTORIZADA" já fala de rotinas "previamente autorizadas, sem confirmação por mensagem": esta emenda é essa autorização prévia), `agents/` nem o esquema de comandos; a operação `agendar_rotina` continua só **proposta** (E24).

## O que muda

Deixa de ser exigida a frase `AUTORIZO` (do proprietário ou do estudante) para: criar, alterar ou ligar **rotina, lembrete ou hook** na Zapia; os **comandos de Tutor e Coach** à Zapia (inclusive TEC e Gemini Notebook por ela); e o envio de prompts ao Notebook (S10). Passa a valer a **autorização permanente**: a aprovação deste texto, registrada no repositório, com **escopo fechado** nos tipos de rotina e operações que as especificações e a E24 listam.

## O que substitui a frase (travas que NÃO dependem de pessoa)

1. **Caixa de comandos** valida forma, origem, janela, idempotência e filtros de conteúdo (sem URL, instrução embutida, texto de questão, dado pessoal, credencial).
2. **Tetos:** rotina diária do Coach com no máximo 1 mensagem e 1 segundo lembrete por dia; 2 notificações por dia (regra do F1); jobs de 900 s e 32 por dia (S8-R5); 1 pedido de agendamento por dia por origem.
3. **Recibo de mesmo hash** para todo comando; o recibo de volta da Zapia é obrigatório e conferido por código (`zapia_entrega.py`, `zapia_disparo.py`). Sem recibo, o verificador marca **não provado** e a emissão seguinte do mesmo modelo é bloqueada.
4. **Teste sem efeito antes (S8-R8, S15-R4) continua, agora automático:** a primeira execução de cada modelo roda só com carimbo, sem notificação ao estudante, **sem frase**.
5. **Parada:** o proprietário pausa ou apaga a rotina na Zapia quando quiser (efeito imediato, sem código); uma **chave de parada versionada** entra no lote de aplicação (arquivo de contrato, outro PR).
6. **Origem não provada na nuvem (S4-R2):** continua não atendida; o recibo e a parada são a defesa.

## O que NÃO muda (não é aprovação de automação)

- **Leitura de e-mail** (`E-07`, D-28): segue exigindo `AUTORIZO` própria, com finalidade e consulta mínima.
- **Dado pessoal e credencial:** nenhuma credencial vai ao modelo; resultado pessoal só pela fila e pelo portão; **flags** `personal_results_writes_enabled` e do fluxo, **consentimento v4** e **janela PJ** não mudam.
- **Merge e contratos:** merge só por pedido expresso dele citando PR e head; `agents/`, esquema, `AGENTS.md` e `PRODUCT.md` só mudam com aprovação expressa.
- **Atos dele na conta** (renovar tokens, criar a janela PJ, apagar branch): não são automação entre agentes.

## Limites que o repositório não controla (declarados)

- **A Zapia, o TEC e o Gemini têm regras próprias.** Se a Zapia ou o app pedirem confirmação, **ou** o TEC exigir login (código de acesso por e-mail, D-28) ou CAPTCHA, ou o Gemini pedir permissão, **isso é da plataforma e não é removido por este texto**. A automação para no primeiro bloqueio e relata o erro literal, sem laço (S20-R9).
- **Risco aceito por ele:** sem confirmação humana por rotina, uma automação errada só aparece na notificação ou no recibo; os tetos limitam o dano.
- A Zapia é um modelo: o que ela fez só se confirma pelo **recibo de volta** e pela captura do app (confiança B quando o código confere).

## Onde está emendado

`PRODUCT.md` (D-31), `docs/especificacoes/S5`, `S6`, `S8`, `S14`, `S15`, `S19` e `S20` (seção "Emenda do AUTORIZO (E26)" no fim e aviso no topo). A E24 e o E25 passam a apontar para este texto. O roteiro de teste da rotina (`ROTEIRO_ZAPIA_ROTINA_TESTE_20261122.md`) deixa de exigir a frase quando esta emenda estiver mesclada.

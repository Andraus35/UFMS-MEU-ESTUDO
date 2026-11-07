# Plano de estudos: Método 4.2 e revisão em 7, 15 e 30 dias (especificação v1.0)

**Natureza:** especificação do plano de estudos que o Tutor entrega ao Coach. É o **padrão do proprietário** (decisão D-11 do `PRODUCT.md`), implementado por `scripts/study_plan.py` e configurado em `settings.json` (`study.owner_default_plan`). O Tutor pode ajustá-lo com justificativa. Este documento não contém estado.

**Por que existe:** o repositório só tinha uma linha sobre o 4.2 como "referência opcional" (`rules/STUDY.md`) e nenhuma especificação de revisão em 7, 15 e 30 dias. Pesquisa e limites: `docs/pedagogia/ESTADO_DA_ARTE_TUTOR_COACH_20261107.md`.

## 1. Origem de cada regra

| Regra | Origem | Confiança |
|---|---|---|
| Ciclo de 7 dias: 4 de teoria, 2 de revisão, 1 de descanso | Método 4.2 de Revisão, Prof. Rafael Barbosa, Estratégia Concursos, 19/02/2018 (texto lido) | Prática de cursinho; sem estudo controlado |
| Teoria: no máximo 2 horas por disciplina; grifos e anotações curtos | Mesmo artigo | Idem |
| Revisão: recuperar as anotações da semana e resolver questões | Mesmo artigo, com a troca de "reler" por "recuperar" (Dunlosky 2013; Roediger e Karpicke 2006) | Proposta nossa, apoiada em evidência |
| Revisões em 7, 15 e 30 dias | Decisão do proprietário, variação do esquema difundido de 24 h, 7 e 30 dias | Origem de cursinho; evidência primária só indireta (Cepeda 2008) |

## 2. As três camadas

**A. Ciclo semanal (4.2).** Ciclos de 7 dias contados do início do plano. Cada ciclo tem **um dia de descanso fixo** (escolhido pelo humano), **4 dias de teoria** e **2 dias de revisão**, nessa ordem entre os dias de estudo.

- Dia de teoria: tópicos novos do edital, **até 120 minutos por disciplina** e **disciplinas distintas no mesmo dia**; o tempo diário define quantas disciplinas cabem (por exemplo, 240 min = 2 disciplinas de 120 min; 60 min = 1 de 60 min).
- Dia de revisão: recuperação das anotações dos tópicos da semana e questões. **Adaptação nossa:** a revisão da semana é **dividida** entre os dois dias (primeira metade dos tópicos num, segunda metade no outro), em vez de repetir tudo nos dois.
- A **meta semanal de questões** (200 a 300 no 4.2) **não é presumida**: só entra se o humano a informar (`weekly_question_target`), e é dividida entre os dois dias de revisão.
- Depois que todos os tópicos tiveram a primeira passagem, os dias de teoria viram **consolidação** (só revisões espaçadas e questões).

**B. Revisão espaçada (7, 15 e 30).** Para cada tópico, a partir do **dia do primeiro estudo**, o plano marca revisões em **D+7, D+15 e D+30**.

- A revisão vai para o **primeiro dia de estudo a partir do alvo** (o descanso empurra para o dia seguinte).
- Atividade: **recuperação ativa com questões**. O tempo **não é fixo**: o Tutor decide.
- Revisão cujo alvo cai na **fase final** ou depois do prazo é **absorvida pela fase final** e aparece em `unscheduled_reviews`.
- Revisão cujo alvo é **anterior ao início do plano** (tópico já estudado) é sinalizada como **vencida**, para o Tutor decidir; o plano não a reagenda sozinho.

**C. Fase final.** Nos últimos `final_phase_days` antes da prova não há teoria: só recuperação ativa e questões, em rodízio pelos tópicos. O padrão é **0 (desabilitada)** até o Tutor propor um valor com o humano. Simulados seguem `docs/pedagogia/PROTOCOLO_SIMULADOS_v1.4.md`.

## 3. Parâmetros

| Parâmetro | De onde vem |
|---|---|
| Ciclo 4/2/1, 120 min por disciplina, intervalos 7, 15 e 30 | Padrão do proprietário, em `settings.json` |
| `start_date` | Humano |
| `exam_date` | `config/concursos.json` (edital) |
| `daily_minutes` | Humano (tempo diário real; nunca presumido) |
| `rest_weekday` | Humano (0 = segunda a 6 = domingo) |
| `topics` | `config/topics.csv` filtrado pelo cargo (523, 324 ou ambos, sem duplicar tópico compartilhado) |
| `priorities` | Tutor, de 1 a 5 (padrão 3); desempata pela ordem do edital |
| `completed` | Humano: tópicos já estudados e a data do primeiro estudo |
| `final_phase_days` | Tutor com o humano (padrão 0) |
| `weekly_question_target` | Humano ou Tutor, depois do diagnóstico (padrão: não definida) |

## 4. Saída

Um JSON com `parameters`, `days` (uma entrada por data, do início à prova, com `kind` = `teoria`, `revisao_semanal`, `consolidacao`, `revisao_final`, `descanso` ou `prova`, e `items`), `unscheduled_reviews`, `topics_not_reached` e `note`. O plano **nunca marca conclusão** nem conclui domínio. O Tutor o registra com o comando `registrar_plano` e o Coach o usa no acompanhamento.

Exemplo, só para conferir o formato (parâmetros fictícios):

```text
python scripts/study_plan.py --start 2026-11-09 --exam 2027-01-17 --daily-minutes 240 --rest-weekday 6 --cargo 523 --final-phase-days 14
```

## 5. Quando o Tutor pode se afastar do padrão

O Tutor pode mudar intervalos, carga, ordem e fase final **com justificativa e evidência registradas**, por exemplo: desempenho por tópico (declarando n e período), tempo realmente disponível, dificuldade do conteúdo, proximidade da prova e tópicos compartilhados entre os cargos. Não pode: remover a revisão sem justificativa, presumir disponibilidade do humano ou tratar o plano como prova de domínio.

## 6. Informações que o humano precisa fornecer

Data de início, tempo diário real, dia de descanso, cargo (523, 324 ou ambos), tópicos já estudados e quando, prioridades que queira indicar e, se desejar, a meta semanal de questões. Sem isso o plano não é gerado.

## 7. Limites

- Nem o Método 4.2 nem a revisão em 7, 15 e 30 dias têm **estudo controlado** que prove sua eficácia (ver a pesquisa).
- O plano é uma **proposta calculada**, não uma previsão de desempenho.
- A emenda de governança que acomoda este padrão (`AGENTS.md`, `rules/STUDY.md`, `rules/CORE.md`) é parte do PR que o criou e depende da aprovação do proprietário.

# Índice de memória — carregamento seletivo

- `ROADMAP.md` (na raiz): **ler sempre depois de AGENTS.md, antes de qualquer atividade operacional**, conferindo prioridades RM e bloqueadores.

- `memory/HANDOFF.md`: último checkpoint, pendências e próxima ação; **ler sempre**.
- `state/CURRENT.json`: estado consolidado e cursor de eventos; **ler sempre**.
- `memory/PROFILE.md`: preferências e restrições duradouras, não pessoais/sensíveis; ler quando necessário.
- `memory/DECISIONS.md`: registro de decisões estruturais e razões; consultar quando surgir mudança de regras ou divergência.
- `state/events/*.jsonl`: histórico append-only; consultar por caderno, assunto ou período quando necessário.
- `state/PROGRESS.csv`: evidências quantitativas derivadas por tópico, sem inferência de domínio; ler para recomendar.
- `config/topics.csv`: mapa dos blocos do edital; ler para montar cadernos.
- `config/concursos.json`: cargos, pesos e cronograma; ler para planejar e comparar.
- `docs/`: explicação metodológica e referências; leitura sob demanda.

Não carregar todo o histórico em cada chamada. **Não condensar/reescrever eventos originais em resumos de memória.**

- `edital/INDEX.md`: consulta sob demanda quando o tema depender do edital; recuperar apenas páginas e chunks necessários.

- `memory/HANDOFF_ARCHIVE_2026-11-05.md`: histórico completo anterior ao handoff curto; leitura apenas quando necessária para auditar decisões.

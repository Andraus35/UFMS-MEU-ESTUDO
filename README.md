# UFMS MEU ESTUDO — harness de aprendizagem por questões

Tutor assistido por IA para os cargos **523 (Analista em Educação / Gestão Pública)** e **324 (Técnico em Educação / Assuntos Estudantis)** do Edital PROGEP/UFMS nº 152/2026. Prova prevista para **17/01/2027**, banca **FAPEC**.

## Objetivo

Persistir o contexto entre sessões, orientar cadernos de questões no TEC Concursos/Qconcursos, receber os resultados que o estudante fornecer e recomendar intervenções pedagógicas **sem rigidez metodológica**.

- **GitHub = fonte de verdade persistente.** A memória de uma conversa não substitui registros confirmados.
- **A IA não consulta as contas TEC/Qconcursos automaticamente.** O estudante cria o caderno e entrega resultados exportados ou resumidos.
- **Não são armazenadas questões ou comentários integrais de plataformas privadas.** Apenas metadados, links, decisões e resultados permitidos.
- **Sem dados pessoais no repositório público.** Antes de registrar desempenho individual, torne o repositório **privado**.
- **Alterações estruturais por PR**, sem merge sem aprovação. Resultados individuais continuam **bloqueados** mesmo em repositório privado. A futura liberação exige autorização explícita, verificação atual da visibilidade e revisão do gate.

## Iniciar uma sessão

1. Ler `AGENTS.md` e os nove arquivos do bootstrap, nesta ordem.
2. Executar `python scripts/bootstrap.py` para verificar a estrutura e obter um sumário compacto.
3. Recuperar apenas documentos e eventos relevantes à solicitação.
4. Recomendar **um próximo caderno principal**, explicar os filtros e aguardar resultados; ou processar resultado recebido.
5. Quando houver mutação autorizada, validar, gravar, verificar e atualizar o handoff.

## Testar

```bash
python scripts/validate.py
python -m unittest discover -s tests -v
python scripts/rebuild.py --check
```

`settings.json` é **configuração própria deste projeto**, não um arquivo reconhecido automaticamente por todas as ferramentas de IA. Os hooks exigem registro explícito no ambiente ou execução via workflow/script.

A CI inclui `scripts/write_policy.py --check` e os contratos verificáveis de bootstrap/hooks. Ver `docs/OPERACAO.md` para START/DELIVERY e para as limitações de execução automática.

Para escritas pela API, a política de pré-validação, a auditoria da CI e os limites de proteção administrativa estão documentados em [`docs/API_WRITE_GOVERNANCE.md`](docs/API_WRITE_GOVERNANCE.md). O adaptador é voluntário: não intercepta chamadas externas, não substitui autenticação/verificação independente e não libera dados pessoais.

## Fonte e limites

**Fonte oficial de partida:** PDF local do Edital PROGEP/UFMS nº 152/2026, integrante do projeto ESTUDO UFMS, com 47 páginas e SHA-256 fixado em `edital/manifest.json`. O responsável pelo projeto confirmou sua autoridade; **não esperar download ou hash de outra cópia na internet para estudar**. A transcrição integral e imutável está em `EDITAL_UFMS_152_2026.md`, com índice e chunks em `edital/`.

**Atualização normativa:** monitorar possíveis retificações da FAPEC/UFMS. Confirmar cada nova publicação e versioná-la separadamente; somente os itens efetivamente retificados prevalecem sobre a edição inicial, com fonte e data identificadas. O cronograma original contém um alerta de divergência na p. 13, que deve permanecer assinalado até esclarecimento oficial, sem impedir o estudo de tópicos não afetados.

Contrato completo em [`docs/FONTES.md`](docs/FONTES.md) e protocolo de retificações em [`docs/RETIFICACOES_E_PROVENIENCIA.md`](docs/RETIFICACOES_E_PROVENIENCIA.md).

## Busca de baixo custo

Exemplos: `python scripts/search_edital.py 'conduta estudantil' --cargo 324 --limit 4` e `python scripts/search_edital.py --page 29`. Conferir integridade: `python scripts/chunk_edital.py --check`.

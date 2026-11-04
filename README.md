# UFMS MEU ESTUDO — harness de aprendizagem por questões

Tutor assistido por IA para os cargos **523 (Analista em Educação / Gestão Pública)** e **324 (Técnico em Educação / Assuntos Estudantis)** do Edital PROGEP/UFMS nº 152/2026. Prova prevista para **17/01/2027**, banca **FAPEC**.

## Objetivo

Persistir o contexto entre sessões, orientar cadernos de questões no TEC Concursos/Qconcursos, receber os resultados que o estudante fornecer e recomendar intervenções pedagógicas **sem rigidez metodológica**.

- **GitHub = fonte de verdade persistente.** A memória de uma conversa não substitui registros confirmados.
- **A IA não consulta as contas TEC/Qconcursos automaticamente.** O estudante cria o caderno e entrega resultados exportados ou resumidos.
- **Não são armazenadas questões ou comentários integrais de plataformas privadas.** Apenas metadados, links, decisões e resultados permitidos.
- **Sem dados pessoais no repositório público.** Antes de registrar desempenho individual, torne o repositório **privado**.
- **Alterações estruturais por PR**, sem merge sem aprovação. Resultados podem ser registrados por fluxo ordinário autorizado após tornar o repositório privado.

## Iniciar uma sessão

1. Ler `AGENTS.md` e os sete arquivos do bootstrap, nesta ordem.
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

## Fonte e limites

O documento primário de escopo é o edital UFMS nº 152 de 29/10/2026. Veja `docs/EDITAL.md` e `docs/FONTES.md`. Em caso de retificação, interrompa a propagação de dados antigos até conferir a versão oficial.

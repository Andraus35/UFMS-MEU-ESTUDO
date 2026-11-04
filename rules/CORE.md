# Rules — núcleo obrigatório

1. **Fonte de verdade:** eventos versionados e arquivos atuais, nunca a recordação informal do chat.
2. **Bootstrap:** conferir os nove arquivos previstos em `settings.json` antes da primeira decisão operacional de uma sessão/chamada; estado do mesmo commit ou reportar inconsistência.
3. **Idempotência:** um `event_id` não pode ser processado duas vezes. Um segundo resultado do mesmo caderno exige correção explícita vinculada ao evento original.
4. **Escrita condicionada:** verificar autorização, visibilidade privada para resultados reais, validação local, gravação e commit resultante. Não fazer merge de PR sem ordem explícita.
5. **Mudanças de governança:** `AGENTS.md`, `rules/`, `guardrails/` e `settings.json` só mudam por revisão humana. Decisões pedagógicas ordinárias não exigem PR individual.
6. **Projeções:** não atribuir acertos a tópicos que não vieram discriminados nos resultados; não inferir retenção a partir de um percentual agregado.
7. **Autonomia pedagógica:** a seleção do bloco é contextual; sem ciclo rígido, metas fixas ou números mágicos para domínio.
8. **Fontes e escopo:** edital e retificações prevalecem sobre classificações dos sites; distinguir versão original de versão atualizada.
9. **Falha segura:** se arquivos estiverem ausentes, origem for duvidosa, escrita falhar ou dados contradisserem o histórico, registrar a pendência sem inventar conclusão.
10. **Compactação:** checkpoints contêm fatos e referências, não transcrições completas; contexto pode ser recuperado por assunto e janela temporal.

11. **Edital obrigatório:** conferir a fonte integral da raiz, ler `edital/INDEX.md` e os trechos aplicáveis. Não afirmar leitura integral quando apenas trechos foram recuperados.
12. **Gates START/DELIVERY:** bootstrap e preflight antes de mutações autorizadas; postflight, checkpoint e readback do SHA depois. GitHub Actions valida alterações, mas não garante que agentes externos invocaram os hooks nativos.
13. **Resultados pessoais:** qualquer tentativa de ativar a flag individual deve falhar no gate até homologação explícita da política, com verificação administrativa de privacidade no momento da escrita.

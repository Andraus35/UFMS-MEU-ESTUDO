# Ciclo operacional humano ↔ IA

1. O agente lê os dez arquivos obrigatórios (incluindo `ROADMAP.md`) e recupera histórico pertinente.
2. A IA recomenda **um caderno principal** com ID, cargo, assuntos, bloco, plataforma, filtros e critério de expansão.
3. O estudante monta o caderno no TEC/Qconcursos e resolve sem manipulação automatizada da plataforma.
4. O estudante devolve resultados agregados e, quando disponíveis, dados por tópico; informa questões repetidas e dúvidas relevantes.
5. O agente valida consistência e origem; somente depois de habilitação homologada, autorização específica e verificação de privacidade, registra evento append-only.
6. O agente atualiza projeções e handoff; recomenda avanço/revisão/correção sem intervalos fixos.

**Nota de controle:** se houver resultado discriminado por assunto, os subtotais de tentativas, acertos e erros não podem superar as respectivas contagens agregadas; quando existir recomendação do mesmo caderno, os tópicos informados devem estar contidos no escopo dela. Resultados agregados sem discriminação não geram acertos por tópico. Uma alteração de `settings.json` não substitui a verificação de privacidade e a autorização para escrita real.

**Nota de integridade:** um resultado apenas consolidado de várias matérias NÃO pode ser imputado integralmente a qualquer tópico. As estatísticas por tópico só são calculadas quando fornecidas de modo explícito.

**Ponto de corte:** sem confirmação de commit, a próxima sessão trata a escrita como pendente, não como finalizada.


## START/DELIVERY — contrato local verificável

1. **START em checkout local:** conferir HEAD/branch e os nove arquivos obrigatórios; `python scripts/bootstrap.py` lê os bytes e informa SHA-256 por arquivo; `python scripts/roadmap_gate.py --check` valida referências ao roadmap. Antes de trabalhar, ler ROADMAP do mesmo HEAD e identificar item RM. Conferir a CI vinculada ao HEAD exato.
2. **Pré-escrita autorizada:** executar `python hooks/before_write.py` e `python scripts/write_policy.py --check`. Falha interrompe operação; não usar direct-write como atalho. **Não registrar resultados pessoais**: `personal_results_writes_enabled` permanece `false`, e alterar só a flag reprova a CI.
3. **DELIVERY:** executar `python hooks/after_write.py`, `python hooks/checkpoint.py` e testes; conferir persistência remota por SHA exato após commit. Atualizar handoff com evidências e limitações, nunca com êxito presumido.
4. **Limite de implementação:** os scripts de hook são *invocáveis e testados*, mas **não são automaticamente registrados** por GitHub, ChatGPT ou outro agente. Um agente que escreva diretamente pela API pode ignorar o preflight. A CI fornece um gate de validação após o push; proteções de branch e autorização humana seguem necessárias para impedir bypass/merge.
5. **Roadmap:** toda execução controlada depende de `ROADMAP.md` válido, na segunda posição após AGENTS. Gate e CI rejeitam ausência, placeholder e referências removidas; agente externo ainda pode ignorar hooks locais. Atualizar roadmap e handoff quando mudar prioridade/estado.
6. **Privacidade:** nenhum dado de resultado individual pode ser persistido nesta fase. A liberação futura requer verificação autenticada da visibilidade do repositório no momento da escrita, consentimento e revisão do gate; a CI não realiza essa liberação.
7. **Administração de main e agentes externos:** ver `docs/PROTECAO_MAIN.md`; script `scripts/protect_main.py --check` confirma readback autenticado. Copilot usa instruções em `.github/copilot-instructions.md` apenas se o cliente as carregar; seu papel segue consultivo, sem autorização de escrita.
8. **Escrita via API do GitHub:** sem checkout, não é possível executar o preflight local na máquina do agente. Operar apenas em branch/PR draft, sem dados pessoais, fazer readback dos arquivos estratégicos e SHA de cada commit e aguardar CI do HEAD; registrar explicitamente a limitação do gate, não declarar hook nativo executado. Para impor proteção universal, avaliar branch protection e permissões independentes do próprio PR.


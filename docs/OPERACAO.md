# Ciclo operacional humano ↔ IA

1. O agente lê os nove arquivos obrigatórios e recupera histórico pertinente.
2. A IA recomenda **um caderno principal** com ID, cargo, assuntos, bloco, plataforma, filtros e critério de expansão.
3. O estudante monta o caderno no TEC/Qconcursos e resolve sem manipulação automatizada da plataforma.
4. O estudante devolve resultados agregados e, quando disponíveis, dados por tópico; informa questões repetidas e dúvidas relevantes.
5. O agente valida consistência e origem; quando autorizado e em repositório privado, registra evento append-only.
6. O agente atualiza projeções e handoff; recomenda avanço/revisão/correção sem intervalos fixos.

**Nota de controle:** se houver resultado discriminado por assunto, os subtotais de tentativas, acertos e erros não podem superar as respectivas contagens agregadas; quando existir recomendação do mesmo caderno, os tópicos informados devem estar contidos no escopo dela. Resultados agregados sem discriminação não geram acertos por tópico. Uma alteração de `settings.json` não substitui a verificação de privacidade e a autorização para escrita real.\n\n**Nota de integridade:** um resultado apenas consolidado de várias matérias NÃO pode ser imputado integralmente a qualquer tópico. As estatísticas por tópico só são calculadas quando fornecidas de modo explícito.

**Ponto de corte:** sem confirmação de commit, a próxima sessão trata a escrita como pendente, não como finalizada.

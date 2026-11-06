# Ciclo operacional humano ↔ IA

1. O agente lê os quatro arquivos obrigatórios (AGENTS, ROADMAP, HANDOFF, CURRENT), depois recupera o histórico pertinente somente se necessário.
2. A IA recomenda **um caderno principal** com ID, cargo, assuntos, bloco, plataforma, filtros e critério de expansão.
3. O estudante monta o caderno no TEC/Qconcursos e resolve sem manipulação automatizada da plataforma.
4. O estudante devolve resultados agregados e, quando disponíveis, dados por tópico; informa questões repetidas e dúvidas relevantes.
5. O agente valida consistência e origem; somente depois de habilitação homologada, autorização específica e verificação de privacidade, registra evento append-only.
6. O agente atualiza projeções e handoff; recomenda avanço/revisão/correção sem intervalos fixos.

**Nota de controle:** se houver resultado discriminado por assunto, os subtotais de tentativas, acertos e erros não podem superar as respectivas contagens agregadas; quando existir recomendação do mesmo caderno, os tópicos informados devem estar contidos no escopo dela. Resultados agregados sem discriminação não geram acertos por tópico. Uma alteração de `settings.json` não substitui a verificação de privacidade e a autorização para escrita real.

**Nota de integridade:** um resultado apenas consolidado de várias matérias NÃO pode ser imputado integralmente a qualquer tópico. As estatísticas por tópico só são calculadas quando fornecidas de modo explícito.

**Ponto de corte:** sem confirmação de commit, a próxima sessão trata a escrita como pendente, não como finalizada.


## Autonomia cognitiva e gates proporcionais

Para comunicação com o estudante, diferenciar:
- **ORIENTACAO / NONE:** proposta do LLM, verificação automática de escopo/fonte/dados e entrega sem aprovação humana por mensagem.
- **ROTINA_AUTORIZADA / TOOL:** envio pela Zapia ao proprietário e lembrete de agenda somente após implantação comprovada de conector e autorização prévia de escopo; o gateway valida destino, quotas, duplicação e readback. Uma rotina autorizada não pede confirmação individual a cada mensagem.
- **SENSIVEL / TOOL:** mudanças estruturais, divulgação a terceiros, acesso a dados pessoais e integração de código exigem controles mais fortes e aprovação humana quando aplicável.

A falha de um canal externo não deve paralisar cognição/orientação sem efeito externo. Este documento especifica o contrato; não afirma que Zapia ou o executor real já estejam funcionando. Manter bloqueada a gravação de resultados individuais enquanto a política vigente não a habilitar com privacidade comprovada.

## START/DELIVERY — contrato local verificável

1. **START em checkout local:** conferir HEAD/branch e os quatro arquivos obrigatórios; `python scripts/bootstrap.py --mode engineering` para engenharia (cinco arquivos, com `state/WORKFLOW.json`) ou `python scripts/bootstrap.py --mode study` para estudo (quatro arquivos) lê os bytes e informa SHA-256 por arquivo; `python scripts/roadmap_gate.py --check` valida referências ao roadmap. Antes de trabalhar, ler ROADMAP do mesmo HEAD e identificar item RM. Conferir a CI vinculada ao HEAD exato.
2. **Pré-escrita autorizada:** executar `python hooks/before_write.py` e `python scripts/write_policy.py --check`. Falha interrompe operação; não usar direct-write como atalho. **Não registrar resultados pessoais**: `personal_results_writes_enabled` permanece `false`, e alterar só a flag reprova a CI.
3. **DELIVERY:** executar `python hooks/after_write.py`, `python hooks/checkpoint.py`, `python scripts/governance_sync_gate.py` e testes; conferir persistência remota por SHA exato após commit. Quando o ciclo mudar, reconciliar HANDOFF, WORKFLOW, ROADMAP e STATUS. O gate determinístico rejeita snapshots divergentes e exige o SHA do último merge comprovado.
4. **Limite de implementação:** os scripts de hook são *invocáveis e testados*, mas **não são automaticamente registrados** por GitHub, ChatGPT ou outro agente. Um agente que escreva diretamente pela API pode ignorar o preflight. A CI fornece um gate de validação após o push; proteções de branch e autorização humana seguem necessárias para impedir bypass/merge.
5. **Roadmap:** toda execução controlada depende de `ROADMAP.md` válido, na segunda posição após AGENTS. Gate e CI rejeitam ausência, placeholder e referências removidas; agente externo ainda pode ignorar hooks locais. Atualizar roadmap e handoff quando mudar prioridade/estado.
6. **Privacidade:** nenhum dado de resultado individual pode ser persistido nesta fase. A liberação futura requer verificação autenticada da visibilidade do repositório no momento da escrita, consentimento e revisão do gate; a CI não realiza essa liberação.
7. **Administração de main e agentes externos:** ver `docs/PROTECAO_MAIN.md`; script `scripts/protect_main.py --check` confirma readback autenticado. Copilot usa instruções em `.github/copilot-instructions.md` apenas se o cliente as carregar; seu papel segue consultivo, sem autorização de escrita.
8. **Escrita via API do GitHub:** sem checkout, não é possível executar o preflight local na máquina do agente. Operar apenas em branch/PR draft, sem dados pessoais, fazer readback dos arquivos estratégicos e SHA de cada commit e aguardar CI do HEAD; registrar explicitamente a limitação do gate, não declarar hook nativo executado. Para impor proteção universal, avaliar branch protection e permissões independentes do próprio PR.


**Prova versus promessa (05/11/2026):** a CI valida o START controlado de engenharia e o inventário remoto de PRs, mas não registra nem intercepta automaticamente toda inicialização de ChatGPT, Tutor, Coach ou outros clientes. Sem passagem obrigatória pelo executor, não existe prova universal de leitura semântica. Não alegar tal garantia.

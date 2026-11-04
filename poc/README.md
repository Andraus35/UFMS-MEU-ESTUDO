# POCs Zapia — somente evidência sintética (04/11/2026)

Os arquivos `POC-UFMS-003.json`, `POC-UFMS-005.json` e `POC-UFMS-007.json` registram **experimentos fictícios e históricos**, não são dados pessoais ou atividade de estudo real.

- Nunca incorporar estes valores ao `state/CURRENT.json`, `state/PROGRESS.csv` ou à fila real de revisões.
- O campo `dados_ficticios: true` é obrigatório em cada registro; não alterar para `false`.
- O sucesso das POCs comprova operações pontuais: leitura/escrita compartilhada e coordenação controlada; não comprova execução recorrente, autenticação em serviços de questões nem domínio pedagógico.
- Nenhuma credencial ou progresso pessoal deve ser registrado no repositório enquanto estiver público.
- Os arquivos originais são preservados apenas para auditoria e contraprovas.

Cadeia documental: POC-003 (registro inicial) → POC-005 (Tutor/Notebook/Coach) → POC-007 (retorno e no-op sequencial). As provas de notificação e agenda (POCs 006 e 008) foram relatadas pela Zapia, não versionadas nestes JSONs.

**Fonte da verdade operacional:** `state/` e suas regras de validação, nunca `poc/`.

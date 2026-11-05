# PR #5 — prova sintética de composição (somente leitura)

**Objeto:** teste do `refs/pull/5/merge` disponibilizado pelo GitHub, com `main` e HEAD do PR #5 como pais, sem criar merge real, sem alterar branch e sem permissões de escrita.

- Fluxo: `.github/workflows/verify-spec-composition.yml`.
- Verificador: `composition-tests/prove.py`.
- Negativas: `composition-tests/test_prove.py`.
- Verificações: identidade PR/repositório, SHA dos pais, SHA da `main` atual por `git ls-remote`, presença do harness/edital e imutabilidade dos blobs r2 já aprovados. Executa `scripts/validate.py` e suíte principal na árvore sintética.
- O `composition-lock.json` anterior permanece um snapshot **histórico**, não fonte do HEAD atualizado da `main`. O resultado desta verificação constitui recibo específico do workflow, não promove retrospectivamente o lock antigo.
- Se `main` mudar entre a síntese e a leitura, a composição falha fechada e pode ser repetida sobre novo merge sintético.
- A CI deverá fornecer recibo de SHA, logs e artifacts, separados das provas documentais anteriores. **Não declarar GQD-03 encerrada** antes de avaliação independente.
- O cumprimento funcional dos 27 Cognitive Gates permanece **NOT_RUN**, e o PLAN r3 continua **NÃO APROVADO**. Nenhum teste LLM, Zapia, Agenda, ferramenta privilegiada ou gravação pessoal é realizado.
- O checkout permite somente leitura de `main` + PR #5 e **não é autorização para mesclar o PR**.


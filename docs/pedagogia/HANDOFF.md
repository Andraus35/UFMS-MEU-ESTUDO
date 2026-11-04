# Handoff da sessão de estratégia pedagógica — UFMS

**Checkpoint:** 04/11/2026, America/Campo_Grande — **loop autônomo, ciclo 1**.  
**Status:** cotejo textual dos conteúdos específicos 523/324 no edital original. Sem homologação GP-0.

## START confirmado

- Repositório: `Andraus35/UFMS-MEU-ESTUDO`; PR pedagógico [#2](https://github.com/Andraus35/UFMS-MEU-ESTUDO/pull/2), branch `docs/especificacao-pedagogica-v1-2`, aberto em draft sem merge.
- HEAD **anterior** a este commit: `443fc04158fdebb2c30777393603afefe43e4027`. Obter HEAD novo por readback, pois não é possível inscrever o SHA do próprio commit dentro dele.
- PR técnico [#1](https://github.com/Andraus35/UFMS-MEU-ESTUDO/pull/1), HEAD observado no início do ciclo `ed263a7999dd816c32af086a41ea8cefa8ab13c9`; não escrever nessa branch.
- `main` não modificada por esta entrega.

## Entrega — ciclo 1

- [COTEJO_ESPECIFICOS_523_324_2026-11-04.md](COTEJO_ESPECIFICOS_523_324_2026-11-04.md): sete interseções textuais localizadas no Anexo V do original UFMS, com limites, linhas/páginas, conteúdos exclusivos, incerteza normativa e cuidados de dupla contagem.
- [README.md](README.md): índice atualizado.
- [HANDOFF.md](HANDOFF.md): este checkpoint no mesmo commit.
- [CRITERIOS_DE_ACEITACAO.md](CRITERIOS_DE_ACEITACAO.md): **102 cenários documentados**, sem adição nem execução nesta entrega.
- Especificações v1.0–v1.8 permanecem propostas; nada foi implementado no motor.

## Evidência e incerteza

- Documento original: https://www.ufms.br/wp-content/uploads/2026/10/SEI_6775306_Edital.pdf, páginas impressas 35–36 (523) e 45 (324).
- As interseções são parciais; nenhum bloco completo deve ser fundido por nome.
- FAPEC lista `001/2026` enquanto UFMS apresenta `152/2026`. Não foi possível ler o PDF FAPEC nem demonstrar ausência de retificações. **GP-0 continua pendente**.
- Não realizar alterações em `config/topics.csv`, índices/chunks, código, `settings.json` ou persistência pessoal.

## Próxima tarefa do loop

Verificar a consistência de classificação de temas exclusivos e sobrepostos em **contraprovas documentais** dos blocos 523/324 e converter o mapeamento em um conjunto curto de exemplos de caderno com filtros apropriados, **sem afirmar estoque de questões real**. Outra alternativa somente se houver evidência nova é confrontar arquivo FAPEC/retificações. Cada entrega requer commit e readback.

## Guardrails

Não merge; não tocar PR #1; não supor resultados pessoais; não declarar CI aprovada sem execução observada; revalidar HEAD e handoff antes de prosseguir.

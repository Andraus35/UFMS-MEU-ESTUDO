# Handoff da sessão de estratégia pedagógica — UFMS

**Checkpoint:** 04/11/2026, America/Campo_Grande.  
**Natureza:** verificação documental complementar do GP-0. A especificação pedagógica v1.0–v1.8 permanece preservada; **não há motor adaptativo homologado**.

## START / identidades conferidas

- Repositório privado: `Andraus35/UFMS-MEU-ESTUDO`.
- PR pedagógico [#2](https://github.com/Andraus35/UFMS-MEU-ESTUDO/pull/2), branch `docs/especificacao-pedagogica-v1-2`, aberto em draft, sem merge.
- HEAD **anterior** ao commit deste checkpoint: `d698b480ed15b392aef6e3a1396c30e074716775`. O SHA final deve ser conferido por readback remoto, nunca presumido dentro do próprio commit.
- PR técnico [#1](https://github.com/Andraus35/UFMS-MEU-ESTUDO/pull/1): aberto, sem merge; último HEAD consultado nesta entrega: `beefee3581c205bacc30065ced29288e215541a2`. Reconfirmar em próxima sessão.
- A `main` não foi editada nem mesclada por esta entrega.

## Estado pedagógico

- Método e contratos v1.0–v1.8 estão indexados em [README.md](README.md).
- [CRITERIOS_DE_ACEITACAO.md](CRITERIOS_DE_ACEITACAO.md): **102 cenários documentados**, não executados como suíte completa do motor; sem novos cenários nesta entrega.
- [PROTOCOLO_ENTREGA_CONTINUIDADE.md](PROTOCOLO_ENTREGA_CONTINUIDADE.md): protocolo de commit/handoff por entrega substantiva e readback.

## Evidência complementar produzida

O arquivo [VERIFICACAO_GP0_GP1_2026-11-04.md](VERIFICACAO_GP0_GP1_2026-11-04.md) recebeu uma seção 5 com:
- identificação original do edital UFMS nº 152/2026 no PDF primário de 47 páginas;
- confirmação do rótulo diferente `001/2026` na página do concurso FAPEC; link `DOWNLOAD` redirecionou a objeto S3 não acessível no mecanismo consultado, sem cotejo;
- datas originais do Anexo II: inscrições 04/11–04/12, isenção 04–11/11, pagamento 07/12, ensalamento 11/01 e prova 17/01/2027;
- possível incongruência de cronograma: recurso `11 e 12/01/2027` associado a resultado preliminar de `10/02/2027`, sem correção presumida;
- buscas sem identificação positiva de retificação não constituem prova de ausência de retificações.

**Vereditos:** GP-0 continua PENDENTE nas dimensões de atualidade/retificações, FAPEC e integridade de cronograma; GP-1 continua PENDENTE quanto a contratos de engenharia; GP-2..GP-5 não homologados.

## Mudanças pretendidas neste commit

- Complementar `VERIFICACAO_GP0_GP1_2026-11-04.md`, sem reescrever verificações históricas.
- Atualizar `README.md` e este `HANDOFF.md` no mesmo commit.
- Sem alterações em código, PR #1, `config/concursos.json`, fontes canônicas ou dados pessoais.
- Confirmar remotamente SHA e os três arquivos após a publicação; anotar situação real da CI.

## Próxima ação

**Para GP-0/ENG-00:** obter, por meio autorizado, os bytes do PDF listado na FAPEC, comparar identidade e conteúdo com o PDF UFMS, registrar hashes, verificar retificações e esclarecer a data cronologicamente inconsistente.

**Para o planejamento pedagógico:** não estender artificialmente o manual; o aluno pode iniciar diagnósticos reais por questões sem aguardar a automação, devolvendo resultados sem gravação automática enquanto a permissão técnica continuar bloqueada.

**Guardrails:** não declarar que houve retificação ou que ela não existe; não afirmar leitura do PDF FAPEC; sem merge e sem escrita de resultados privados não autorizada.

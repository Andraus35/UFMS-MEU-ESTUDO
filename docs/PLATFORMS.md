# Mecânica TEC Concursos e Qconcursos — operação humana

A IA prescreve **filtros configuráveis**, não inventa um caderno publicado ou questões concretas. O estudante cria e resolve cadernos nas plataformas e devolve resultado (total, acertos, erros, data, tópicos e, quando possível, resultados discriminados por tópico).

- TEC Concursos: priorizar cadernos por assunto e estatísticas verificadas pelo usuário; exportação CSV está sujeita ao plano e formato real do arquivo.
- Qconcursos: usar filtros por disciplina/assunto, banca, ano, dificuldade e histórico quando disponíveis; não presumir exportação CSV.
- Para provas FAPEC: começar por questões próximas e ampliar filtros explicitamente quando a amostra for insuficiente.
- Acesso à conta do proprietário só pelo conector local descrito abaixo (decisões D-14 e D-15 do `PRODUCT.md`); nenhum outro robô, nenhum scraping em escala e nenhum acesso a contas de terceiros. Não armazenar comentários ou enunciados completos de terceiros sem autorização.
- Estudante pode fornecer relatórios por tabela, captura legível ou arquivo exportado. **A estrutura exata do CSV do TEC permanece por validar.**

## Conector local de leitura das plataformas (especificação S4, PR-017)

**Objetivo:** ler cadernos e estatísticas da conta do proprietário no TEC Concursos e no Qconcursos, **somente leitura**, sem entregar credencial ao modelo (D-14). Referência de padrão: ponte local por Chrome DevTools Protocol, como em `LewisWJackson/tradingview-mcp-jackson` (lida só como referência; nenhum código é copiado).

**Onde roda:** no computador do proprietário, em um Chromium com **perfil dedicado**, logado só no TEC e no Qconcursos (nunca Google ou GitHub), com a porta de depuração aberta **somente em localhost**. A sessão fica no perfil do navegador; não vai ao repositório, à Zapia nem ao modelo.

**Ferramentas (somente leitura):** `plataformas_status`, `listar_cadernos`, `ler_resultado_caderno`, `ler_estatisticas`. Cada uma devolve JSON no formato do contrato de ingestão (PR-016), com plataforma, data da leitura e `origem = leitura_direta`. Não devolve cookie, token, HTML bruto nem enunciado completo.

**Regras fixas:**
- Só os domínios do TEC e do Qconcursos (lista fechada); qualquer outro é recusado.
- Proibido resolver questão, criar, editar ou apagar caderno, enviar formulário ou executar código recebido do modelo.
- Limite de taxa inicial, ajustável pelo proprietário: no máximo 1 página a cada 10 segundos e 30 páginas por sessão.
- O que foi lido é dado não confiável e passa pelo contrato de ingestão como qualquer entrada.
- O TEC vem primeiro; o Qconcursos só entra depois do teste aceito no TEC (D-14). A primeira leitura em conta real exige consulta ao suporte do TEC (OPEN-12) e aprovação do proprietário.

**Critérios de aceite (verificáveis sem conta real):** testes com páginas sintéticas; recusa de domínio fora da lista; recusa de qualquer operação de escrita; saída sem cookie, token ou HTML bruto; limite de taxa aplicado.

**Como os dados chegam ao Tutor:** o conector só alcança o computador do proprietário. Se o Tutor rodar lá, lê direto; se rodar na nuvem, o conector gera um arquivo local que o proprietário entrega (pela Zapia), o que depende do OPEN-09.

**Alternativa:** a exportação manual (relatório, captura legível ou arquivo), usada quando o conector não estiver disponível.

**Limites:** especificação; não há implementação nem teste em conta real. As plataformas podem mudar suas páginas e bloquear a conta pelos seus termos (E-12).

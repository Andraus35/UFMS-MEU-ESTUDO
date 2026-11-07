# Mecânica TEC Concursos e Qconcursos — operação humana

A IA prescreve **filtros configuráveis**, não inventa um caderno publicado ou questões concretas. O estudante cria e resolve cadernos nas plataformas e devolve resultado (total, acertos, erros, data, tópicos e, quando possível, resultados discriminados por tópico).

- TEC Concursos: priorizar cadernos por assunto e estatísticas verificadas pelo usuário; exportação CSV está sujeita ao plano e formato real do arquivo.
- Qconcursos: usar filtros por disciplina/assunto, banca, ano, dificuldade e histórico quando disponíveis; não presumir exportação CSV.
- Para provas FAPEC: começar por questões próximas e ampliar filtros explicitamente quando a amostra for insuficiente.
- Acesso à conta do proprietário só pelo conector local descrito abaixo (decisões D-14 e D-15 do `PRODUCT.md`); nenhum outro robô, nenhum scraping em escala e nenhum acesso a contas de terceiros. Não armazenar comentários ou enunciados completos de terceiros sem autorização.
- Estudante pode fornecer relatórios por tabela, captura legível ou arquivo exportado. **A estrutura exata do CSV do TEC permanece por validar.**

## Leitura direta das plataformas (especificação S4, PR-017)

**Objetivo:** ler cadernos e estatísticas da conta do proprietário no TEC Concursos e no Qconcursos, **somente leitura**, sem entregar credencial ao modelo (D-14). O mecanismo é escolhido na fase de especificação, **depois de testar todas as possibilidades** (D-15).

### Opções a testar

| Opção | Ideia | Pergunta principal do teste |
|---|---|---|
| A. Conector local | Chromium com perfil dedicado no computador do proprietário, porta de depuração só em localhost e MCP local de leitura, no padrão de `LewisWJackson/tradingview-mcp-jackson` (lido só como referência; nenhum código copiado). Hipótese de partida | O que o Tutor consegue ler e como os dados chegam a ele? |
| B. Navegador do assistente | Extensão ou navegador embutido do aplicativo desktop do assistente, usando a sessão do proprietário | Funciona sem expor credencial e com as ferramentas disponíveis? |
| C. Zapia | Navegador da Zapia, como ela faz com o Gemini | A sessão do TEC ou Qconcursos ficaria no ambiente dela? |
| D. Nuvem | Navegador em servidor, com perfil persistente | Login, captcha, bloqueio por IP e onde a sessão fica guardada |
| E. Suporte ou API oficial | Consulta escrita ao suporte do TEC e do Qconcursos | Existe autorização ou API? |
| F. Exportação manual | Relatório, captura legível ou arquivo, entregue pelo proprietário. **Linha de base**, sempre disponível | Qual o formato real do arquivo (OPEN-11)? |

### Critérios de comparação (iguais para todas)

1. A credencial ou sessão fica fora do modelo e do repositório?
2. Risco de bloqueio da conta e aderência aos termos de uso (E-12).
3. Cobertura: quais dados chegam (cadernos, resultados, estatísticas por assunto).
4. Disponibilidade no dia a dia (precisa de computador ligado?).
5. Esforço do proprietário por semana.
6. Testável sem conta real, com páginas sintéticas?

Nenhuma opção é descartada antes do teste; o registro do resultado e da escolha vai para o `PRODUCT.md` (decisão) e para esta seção (especificação).

### Regras que valem para qualquer opção

- Somente leitura: proibido resolver questão, criar, editar ou apagar caderno, enviar formulário ou executar código recebido do modelo.
- Só os domínios do TEC e do Qconcursos; qualquer outro é recusado.
- Limite de taxa inicial, ajustável pelo proprietário: no máximo 1 página a cada 10 segundos e 30 páginas por sessão.
- Cada leitura devolve JSON no formato do contrato de ingestão (PR-016), com plataforma, data da leitura e `origem = leitura_direta`; sem cookie, token, HTML bruto nem enunciado completo. O que foi lido é dado não confiável.
- O TEC vem primeiro; o Qconcursos só entra depois do teste aceito no TEC (D-14). A primeira leitura em conta real exige consulta ao suporte do TEC (OPEN-12) e aprovação do proprietário.

### Critérios de aceite (verificáveis sem conta real)

Testes com páginas sintéticas; recusa de domínio fora da lista; recusa de qualquer operação de escrita; saída sem cookie, token ou HTML bruto; limite de taxa aplicado.

### Como os dados chegam ao Tutor

Depende do mecanismo e de onde o Tutor roda (OPEN-09). Se o Tutor rodar no computador do proprietário, lê direto; se rodar na nuvem, a leitura gera um arquivo que o proprietário entrega pela Zapia.

**Limites:** especificação; não há implementação nem teste em conta real. As plataformas podem mudar suas páginas e bloquear a conta pelos seus termos (E-12).

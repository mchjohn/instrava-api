Atue como um Desenvolvedor de Software Sênior especializado em Python, FastAPI e Arquitetura Limpa. Sua missão é explicar a implementação da SDD referente ao documento [AUTH-01.md](file;file:///home/mjos/Developer/Projetos/instrava-api/docs/sdd/AUTH-01.md) e aos arquivos atualmente em *staged* no Git para um Desenvolvedor Júnior da equipe, focando na fixação e na compreensão prática dos conceitos.

### Parte 1: Explicação Técnica Didática
Explique a implementação de forma clara, amigável e estruturada. Para cada conceito/arquivo implementado, forneça:
1. **O que foi feito:** Descrição objetiva da mudança e dos arquivos afetados.
2. **Por que foi feito:** A motivação arquitetural e as boas práticas por trás da escolha (ex: segurança, separação de responsabilidades, testabilidade, desacoplamento).
3. **Como funciona no fluxo:** Como essa parte se conecta com o restante da aplicação (visão do fluxo completo de requisição/resposta).
4. **Conceitos-chave para um Jr:** Destaques sobre bibliotecas, padrões de projeto (ex: Repository Pattern, Dependency Injection, Pydantic Schemas, tratamento de race conditions, hashing seguro) e armadilhas comuns a evitar.

---

### Parte 2: Geração do Arquivo de Fixação ([AUTH-01-QUESTOES.md](file;file:///home/mjos/Developer/Projetos/instrava-api/docs/estudo/AUTH-01-QUESTOES.md))
Após a explicação, crie/atualize o arquivo [AUTH-01-QUESTOES.md](file;file:///home/mjos/Developer/Projetos/instrava-api/docs/estudo/AUTH-01-QUESTOES.md) contendo exatamente **10 perguntas de estudo e fixação** baseadas na implementação.

**Regras para as perguntas:**
- Devem cobrir os pontos mais críticos da arquitetura, segurança e regras de negócio implementadas.
- Misture perguntas conceituais ("Por que usamos X em vez de Y?") e cenários práticos ("O que acontece se duas requisições com o mesmo e-mail chegarem ao mesmo tempo?").
- Inclua um gabarito/respostas explicativas ao final do arquivo para autoavaliação.
# Perguntas de Estudo e Fixação — SDD Auth-01 (Cadastro de Usuário)

Este documento reúne **10 perguntas essenciais** sobre a implementação da funcionalidade de cadastro de usuários (especificada em [AUTH-01.md](/home/mjos/Developer/Projetos/instrava-api/docs/sdd/AUTH-01.md)), cobrindo decisões arquiteturais, segurança da informação, manipulação de concorrência e boas práticas com Python, FastAPI e SQLAlchemy.

Ao final do documento encontra-se o **gabarito comentado**, detalhando as respostas esperadas e os conceitos fundamentais para autoavaliação.

---

## Questões

### Questão 1 (Segurança e Criptografia de Senhas)
No módulo [security.py](/home/mjos/Developer/Projetos/instrava-api/src/instrava_api/core/security.py), adotamos a biblioteca `pwdlib` com o algoritmo **Argon2id** para gerar o hash das senhas dos usuários, em vez de funções de hash comuns como MD5, SHA-256 ou algoritmos anteriores como bcrypt.
1. Por que algoritmos rápidos como MD5 e a família SHA (mesmo com *salt*) são considerados inseguros para armazenamento de senhas?  
*Porque algoritmos como MD5 e SHA foram projetados para alta velocidade de processamento. Com o uso de GPUs e ASICs altamente paralelos, um invasor consegue testar bilhões de combinações por segundo (brute force), já que esses algoritmos não exigem consumo intensivo de memória RAM.*
2. O que significa uma função criptográfica ser classificada como **memory-hard** (com custo de memória) e qual a vantagem do Argon2id contra ataques de força bruta com placas de vídeo (GPUs) e ASICs?  
*Memory-hard significa que o cálculo do hash exige alocação pesada de memória RAM. A vantagem do Argon2id é que GPUs possuem muita capacidade de processamento bruto, mas possuem restrições de largura de banda e acesso à memória comparadas à CPU+RAM, o que inviabiliza ataques de força bruta em larga escala.*

---

### Questão 2 (Arquitetura em Camadas e Responsabilidades)
Na estrutura do projeto, separamos o código em:
- [routers/auth.py](/home/mjos/Developer/Projetos/instrava-api/src/instrava_api/routers/auth.py)
- [schemas/user.py](/home/mjos/Developer/Projetos/instrava-api/src/instrava_api/schemas/user.py)
- [services/user_service.py](/home/mjos/Developer/Projetos/instrava-api/src/instrava_api/services/user_service.py)
- [repositories/user_repository.py](/home/mjos/Developer/Projetos/instrava-api/src/instrava_api/repositories/user_repository.py)
- [models/user.py](/home/mjos/Developer/Projetos/instrava-api/src/instrava_api/models/user.py)

Qual problema arquitetural aconteceria se escrevêssemos as consultas SQL/ORM e a lógica de verificação de regras de negócio diretamente dentro da função de rota ([routers/auth.py](/home/mjos/Developer/Projetos/instrava-api/src/instrava_api/routers/auth.py))? Cite pelo menos duas vantagens práticas imediatas de manter o [UserService](/home/mjos/Developer/Projetos/instrava-api/src/instrava_api/services/user_service.py#L11) e o [UserRepository](/home/mjos/Developer/Projetos/instrava-api/src/instrava_api/repositories/user_repository.py#L7) isolados.  
*Colocar lógica de banco e de negócio nas rotas gera alto acoplamento, tornando o código rígido, impossível de testar unitariamente sem subir uma API HTTP e inviável de reutilizar.*
Vantagens de isolar Service e Repository:
- *Testabilidade: Podemos testar regras de negócio isoladamente mockando o repositório.*
- *Manutenibilidade e Separação de Responsabilidades: Se a forma de acesso a dados mudar (ex: trocar SQLAlchemy por outro ORM), mexemos apenas no repositório sem tocar nas regras de negócio.*

---

### Questão 3 (Concorrência e Condições de Corrida / Race Conditions)
Observe o trecho de código em [user_service.py](/home/mjos/Developer/Projetos/instrava-api/src/instrava_api/services/user_service.py#L22-L42):
```python
existing_user = await self.user_repo.get_by_email(normalized_email)
if existing_user is not None:
    raise EmailAlreadyRegisteredError()

# ... hash e instanciação ...

try:
    user = await self.user_repo.create(new_user)
    await self.session.commit()
    await self.session.refresh(user)
    return user
except IntegrityError as exc:
    await self.session.rollback()
    raise EmailAlreadyRegisteredError() from exc
```

Se a verificação `get_by_email` já checa se o e-mail existe antes de tentar cadastrar, por que ainda é **estritamente obrigatório** envolver o `create`/`commit` em um bloco `try ... except IntegrityError`? Descreva um cenário real de concorrência onde isso acontece.  
*Para prevenir condições de corrida (Race Conditions). Se duas requisições idênticas chegarem exatamente no mesmo milissegundo, ambas podem passar pelo get_by_email (encontrando None) antes que qualquer uma delas seja salva. Quando ambas tentarem o create, o banco de dados impõe a restrição única (unique constraint) no índice do e-mail, disparando uma IntegrityError que capturamos para retornar o erro 409 com segurança.*

---

### Questão 4 (Normalização de Dados e Case Insensitivity)
No schema Pydantic [UserRegister](/home/mjos/Developer/Projetos/instrava-api/src/instrava_api/schemas/user.py#L6), temos o validador:
```python
@field_validator("email")
@classmethod
def normalize_email(cls, value: str) -> str:
    return value.strip().lower()
```
E repetimos a sanitização no [UserRepository](/home/mjos/Developer/Projetos/instrava-api/src/instrava_api/repositories/user_repository.py#L13) e [UserService](/home/mjos/Developer/Projetos/instrava-api/src/instrava_api/services/user_service.py#L20).
1. Por que e-mails devem ser normalizados antes de serem gravados ou consultados?  
*Para garantir a consistência dos dados, evitando que variações de digitação (espaços extras ou letras maiúsculas) criem registros duplicados ou falhem em buscas futuras.*
2. O que aconteceria se o sistema permitisse cadastrar `carlos@empresa.com` e `Carlos@Empresa.com` como dois usuários distintos?  
*Porque e-mails são semanticamente case-insensitive. Se o sistema permitisse duas contas com variações de maiúsculas/minúsculas, o usuário legítimo perderia o acesso, receberia mensagens trocadas ou sofreria falhas de autenticação.*

---

### Questão 5 (Desacoplamento de Exceções de Domínio vs Protocolo HTTP)
No arquivo [core/exceptions.py](/home/mjos/Developer/Projetos/instrava-api/src/instrava_api/core/exceptions.py), criamos [EmailAlreadyRegisteredError](/home/mjos/Developer/Projetos/instrava-api/src/instrava_api/core/exceptions.py#L5) herdando de `DomainError`. Em vez disso, poderíamos simplesmente ter feito no Service:
```python
raise HTTPException(status_code=409, detail={"code": "EMAIL_ALREADY_REGISTERED", ...})
```
Por que acoplar exceções HTTP (`fastapi.HTTPException`) dentro da camada de Service ou Repository fere os princípios da Arquitetura Limpa e prejudica a reutilização de código? Onde essa exceção de domínio é convertida no JSON de resposta da API?  
*Acoplar HTTPException na camada de serviço viola a Arquitetura Limpa porque acopla a regra de negócio a um protocolo de transporte específico (HTTP). A Service deve retornar exceções de domínio puras (DomainError). A conversão para o JSON/HTTP ocorre na camada de apresentação através de Exception Handlers globais no FastAPI.*

---

### Questão 6 (Data Transfer Objects / Pydantic e Prevenção de Vazamento)
Na camada de schemas ([schemas/user.py](/home/mjos/Developer/Projetos/instrava-api/src/instrava_api/schemas/user.py)), definimos dois modelos distintos:
- [UserRegister](/home/mjos/Developer/Projetos/instrava-api/src/instrava_api/schemas/user.py#L6): recebe `name`, `email` e `password`.
- [UserPublic](/home/mjos/Developer/Projetos/instrava-api/src/instrava_api/schemas/user.py#L29): expõe `id`, `name`, `email` e `created_at`.
1. Como essa separação impede o vazamento tanto da senha em texto puro quanto do `password_hash` para o cliente?  
*O schema de saída (UserPublic) atua como uma whitelist explícita de quais campos podem ser serializados e enviados ao cliente, bloqueando automaticamente atributos sensíveis como password_hash.*
2. Para que serve a instrução `model_config = ConfigDict(from_attributes=True)` no modelo [UserPublic](/home/mjos/Developer/Projetos/instrava-api/src/instrava_api/schemas/user.py#L29)?  
*O from_attributes=True instrui o Pydantic a ler os dados de objetos baseados em atributos (como instâncias de modelos ORM do SQLAlchemy) e não apenas de dicionários Python puros.*

---

### Questão 7 (Injeção de Dependência e Ciclo de Vida da Sessão no FastAPI)
A rota [register](/home/mjos/Developer/Projetos/instrava-api/src/instrava_api/routers/auth.py#L20) recebe o banco de dados via:
```python
db: Annotated[AsyncSession, Depends(get_db)]
```
E a dependência [get_db](/home/mjos/Developer/Projetos/instrava-api/src/instrava_api/core/database.py#L22) é definida como um gerador assíncrono:
```python
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
```
1. Como o FastAPI gerencia o ciclo de vida dessa conexão (abertura, uso e encerramento)?  
*O FastAPI utiliza geradores assíncronos (async generators) com blocos async with para abrir a sessão do banco no início da requisição e garantir automaticamente o seu fechamento e retorno ao pool de conexões logo após a resposta ser enviada.*
2. O que acontece com a sessão do banco se uma exceção não tratada for disparada durante a execução da rota?  
*Exceções não tratadas encerram o ciclo da requisição, fechando a sessão e acionando o mecanismo de rollback automático para evitar sujeira ou transações travadas no banco.*

---

### Questão 8 (Persistência e Transações: `flush()` vs `commit()`)
No método [create](/home/mjos/Developer/Projetos/instrava-api/src/instrava_api/repositories/user_repository.py#L18) do [UserRepository](/home/mjos/Developer/Projetos/instrava-api/src/instrava_api/repositories/user_repository.py), executamos:
```python
self.session.add(user)
await self.session.flush()
```
Enquanto o `await self.session.commit()` só é executado no [UserService](/home/mjos/Developer/Projetos/instrava-api/src/instrava_api/services/user_service.py#L36).
1. Qual a diferença técnica entre chamar `session.flush()` e `session.commit()` no SQLAlchemy?  
*session.flush() envia os comandos SQL pendentes para o banco (gerando IDs automáticos e ativando restrições) sem encerrar a transação. session.commit() efetiva e encerra a transação permanentemente no banco.*
2. Por que a responsabilidade de efetivar a transação (`commit`) deve pertencer à camada de Serviço e não ao Repositório?  
*A transação envolve regras de negócio completas que podem cruzar múltiplos repositórios; portanto, a decisão de salvar permanentemente (commit) pertence à camada de Serviço, enquanto o repositório executa apenas operações atômicas de persistência.*

---

### Questão 9 (Tratamento Global de Erros 500 e Sanitização de Erros Internos)
No arquivo [main.py](/home/mjos/Developer/Projetos/instrava-api/src/instrava_api/main.py#L32-L43), foi implementado o seguinte exception handler:
```python
@application.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    if isinstance(exc, (HTTPException, RequestValidationError)):
        raise exc
    logger.error("Internal server error: %s", type(exc).__name__)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )
```
1. Por que uma API em produção nunca deve devolver mensagens de erro internas cruas (como detalhes de conexão do PostgreSQL, query SQL com falha ou stack traces) na resposta HTTP?  
*Para proteger a aplicação contra vazamento de informações sensíveis (como nomes de tabelas, estrutura de banco, versões de software ou detalhes de conexão) que poderiam ser usadas por invasores em ataques direcionados, além de garantir uma boa experiência ao usuário (UX).*
2. Como o código acima garante essa proteção sem mascarar erros legítimos de validação do FastAPI (`RequestValidationError`)?  
*O handler usa uma verificação explícita (if isinstance(exc, (HTTPException, RequestValidationError)): raise exc), permitindo que erros controlados da API e falhas de validação do Pydantic passem intactos, capturando apenas exceções genéricas de sistema.*

---

### Questão 10 (Estratégia de Testes Automatizados com Fixtures e Mocks)
No arquivo [tests/conftest.py](/home/mjos/Developer/Projetos/instrava-api/tests/conftest.py) e [tests/test_auth_register.py](/home/mjos/Developer/Projetos/instrava-api/tests/test_auth_register.py):
1. Por que usamos `app.dependency_overrides[get_db]` com SQLite em memória (`aiosqlite` + `StaticPool`) nos testes em vez de apontar para o banco de dados PostgreSQL real?  
*O SQLite em memória (aiosqlite + StaticPool) garante isolamento completo e extrema velocidade nos testes, eliminando a necessidade de subir e limpar um servidor PostgreSQL real a cada execução de teste.*
2. No teste de condição de corrida (`test_race_condition_integrity_error_mapped_to_409`), usamos `unittest.mock.patch` para simular uma `IntegrityError` lançada pelo `UserRepository.create`. Por que o uso de mock é útil e recomendado nesse caso específico?  
*O uso de unittest.mock.patch permite simular um erro de integridade do banco de forma determinística e controlada, sem precisar armar cenários complexos de concorrência real na thread de teste.*

---

## Gabarito e Respostas Comentadas

### Resposta 1
1. **Algoritmos rápidos (MD5, SHA-1, SHA-256):** Foram projetados para verificar integridade e calcular somas de verificação rapidamente (processando gigabytes por segundo). Se um atacante obtiver uma base com hashes SHA-256 de senhas, ele pode testar bilhões de combinações por segundo usando ataques de dicionário ou tabelas arco-íris, quebrando senhas fracas ou moderadas quase instantaneamente.
2. **Memory-hardness do Argon2id:** Funções *memory-hard* exigem uma quantidade configurável e substancial de memória RAM dedicada para computar cada hash. Placas de vídeo (GPUs) e chips especializados (ASICs) possuem milhares de núcleos de processamento rápidos, mas pouca memória dedicada por núcleo. Ao exigir muita memória para cada cálculo, o Argon2id inviabiliza financeiramente e tecnicamente ataques massivos em paralelo, sendo o padrão ouro moderno (vencedor do *Password Hashing Competition*). A variante `id` é híbrida, resistindo tanto a ataques de canal lateral quanto a ataques de compromisso tempo-memória.

### Resposta 2
1. **Problemas de colocar tudo no router:**
   - **Alto acoplamento:** O código HTTP fica misturado com lógica de persistência e regras de negócio.
   - **Dificuldade de manutenção e teste:** Para testar a lógica (ex: normalização, hash, tratamento de concorrência), seria obrigatório subir requisições HTTP completas; não haveria como testar a regra de negócio em isolamento com testes de unidade puros.
   - **Impossibilidade de reuso:** Se amanhã um comando CLI, uma fila assíncrona (Celery, Kafka) ou uma rotina batch precisar cadastrar um usuário, a lógica teria que ser duplicada, já que estava presa a um endpoint HTTP.
2. **Vantagens de isolar Service e Repository:**
   - **Separação de Preocupações (SoC):** O repositório cuida exclusivamente de como falar com o banco de dados (dialeto SQL, queries, mapeamento ORM). O serviço cuida das regras de negócio e orquestração. O router cuida do protocolo web (rotas, serialização, status HTTP).
   - **Testabilidade:** Podemos criar mocks do repositório para testar todas as ramificações do serviço sem depender de um banco de dados ligado.

### Resposta 3
- **Motivo:** Ocorre o fenômeno clássico conhecido como **Time-of-Check to Time-of-Wait / Race Condition** (concorrência entre leitura e escrita).
- **Cenário Real:**
  1. Suponha que duas requisições de cadastro com o mesmo e-mail `joao@example.com` cheguem ao servidor quase no mesmo milissegundo (duplo clique no botão de cadastrar ou duas instâncias em paralelo).
  2. A **Requisição A** executa `get_by_email` e o banco responde "não existe".
  3. No mesmo instante, a **Requisição B** executa `get_by_email` e o banco também responde "não existe".
  4. Ambas as requisições prosseguem com o hash e tentam executar `INSERT`.
  5. A requisição A é gravada primeiro com sucesso.
  6. Quando a requisição B tentar gravar, o banco de dados rejeitará com erro de restrição de unicidade (`IntegrityError` decorrente do índice único em `email`).
- Se não capturássemos o `IntegrityError`, a requisição B falharia com erro `500 Internal Server Error`. Capturando o erro e lançando `EmailAlreadyRegisteredError`, garantimos que o cliente receba corretamente o status `409 Conflict`. A restrição única no banco é a **última e infalível barreira de integridade**.

### Resposta 4
1. **Motivo da normalização:** Na especificação de e-mails (RFC 5321), a parte do domínio é estritamente *case-insensitive* e, na prática, quase todos os provedores tratam a caixa alta e baixa de forma idêntica (`Usuario@gmail.com` e `usuario@gmail.com` pertencem à mesma caixa de entrada). Espaços em branco nas extremidades (`strip`) ocorrem comumente por copiar/colar em formulários móveis.
2. **Consequências de não normalizar:**
   - Um usuário poderia criar uma conta com `maria@site.com` e outro usuário registrar `Maria@site.com`. Ambos disputariam a mesma identidade conceitual, gerando problemas de segurança (usurpação de conta, confusão de entrega de mensagens).
   - O próprio usuário poderia esquecer se digitou a primeira letra maiúscula no cadastro e depois não conseguir logar ou receber mensagens de erro confusas.

### Resposta 5
- **Por que não usar `HTTPException` no Service:**
  A camada de domínio e aplicação (Service) não deve conhecer detalhes de transporte (HTTP, gRPC, WebSocket, CLI). Se usarmos `HTTPException` no service, tornamos a regra de negócio dependente do protocolo HTTP e do framework FastAPI. Se a aplicação um dia for executada a partir de uma fila RabbitMQ ou CLI, códigos de status HTTP como 409 perdem o sentido.
- **Onde é feita a conversão:**
  No ponto de entrada da aplicação web, no arquivo [main.py](/home/mjos/Developer/Projetos/instrava-api/src/instrava_api/main.py#L23-L30), através de um **Custom Exception Handler**:
  ```python
  @application.exception_handler(EmailAlreadyRegisteredError)
  async def email_already_registered_handler(request: Request, exc: EmailAlreadyRegisteredError):
      return JSONResponse(status_code=409, content={"detail": {"code": exc.code, "message": exc.message}})
  ```
  Isso mantém o Service 100% puro e a camada Web responsável pela tradução para HTTP.

### Resposta 6
1. **Prevenção de vazamento:**
   - [UserRegister](/home/mjos/Developer/Projetos/instrava-api/src/instrava_api/schemas/user.py#L6) aceita `password`, mas é utilizado estritamente como modelo de entrada (Request Body).
   - [UserPublic](/home/mjos/Developer/Projetos/instrava-api/src/instrava_api/schemas/user.py#L29) define apenas os campos autorizados para leitura externa (`id`, `name`, `email`, `created_at`). Os atributos `password` e `password_hash` sequer existem na declaração do schema de saída.
   - No router, a rota é decorada com `response_model=UserPublic`, garantindo que o FastAPI filtre e serialize unicamente os campos permitidos.
2. **Papel de `from_attributes=True`:**
   Permite que o Pydantic leia os dados diretamente dos atributos de instâncias de classes do SQLAlchemy (`user.id`, `user.name`, etc.) em vez de exigir dicionários Python. Isso torna possível fazer `UserPublic.model_validate(user)` diretamente a partir do objeto retornado pelo ORM.

### Resposta 7
1. **Ciclo de vida gerenciado pelo FastAPI:**
   Quando a requisição HTTP chega, o FastAPI entra no bloco `async with async_session_maker()` através do `get_db`. A sessão é aberta e entregue à rota pelo `yield`. A rota e os serviços executam suas operações usando essa sessão única. Ao terminar a requisição (seja com sucesso ou com erro), o FastAPI retoma a execução após o `yield`, onde o context manager assíncrono do SQLAlchemy garante o fechamento (`session.close()`), devolvendo a conexão para o pool.
2. **Em caso de exceção:**
   O context manager da sessão desfaz automaticamente qualquer alteração pendente (executando rollback na transação não commitada) e fecha a sessão, evitando vazamento de conexões (*connection leaks*) ou transações órfãs travando tabelas.

### Resposta 8
1. **Diferença entre `flush()` e `commit()`:**
   - **`flush()`:** Envia os comandos SQL gerados (ex: `INSERT INTO users ...`) para o banco de dados dentro da transação atual. O banco gera os identificadores automáticos (como a chave primária `id`), valida restrições imediatas e atualiza o estado em memória dos objetos, mas **a transação continua aberta** e as mudanças não estão visíveis para outras sessões do banco.
   - **`commit()`:** Efetiva permanentemente a transação no banco de dados (*durability* do ACID), tornando as modificações visíveis para o restante do sistema e liberando eventuais *locks* de linhas/tabelas.
2. **Por que o commit fica no Service:**
   O Service representa a fronteira do caso de uso (unidade de trabalho / *Unit of Work*). Uma regra de negócio pode precisar cadastrar um usuário, criar um log de auditoria e registrar uma preferência padrão. Se o repositório fizesse `commit()` a cada inserção, não seria possível dar rollback no usuário caso o passo seguinte falhasse. Quem orquestra quando uma transação de negócio terminou com êxito é o Serviço.

### Resposta 9
1. **Risco de expor erros cruas:**
   Mensagens de erro não tratadas frequentemente revelam nomes de tabelas, estruturas de colunas, nomes de usuários do banco, IPs de servidores internos, senhas de connection string ou versões de bibliotecas. Essas informações são valiosas para agentes mal-intencionados realizarem reconhecimento e exploração de vulnerabilidades (*Information Disclosure* / CWE-209).
2. **Proteção sem mascarar validações:**
   O handler intercepta `Exception` genérica, mas verifica primeiro:
   ```python
   if isinstance(exc, (HTTPException, RequestValidationError)):
       raise exc
   ```
   Dessa forma, erros legítimos do FastAPI (como erro 422 de dados inválidos ou erros 4xx disparados explicitamente) continuam sendo tratados pelos handlers nativos do FastAPI, enquanto exceções inesperadas (como falhas de I/O ou bugs de código) geram log de erro no servidor e devolvem apenas `{"detail": "Internal server error"}` com status 500 para o cliente.

### Resposta 10
1. **Vantagens do `dependency_overrides` com SQLite em memória:**
   - **Velocidade:** Testes rodam em fração de segundo na memória RAM (centenas de milissegundos), sem latência de rede ou disco.
   - **Isolamento e Reprodutibilidade:** O banco é criado (`create_all`) e destruído (`drop_all`) a cada teste ou suíte, garantindo que nenhum teste sofra efeito colateral de dados deixados por testes anteriores.
   - **Independência de Infraestrutura:** Qualquer desenvolvedor ou pipeline de CI/CD consegue executar `pytest` sem precisar subir previamente um container Docker do PostgreSQL.
2. **Uso de mock para simular race condition:**
   Reproduzir uma condição de corrida no banco de dados real em um teste automatizado exigiria disparar múltiplas threads ou tasks assíncronas concorrentes de forma sincronizada no nível de milissegundos, tornando o teste frágil (*flaky*), lento e imprevisível. Com `patch("instrava_api.repositories.user_repository.UserRepository.create", side_effect=IntegrityError(...))`, forçamos de maneira determinística e instantânea o exato comportamento de erro de banco, comprovando que a aplicação trata o erro e devolve o status `409 Conflict` esperado.

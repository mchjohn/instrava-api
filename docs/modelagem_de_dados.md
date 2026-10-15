# Modelo Conceitual

## Entidades

- Usuário
- Atividades
- ArquivoCSV

### Relacionamentos

- Um Usuário tem muitas Atividades
- Uma Atividade pertence a um Usuário


# Modelo Lógico

## Tabelas

```usuarios (id, name, email, password, created_at)```
```
atividades (
    id,                      -- Identificador único interno (UUID ou Auto-incremento)
    usuario_id,              -- Chave estrangeira ligando ao usuário dono da atividade
    external_activity_id,    -- ID original da atividade no Strava / CSV (evita duplicatas)
    name,                    -- Nome da atividade (ex: "Corrida matinal", "Pedalada matinal")
    sport_type,              -- Tipo de esporte: restrito a "Pedalada" ou "Corrida"
    description,             -- Descrição opcional da atividade
    start_date,              -- Data e hora de início da atividade
    distance,                -- Distância percorrida (em metros)
    moving_time,             -- Tempo em movimento (em segundos)
    elapsed_time,            -- Tempo total decorrido (em segundos)
    average_speed,           -- Velocidade média (m/s ou km/h conforme conversão)
    max_speed,               -- Velocidade máxima
    elevation_gain,          -- Ganho de elevação acumulado (subida)
    elevation_loss,          -- Perda de elevação acumulada (descida)
    average_heartrate,       -- Frequência cardíaca média (bpm)
    max_heartrate,           -- Frequência cardíaca máxima (bpm)
    average_watts,           -- Potência média (aplicável principalmente a Bike com medidor)
    calories,                -- Total de calorias gastas
    relative_effort,         -- Esforço relativo (Suffer Score do Strava)
    gear                     -- Equipamento ou bicicleta utilizada (ex: "Laranja Mecânica 🍊", "Fila Maxximus")
)
```


# ERD (Entity-Relationship Diagram)

- Ver [dbdiagram_erd.dbml](docs/dbdiagram_erd.dbml)

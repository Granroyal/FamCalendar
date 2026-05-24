# Smart Kalender App med AI-assistent

Eksamen i Introduktion til Python.

## Beskrivelse af programmet

Programmet er en webbaseret kalenderapplikation, hvor brugeren kan oprette, se, redigere og slette aftaler.
Brugeren får et simpelt overblik over sine aftaler i en kalender og kan også se aftalerne som en
Pandas dataframe.

Derudover indeholder programmet en AI-assistent, hvor brugeren kan skrive en aftale med almindeligt
sprog, fx "Tilføj tandlæge på fredag kl. 10". Backend'en bruger OpenAI til at fortolke beskeden og
udtrække dato, tidspunkt, aftaletekst og kategori. Derefter bliver aftalen gemt i kalenderen.

Programmet analyserer også aftalerne med NumPy og viser simple mønstre, fx hvilke tidspunkter,
datoer og ugedage der bruges mest. Der er også Matplotlib-diagrammer, som viser antal aftaler pr.
ugedag og måned.

## Applikationens teknologier

Programmet bruger:

1. Streamlit til frontend.
2. FastAPI til backend.
3. NumPy, Pandas og Matplotlib til data og visning.
4. OpenAI API til AI-assistenten.
5. Pytest til unit tests.
6. JSON-fil til at gemme aftaler lokalt.

## OpenAI API

AI-assistenten bruger OpenAI Responses API fra backend'en. API-nøglen skal ligge i en lokal `.env`-fil,
så den ikke bliver gemt i Git.

Opret en fil der hedder `.env` i projektets rodmappe, samme sted som `README.md`, og skriv:

```env
OPENAI_API_KEY=din-api-noegle
FAMCALENDAR_OPENAI_MODEL=gpt-5.4-nano
```

Der ligger også en `.env.example`, som viser formatet.

## Start programmet med Docker Compose

Hele applikationen køres samlet med Docker Compose. Sørg først for at `.env` findes i
projektets rodmappe:

```env
OPENAI_API_KEY=din-api-noegle
FAMCALENDAR_OPENAI_MODEL=gpt-5.4-nano
```

Start derefter både backend og frontend med:

```bash
make up
```

Det svarer til:

```bash
docker compose up --build
```

Frontend kan åbnes på:

```text
http://localhost:8501
```

Backend kører på:

```text
http://localhost:8000
```

Docker Compose gemmer aftaler i en Docker-volume, så `appointments.json` bevares mellem genstarter.
Stop services igen med:

```bash
make down
```

Eksempel på besked i AI-assistenten:

```text
Tilføj tandlæge på fredag kl. 10
```

## Kvalitetssikring

Projektet bruger pytest til tests, mypy til type checks og ruff til code analysis.

Kør dem lokalt med uv:

```bash
PYTHONPATH=. uv run --with pytest pytest
uv run --with mypy mypy FamCalender tests
uv run --with ruff ruff check .
```

# Smart Kalender App med AI-assistent

Eksamen i Introduktion til Python.

## Beskrivelse af programmet

Programmet er en webbaseret kalenderapplikation, hvor brugeren kan oprette, se og slette aftaler.
Brugeren får et simpelt overblik over sine aftaler i en kalender og kan også se aftalerne som en
Pandas dataframe.

Derudover indeholder programmet en AI-assistent, hvor brugeren kan skrive en aftale med almindeligt
sprog, fx "Tilføj tandlæge på fredag kl. 10". Backend'en bruger OpenAI til at fortolke beskeden og
udtrække dato, tidspunkt, aftaletekst og kategori. Derefter bliver aftalen gemt i kalenderen.

Programmet analyserer også aftalerne med NumPy og viser simple mønstre, fx hvilke tidspunkter,
datoer og ugedage der bruges mest. Der er også et Matplotlib-diagram, som viser antal aftaler pr.
måned.

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

## Start programmet

Det nemmeste er at bruge `make`:

```bash
make backend
make frontend
```

`make backend` starter backend'en, og `make frontend` starter Streamlit i en ny terminal.

Hvis du hellere vil køre kommandoerne direkte, kan du også bruge:

```bash
uv run uvicorn FamCalender.backend.main:app --reload --port 8000
uv run streamlit run FamCalender/frontend/streamlit.py
```

Eksempel på besked i AI-assistenten:

```text
Tilføj tandlæge på fredag kl. 10
```

## Tests

Testene kan køres med:

```bash
make test
```

## Mangler eller kan tilføjes

- Redigering af eksisterende aftaler er ikke lavet endnu.
- Docker Compose er ikke tilføjet endnu.
- Type checks og code analysis kan tilføjes senere.
- Kalenderen bruger året 2026.

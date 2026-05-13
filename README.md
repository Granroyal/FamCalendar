# Smart Kalender App med AI-assistent
Eksamen i Introduktion til Python

## Beskrivelse af programmet
Programmet er en webbaseret kalenderapplikation, hvor brugeren kan oprette, redigere og slette aftaler.
Brugeren får et simpelt overblik over sine aftaler og kan se dem organiseret efter dato.
Derudover indeholder programmet en AI-assistent, hvor brugeren kan skrive beskeder i naturligt
sprog, fx: “Lav en aftale på fredag kl. 10”. Systemet bruger en LLM API til at fortolke brugerens
tekstinput og udtrække relevant information såsom dato, tidspunkt og beskrivelse, som derefter bruges
til at oprette en aftale i kalenderen.
Programmet analyserer også brugerens data og viser, hvilke ugedage der oftest er aftaler. Formålet
er at gøre planlægning nemmere og skabe bedre overblik i hverdagen.


## Applikationens format
Din applikation skal gøre brug af følgende teknologier:

1. Streamlit
2. Flask eller FastAPI
3. Numpy, Pandas og Matplotlib
4. Interaktion med en LLM´s API (feks. Mistral).    
5. Unitests, type checks, code analisys.
6. Din applikation skal desuden kunne køres ved hjælp af Docker Compose `docker compose up`, `docker compose down`.
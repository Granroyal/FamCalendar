import json
import os
from datetime import date
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import numpy as np
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field, ValidationError


# Laeser variabler fra .env, saa API-noeglen ikke skal ligge direkte i koden.
load_dotenv()

DATA_FILE = Path(__file__).with_name("appointments.json")
OPENAI_RESPONSES_URL = "https://api.openai.com/v1/responses"
OPENAI_MODEL = os.environ.get("FAMCALENDAR_OPENAI_MODEL", "gpt-5.4-nano")
CATEGORIES = ["Familie", "Skole", "Sundhed", "Hverdag", "Fritid"]
WEEKDAYS_DA = [
    "Mandag",
    "Tirsdag",
    "Onsdag",
    "Torsdag",
    "Fredag",
    "Loerdag",
    "Soendag",
]

app = FastAPI(title="FamCalendar API")


# Pydantic-modellerne validerer data, foer de bliver brugt eller gemt.
class AppointmentCreate(BaseModel):
    dato: date
    tid: str = Field(min_length=5, max_length=5, pattern=r"^\d{2}:\d{2}$")
    aftale: str = Field(min_length=1, max_length=100)
    kategori: str = Field(min_length=1, max_length=50)


class Appointment(AppointmentCreate):
    id: int


class LLMAppointmentRequest(BaseModel):
    besked: str = Field(min_length=3, max_length=500)


# Bruges til et enkelt analyseresultat, fx "Mandag: 3 aftaler".
class CountResult(BaseModel):
    label: str
    count: int


# Samler alle NumPy-resultaterne i et fast response-format til frontend'en.
class NumpyAnalytics(BaseModel):
    total_appointments: int
    most_used_times: list[CountResult]
    busiest_dates: list[CountResult]
    most_active_weekdays: list[CountResult]
    most_active_hours: list[CountResult]


def read_appointments() -> list[Appointment]:
    # JSON-filen fungerer som et simpelt lokalt lager i stedet for en database.
    if not DATA_FILE.exists():
        return []

    with DATA_FILE.open("r", encoding="utf-8") as file:
        data = json.load(file)

    return [Appointment.model_validate(item) for item in data]


def write_appointments(appointments: list[Appointment]) -> None:
    # mode="json" laver date-objekter om til tekst, saa de kan gemmes i JSON.
    data = [
        appointment.model_dump(mode="json")
        for appointment in appointments
    ]

    with DATA_FILE.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=True)


def count_max_values(labels: np.ndarray) -> list[CountResult]:
    # Finder den eller de vaerdier, der forekommer flest gange i et NumPy-array.
    if labels.size == 0:
        return []

    # np.unique taeller hvor mange gange hvert tidspunkt, dato eller ugedag findes.
    unique_labels, counts = np.unique(labels, return_counts=True)
    max_count = int(np.max(counts))
    winners = unique_labels[counts == max_count]

    return [
        CountResult(label=str(label), count=max_count)
        for label in sorted(winners.tolist())
    ]


def analyze_appointments_with_numpy(
    appointments: list[Appointment],
) -> NumpyAnalytics:
    # Returnerer tomme lister, hvis der endnu ikke er aftaler at analysere.
    if not appointments:
        return NumpyAnalytics(
            total_appointments=0,
            most_used_times=[],
            busiest_dates=[],
            most_active_weekdays=[],
            most_active_hours=[],
        )

    # Laver aftalernes felter om til NumPy-arrays, saa de kan analyseres samlet.
    times = np.array([appointment.tid for appointment in appointments])
    dates = np.array([appointment.dato.isoformat() for appointment in appointments])
    weekday_indexes = np.array(
        [appointment.dato.weekday() for appointment in appointments]
    )
    weekdays = np.array([WEEKDAYS_DA[index] for index in weekday_indexes])
    # Grupperer tider i hele timer, saa vi kan se hvor brugeren er mest aktiv.
    hours = np.array(
        [
            f"{int(appointment.tid[:2]):02d}:00-{int(appointment.tid[:2]):02d}:59"
            for appointment in appointments
        ]
    )

    # Hver kategori sendes gennem samme taellefunktion og pakkes som JSON-svar.
    return NumpyAnalytics(
        total_appointments=len(appointments),
        most_used_times=count_max_values(times),
        busiest_dates=count_max_values(dates),
        most_active_weekdays=count_max_values(weekdays),
        most_active_hours=count_max_values(hours),
    )


def extract_openai_text(response_data: dict) -> str:
    # OpenAI kan returnere teksten i output_text eller i output-listen.
    output_text = response_data.get("output_text")
    if isinstance(output_text, str) and output_text.strip():
        return output_text

    for output_item in response_data.get("output", []):
        for content_item in output_item.get("content", []):
            text = content_item.get("text")
            if isinstance(text, str) and text.strip():
                return text

    raise HTTPException(
        status_code=status.HTTP_502_BAD_GATEWAY,
        detail="OpenAI svarede ikke med tekst",
    )


def parse_appointment_with_llm(message: str) -> AppointmentCreate:
    # Henter API-noeglen fra .env eller terminalens miljoevariabler.
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="OPENAI_API_KEY mangler i backend-miljoeet",
        )

    today = date.today().isoformat()

    # JSON-schemaet tvinger OpenAI til at svare med de felter kalenderen skal bruge.
    schema = {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "dato": {
                "type": "string",
                "description": "Dato i ISO-format YYYY-MM-DD.",
            },
            "tid": {
                "type": "string",
                "description": "Tidspunkt i 24-timers format HH:MM.",
                "pattern": "^\\d{2}:\\d{2}$",
            },
            "aftale": {
                "type": "string",
                "description": "Kort titel paa aftalen.",
            },
            "kategori": {
                "type": "string",
                "enum": CATEGORIES,
            },
        },
        "required": ["dato", "tid", "aftale", "kategori"],
    }
    payload = {
        "model": OPENAI_MODEL,
        # Instructions forklarer modellen dens rolle og hvordan relative datoer skal tolkes.
        "instructions": (
            "Du er en dansk kalenderassistent. Udtraek en kalenderaftale fra "
            "brugerens besked. Brug dagens dato til relative datoer. Hvis "
            "brugeren ikke skriver en kategori, vaelg den mest passende kategori."
        ),
        "input": (
            f"I dag er {today}. Mulige kategorier er: {', '.join(CATEGORIES)}.\n"
            f"Brugerens besked: {message}"
        ),
        "text": {
            "format": {
                "type": "json_schema",
                "name": "calendar_appointment",
                "strict": True,
                "schema": schema,
            }
        },
    }
    request = Request(
        OPENAI_RESPONSES_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            # Bearer-token er den maade OpenAI API'et modtager API-noeglen paa.
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        # Sender beskeden til OpenAI og laeser svaret som JSON.
        with urlopen(request, timeout=15) as response:
            response_data = json.load(response)
    except HTTPError as error:
        try:
            error_data = json.load(error)
            detail = error_data.get("error", {}).get("message", str(error))
        except json.JSONDecodeError:
            detail = str(error)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"OpenAI-fejl: {detail}",
        ) from error
    except URLError as error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Kunne ikke kontakte OpenAI: {error.reason}",
        ) from error

    try:
        # OpenAI-teksten er selv JSON, saa den parses til en Python-dict.
        parsed_data = json.loads(extract_openai_text(response_data))
    except json.JSONDecodeError as error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="OpenAI svarede ikke med gyldig JSON",
        ) from error

    try:
        # Validerer at AI-svaret passer til AppointmentCreate, foer aftalen gemmes.
        return AppointmentCreate.model_validate(parsed_data)
    except ValidationError as error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="OpenAI svarede med aftaledata i et ugyldigt format",
        ) from error


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "FamCalendar backend koerer"}


@app.get("/appointments", response_model=list[Appointment])
def get_appointments() -> list[Appointment]:
    # Returnerer hele listen, som frontend'en bruger til kalender og dataframe.
    return read_appointments()


@app.get("/appointments/{appointment_date}", response_model=list[Appointment])
def get_appointments_by_date(appointment_date: date) -> list[Appointment]:
    appointments = read_appointments()
    return [
        appointment
        for appointment in appointments
        if appointment.dato == appointment_date
    ]


@app.get("/analytics/numpy", response_model=NumpyAnalytics)
def get_numpy_analytics() -> NumpyAnalytics:
    # Endpointet bruges af frontend'en til at hente de beregnede kalender-moenstre.
    appointments = read_appointments()
    return analyze_appointments_with_numpy(appointments)


@app.post(
    "/appointments",
    response_model=Appointment,
    status_code=status.HTTP_201_CREATED,
)
def create_appointment(new_appointment: AppointmentCreate) -> Appointment:
    appointments = read_appointments()
    # ID'et beregnes ud fra eksisterende aftaler, saa det bliver unikt efter sletning.
    next_id = max((appointment.id for appointment in appointments), default=0) + 1

    appointment = Appointment(id=next_id, **new_appointment.model_dump())
    appointments.append(appointment)
    write_appointments(appointments)

    return appointment


@app.post(
    "/llm/appointments",
    response_model=Appointment,
    status_code=status.HTTP_201_CREATED,
)
def create_appointment_from_llm(request: LLMAppointmentRequest) -> Appointment:
    # AI'en laver fri tekst om til samme struktur som en manuel oprettelse.
    new_appointment = parse_appointment_with_llm(request.besked)
    return create_appointment(new_appointment)


@app.delete("/appointments/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_appointment(appointment_id: int) -> None:
    appointments = read_appointments()
    # Beholder alle aftaler undtagen den, brugeren vil slette.
    remaining_appointments = [
        appointment
        for appointment in appointments
        if appointment.id != appointment_id
    ]

    if len(remaining_appointments) == len(appointments):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aftalen findes ikke",
        )

    write_appointments(remaining_appointments)

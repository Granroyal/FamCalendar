import json
from datetime import date
from pathlib import Path

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field


DATA_FILE = Path(__file__).with_name("appointments.json")

app = FastAPI(title="FamCalendar API")


class AppointmentCreate(BaseModel):
    dato: date
    tid: str = Field(min_length=5, max_length=5, pattern=r"^\d{2}:\d{2}$")
    aftale: str = Field(min_length=1, max_length=100)
    kategori: str = Field(min_length=1, max_length=50)


class Appointment(AppointmentCreate):
    id: int


def read_appointments() -> list[Appointment]:
    if not DATA_FILE.exists():
        return []

    with DATA_FILE.open("r", encoding="utf-8") as file:
        data = json.load(file)

    return [Appointment.model_validate(item) for item in data]


def write_appointments(appointments: list[Appointment]) -> None:
    data = [
        appointment.model_dump(mode="json")
        for appointment in appointments
    ]

    with DATA_FILE.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=True)


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "FamCalendar backend koerer"}


@app.get("/appointments", response_model=list[Appointment])
def get_appointments() -> list[Appointment]:
    return read_appointments()


@app.get("/appointments/{appointment_date}", response_model=list[Appointment])
def get_appointments_by_date(appointment_date: date) -> list[Appointment]:
    appointments = read_appointments()
    return [
        appointment
        for appointment in appointments
        if appointment.dato == appointment_date
    ]


@app.post(
    "/appointments",
    response_model=Appointment,
    status_code=status.HTTP_201_CREATED,
)
def create_appointment(new_appointment: AppointmentCreate) -> Appointment:
    appointments = read_appointments()
    next_id = max((appointment.id for appointment in appointments), default=0) + 1

    appointment = Appointment(id=next_id, **new_appointment.model_dump())
    appointments.append(appointment)
    write_appointments(appointments)

    return appointment


@app.delete("/appointments/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_appointment(appointment_id: int) -> None:
    appointments = read_appointments()
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

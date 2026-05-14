from datetime import date
import json

from FamCalender.backend import main


def test_read_appointments_reads_json(tmp_path, monkeypatch):
    data_file = tmp_path / "appointments.json"
    data_file.write_text(
        json.dumps(
            [
                {
                    "id": 1,
                    "dato": "2026-01-05",
                    "tid": "10:00",
                    "aftale": "Tandlaege",
                    "kategori": "Sundhed",
                }
            ]
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(main, "DATA_FILE", data_file)

    appointments = main.read_appointments()

    assert len(appointments) == 1
    assert appointments[0].aftale == "Tandlaege"


def test_create_and_delete_appointment(tmp_path, monkeypatch):
    data_file = tmp_path / "appointments.json"
    data_file.write_text("[]", encoding="utf-8")
    monkeypatch.setattr(main, "DATA_FILE", data_file)

    created = main.create_appointment(
        main.AppointmentCreate(
            dato=date(2026, 7, 13),
            tid="12:00",
            aftale="Foedselsdag",
            kategori="Familie",
        )
    )

    assert created.id == 1
    assert main.read_appointments()[0].aftale == "Foedselsdag"

    main.delete_appointment(created.id)

    assert main.read_appointments() == []


def test_create_appointment_from_llm_saves_parsed_appointment(tmp_path, monkeypatch):
    data_file = tmp_path / "appointments.json"
    data_file.write_text("[]", encoding="utf-8")
    monkeypatch.setattr(main, "DATA_FILE", data_file)
    monkeypatch.setattr(
        main,
        "parse_appointment_with_llm",
        lambda message: main.AppointmentCreate(
            dato=date(2026, 5, 22),
            tid="10:00",
            aftale=message,
            kategori="Sundhed",
        ),
    )

    created = main.create_appointment_from_llm(
        main.LLMAppointmentRequest(besked="Tandlaege paa fredag kl. 10")
    )

    assert created.id == 1
    assert created.aftale == "Tandlaege paa fredag kl. 10"
    assert main.read_appointments()[0].kategori == "Sundhed"


def test_analyze_appointments_with_numpy_finds_patterns():
    appointments = [
        main.Appointment(
            id=1,
            dato=date(2026, 5, 18),
            tid="10:00",
            aftale="Skole",
            kategori="Skole",
        ),
        main.Appointment(
            id=2,
            dato=date(2026, 5, 18),
            tid="10:00",
            aftale="Tandlaege",
            kategori="Sundhed",
        ),
        main.Appointment(
            id=3,
            dato=date(2026, 5, 19),
            tid="15:30",
            aftale="Sport",
            kategori="Fritid",
        ),
    ]

    analysis = main.analyze_appointments_with_numpy(appointments)

    assert analysis.total_appointments == 3
    assert analysis.most_used_times == [main.CountResult(label="10:00", count=2)]
    assert analysis.busiest_dates == [
        main.CountResult(label="2026-05-18", count=2)
    ]
    assert analysis.most_active_weekdays == [
        main.CountResult(label="Mandag", count=2)
    ]
    assert analysis.most_active_hours == [
        main.CountResult(label="10:00-10:59", count=2)
    ]

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

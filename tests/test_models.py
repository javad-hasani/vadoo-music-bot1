from app.models import Track


def test_duration_text() -> None:
    assert Track("x", "u", "s", 65, "r").duration_text == "01:05"
    assert Track("x", "u", "s", 3661, "r").duration_text == "01:01:01"

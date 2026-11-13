from timeutil import to_ist


def add_log(conn, timestamp):
    conn.execute(
        "INSERT INTO activity_logs (event, timestamp) VALUES (?, ?)",
        ("Test event", timestamp),
    )
    conn.commit()


def test_converts_utc_to_india_time():
    assert to_ist("2026-11-08 15:35:51") == "2026-11-08 21:05:51"


def test_time_after_midnight_moves_to_next_day():
    assert to_ist("2026-11-08 20:00:00") == "2026-11-09 01:30:00"


def test_empty_values_give_empty_text():
    assert to_ist("") == ""
    assert to_ist(None) == ""


def test_text_that_is_not_a_date_is_unchanged():
    assert to_ist("not a date") == "not a date"


def test_logs_page_shows_india_time(logged_in_client, conn):
    add_log(conn, "2026-11-08 15:35:51")
    response = logged_in_client.get("/logs")
    assert b"2026-11-08 21:05:51" in response.data
    assert b"15:35:51" not in response.data


def test_dashboard_shows_india_time(logged_in_client, conn):
    add_log(conn, "2026-11-08 15:35:51")
    response = logged_in_client.get("/dashboard")
    assert b"2026-11-08 21:05:51" in response.data
    assert b"15:35:51" not in response.data


# end of test_time.py
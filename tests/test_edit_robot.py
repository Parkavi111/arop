def get_robot(conn, robot_id):
    return conn.execute("SELECT * FROM robots WHERE id = ?", (robot_id,)).fetchone()


def test_rename_page_opens(logged_in_client, make_robot):
    robot_id = make_robot(name="Alpha")
    response = logged_in_client.get(f"/robots/{robot_id}/edit")
    assert response.status_code == 200
    assert b"Alpha" in response.data


def test_rename_changes_only_the_name(logged_in_client, conn, make_robot):
    robot_id = make_robot(name="Alpha", status="idle", battery=80)
    logged_in_client.post(f"/robots/{robot_id}/edit", data={"name": "Beta"})
    robot = get_robot(conn, robot_id)
    assert robot["name"] == "Beta"
    assert robot["battery"] == 80
    assert robot["status"] == "idle"


def test_rename_removes_extra_spaces(logged_in_client, conn, make_robot):
    robot_id = make_robot(name="Alpha")
    logged_in_client.post(f"/robots/{robot_id}/edit", data={"name": "  Gamma  "})
    assert get_robot(conn, robot_id)["name"] == "Gamma"


def test_rename_cuts_long_name_to_50(logged_in_client, conn, make_robot):
    robot_id = make_robot(name="Alpha")
    logged_in_client.post(f"/robots/{robot_id}/edit", data={"name": "x" * 60})
    assert len(get_robot(conn, robot_id)["name"]) == 50


def test_empty_name_is_not_saved(logged_in_client, conn, make_robot):
    robot_id = make_robot(name="Alpha")
    logged_in_client.post(f"/robots/{robot_id}/edit", data={"name": "   "})
    assert get_robot(conn, robot_id)["name"] == "Alpha"


def test_busy_robot_can_be_renamed(logged_in_client, conn, make_robot):
    robot_id = make_robot(name="Alpha", status="busy")
    logged_in_client.post(f"/robots/{robot_id}/edit", data={"name": "Beta"})
    robot = get_robot(conn, robot_id)
    assert robot["name"] == "Beta"
    assert robot["status"] == "busy"


def test_unknown_robot_goes_back_to_list(logged_in_client):
    response = logged_in_client.get("/robots/99999/edit")
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/robots")


def test_rename_requires_login(client, conn, make_robot):
    robot_id = make_robot(name="Locked")
    page = client.get(f"/robots/{robot_id}/edit")
    assert page.status_code == 302
    assert page.headers["Location"].endswith("/login")
    client.post(f"/robots/{robot_id}/edit", data={"name": "Hacked"})
    assert get_robot(conn, robot_id)["name"] == "Locked"


# end of test_edit_robot.py
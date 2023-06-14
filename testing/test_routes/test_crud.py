from settings import config

from fastapi import status


def test_create_task_for_user(client, token_headers):
    data = {"task": config.settings.TEST_TASK, "description": config.settings.TEST_DESC}
    response = client.post("/user/task", json=data, headers=token_headers)
    assert response.status_code == status.HTTP_201_CREATED
    new_data = response.json()
    assert new_data["task"] == config.settings.TEST_TASK
    assert new_data["description"] == config.settings.TEST_DESC


def test_get_user_task_by_id(client, token_headers):
    data = {"task": config.settings.TEST_TASK, "description": config.settings.TEST_DESC}
    response = client.post("/user/task/", json=data, headers=token_headers)

    response = client.get("/user/task/1/", headers=token_headers)
    assert response.status_code == status.HTTP_200_OK
    new_data = response.json()
    assert new_data["task"] == config.settings.TEST_TASK


def test_get_user_tasks(client, token_headers):
    data = {"task": config.settings.TEST_TASK, "description": config.settings.TEST_DESC}
    client.post("/user/task/", json=data, headers=token_headers)
    client.post("/user/task/", json=data, headers=token_headers)

    response = client.get("/user/task", headers=token_headers)
    assert response.status_code == status.HTTP_200_OK
    new_data = response.json()
    assert new_data[0]
    assert new_data[1]


def test_update_task(client, token_headers):
    data = {"task": config.settings.TEST_TASK, "description": config.settings.TEST_DESC}

    client.post("/user/task/", json=data, headers=token_headers)
    data["task"] = "new test task"
    response = client.put("/user/task/1", json=data, headers=token_headers)
    assert response.status_code == status.HTTP_202_ACCEPTED
    new_data = response.json()
    assert new_data["task"] == "new test task"
    assert new_data["description"] == config.settings.TEST_DESC


def test_mark_as_complete(client, token_headers):
    data = {"task": config.settings.TEST_TASK, "description": config.settings.TEST_DESC}
    client.post("/user/task/", json=data, headers=token_headers)

    data["is_complete"] = True
    response = client.post("/user/task/1", json=data, headers=token_headers)
    assert response.status_code == status.HTTP_202_ACCEPTED
    new_data = response.json()
    assert new_data["is_complete"] == True


def test_delete_task(client, token_headers):
    data = {"task": config.settings.TEST_TASK, "description": config.settings.TEST_DESC}
    client.post("/user/task/", json=data, headers=token_headers)

    response = client.delete("/user/task/1", headers=token_headers)
    response = client.get("/user/task/1", headers=token_headers)
    assert response.status_code == 400

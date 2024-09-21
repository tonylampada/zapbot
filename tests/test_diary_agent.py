from datetime import datetime
from jarbas_agents import diary_agent
from jarbas_actions import diary_create
from database import dbsession
from random import random

def test_hello():
    user = f"test_user_{random()}"
    t = datetime.now().timestamp()
    with dbsession() as db:
        diary_create(user, "Pessoal", "Meu diario pessoal", db)
        diary_create(user, "Trabalho", "Meu diario de coisas do trabalho", db)
    messages_replied = diary_agent.chat(user, "Bom dia Jarbas.", t)
    assert len(messages_replied) == 3
    assert messages_replied[0]['tool_calls'][0]['function']['name'] == "diary_list"


def test_list_diaries():
    user = f"test_user_{random()}"
    t = datetime.now().timestamp()
    with dbsession() as db:
        diary_create(user, "Pessoal", "Meu diario pessoal", db)
        diary_create(user, "Trabalho", "Meu diario de coisas do trabalho", db)
    messages_replied = diary_agent.chat(user, "Quais os meus diarios?", t)
    assert len(messages_replied) == 3
    assert "Pessoal" in messages_replied[-1]["content"]
    assert "Trabalho" in messages_replied[-1]["content"]

def test_add_entry():
    user = f"test_user_{random()}"
    t = datetime.now().timestamp()
    with dbsession() as db:
        diary_create(user, "Pessoal", "Meu diario pessoal", db)
        diary_create(user, "Trabalho", "Meu diario de coisas do trabalho", db)
    messages_replied = diary_agent.chat(user, "Fala Jarbas! Bota aí no diário do trabalho: Comecei a campanha do adwords para estudantes", t)
    assert len(messages_replied) == 3
    assert messages_replied[0]['tool_calls'][0]['function']['name'] == "diary_entry_create"

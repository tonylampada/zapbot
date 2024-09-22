from sqlalchemy.orm import Session
from models import Diary, DiaryEntry
import subprocess

def diary_list(user_id: str, db: Session):
    """
    Retrieve all diaries for a given user.

    Args:
        user_id (str): The ID of the user.
        db (Session): The database session.

    Returns:
        list: A list of dictionaries containing diary information.
    """
    diaries = db.query(Diary).filter(Diary.user_id == user_id).all()
    return [{"id": diary.id, "name": diary.name, "description": diary.description} for diary in diaries]

from sqlalchemy.exc import SQLAlchemyError

def diary_create(user_id: str, name: str, description: str, db: Session):
    """
    Create a new diary for a user.

    Args:
        user_id (str): The ID of the user.
        name (str): The name of the diary.
        description (str): The description of the diary.
        db (Session): The database session.

    Returns:
        dict: A dictionary containing the newly created diary information.

    Raises:
        ValueError: If there's an error creating the diary.
    """
    try:
        new_diary = Diary(user_id=user_id, name=name, description=description)
        db.add(new_diary)
        db.commit()
        db.refresh(new_diary)
        return {"id": new_diary.id, "name": new_diary.name, "description": new_diary.description}
    except SQLAlchemyError as e:
        db.rollback()
        raise ValueError(f"Error creating diary: {str(e)}")

def diary_entry_list(user_id: str, diary_id: int, db: Session):
    """
    Retrieve diary entries for a user, optionally filtered by diary.

    Args:
        user_id (str): The ID of the user.
        diary_id (int): The ID of the diary to filter by (optional).
        db (Session): The database session.

    Returns:
        list: A list of dictionaries containing diary entry information.
    """
    query = db.query(DiaryEntry).join(Diary).filter(Diary.user_id == user_id)
    if diary_id:
        query = query.filter(DiaryEntry.diary_id == diary_id)
    entries = query.order_by(DiaryEntry.created_at.desc()).all()
    return [{"id": entry.id, "diary_id": entry.diary_id, "description": entry.description, "created_at": entry.created_at} for entry in entries]

def diary_entry_create(user_id: str, diary_id: int, description: str, db: Session):
    """
    Create a new diary entry for a user's diary.

    Args:
        user_id (str): The ID of the user.
        diary_id (int): The ID of the diary.
        description (str): The content of the diary entry.
        db (Session): The database session.

    Returns:
        dict: A dictionary containing the newly created diary entry information.

    Raises:
        ValueError: If the diary is not found or doesn't belong to the user.
    """
    diary = db.query(Diary).filter(Diary.id == diary_id, Diary.user_id == user_id).first()
    if not diary:
        raise ValueError("Diary not found or doesn't belong to the user")
    new_entry = DiaryEntry(diary_id=diary_id, description=description)
    db.add(new_entry)
    db.commit()
    db.refresh(new_entry)
    return {"id": new_entry.id, "diary_id": new_entry.diary_id, "description": new_entry.description, "created_at": new_entry.created_at}

def execute_command(command: str):
    """
    Execute a command in the terminal.

    Args:
        command (str): The command to execute.

    Returns:
        dict: A dictionary containing the command output and error (if any).
    """
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        return {
            "output": result.stdout,
            "error": result.stderr
        }
    except subprocess.CalledProcessError as e:
        return {
            "output": e.stdout,
            "error": e.stderr
        }

DIARY_LIST = {
    'name': 'diary_list',
    'description': 'Retrieve all diaries for a given user',
    'parameters': {
        'type': 'object',
        'properties': {},
        'required': [],
    },
}

DIARY_CREATE = {
    'name': 'diary_create',
    'description': 'Create a new diary for a user',
    'parameters': {
        'type': 'object',
        'properties': {
            'name': {
                'type': 'string',
                'description': 'The name of the diary',
            },
            'description': {
                'type': 'string',
                'description': 'The description of the diary',
            },
        },
        'required': ['name', 'description'],
    },
}

DIARY_ENTRY_LIST = {
    'name': 'diary_entry_list',
    'description': 'Retrieve diary entries for a user, optionally filtered by diary',
    'parameters': {
        'type': 'object',
        'properties': {
            'diary_id': {
                'type': 'integer',
                'description': 'The ID of the diary to filter by (optional)',
            },
        },
        'required': [],
    },
}

DIARY_ENTRY_CREATE = {
    'name': 'diary_entry_create',
    'description': 'Create a new diary entry for a user\'s diary',
    'parameters': {
        'type': 'object',
        'properties': {
            'diary_id': {
                'type': 'integer',
                'description': 'The ID of the diary',
            },
            'description': {
                'type': 'string',
                'description': 'The content of the diary entry',
            },
        },
        'required': ['diary_id', 'description'],
    },
}

EXECUTE_COMMAND = {
    'name': 'execute_command',
    'description': 'Execute a command in the terminal',
    'parameters': {
        'type': 'object',
        'properties': {
            'command': {
                'type': 'string',
                'description': 'The command to execute in the terminal',
            },
        },
        'required': ['command'],
    },
}

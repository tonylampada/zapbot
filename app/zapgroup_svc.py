from database import dbsession
from models import ZapMessage
from datetime import datetime
import zap

group_cache = {}

def save_group_chat(groupChat):
    with dbsession() as db:
        group_id = groupChat['group_id']
        group_name = _get_group_name(group_id)
        message_id = groupChat['message_id']
        message_type = groupChat['message_type']
        message_body = groupChat['message_body']
        from_number = groupChat['from_number']
        from_name = groupChat['from_name']
        timestamp = groupChat['timestamp']
        new_entry = ZapMessage(
            group_id = group_id,
            group_name = group_name,
            message_id = message_id,
            message_type = message_type,
            message_body = message_body,
            from_number = from_number,
            from_name = from_name,
            timestamp = timestamp,
        )
        db.add(new_entry)
        db.commit()
        db.refresh(new_entry)

def deleted_message(group_id, message_id):
    with dbsession() as db:
        db.query(ZapMessage).filter(ZapMessage.group_id == group_id, ZapMessage.message_id == message_id).update({'deleted_on': datetime.now()})
        db.commit()

def _get_group_name(group_id):
    group = group_cache.get(group_id)
    if group is None:
        _load_group_cache()
        group = group_cache.get(group_id)
    return group['name']

def _load_group_cache():
    groups = zap.list_chats("jarbas", onlyGroups=True)
    for group in groups:
        _id = group['id']['_serialized']
        name = group.get('name') or group.get('contact', {}).get('name', '[UNKNOWN GROUP NAME]')
        group_cache[_id] = {'name': name}
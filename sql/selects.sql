select 
    id, 
    group_name, 
    timestamp, 
    from_name, 
    message_type, 
    message_body,
    deleted_on

from zap_messages

-- select distinct group_id, group_name from zap_messages
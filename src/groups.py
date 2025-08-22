import logging
from uptime_kuma_api import MonitorType

def find_group_in_monitors(existing_monitors, group_name):
    if not group_name: return None
    for m in existing_monitors:
        if m.get("type")==MonitorType.GROUP and (m.get("name") or "").strip().lower()==group_name.lower():
            return m.get("id") or m.get("monitorID")
    return None

def create_group_if_missing(api, group_name, existing_monitors):
    gid=find_group_in_monitors(existing_monitors, group_name)
    if gid: return gid
    try:
        logging.info("组 '%s' 不存在，尝试创建...", group_name)
        res = api.add_monitor(type=MonitorType.GROUP,name=group_name)
        new_id = res.get("monitorID") or res.get("id")
        if not new_id:
            existing_new = api.get_monitors() or []
            return find_group_in_monitors(existing_new, group_name)
        logging.info("成功创建组 '%s' (ID=%s)", group_name, new_id)
        return new_id
    except Exception as e:
        logging.warning("创建组 '%s' 失败: %s", group_name,e)
        try:
            existing_new = api.get_monitors() or []
            return find_group_in_monitors(existing_new, group_name)
        except: return None

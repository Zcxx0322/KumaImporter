from uptime_kuma_api import UptimeKumaApi
from src.groups import find_group_in_monitors
from uptime_kuma_api import MonitorType


FIELD_MAP = {"reverse":"upsideDown","note":"description","repeat_notify_interval":"resendInterval"}
BASIC_FIELDS = {"maxretries","retryInterval","packetSize"}

def build_create_kwargs(interval, name, host, extra_kwargs, resolved_parent_id):
    create_kwargs = {
        "type": MonitorType.PING,  # ← 这里必须是 MonitorType.PING
        "name": name,
        "hostname": host,
        "interval": max(20, int(interval)),
    }
    mapped = {}
    for k, v in extra_kwargs.items():
        if v is None:
            continue
        if k in FIELD_MAP:
            mk = FIELD_MAP[k]
            if mk == "upsideDown":
                mapped[mk] = bool(v)
            elif mk == "description":
                mapped[mk] = str(v)
            else:
                mapped[mk] = int(v)
        elif k in BASIC_FIELDS:
            mapped[k] = v
    if resolved_parent_id:
        mapped["parent"] = int(resolved_parent_id)
    create_kwargs.update(mapped)
    return create_kwargs

def build_create_kwargs_preview(interval, name, host, extra_kwargs, parent_raw, existing_monitors):
    resolved_parent_id = find_group_in_monitors(existing_monitors, parent_raw) if parent_raw else None
    return build_create_kwargs(interval, name, host, extra_kwargs, resolved_parent_id)

def clear_all(api: UptimeKumaApi):
    """
    清除所有监控和标签
    """
    try:
        monitors = api.get_monitors() or []
        for m in monitors:
            mid = m.get("id") or m.get("monitorID") or m.get("monitorId")
            if mid:
                try:
                    api.delete_monitor(mid)
                    print(f"已删除监控: {m.get('name')}")
                except Exception as e:
                    print(f"删除监控失败: {m.get('name')} - {e}")

        tags = api.get_tags() or []
        for t in tags:
            tid = t.get("id") or t.get("tagID")
            if tid:
                try:
                    api.delete_tag(tid)
                    print(f"已删除标签: {t.get('name')}")
                except Exception as e:
                    print(f"删除标签失败: {t.get('name')} - {e}")

        print("已清空所有监控和标签")
    except Exception as e:
        print("清空失败:", e)
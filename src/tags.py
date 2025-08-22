import re
import logging
from typing import List
from uptime_kuma_api import UptimeKumaApi

ALLOWED_COLORS = {"grey", "red", "orange", "green", "blue", "indigo", "purple", "pink"}

def ensure_tags_and_bind(api: UptimeKumaApi, monitor_id: int, tags: List[str]):
    """
    自动确保标签存在并绑定到监控
    - 支持格式： 标签名:颜色:值  或 标签名:颜色
    - 如果 tags 为空，则默认创建并绑定标签 '未分组:grey'
    """
    if not tags:
        tags = ["未分组:grey"]

    try:
        all_tags = api.get_tags() or []
    except Exception:
        all_tags = []

    # 建立 name -> tag 对象映射，方便查找
    name_map = { (t.get("name") or "").strip().lower(): t for t in all_tags if t.get("name") }

    for tag_spec in tags:
        if not tag_spec or not str(tag_spec).strip():
            continue

        parts = [p.strip() for p in re.split(r'[:;]', str(tag_spec)) if p.strip()]
        tag_name = parts[0]               # 标签名
        tag_color = parts[1].lower() if len(parts) > 1 else "grey"
        tag_value = parts[2] if len(parts) > 2 else ""

        # 限制颜色
        if tag_color not in ALLOWED_COLORS:
            logging.warning("标签 '%s' 使用了不支持的颜色 '%s'，已自动改为 grey", tag_name, tag_color)
            tag_color = "grey"

        # 将 value 拼到 name，保证界面显示
        full_tag_name = f"{tag_name} : {tag_value}" if tag_value else tag_name

        # 查找标签（不区分大小写）
        tag_obj = name_map.get(full_tag_name.lower())
        if not tag_obj:
            try:
                result = api.add_tag(name=full_tag_name, color=tag_color)
                tag_id = result.get("id") or result.get("tagID")
                if tag_id:
                    all_tags = api.get_tags() or []
                    name_map = { (t.get("name") or "").strip().lower(): t for t in all_tags if t.get("name") }
                    tag_obj = name_map.get(full_tag_name.lower())
                else:
                    logging.warning("创建标签 '%s' 成功但未返回 tagID", full_tag_name)
                    continue
            except Exception as e:
                logging.warning("创建标签 '%s' 失败: %s", full_tag_name, e)
                continue

        if not tag_obj:
            logging.warning("无法创建或找到标签 '%s'，跳过绑定", full_tag_name)
            continue

        tag_id = tag_obj.get("id") or tag_obj.get("tagID")
        if not tag_id:
            logging.warning("标签对象缺少 id: %s，跳过绑定", tag_obj)
            continue

        # 绑定标签到监控，value 已拼到 name，无需再传 value
        try:
            api.add_monitor_tag(int(tag_id), int(monitor_id), "")
            logging.info("已绑定标签 '%s' (color=%s) 到监控 %s", full_tag_name, tag_color, monitor_id)
        except Exception as e:
            logging.warning("绑定标签 '%s' 到监控 %s 失败: %s", full_tag_name, monitor_id, e)

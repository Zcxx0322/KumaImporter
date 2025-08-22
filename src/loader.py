import os, csv, openpyxl
from typing import List, Dict, Any
from src.utils import safe_int, parse_bool, norm_header

CHINESE_TO_PARAM = {
    "名称":"name", "监控名称":"name",
    "主机":"host", "地址":"host",
    "心跳间隔":"interval", "间隔":"interval", "间隔(秒)":"interval",
    "重试次数":"maxretries","最大重试次数":"maxretries",
    "心跳重试间隔":"retryInterval","重试间隔":"retryInterval","重试间隔(秒)":"retryInterval",
    "连续失败时重复发送通知的间隔次数":"repeat_notify_interval",
    "重复通知间隔":"repeat_notify_interval",
    "是否反转模式":"reverse","反转":"reverse",
    "数据包大小":"packetSize","包大小":"packetSize",
    "监控项组":"parent","组":"parent",
    "描述":"note","说明":"note",
    "标签":"tags","tags":"tags",
}

def load_targets(file_path: str, default_interval: int) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    name_map = CHINESE_TO_PARAM
    _, ext = os.path.splitext(file_path.lower())

    def push_from_dict(d: Dict[str, Any]):
        parsed = {}
        for k,v in d.items():
            key = norm_header(k)
            if not key: continue
            mapped = name_map.get(key)
            parsed[mapped if mapped else key] = v

        host = str(parsed.get("host") or "").strip()
        if not host: return
        name = str(parsed.get("name") or host).strip()
        interval = safe_int(parsed.get("interval"), default_interval) or default_interval

        kwargs = {"name":name, "host":host, "interval":max(20,interval)}
        for field in ["maxretries","retryInterval","packetSize","reverse","note","repeat_notify_interval","parent"]:
            if field in parsed: kwargs[field]=parsed[field]
        # 多列标签支持：收集列名为 tags/tag/标签 及其数字后缀（如 标签1、标签2、tags1）
        import re
        def extend_tags_from_value(container: list, val: Any):
            if val is None:
                return
            if isinstance(val, str):
                s = val.strip()
                if not s:
                    return
                parts = [t.strip() for t in s.replace("; ", ",").split(",") if t.strip()]
                container.extend(parts)
                return
            if isinstance(val, (list, tuple)):
                container.extend([str(t).strip() for t in val if str(t).strip()])
                return
            s = str(val).strip()
            if s:
                container.append(s)

        tags: list = []
        # 先处理标准列 tags
        extend_tags_from_value(tags, parsed.get("tags"))
        # 处理其它匹配列
        for pk, pv in parsed.items():
            if pk == "tags":
                continue
            key_norm = str(pk).strip()
            if not key_norm:
                continue
            if re.match(r'^(tags?|标签)\s*\d*$', key_norm, flags=re.IGNORECASE):
                extend_tags_from_value(tags, pv)

        kwargs["tags_raw"] = tags
        if "parent" in kwargs: kwargs["parent_raw"]=kwargs.pop("parent")
        rows.append(kwargs)

    if ext==".csv":
        with open(file_path,newline="",encoding="utf-8",errors="replace") as f:
            reader = csv.DictReader(f)
            for r in reader: push_from_dict({norm_header(k):v for k,v in r.items()})
    elif ext in (".xls",".xlsx"):
        wb = openpyxl.load_workbook(file_path,data_only=True)
        ws = wb.active
        headers = [norm_header(c.value) for c in ws[1]]
        for row in ws.iter_rows(min_row=2,values_only=True):
            d={headers[i]:row[i] for i in range(len(headers))}
            push_from_dict(d)
    else:
        with open(file_path,encoding="utf-8",errors="replace") as f:
            for line in f:
                line=line.strip()
                if not line or line.startswith("#"): continue
                push_from_dict({"主机":line,"名称":line})
    return rows

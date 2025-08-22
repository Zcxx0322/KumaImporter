#!/usr/bin/env python3
import argparse
import logging
import os
import sys
import time

from src.config import load_config_with_cli
from src.loader import load_targets
from src.monitor import build_create_kwargs_preview, clear_all
from src.groups import create_group_if_missing
from src.tags import ensure_tags_and_bind
from uptime_kuma_api import UptimeKumaApi

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")

def main():
    parser = argparse.ArgumentParser(description="批量导入 Uptime Kuma 监控")
    parser.add_argument("--config", help="配置文件路径（默认 config/config.ini）")
    parser.add_argument("--url", help="Uptime Kuma 地址")
    parser.add_argument("--user", help="用户名或 API Key")
    parser.add_argument("--password", help="密码或 API Key")
    parser.add_argument("--file", help="目标文件 CSV/XLSX/TXT")
    parser.add_argument("--dry-run", action="store_true", help="仅预演，不实际创建")
    parser.add_argument("--clear-all", action="store_true", help="清空所有监控和标签（无确认）")
    args = parser.parse_args()

    # 默认配置文件
    default_config_path = os.path.join(os.getcwd(), "config", "config.ini")
    config_file = args.config if args.config else default_config_path

    if not os.path.exists(config_file):
        print(f"读取配置文件失败: 配置文件不存在: {config_file}\n")
        parser.print_help()
        sys.exit(1)

    cfg = load_config_with_cli(args)

    try:
        with UptimeKumaApi(cfg["url"]) as api:
            api.login(cfg["user"], cfg["password"])

            # 清空所有监控和标签
            clear_flag = args.clear_all or cfg.get("clear_all", False)
            if clear_flag:
                logging.warning("正在清空所有监控和标签...")
                clear_all(api)
                return

            # 读取目标
            targets = load_targets(cfg["file"], cfg.get("default_interval", 60))
            logging.info("读取 %d 条监控", len(targets))
            if not targets:
                return

            existing_monitors = api.get_monitors() or []
            name_set = set(m.get("name", "").strip().lower() for m in existing_monitors if m.get("name"))
            host_set = set(m.get("hostname", "").strip().lower() for m in existing_monitors if m.get("hostname"))

            created = skipped = failed = 0

            for t in targets:
                name = t.get("name")
                host = t.get("host")
                interval = t.get("interval", cfg.get("default_interval", 60))
                tags = t.get("tags_raw", [])
                parent_raw = t.get("parent_raw")

                if not name or not host:
                    logging.warning("跳过一行，因为 name 或 host 缺失：%s", t)
                    skipped += 1
                    continue

                nl = name.strip().lower()
                hl = host.strip().lower()
                if nl in name_set or hl in host_set:
                    logging.info("[SKIP] %s 已存在，跳过", name)
                    skipped += 1
                    continue

                if cfg.get("dry_run"):
                    preview = build_create_kwargs_preview(interval, name, host, t, parent_raw, existing_monitors)
                    logging.info("[DRY RUN] 将要创建监控：%s 标签=%s parent_raw=%s", preview, tags, parent_raw)
                    created += 1
                    continue

                resolved_parent_id = None
                if parent_raw:
                    resolved_parent_id = create_group_if_missing(api, parent_raw, existing_monitors)
                    if resolved_parent_id:
                        existing_monitors = api.get_monitors() or []

                create_kwargs = build_create_kwargs_preview(interval, name, host, t, parent_raw, existing_monitors)
                try:
                    res = api.add_monitor(**create_kwargs)
                    monitor_id = res.get("monitorID") or res.get("id")
                    if monitor_id:
                        logging.info("[OK] 创建监控 %s -> %s (ID=%s)", name, host, monitor_id)
                        created += 1
                        if tags:
                            ensure_tags_and_bind(api, monitor_id, tags)
                        name_set.add(nl)
                        host_set.add(hl)
                    else:
                        logging.warning("[ERR] 创建监控 %s 成功但未返回 ID", name)
                        failed += 1
                    if cfg.get("sleep_after_create", 0) > 0:
                        time.sleep(cfg["sleep_after_create"])
                except Exception as e:
                    logging.exception("[ERR] 创建监控 %s 失败: %s", name, e)
                    failed += 1

            logging.info("完成：创建 %d，跳过 %d，失败 %d", created, skipped, failed)

    except KeyboardInterrupt:
        print("\n用户中断程序，安全退出。")
        sys.exit(0)

if __name__ == "__main__":
    main()

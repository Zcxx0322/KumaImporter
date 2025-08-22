import os
import argparse
import configparser
import logging
import sys

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")

logging.info("当前工作目录: %s", os.getcwd())
logging.info("配置文件路径: %s", os.path.join("config", "config.ini"))

def load_config(config_file=None):
    if config_file is None:
        config_file = os.path.join("config", "config.ini")

    if not os.path.exists(config_file):
        print(f"读取配置文件失败: 配置文件不存在: {config_file}\n")
        parser = argparse.ArgumentParser(description="批量导入 Uptime Kuma 监控")
        parser.print_help()
        sys.exit(1)

    parser = configparser.ConfigParser()
    parser.read(config_file, encoding="utf-8")

    result = {}
    try:
        uk = parser["uptime_kuma"]
        im = parser["importer"]
    except KeyError as e:
        print(f"配置文件缺少必要的区块: {e}")
        sys.exit(1)

    result.update({
        "url": uk.get("url"),
        "user": uk.get("user"),
        "password": uk.get("password"),
        "file": im.get("file"),
        "default_interval": im.getint("default_interval", 60),
        "retry_interval": im.getint("retry_interval", 30),
        "max_retries": im.getint("max_retries", 2),
        "dry_run": im.getboolean("dry_run", False),
        "clear_all": im.getboolean("clear_all", False),
        "sleep_after_create": im.getfloat("sleep_after_create", 0.2),
        "no_auto_create_groups": im.getboolean("no_auto_create_groups", False),
    })
    return result

def load_config_with_cli(args: argparse.Namespace):
    cfg = load_config(getattr(args, "config", None))

    # CLI 优先级覆盖
    for k in ["url", "user", "password", "file"]:
        val = getattr(args, k, None)
        if val:
            cfg[k] = val

    if getattr(args, "dry_run", False):
        cfg["dry_run"] = True
    if getattr(args, "clear_all", False):
        cfg["clear_all"] = True

    return cfg

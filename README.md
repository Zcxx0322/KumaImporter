# KumaImporter

KumaImporter是一个用于批量导入和管理Uptime Kuma监控的工具。  
支持从 Excel/CSV/TXT 文件读取监控配置，一键创建监控、分组和标签，还可以清空所有监控。

## 功能特点

- 批量导入 PING 类型监控  
- 支持自定义分组和标签  
- 支持 **dry-run** 预演模式，不会实际创建监控  
- 可一键清空所有监控和标签  
- 使用 **INI 配置文件** 或命令行参数配置  

## 安装

克隆仓库：
```bash
git clone https://github.com/Zcxx0322/KumaImporter.git
cd KumaImporter
```

## 依赖环境

- Python 3.7+
- Uptime Kuma 版本支持：

| Uptime Kuma | uptime-kuma-api |
|-------------|----------------|
| 1.21.3 - 1.23.2 | 1.0.0 - 1.2.1 |
| 1.17.0 - 1.21.2 | 0.1.0 - 0.13.0 |

## 安装依赖

推荐通过 `requirements.txt` 安装依赖：

```txt
pip install -r requirements.txt
```

## 配置文件

默认配置文件路径：`config/config.ini`

示例 `config.ini`：

```ini
[uptime_kuma]
url = http://127.0.0.1:3001
user = admin
password = your_password

[importer]
file = targets.xlsx
dry_run = true
clear_all = false
default_interval = 60
retry_interval = 30
max_retries = 2
sleep_after_create = 0.2
no_auto_create_groups = false
```

---

## 使用方法

* 默认读取 `config/config.ini`：

```bash
python cli.py
```

* 使用命令行参数覆盖配置：

```bash
python cli.py --file targets.xlsx --dry-run
```

* 一键清空所有监控和标签：

```bash
python cli.py --clear-all
```

---

## 注意事项

* 启用 `clear_all` 会删除所有监控和标签，请谨慎使用
* `dry_run` 模式仅预演，不会实际创建监控

---

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

## 多列标签支持

现在支持在 Excel/CSV 中使用多列标签，工具会自动合并为同一监控的标签集合：

- 支持的列名：`标签`、`tag`、`tags` 以及它们的数字后缀，如 `标签1`、`标签2`、`tag1`、`tags2` 等（不区分大小写，允许空格，例如 `标签 1`）。
- 每个标签单元格可以填写：
  - 单个标签，如：`业务:blue:核心` 或 `重要:red`
  - 多个标签用逗号或分号分隔：`业务:blue, 重要:red` 或 `业务:blue; 重要:red`
- 颜色可选：`grey/red/orange/green/blue/indigo/purple/pink`，不合法颜色会自动回退为 `grey`。
- 若整行没有任何标签，默认会绑定 `未分组:grey`。

示例（Excel 表头）：

```
名称 | 主机 | 标签 | 标签1 | 标签2
web-01 | 10.0.0.1 | 业务:blue:核心 | 重要:red | 区域:green:华东
```

上例将为 `web-01` 绑定三个标签：`业务 : 核心 (blue)`、`重要 (red)`、`区域 : 华东 (green)`。

---
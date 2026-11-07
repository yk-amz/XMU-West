# XMU-West · COLMAP 数据集

## 三维模型成果

[2026-11-07 校园片区修复版](results/2026-11-07/README.md)包含西端重影修复对比、模型说明与发布包校验值。

原始位置：`D:\Colmap\Project`。本次快照包含 **11,490 个文件、168.784 GiB（181,230,603,441 字节）**。

数据保存在 [Google Drive 私有 Colmap 文件夹](https://drive.google.com/drive/folders/1wHHEzQ8SNW0NyFadkIluY1Ken9k7xc0S)，GitHub 保存清单、校验值和恢复工具。GitHub 仓库已公开，Google Drive 的归档访问权限由 Drive 分享设置管理。

当前状态：**未完成（仅部分分卷已上传）**。已上传并核对大小 **1/87 包**，覆盖原始数据 0.134 GiB。实时进度以本文件和 `datasets/colmap/archives.json` 的最近一次提交为准。

## 范围

完整保留 `Project` 内的原始图片、SQLite 数据库、稀疏/稠密重建、点云、网格、配置和脚本，以及各自相对路径和重复副本。`COLMAP.bat`、`RUN_TESTS.bat`、`bin`、`plugins`、`汇报` 不属于本次 Project 数据集备份。源文件保持原样。

## 下载与恢复

1. 使用有权限的 Google 账户打开上面的 Drive 文件夹，下载全部 `Project.part-*.zip`。
2. 下载本仓库的 `datasets/colmap` 整个目录，保留 `archives.json`、`manifest` 文件夹和 `restore.py` 的相对位置。
3. 确认状态为 `complete`，再运行 `python restore.py "压缩包目录" "空的恢复目标目录"`。

数据按原始大小分为 87 组，每组约 2 GiB。小组直接保存为 ZIP；较大的 ZIP 拆成不超过 64 MiB 的 `.zip.small-001`、`.zip.small-002` 等分卷，以满足传输链路限制。恢复工具直接读取分卷，无需预先合并；它先验证 SHA-256，再解压，最后核对全部原始文件的 SHA-256。它会拒绝不完整备份及已有的目标文件。

## 清单与校验

- [`manifest`](datasets/colmap/manifest)：每个文件的相对路径、字节数、原始修改时间（纳秒）、所在压缩包、SHA-256 和 MD5。清单按每 750 行拆分，便于浏览。上传进行中时，未打包文件的校验值为空。
- [`archives.json`](datasets/colmap/archives.json)：全部分包的状态、下载链接、原始大小、压缩大小和校验值。
- 校验说明：本地计算逐文件及逐包 SHA-256/MD5；上传后回读 Google Drive 元数据，核对包大小。当前连接工具未提供云端 MD5，因此未声称逐包完成云端哈希比对。

这是 2026-10-31 的一次性快照同步，未设置自动周期同步。分包状态保存在本地，后续续传可跳过已完成的包。

<img width="1704" height="1368" alt="image" src="https://github.com/user-attachments/assets/01170cd0-e80f-4734-b1fa-2bbc82238a42" /># 📁 File Organizer Pro - 智能文件整理工具

> 一款功能强大的Windows文件整理工具，支持发票专项整理、AI智能识别、多策略分类

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows-blue.svg)]()

## ✨ 核心功能

| 功能 | 说明 |
|------|------|
| 🧾 **发票整理** | 自动识别PDF/JPG格式发票，按月份/类型归档 |
| 🤖 **AI识别** | 调用OpenAI API智能分析文件内容 |
| 📂 **多策略分类** | 按名称/扩展名/内容/智能组合分类 |
| 🖥️ **图形界面** | 简单易用的Windows GUI |
| 📊 **整理报告** | 自动生成详细整理报告 |
| 👁️ **预览模式** | 整理前预览效果，避免误操作 |

## 🚀 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
2.运行程序
# 图形界面模式（推荐）
cd /d '安装路径根文件夹'
FileOrganizerPro.exe --gui

更新：
新支持了ai分类 配置文件在config/default_rules.json 如果需要的话请修改后编译
在60-80行会发现
{
  "ai_settings": {
    "enabled": true,
    "api_key": "sk-你的OpenAI_API_Key", (修改为你的openai的apikey)
    "model": "gpt-3.5-turbo", (修改为你想使用的openai模型)
    "max_tokens": 50,
    "temperature": 0.3
  }
}
↑这些代码 目前仅适配openai


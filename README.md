# 智慧课堂互动平台 (iClass)

## 1. 项目简介

iClass 是一个基于 Django 和 Vue.js 开发的前后端分离的智慧课堂互动平台。它旨在通过现代化的 Web 技术连接教师与学生，提供丰富的教学互动、课程管理、作业考试和智能辅助功能，从而提升教学效率和学习体验。

## 2. 技术选型 (Technology Stack)

*   **后端 (Backend):**
    *   **框架:** Django
    *   **API:** Django REST Framework
    *   **异步/实时:** Django Channels (用于 WebSocket 实时互动)
    *   **认证:** djangorestframework-simplejwt (JWT)
    *   **数据库:** SQLite (默认)，可轻松替换为 PostgreSQL / MySQL

*   **前端 (Frontend):**
    *   **框架:** Vue.js 3
    *   **状态管理:** Pinia
    *   **UI 库:** Element Plus
    *   **图表:** ECharts
    *   **路由:** Vue Router
    *   **构建工具:** Vite

*   **部署:**
    *   **Web 服务器:** Nginx
    *   **应用服务器:** Gunicorn + Uvicorn (用于 ASGI)
    *   **容器化:** Docker (推荐)

## 3. 功能模块

根据用户角色，系统功能分为三大端：

### 3.1 教师端

*   **课程管理:** 创建和管理课程，上传课程资料，发布课程公告。
*   **作业与考试:** 发布和批改作业，创建和管理在线考试。
*   **课堂互动:** 发起实时签到、投票、问答，管理课堂讨论区和随机点名。
*   **教学反馈:** 发布教学问卷，查看学生反馈的统计结果。
*   **智能助手:** 使用 AI 辅助课程问答和内容管理。
*   **个人中心:** 管理个人信息。

### 3.2 学生端

*   **课程学习:** 加入课程，查看课程列表，下载学习资料。
*   **作业与考试:** 在线完成并提交作业与考试，查看成绩。
*   **课堂互动:** 参与实时签到、投票、问答和讨论。
*   **学习反馈:** 填写教学问卷，提供课程反馈。
*   **智能助手:** 获取课程相关的 AI 问答服务。
*   **个人中心:** 查看个人信息。

### 3.3 后台管理端

*   **用户管理:** 管理所有教师、学生账户及权限分配。
*   **系统监控:** 查看系统操作日志，监控平台运行状态。
*   **数据分析:** 提供教学数据的统计与可视化分析。

## 4. 项目启动与安装

### 4.1. 环境准备

*   Node.js (v20+)
*   Python (v3.10+)

### 4.2. 后端启动

1.  **克隆项目:**
    ```bash
    git clone https://github.com/Keke2004/iclass.git
    cd iclass
    ```

2.  **创建并激活虚拟环境:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # on Windows: venv\Scripts\activate
    ```

3.  **数据库迁移:**
    ```bash
    python manage.py migrate
    ```

4.  **启动开发服务器:**
    ```bash
    python manage.py runserver
    ```

### 4.3. 前端启动

1.  **进入前端目录:**
    ```bash
    cd frontend
    ```

2.  **安装依赖:**
    ```bash
    npm install
    ```

3.  **启动开发服务器:**
    ```bash
    npm run dev
    ```

前端应用将在 `http://localhost:5173` 上运行，并与运行在 `http://127.0.0.1:8000` 的后端 API 通信。

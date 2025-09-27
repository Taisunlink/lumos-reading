#!/bin/bash

echo "🚀 初始化 LumosReading 项目"

# 1. 检查必需工具
check_requirements() {
    echo "检查环境依赖..."
    
    # Node.js 18+
    if ! command -v node &> /dev/null; then
        echo "❌ 请安装 Node.js 18+"
        exit 1
    fi
    
    # Python 3.9+
    if ! command -v python3 &> /dev/null; then
        echo "❌ 请安装 Python 3.9+"
        exit 1
    fi
    
    # PostgreSQL
    if ! command -v psql &> /dev/null; then
        echo "❌ 请安装 PostgreSQL"
        exit 1
    fi
    
    echo "✅ 环境检查通过"
}

# 2. 创建项目结构
create_structure() {
    echo "创建项目结构..."
    mkdir -p apps/{web,api,ai-service}
    mkdir -p packages/{ui,tsconfig,eslint-config}
    mkdir -p infrastructure/{docker,k8s,terraform}
    mkdir -p {docs,tests,scripts}
}

# 3. 初始化前端
init_frontend() {
    echo "初始化前端项目..."
    cd apps/web
    npx create-next-app@latest . --typescript --tailwind --app --no-git --yes
    npm install zustand @tanstack/react-query axios
    npm install -D @types/node
    cd ../..
}

# 4. 初始化后端
init_backend() {
    echo "初始化后端项目..."
    cd apps/api
    python3 -m venv venv
    source venv/bin/activate
    pip install fastapi uvicorn sqlalchemy alembic psycopg2-binary
    pip install redis celery pydantic python-jose passlib
    cd ../..
}

# 5. 设置环境变量
setup_env() {
    echo "设置环境变量..."
    if [ ! -f .env.local ]; then
        cp env.example .env.local
        echo "✅ 已创建 .env.local 文件，请编辑其中的配置"
    else
        echo "⚠️  .env.local 文件已存在，跳过创建"
    fi
}

# 6. 安装依赖
install_dependencies() {
    echo "安装项目依赖..."
    npm install
}

# 执行初始化
check_requirements
create_structure
init_frontend
init_backend
setup_env
install_dependencies

echo "✅ 项目初始化完成"
echo ""
echo "下一步："
echo "1. 编辑 .env.local 文件，填入必要的API密钥"
echo "2. 运行 'npm run docker:up' 启动数据库"
echo "3. 运行 'npm run dev' 启动开发服务器"

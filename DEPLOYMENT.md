# 系统部署指南

## 开发环境部署

### 1. 环境准备

#### 必需软件
- **Python 3.9+**: [下载地址](https://www.python.org/downloads/)
- **Node.js 16+**: [下载地址](https://nodejs.org/)
- **Git**: [下载地址](https://git-scm.com/downloads)

#### 可选软件
- **VS Code**: 推荐的IDE
- **Postman**: API测试工具

### 2. 后端部署

```bash
# 进入后端目录
cd backend

# 创建虚拟环境（推荐）
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 启动服务
python main.py
```

### 3. 前端部署

```bash
# 在项目根目录
npm install

# 开发模式启动
npm run dev

# 生产构建
npm run build
```

### 4. 一键启动（推荐）

```bash
# Windows
start-all.bat

# Linux/Mac (创建start-all.sh)
#!/bin/bash
# 后端
cd backend && python main.py &
# 前端
npm run dev
```

## 生产环境部署

### 方案一：Docker部署

#### Dockerfile (后端)
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install -r requirements.txt

COPY backend/ .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Dockerfile (前端)
```dockerfile
FROM node:16-alpine as builder

WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

#### docker-compose.yml
```yaml
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    ports:
      - "8000:8000"
    environment:
      - PYTHONUNBUFFERED=1

  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    ports:
      - "80:80"
    depends_on:
      - backend
```

### 方案二：云服务器部署

#### 阿里云/腾讯云/AWS
1. **购买服务器**: 推荐2核4G配置
2. **安装环境**: Python 3.9 + Node.js 16
3. **上传代码**: 使用Git或FTP
4. **配置域名**: 解析到服务器IP
5. **配置SSL**: 使用Let's Encrypt免费证书

#### 使用Nginx反向代理
```nginx
# /etc/nginx/sites-available/pv-climate

server {
    listen 80;
    server_name your-domain.com;

    # 前端静态文件
    location / {
        root /var/www/pv-climate/dist;
        try_files $uri $uri/ /index.html;
    }

    # 后端API代理
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 方案三：Serverless部署

#### Vercel (前端)
```bash
# 安装Vercel CLI
npm i -g vercel

# 部署
vercel
```

#### Railway/Render (后端)
```bash
# 安装Railway CLI
npm i -g railway

# 部署
railway up
```

## 性能优化

### 前端优化
1. **代码分割**: 使用动态import
2. **图片优化**: WebP格式 + 懒加载
3. **缓存策略**: Service Worker缓存
4. **CDN加速**: 静态资源CDN

### 后端优化
1. **缓存机制**: Redis缓存计算结果
2. **异步处理**: 使用Celery处理长时间计算
3. **负载均衡**: 多实例部署
4. **数据库**: PostgreSQL存储历史数据

## 监控和日志

### 前端监控
```javascript
// src/utils/monitoring.js
export function trackError(error) {
  // 发送到监控服务
  console.error('Error tracked:', error)
}

export function trackPerformance(metric) {
  // 性能监控
  console.log('Performance:', metric)
}
```

### 后端监控
```python
# backend/monitoring.py
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def log_simulation(params, result):
    logger.info(f"Simulation: {params} -> {result}")
```

## 安全配置

### API安全
1. **CORS配置**: 限制允许的域名
2. **速率限制**: 防止API滥用
3. **输入验证**: 严格验证所有输入
4. **HTTPS**: 生产环境强制HTTPS

### 数据安全
1. **敏感数据**: 加密存储
2. **备份策略**: 定期备份
3. **访问控制**: 基于角色的访问

## 故障排查

### 常见问题

#### 1. 前端无法连接后端
- 检查CORS配置
- 确认后端服务运行状态
- 验证API地址正确

#### 2. 计算结果异常
- 验证输入参数范围
- 检查模型公式实现
- 查看后端日志

#### 3. 性能问题
- 启用缓存机制
- 优化数据库查询
- 使用异步处理

### 日志位置
- **后端日志**: `backend/logs/`
- **前端日志**: 浏览器开发者工具Console
- **Nginx日志**: `/var/log/nginx/`

## 更新和维护

### 版本更新
```bash
# 拉取最新代码
git pull origin main

# 更新依赖
pip install -r requirements.txt --upgrade
npm update

# 重启服务
systemctl restart pv-climate
```

### 数据备份
```bash
# 备份数据库
pg_dump pv_climate > backup_$(date +%Y%m%d).sql

# 备份配置文件
tar -czf config_backup_$(date +%Y%m%d).tar.gz config/
```

## 扩展开发

### 添加新的计算模型
1. 在`backend/`创建新的模型文件
2. 实现标准接口
3. 在`main.py`注册路由
4. 前端添加对应UI组件

### 国际化支持
```javascript
// src/i18n.js
export const messages = {
  en: {
    title: 'PV Climate Effect Monitor'
  },
  zh: {
    title: '光伏气候效应监测'
  }
}
```

## 技术支持

如有问题，请联系：
- 技术支持邮箱
- GitHub Issues
- 在线文档

---

**最后更新**: 2024-01-20

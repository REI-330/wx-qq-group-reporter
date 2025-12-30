# Docker 部署指南

本文档说明如何使用 Docker 部署 QQ群聊年度报告分析器。

如果网络出现报错可以手动pull或者找一个靠谱镜像

## 前置要求

- Docker >= 20.10
- Docker Compose >= 2.0（可选，但推荐）

## 快速开始

### 方式一：使用 Docker Compose（推荐）

1. **构建并启动服务**

```bash
docker-compose up -d --build
```
如果开启服务之后点击前端链接没反应可以换个端口，换成5001,5002啥的试试

2. **查看日志**

```bash
docker-compose logs -f
```

3. **停止服务**

```bash
docker-compose down
```

### 方式二：使用 Docker 命令

1. **构建镜像**

```bash
docker build -t qqgroup-report-analyzer .
```

2. **运行容器**

```bash
docker run -d \
  --name qqgroup-report \
  -p 5000:5000 \
  -v $(pwd)/runtime_outputs:/app/runtime_outputs \
  qqgroup-report-analyzer
```

3. **查看日志**

```bash
docker logs -f qqgroup-report
```

4. **停止容器**

```bash
docker stop qqgroup-report
docker rm qqgroup-report
```

## 环境变量配置

可以通过环境变量配置应用行为：

### docker-compose.yml 中配置

编辑 `docker-compose.yml` 文件的 `environment` 部分：

```yaml
environment:
  - FLASK_ENV=production
  - PORT=5000
  - ENABLE_IMAGE_EXPORT=true
  - MAX_UPLOAD_SIZE_MB=50
  - STORAGE_MODE=json  # 或 mysql
  - OPENAI_API_KEY=your-api-key  # 可选
  - OPENAI_BASE_URL=https://api.openai.com/v1  # 可选
  - OPENAI_MODEL=gpt-4o-mini  # 可选
```

### Docker 命令中配置

```bash
docker run -d \
  --name qqgroup-report \
  -p 5000:5000 \
  -e ENABLE_IMAGE_EXPORT=true \
  -e OPENAI_API_KEY=your-api-key \
  qqgroup-report-analyzer
```

## 访问应用

部署成功后，访问：

- 前端页面：http://localhost:5000
- API 健康检查：http://localhost:5000/api/health

## 数据持久化

运行时生成的文件会保存在 `runtime_outputs` 目录。使用 Docker Compose 时，该目录会自动挂载到容器中。

如果需要持久化数据库（MySQL 模式），可以添加数据卷：

```yaml
volumes:
  - ./runtime_outputs:/app/runtime_outputs
  - mysql_data:/var/lib/mysql  # MySQL 数据持久化
```

## 生产环境建议

1. **使用反向代理**

   建议使用 Nginx 或 Traefik 作为反向代理，处理 HTTPS 和静态文件：

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

2. **资源限制**

   在 `docker-compose.yml` 中添加资源限制：

```yaml
services:
  web:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

3. **健康检查**

   Docker Compose 已配置健康检查，可以通过以下命令查看：

```bash
docker-compose ps
```

## 故障排查

### 1. 容器无法启动

检查日志：

```bash
docker-compose logs web
```

常见问题：
- 端口被占用：修改 `docker-compose.yml` 中的端口映射
- 内存不足：Playwright 需要足够内存，建议至少 1GB

### 2. 图片生成失败

确保：
- `ENABLE_IMAGE_EXPORT=true`
- 容器有足够内存（Playwright 需要）
- 检查日志中是否有 Playwright 相关错误

### 3. 前端页面无法访问

- 确认容器正在运行：`docker ps`
- 检查端口映射是否正确
- 查看容器日志：`docker logs qqgroup-report`

## 更新应用

1. **拉取最新代码**

```bash
git pull
```

2. **重新构建并启动**

```bash
docker-compose up -d --build
```

## 清理

删除所有容器、镜像和数据：

```bash
docker-compose down -v
docker rmi qqgroup-report-analyzer
```


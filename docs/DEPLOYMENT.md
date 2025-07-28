# 部署指南 🚀

本文档介绍如何将虚拟货币查询工具部署到各种平台。

## 📋 部署前准备

确保你的项目已经上传到GitHub，并且包含以下文件：
- `app.py` - 主应用文件
- `requirements.txt` - Python依赖
- `templates/index.html` - 前端模板
- `Procfile` - 部署配置
- `runtime.txt` - Python版本

## 🌐 部署到Heroku

### 1. 准备工作
- 注册 [Heroku](https://heroku.com) 账号
- 安装 [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)

### 2. 部署步骤
```bash
# 登录Heroku
heroku login

# 创建应用
heroku create your-app-name

# 部署
git push heroku main

# 打开应用
heroku open
```

## ⚡ 部署到Vercel

### 1. 准备工作
- 注册 [Vercel](https://vercel.com) 账号
- 安装 Vercel CLI: `npm i -g vercel`

### 2. 创建vercel.json配置
```json
{
  "version": 2,
  "builds": [
    {
      "src": "./app.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "/"
    }
  ]
}
```

### 3. 部署
```bash
vercel --prod
```

## 🐳 Docker部署

### 1. 创建Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
```

### 2. 构建和运行
```bash
# 构建镜像
docker build -t crypto-price-checker .

# 运行容器
docker run -p 5000:5000 crypto-price-checker
```

## 🔧 环境变量配置

如果需要配置环境变量，可以在各平台设置：

- `FLASK_ENV=production` - 生产环境
- `PORT=5000` - 端口号（某些平台会自动设置）

## 📊 性能优化建议

1. **启用缓存**：为API响应添加缓存机制
2. **压缩静态文件**：启用gzip压缩
3. **CDN加速**：使用CDN加速静态资源
4. **监控告警**：设置应用监控和告警

## 🔍 故障排除

### 常见问题

1. **端口问题**
   ```python
   # 确保app.py中使用环境变量端口
   port = int(os.environ.get('PORT', 5000))
   app.run(host='0.0.0.0', port=port)
   ```

2. **依赖问题**
   ```bash
   # 更新requirements.txt
   pip freeze > requirements.txt
   ```

3. **API超时**
   - 增加请求超时时间
   - 添加重试机制
   - 使用多个API源

## 📱 移动端适配

应用已经使用Bootstrap响应式设计，支持移动端访问。

## 🔐 安全建议

1. 不要在代码中硬编码API密钥
2. 使用HTTPS
3. 添加请求频率限制
4. 验证用户输入

## 📈 监控和分析

推荐使用以下工具：
- Google Analytics - 用户行为分析
- Sentry - 错误监控
- New Relic - 性能监控

---

如有部署问题，请查看项目的Issue页面或联系维护者。
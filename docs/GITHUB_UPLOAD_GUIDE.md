# 📤 GitHub上传指南

## 🎯 快速上传步骤

### 1. 创建GitHub仓库
1. 访问 [GitHub](https://github.com)
2. 点击右上角 "+" → "New repository"
3. 填写信息：
   - Repository name: `crypto-price-checker`
   - Description: `一个简洁美观的加密货币价格查询工具`
   - 选择 Public 或 Private
   - **不要勾选** "Initialize this repository with a README"
4. 点击 "Create repository"

### 2. 获取仓库URL
创建后，GitHub会显示类似这样的URL：
```
https://github.com/你的用户名/crypto-price-checker.git
```

### 3. 上传代码
在项目目录中运行以下命令（替换YOUR_USERNAME为你的GitHub用户名）：

```bash
# 添加远程仓库
git remote add origin https://github.com/YOUR_USERNAME/crypto-price-checker.git

# 重命名分支为main
git branch -M main

# 推送代码
git push -u origin main
```

### 4. 验证上传
访问你的GitHub仓库页面，应该能看到所有文件已经上传成功。

## 📁 项目文件说明

上传后的项目包含以下文件：

```
crypto-price-checker/
├── 📄 README.md              # 项目说明文档
├── 🐍 app.py                 # Flask应用主文件
├── 📋 requirements.txt       # Python依赖列表
├── 📁 templates/
│   └── 🌐 index.html        # 前端页面模板
├── 🧪 test_api.py           # API连接测试脚本
├── 🚀 Procfile              # Heroku部署配置
├── 🐍 runtime.txt           # Python版本指定
├── 📜 LICENSE               # MIT开源许可证
├── 🚫 .gitignore            # Git忽略文件配置
├── 📖 DEPLOYMENT.md         # 部署指南
└── 📤 GITHUB_UPLOAD_GUIDE.md # 本文件
```

## 🎉 上传成功后的操作

### 1. 设置仓库描述
在GitHub仓库页面点击 "⚙️ Settings" → "General"，添加：
- Description: `一个简洁美观的加密货币价格查询工具`
- Website: 如果部署了在线版本，填写URL
- Topics: `cryptocurrency`, `price-checker`, `flask`, `python`, `web-app`

### 2. 创建Release
1. 点击 "Releases" → "Create a new release"
2. Tag version: `v1.0.0`
3. Release title: `虚拟货币查询工具 v1.0.0`
4. 描述功能特性和使用方法

### 3. 启用GitHub Pages（可选）
如果想要静态展示页面：
1. Settings → Pages
2. Source: Deploy from a branch
3. Branch: main
4. Folder: / (root)

## 🔧 后续维护

### 更新代码
```bash
# 添加更改
git add .

# 提交更改
git commit -m "描述你的更改"

# 推送到GitHub
git push origin main
```

### 创建分支
```bash
# 创建新功能分支
git checkout -b feature/new-feature

# 开发完成后合并
git checkout main
git merge feature/new-feature
git push origin main
```

## 🌟 推广项目

1. **添加README徽章**：显示构建状态、许可证等
2. **编写详细文档**：使用说明、API文档等
3. **添加截图**：在README中展示界面效果
4. **标记Topics**：便于其他人发现你的项目
5. **分享到社区**：Reddit、Twitter、技术论坛等

## ❓ 常见问题

**Q: 推送时提示权限错误？**
A: 确保你有仓库的写权限，或者使用Personal Access Token

**Q: 如何删除敏感信息？**
A: 使用 `git filter-branch` 或 BFG Repo-Cleaner

**Q: 如何设置协作者？**
A: Settings → Manage access → Invite a collaborator

---

# 第三十四章：部署运维 —— OpenClaw 网关生产环境最佳实践

OpenClaw 设计就是为了生产环境长期运行，本章汇总生产环境部署运维的最佳实践，帮你跑稳跑顺。

## 部署架构选择

### 选项 1：单机部署（推荐个人/小团队）

```
你的服务器 → OpenClaw Gateway 直接跑 → 反向代理 Nginx → 域名 HTTPS
```

- 简单，一台机器搞定
- 数据都在你自己机器
- 维护方便，升级简单

适合：个人使用、小团队、不需要高可用。

### 选项 2：容器部署（Docker Compose）

```yaml
# docker-compose.yml
version: "3"
services:
  openclaw:
    image: openclaw/openclaw:latest
    ports:
      - "18789:18789"
    volumes:
      - ~/.openclaw:/home/openclaw/.openclaw
    restart: always
```

- 环境一致，部署一次到处跑
- 升级就是拉新镜像重启
- 隔离性好，不污染系统

适合：熟悉 Docker 的用户，生产推荐。

### 选项 3：Kubernetes 集群部署（适合团队/企业）

- Deployment 跑 Gateway
- ConfigMap 存配置（密钥放 Secret）
- Service 暴露端口
- Ingress 处理 HTTPS

适合：企业已有 Kubernetes 集群，需要高可用。

## 系统配置建议

### 用户权限

不要用 root 跑！创建专用用户：

```bash
useradd -m openclaw
chown -R openclaw:openclaw ~openclaw/.openclaw
su - openclaw
```

专用用户权限有限，就算出问题影响有限。

### 文件描述符

Gateway 大量并发连接，默认 fd 可能不够：

```
# /etc/security/limits.conf
openclaw soft nofile 65536
openclaw hard nofile 65536
```

重启生效。

### 自动重启（systemd）

创建 `/etc/systemd/system/openclaw.service`:

```ini
[Unit]
Description=OpenClaw Gateway
After=network.target

[Service]
User=openclaw
WorkingDirectory=/home/openclaw/openclaw
ExecStart=/home/openclaw/openclaw/bin/openclaw gateway run
Restart=always
RestartSec=10
Environment=PATH=/usr/local/bin:/usr/bin:/bin
StandardOutput=journal+console
StandardError=journal+console

[Install]
WantedBy=multi-user.target
```

启用：

```bash
systemctl daemon-reload
systemctl enable openclaw
systemctl start openclaw
```

- 开机自动启动
- 崩溃自动重启
- 日志统一走 journald，`journalctl -u openclaw` 看

## 反向代理配置（Nginx）

推荐 Nginx 反向代理，处理 HTTPS：

```nginx
server {
  listen 443 ssl http2;
  server_name openclaw.your-domain.com;

  ssl_certificate /path/to/fullchain.pem;
  ssl_certificate_key /path/to/privkey.pem;

  # 安全headers
  add_header X-Frame-Options DENY;
  add_header X-Content-Type-Options nosniff;
  add_header X-XSS-Protection 1;

  location / {
    proxy_pass http://127.0.0.1:18789;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_read_timeout 300; # 长超时，AI生成可能慢
  }
}
```

HTTP 跳 HTTPS：

```nginx
server {
  listen 80;
  server_name openclaw.your-domain.com;
  return 301 https://$server_name$request_uri;
}
```

好处：
- HTTPS 证书自动续期（Let's Encrypt）
- Nginx 处理连接缓冲，比 Node 直接扛稳
- 可以配置 IP 白名单限制访问

## 备份策略

一定要备份！配置和数据丢了很惨。

### 自动备份脚本

```bash
#!/bin/bash
# backup-openclaw.sh
BACKUP_DIR="/backup/openclaw"
DATE=$(date +%Y%m%d)
CONFIG="$HOME/.openclaw/openclaw.json"
WORKSPACE="$HOME/.openclaw/workspace"

mkdir -p $BACKUP_DIR
tar czf $BACKUP_DIR/openclaw-backup-$DATE.tar.gz $CONFIG $WORKSPACE

# 保留最近 30 天
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete
```

加 cron 每天跑：

```
0 2 * * * /home/openclaw/backup-openclaw.sh >> /var/log/openclaw-backup.log 2>&1
```

每天凌晨 2 点备份，保留 30 天。

### 备份到云端

备份完可以同步到 S3 或者其他云存储：

```bash
aws s3 cp $BACKUP_DIR/openclaw-backup-$DATE.tar.gz s3://your-backup-bucket/openclaw/
```

本地一份云端一份，双重保险。

## 监控

### 基础监控

监控这些指标：

- CPU 使用率
- 内存使用率
- 磁盘空间
- Gateway 进程是否 running
- API 调用成功率
- 每日成本

### 日志轮转

OpenClaw 日志默认写到文件，配置 logrotate 轮转：

```
# /etc/logrotate.d/openclaw
/var/log/openclaw/output.log {
  daily
  rotate 30
  compress
  delaycompress
  missingok
  notifempty
  create 644 openclaw openclaw
  sharedscripts
  postrotate
    systemctl reload openclaw > /dev/null
  endscript
}
```

每月不会越滚越大，自动删老日志。

### 告警

配置告警：

- Gateway 进程挂了 → 告警
- 磁盘满了 → 告警
- 成本超预算 → 告警
- 连续 API 失败 → 告警

OpenClaw 支持告警发到你配置的渠道（Telegram/email）。

## 安全建议

生产环境安全检查清单：

- [ ] 不要用 root 跑 OpenClaw
- [ ] 配对白名单开了吗？不要允许任何用户
- [ ] HTTPS 配置了吗？不要裸 HTTP 跑公网
- [ ] 密钥放对权限了吗？`chmod 600 ~/.openclaw/openclaw.json`
- [ ] 防火墙限制端口了吗？只开需要的端口
- [ ] API 密钥都对吗？不要把测试密钥放生产
- [ ] 定期更新 OpenClaw 吗？更最新版本拿安全修复

## 升级步骤

安全升级步骤：

1. **备份先！** 升级前先备份配置和数据
2. ```git pull``` 拉最新代码
3. ```pnpm install``` 装新依赖
4. ```pnpm build``` 重新构建
5. ```systemctl restart openclaw``` 重启服务
6. 等起来，```openclaw doctor``` 检查健康
7. 有问题切回上个版本，找问题

不要不备份直接升，出问题回不去。

## 性能调优

### Node.js 配置

```bash
# 启动环境变量，调大内存
NODE_OPTIONS="--max-old-space-size=4096" openclaw gateway run
```

Gateway 缓存连接和会话，4GB 足够大多数场景。

### 磁盘IO

- 用 SSD，不要用机械硬盘，响应快很多
- 日志放不同分区，不要跟系统抢 IO

### 网络

- 服务器选离你近的区域，延迟低
- 如果你用中国，选香港/新加坡节点，访问 Anthropic/OpenAI 快

## 高可用（多人/企业）

如果需要高可用：

- 多实例部署，前面放负载均衡
- 数据存共享存储（S3/NFS）
- 配置存在数据库，多实例同步
- 一个实例挂了，负载均衡切另一个

大多数个人使用不需要，单机足够用。

## 故障处理流程

1. **看状态**：`systemctl status openclaw` 看看跑不跑
2. **看日志**：`journalctl -u openclaw -f` 看最近错误
3. **跑 doctor**：`openclaw doctor` 自动检查
4. **配置对不对**：检查密钥、端口、网络
5. **重启试试**：`systemctl restart openclaw`
6. **不行回滚**：回到上个版本，看是不是新版本问题

## 本章小结

- 推荐个人用 Docker Compose 或者 systemd 单机部署，简单够用
- 创建专用用户，不要 root 跑，安全
- 配置自动备份，一定要备份！
- Nginx 反向代理 HTTPS，安全稳定
- 监控日志轮转，告警异常
- 定期更新，升级先备份

按照这个实践，你的 OpenClaw Gateway 能稳定跑很久，不用怎么维护。

---

---

**系列目录**：
- [第一章：OpenClaw 是什么 —— 自托管个人 AI 助手的终极形态](./../01-intro/01-what-is-openclaw.md)
- [第二章：核心架构总览 —— Gateway 为什么是中心控制平面](./../01-intro/02-architecture-overview.md)
- [第三章：Gateway —— 核心网关服务到底做了什么](./../01-intro/03-gateway.md)
- [第四章：多渠道接入 —— 如何支持 25+ 聊天平台](./../01-intro/04-multi-channel-inbox.md)
- [第五章：ACP —— 如何对接外部 AI 客户端](./../01-intro/05-acp.md)
- [第六章：消息路由 —— 消息如何正确送到对的会话](./../01-intro/06-routing.md)
- [第七章：安全模型 —— 配对白名单如何保护你](./../01-intro/07-security-model.md)
- [第八章：为什么你需要一个多智能体框架 —— 单智能体的困境](./../02-multi-agent/08-why-you-need-multi-agent-framework.md)
- [第九章：sessions_spawn —— 多智能体协作的核心原语](./../02-multi-agent/09-sessions-spawn-core-primitive.md)
- [第十章：协作架构模式 —— 从 Master-Worker 到 Hub-and-Spoke](./../02-multi-agent/10-collaboration-architecture-patterns.md)
- [第十一章：隔离设计 —— 为什么每个子智能体需要独立会话](./../02-multi-agent/11-isolation-design.md)
- [第十二章：嵌套协作 —— 如何实现 Orchestrator-Worker 模式](./../02-multi-agent/12-nested-collaboration.md)
- [第十三章：实践案例 —— 从零构建一个代码评审团队](./../02-multi-agent/13-practical-case-code-review-team.md)
- [第十四章：platforms —— 全平台安装部署指南](./../03-core-concepts/14-platforms.md)
- [第十五章：providers —— 各大模型提供者配置大全](./../03-core-concepts/15-providers.md)
- [第十六章：plugins —— 插件系统开发指南](./../03-core-concepts/16-plugins.md)
- [第十七章： refactor —— OpenClaw 重构原则与工作流](./../03-core-concepts/17-refactor.md)
- [第十八章：reference —— 完整配置、模板、CLI 命令参考](./../03-core-concepts/18-reference.md)
- [第十九章：skills —— 技能系统核心概念与开发指南](./../03-core-concepts/19-skills.md)
- [第二十章：ClawHub —— 技能市场如何分享和获取技能](./../03-core-concepts/20-clawhub.md)
- [第二十一章：Canvas A2UI —— 实时可视化协作 workspace](./../04-client-ux/21-canvas.md)
- [第二十二章：语音唤醒 (Voice Wake) —— 语音交互体验](./../04-client-ux/22-voice-wake.md)
- [第二十三章：WebChat —— Gateway WebSocket 聊天界面](./../04-client-ux/23-webchat.md)
- [第二十四章：工具系统 (Tools) —— OpenClaw 工具调用框架设计](./../05-tools-automation/24-tools.md)
- [第二十五章：内置浏览器 —— 网页抓取和交互](./../05-tools-automation/25-browser.md)
- [第二十六章：Cron 自动化 —— 定时任务自动化](./../05-tools-automation/26-cron.md)
- [第二十七章：Onboarding —— 新手引导流程设计](./../05-tools-automation/27-onboarding.md)
- [第二十八章：blogwatcher —— 博客与 RSS 更新监控](./../06-builtin-skills/28-live-covers.md)
- [第二十九章：gh-issues —— GitHub Issues 自动修复编排](./../06-builtin-skills/29-gh-issues.md)
- [第三十章：coding-agent —— 调用外部编码代理](./../06-builtin-skills/30-coding-agent.md)
- [第三十一章：模型故障转移 (Model Failover) —— 如何提高可用性](./31-failover.md)
- [第三十二章：调试技巧 —— 如何排查 OpenClaw 问题](./32-debugging.md)
- [第三十三章：成本优化 —— 如何用模型分级降低总成本](./33-cost-optimization.md)
- 第三十四章：部署运维 —— OpenClaw 网关生产环境最佳实践 👈 当前位置

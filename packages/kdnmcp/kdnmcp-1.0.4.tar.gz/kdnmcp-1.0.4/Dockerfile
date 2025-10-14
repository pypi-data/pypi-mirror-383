# 快递鸟MCP服务 Docker镜像
FROM python:3.12-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1



# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple && \
    pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 复制应用代码
COPY . .

# 创建日志目录
RUN mkdir -p logs

# 创建非root用户
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.path.append('/app'); from kdnmcp.server import KDNiaoMCPServer; print('Health check passed')" || exit 1

# 暴露端口（http模式）
EXPOSE 8000

# 默认启动命令（http模式）
CMD ["python", "-m", "kdnmcp.main", "--transport", "http", "--port", "8000"]
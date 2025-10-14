#!/usr/bin/env python3
"""快递鸟MCP服务器启动脚本"""

import os
import sys
import asyncio
import argparse
from pathlib import Path

# 自动设置UTF-8编码以支持Unicode字符
if sys.platform.startswith('win'):
    import codecs
    # 自动设置控制台编码为UTF-8，无需用户手动配置
    if not os.environ.get('PYTHONIOENCODING'):
        os.environ['PYTHONIOENCODING'] = 'utf-8'
    # 确保标准输出使用UTF-8编码
    if hasattr(sys.stdout, 'reconfigure'):
        try:
            sys.stdout.reconfigure(encoding='utf-8')
            sys.stderr.reconfigure(encoding='utf-8')
        except Exception:
            pass  # 如果重配置失败，继续使用环境变量设置
    

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def setup_environment():
    """设置环境变量"""
    # 直接检查必需的环境变量，不再要求.env文件
    required_vars = [
        "EBUSINESS_ID",
        "API_KEY"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        # 将错误信息输出到stderr，避免干扰MCP协议
        import sys
        print(f"错误: 缺少必需的环境变量: {', '.join(missing_vars)}", file=sys.stderr)
        print("请通过环境变量 EBUSINESS_ID 和 API_KEY 提供配置", file=sys.stderr)
        return False
    
    return True


def validate_config():
    """验证配置"""
    try:
        # 导入配置
        from settings import config
        
        # 检查快递鸟API配置
        if not config.kdniao.ebusiness_id:
            import sys
            print("错误: 快递鸟商户ID未配置", file=sys.stderr)
            return False
        
        if not config.kdniao.api_key:
            import sys
            print("错误: 快递鸟API密钥未配置", file=sys.stderr)
            return False
        
        if not config.kdniao.api_url:
            import sys
            print("错误: 快递鸟API地址未配置", file=sys.stderr)
            return False
        
        # 配置验证成功时的信息也输出到stderr，避免干扰MCP协议
        import sys
        print(f"✓ 快递鸟API配置验证通过", file=sys.stderr)
        print(f"  - 商户ID: {config.kdniao.ebusiness_id}", file=sys.stderr)
        print(f"  - API地址: {config.kdniao.api_url}", file=sys.stderr)
        
        return True
        
    except Exception as e:
        import sys
        print(f"配置验证失败: {e}", file=sys.stderr)
        return False


def print_server_info(transport: str):
    """打印服务器信息"""
    # 导入配置
    from settings import config
    
    print("\n" + "="*60)
    print("🚀 快递鸟MCP服务器")
    print("="*60)
    print(f"版本: 1.0.0")
    print(f"传输方式: {transport.upper()}")
    
    if transport == "sse":
        print(f"服务地址: http://{config.mcp_server.host}:{config.mcp_server.port}")
        print(f"SSE端点: http://{config.mcp_server.host}:{config.mcp_server.port}/sse")
    elif transport == "http":
        print(f"服务地址: http://{config.mcp_server.host}:{config.mcp_server.port}")
        print(f"HTTP端点: http://{config.mcp_server.host}:{config.mcp_server.port}/mcp")
    else:
        print("使用标准输入输出进行通信")
    
    
    if transport == "stdio":
        print("服务器已启动，等待MCP客户端连接...")
        print("按 Ctrl+C 停止服务器")
    else:
        print(f"服务器已启动，访问 http://{config.mcp_server.host}:{config.mcp_server.port}")
        print("按 Ctrl+C 停止服务器")
    
    print("="*60 + "\n")


async def run_server(transport: str, debug: bool = False):
    """运行服务器"""
    server = None
    try:
        # 设置日志级别
        if debug:
            os.environ["LOG_LEVEL"] = "DEBUG"
        
        # 导入必要的模块
        from .server import KDNiaoMCPServer
        
        # 创建服务器
        server = KDNiaoMCPServer()
        
        # 打印服务器信息
        print_server_info(transport)
        
        # 启动服务器
        await server.start_server(transport)
        
    except KeyboardInterrupt:
        print("\n正在关闭服务器...")
    except Exception as e:
        print(f"服务器错误: {e}")
        raise
    finally:
        if server:
            await server.shutdown()
            print("服务器已关闭")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="快递鸟MCP服务器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  python run_server.py                    # 使用stdio传输（默认）
  python run_server.py --transport sse    # 使用SSE传输
  python run_server.py --transport sse --port 8000  # 使用SSE传输并指定端口
  python run_server.py --debug            # 启用调试模式
  python run_server.py --check-config     # 仅检查配置
        """
    )
    
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse", "http"],
        default="stdio",
        help="传输方式 (默认: stdio)"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="启用调试模式"
    )
    
    parser.add_argument(
        "--check-config",
        action="store_true",
        help="仅检查配置并退出"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="服务器端口 (默认: 8000)"
    )
    
    args = parser.parse_args()
    
    try:
        # 设置端口环境变量（必须在导入配置之前）
        if args.port != 8000:  # 只有当端口不是默认值时才设置
            os.environ["MCP_SERVER_PORT"] = str(args.port)
        
        # 现在可以安全地导入配置相关模块
        from settings import config
        from utils.logger import setup_logger, app_logger as logger
        
        # 重新加载配置以应用新的环境变量
        config.reload()
        
        # 设置环境
        # if not setup_environment():
        #     sys.exit(1)
        
        # 验证配置
        # if not validate_config():
        #     sys.exit(1)
        
        # 如果只是检查配置，则退出
        if args.check_config:
            print("✓ 配置检查通过", file=sys.stderr)
            return
        
        # 检查SSE传输的额外要求
        if args.transport == "sse" and not config.protocol.enable_sse:
            print("错误: SSE传输已在配置中禁用", file=sys.stderr)
            print("请在.env文件中设置 ENABLE_SSE=true", file=sys.stderr)
            sys.exit(1)
        
        # 检查HTTP传输的额外要求
        if args.transport == "http" and not config.protocol.enable_http:
            print("错误: HTTP传输已在配置中禁用", file=sys.stderr)
            print("请在.env文件中设置 ENABLE_HTTP=true", file=sys.stderr)
            sys.exit(1)
        
        # 运行服务器（不再需要传递port参数，因为已经通过环境变量设置）
        asyncio.run(run_server(args.transport, args.debug))

        
    except KeyboardInterrupt:
        print("\n用户中断", file=sys.stderr)
    except Exception as e:
        print(f"启动失败: {e}", file=sys.stderr)
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
import argparse
import os
from fastmcp import FastMCP
from daily_hot_mcp.utils.logger import logger
from daily_hot_mcp.tools import all_tools

# 重命名变量，使其符合 mcp dev 命令的预期
server = FastMCP(name = "daily-hot-mcp")

for tool in all_tools:
    server.add_tool(tool)
    logger.info(f"Registered tool: {tool.name}")

def run_http(host: str, port: int, path: str, log_level: str):
    """Run Daily Hot MCP server in HTTP mode."""
    try:
        logger.info(f"Starting Daily Hot MCP server with HTTP transport (http://{host}:{port}{path})")
        server.run(
            transport="http",
            host=host,
            port=port,
            path=path,
            log_level=log_level
        )
    except KeyboardInterrupt:
        logger.info("Server stopped by user")

def main():
    """主入口函数，解析命令行参数并启动服务器"""
    parser = argparse.ArgumentParser(
        description="Daily Hot MCP - 全网热点趋势一站式聚合服务",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 基本启动
  daily-hot-mcp
  
  # 带 API 密钥启动
  daily-hot-mcp --firecrawl-api-key your_api_key
  
  # 带自定义 RSS 源启动
  daily-hot-mcp --custom-rss-url https://your-rss-feed.com/feed
  
  # 同时指定多个参数
  daily-hot-mcp --firecrawl-api-key your_api_key --custom-rss-url https://your-rss-feed.com/feed
        """
    )
    
    parser.add_argument(
        "--firecrawl-api-key",
        type=str,
        help="FireCrawl API 密钥，用于爬取网站内容获取热点详细信息"
    )
    
    parser.add_argument(
        "--custom-rss-url",
        type=str,
        help="自定义 RSS 订阅源 URL，配置后将自动添加 custom-rss 工具"
    )
    
    args = parser.parse_args()
    
    # 将命令行参数设置为环境变量，供工具使用
    if args.firecrawl_api_key:
        os.environ["FIRECRAWL_API_KEY"] = args.firecrawl_api_key
        logger.info("FIRECRAWL_API_KEY 已设置")
    
    if args.custom_rss_url:
        os.environ["TRENDS_HUB_CUSTOM_RSS_URL"] = args.custom_rss_url
        logger.info(f"TRENDS_HUB_CUSTOM_RSS_URL 已设置: {args.custom_rss_url}")
    
    # 使用默认配置启动服务器
    run_http("0.0.0.0", 8000, "/mcp", "INFO")

if __name__ == "__main__":
    main()
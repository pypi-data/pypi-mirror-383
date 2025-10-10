from .server import serve

def main():
    """MCP NovelAI Gen Server"""
    # The 'serve' function now calls a blocking 'run' method,
    # so it should be called directly without asyncio.
    serve()

if __name__ == "__main__":
    main()
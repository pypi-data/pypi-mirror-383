# financial_analyzer_server/src/financial_analyzer_mcp_server/main.py
# L'import de 'server' doit maintenant être relatif si server.py est au même niveau que main.py
from financial_analyzer_mcp_server.server import mcp
import financial_analyzer_mcp_server.tools.inflation_tools
import financial_analyzer_mcp_server.tools.grizzly_tools

def run_mcp_server():
    """Point d'entrée pour démarrer le serveur MCP."""
    print("Licence validée. Démarrage du serveur MCP 'financial_analyzer'...")
    mcp.run()

if __name__ == "__main__":
    run_mcp_server()

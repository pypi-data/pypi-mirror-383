# financial_analyzer_server/src/financial_analyzer_mcp_server/server.py
from mcp.server.fastmcp import FastMCP
from financial_analyzer_mcp_server.license_validator import LicenseValidator
import sys
# C'est l'instance partagée du serveur MCP.
# Le nom "financial_analyzer" sera visible dans Claude for Desktop.
# Validation de licence au démarrage
validator = LicenseValidator()
if not validator.validate_license():
    sys.stderr.write("ARRÊT: Licence invalide ou expirée\n")
    sys.exit(1)

# C'est l'instance partagée du serveur MCP.
# Le nom "financial_analyzer" sera visible dans Claude for Desktop.
mcp = FastMCP("financial_analyzer")

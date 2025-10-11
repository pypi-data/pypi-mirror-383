import os
import requests
import sys

class LicenseValidator:
    def __init__(self):
        self.api_key = os.getenv("MCP_API_KEY")
        if os.getenv("DEBUG") == "true":
            sys.stderr.write(f"API Key: {self.api_key}\n")
        self.validation_url = "https://backend.firstland.fr/api/mcp/validate-license"
        
    def validate_license(self) -> bool:
        """Valide la licence auprès du backend Firstland"""
        if not self.api_key:
            sys.stderr.write("API Key: Not Provided\n")
            sys.exit(1)
            return False
            
        try:
            response = requests.post(
                self.validation_url,
                json={
                    "api_key": self.api_key,
                    "tool_id": 101
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("valid", False)
            else:
                sys.stderr.write(f"ERREUR: Validation échouée (HTTP {response.status_code})\n")
                return False
                
        except requests.exceptions.RequestException as e:
            sys.stderr.write(f"ERREUR: Impossible de contacter le serveur de validation: {e}\n")
            return False
        except Exception as e:
            sys.stderr.write(f"ERREUR: Validation inattendue: {e}\n")
            return False

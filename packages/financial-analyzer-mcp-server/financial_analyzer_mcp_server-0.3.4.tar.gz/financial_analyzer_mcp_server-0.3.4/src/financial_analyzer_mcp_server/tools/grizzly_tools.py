# financial_analyzer_server/src/financial_analyzer_mcp_server/tools/grizzly_tools.py
# Les imports doivent être absolus depuis le package
from financial_analyzer_mcp_server.server import mcp
from financial_analyzer_mcp_server.utils.financial_calculator import (
    calculate_ratio_and_ma_signal,
    generate_signal_chart_base64
)

@mcp.tool()
def get_grizzly_analysis_with_chart(action_ticker: str, gold_ticker: str) -> str:
    """
    Fournit une analyse complète du signal 'Grizzly' (Actions / Or), incluant
    le signal textuel et un graphique de confirmation visuelle.
    Args:
        action_ticker: Symbole de l'indice ou ETF d'actions (ex: 'SPY' pour S&P 500, '^FCHI' pour CAC40).
        gold_ticker: Symbole de l'actif Or (ex: 'GC=F' pour l'or en USD).
    Returns:
        Une chaîne de caractères formatée en Markdown contenant l'analyse et le graphique.
    """
    # 1. Obtenir l'analyse textuelle
    text_analysis = calculate_ratio_and_ma_signal(action_ticker, gold_ticker, "grizzly")

    # 2. Obtenir le graphique en Base64
    chart_data = generate_signal_chart_base64(action_ticker, gold_ticker, "grizzly")

    # 3. Combiner les deux dans une seule réponse Markdown
    if "error" in chart_data:
        # En cas d'erreur sur le graphique, on renvoie juste le texte avec une note d'erreur
        return f"{text_analysis}\n\n(Impossible de générer le graphique : {chart_data['error']})"
    
    # Formatage de l'URL de données pour l'image
    image_data_url = f"data:{chart_data['mime_type']};base64,{chart_data['data']}"
    
    # Création du message final en Markdown
    final_response = (
        f"{text_analysis}\n\n"
        f"Voici le graphique de confirmation visuelle :\n"
        f"![Graphique d'analyse Grizzly]({image_data_url})"
    )
    
    return final_response
# financial_analyzer_server/src/financial_analyzer_mcp_server/tools/inflation_tools.py
# Les imports doivent être absolus depuis le package
from financial_analyzer_mcp_server.server import mcp
from financial_analyzer_mcp_server.utils.financial_calculator import (
    calculate_ratio_and_ma_signal,
    generate_signal_chart_base64
)

@mcp.tool()
def get_inflation_analysis_with_chart(gold_ticker: str, bond_ticker: str) -> str:
    """
    Fournit une analyse complète du signal d'inflation (Or / Obligations d'État), incluant
    le signal textuel et un graphique de confirmation visuelle.
    Args:
        gold_ticker: Symbole de l'actif Or (ex: 'GC=F' pour l'or en USD).
        bond_ticker: Symbole de l'ETF d'obligations d'État (ex: 'EGB.PA' pour un ETF Euro).
    Returns:
        Une chaîne de caractères formatée en Markdown contenant l'analyse et le graphique.
    """
    # 1. Obtenir l'analyse textuelle
    text_analysis = calculate_ratio_and_ma_signal(gold_ticker, bond_ticker, "inflation")

    # 2. Obtenir le graphique en Base64
    chart_data = generate_signal_chart_base64(gold_ticker, bond_ticker, "inflation")

    # 3. Combiner les deux dans une seule réponse Markdown
    if "error" in chart_data:
        return f"{text_analysis}\n\n(Impossible de générer le graphique : {chart_data['error']})"
    
    # Formatage de l'URL de données pour l'image
    image_data_url = f"data:{chart_data['mime_type']};base64,{chart_data['data']}"
    
    # Création du message final en Markdown
    final_response = (
        f"{text_analysis}\n\n"
        f"Voici le graphique de confirmation visuelle :\n"
        f"![Graphique d'analyse Inflation]({image_data_url})"
    )
    
    return final_response
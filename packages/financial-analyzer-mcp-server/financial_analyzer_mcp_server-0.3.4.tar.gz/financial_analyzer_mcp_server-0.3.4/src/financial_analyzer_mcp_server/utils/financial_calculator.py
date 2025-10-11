# financial_analyzer_server/utils/financial_calculator.py
import yfinance as yf
import pandas as pd
import pandas_ta as ta
from pathlib import Path

# NOUVEAUX IMPORTS pour la génération de graphiques
import matplotlib.pyplot as plt
import io
import base64

# Définition de la longueur de la moyenne mobile par défaut (7 ans * 12 mois)
DEFAULT_MA_LENGTH_MONTHS = 7 * 12
# Définition d'une longueur minimale pour que la MA soit significative (par ex. 3 ans * 12 mois)
MIN_MA_LENGTH_MONTHS = 3 * 12

def get_monthly_close_data(ticker: str, years: int = 20) -> pd.Series:
    """
    Récupère les prix de clôture mensuels pour un ticker donné.
    Utilise 20 ans de données pour s'assurer d'avoir suffisamment pour la MA 7 ans.
    """
    try:
        data = yf.Ticker(ticker).history(period=f"{years}y", interval="1mo")
        if data.empty or 'Close' not in data:
            raise ValueError(f"Aucune donnée de clôture trouvée pour le ticker: {ticker}")
        return data['Close']
    except Exception as e:
        raise RuntimeError(f"Erreur lors de la récupération des données pour {ticker}: {e}")

def get_ratio_and_ma_data(numerator_ticker: str, denominator_ticker: str) -> tuple:
    """
    Récupère les données, calcule le ratio et sa moyenne mobile, et les retourne.
    Retourne un tuple: (DataFrame contenant 'ratio' et 'ratio_ma', message sur la longueur de la MA, erreur_message).
    """
    try:
        price_num = get_monthly_close_data(numerator_ticker)
        price_den = get_monthly_close_data(denominator_ticker)

        # Aligner les données sur le même index temporel et gérer les valeurs manquantes
        combined_prices = pd.DataFrame({'num': price_num, 'den': price_den}).dropna()
        available_length = len(combined_prices)

        ma_length_to_use = DEFAULT_MA_LENGTH_MONTHS
        ma_length_message = f"{DEFAULT_MA_LENGTH_MONTHS} mois (7 ans)"

        # Vérifier si même le minimum de données est disponible
        if available_length < MIN_MA_LENGTH_MONTHS:
            error_msg = (f"Erreur: Données historiques insuffisantes ou non alignées pour {numerator_ticker} et {denominator_ticker}. "
                         f"Nécessite au moins {MIN_MA_LENGTH_MONTHS} points de données pour un calcul significatif, mais seulement {available_length} sont disponibles.")
            return None, None, error_msg

        # Si moins de données que la MA par défaut (7 ans) sont disponibles, ajuster la longueur de la MA
        if available_length < DEFAULT_MA_LENGTH_MONTHS:
            # Ajuster la longueur de la MA à la plus grande multiple de 12 (années)
            # qui est inférieure ou égale à la longueur disponible, mais pas moins que le minimum.
            ma_length_to_use = (available_length // 12) * 12
            if ma_length_to_use < MIN_MA_LENGTH_MONTHS:
                ma_length_to_use = MIN_MA_LENGTH_MONTHS # S'assurer qu'on utilise au moins la longueur minimale
            ma_length_message = f"{ma_length_to_use} mois ({ma_length_to_use // 12} ans) - ajusté car l'historique est limité"
        
        # Calcul du ratio
        ratio = combined_prices['num'] / combined_prices['den']

        # Calcul de la moyenne mobile (SMA) avec la longueur ajustée
        ratio_ma = ta.sma(ratio, length=ma_length_to_use)

        # Assurez-vous que la MA est calculée jusqu'à la dernière période
        if ratio_ma.empty or pd.isna(ratio_ma.iloc[-1]):
            return None, None, "Erreur: Impossible de calculer la moyenne mobile jusqu'à la dernière période avec les données disponibles."

        data_df = pd.DataFrame({'ratio': ratio, 'ratio_ma': ratio_ma}, index=ratio.index).dropna()

        return data_df, ma_length_message, None
    except RuntimeError as e:
        return None, None, f"Erreur de récupération de données: {e}"
    except Exception as e:
        return None, None, f"Une erreur inattendue est survenue lors du calcul: {e}"


def calculate_ratio_and_ma_signal(
    numerator_ticker: str,
    denominator_ticker: str,
    signal_type: str # "inflation" ou "grizzly"
) -> str:
    """
    Calcule le ratio entre deux actifs, sa moyenne mobile et retourne un signal TEXTUEL.
    La longueur de la moyenne mobile est ajustée dynamiquement si les données complètes ne sont pas disponibles.
    """
    data_df, ma_length_message, error = get_ratio_and_ma_data(numerator_ticker, denominator_ticker)
    
    if error:
        return error # Retourne l'erreur directement
        
    current_ratio = data_df['ratio'].iloc[-1]
    current_ma = data_df['ratio_ma'].iloc[-1]
    
    # Génération du signal selon la méthode du livre
    if signal_type == "inflation":
        if current_ratio > current_ma:
            return (f"Analyse Inflation (Ratio {numerator_ticker}/{denominator_ticker}, MA sur {ma_length_message}):\n"
                    f"Ratio actuel ({current_ratio:.4f}) est AU-DESSUS de sa MA ({current_ma:.4f}).\n"
                    f"Cela suggère une période **INFLATIONNISTE**. Privilégiez l'**OR** dans la partie dynamique de votre portefeuille.")
        else:
            return (f"Analyse Inflation (Ratio {numerator_ticker}/{denominator_ticker}, MA sur {ma_length_message}):\n"
                    f"Ratio actuel ({current_ratio:.4f}) est EN-DESSOUS de sa MA ({current_ma:.4f}).\n"
                    f"Cela suggère une période **NON-INFLATIONNISTE**. Privilégiez les **OBLIGATIONS D'ÉTAT** dans la partie dynamique de votre portefeuille.")
    elif signal_type == "grizzly":
        if current_ratio > current_ma:
            return (f"Analyse Grizzly (Ratio {numerator_ticker}/{denominator_ticker}, MA sur {ma_length_message}):\n"
                    f"Ratio actuel ({current_ratio:.4f}) est AU-DESSUS de sa MA ({current_ma:.4f}).\n"
                    f"L'investissement en **ACTIONS** est favorable. Pas de signal 'Grizzly'.")
        else:
            return (f"Analyse Grizzly (Ratio {numerator_ticker}/{denominator_ticker}, MA sur {ma_length_message}):\n"
                    f"Ratio actuel ({current_ratio:.4f}) est EN-DESSOUS de sa MA ({current_ma:.4f}).\n"
                    f"ATTENTION : Signal '**Grizzly**' détecté ! Envisagez de **sortir des ACTIONS** et de vous positionner en **OR et/ou CASH**.")
    else:
        return "Erreur : Type de signal inconnu. Utilisez 'inflation' ou 'grizzly'."

def generate_signal_chart_base64(numerator_ticker: str, denominator_ticker: str, signal_type: str) -> dict:
    """
    Génère un graphique du ratio et de sa moyenne mobile et le retourne
    sous forme d'un dictionnaire contenant les données de l'image en Base64.
    """
    data_df, ma_length_message, error = get_ratio_and_ma_data(numerator_ticker, denominator_ticker)
    
    if error:
        return {"error": f"Impossible de générer le graphique : {error}"}

    # Création du graphique en mémoire
    plt.style.use('seaborn-v0_8-darkgrid')
    fig, ax = plt.subplots(figsize=(12, 7))

    # Ligne rouge pour le ratio et ligne bleue pour la MA
    ax.plot(data_df.index, data_df['ratio'], color='red', linewidth=2, label=f'Ratio {numerator_ticker}/{denominator_ticker}')
    ax.plot(data_df.index, data_df['ratio_ma'], color='blue', linestyle='--', linewidth=2, label=f'Moyenne Mobile ({ma_length_message})')

    # Mise en forme
    title = f"Analyse Visuelle du Signal '{signal_type.capitalize()}' ({numerator_ticker} vs {denominator_ticker})"
    plt.title(title, fontsize=16)
    plt.xlabel("Date", fontsize=12)
    plt.ylabel("Valeur du Ratio", fontsize=12)
    plt.legend(fontsize=10)
    plt.grid(True)
    plt.tight_layout()

    # Sauvegarde du graphique dans un buffer en mémoire
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=100)
    buf.seek(0) # Rembobine le buffer au début

    # Encode le contenu binaire du buffer en Base64
    image_base64 = base64.b64encode(buf.read()).decode('utf-8')
    
    plt.close(fig) # Ferme la figure pour libérer la mémoire
    
    # Retourne un dictionnaire que le client pourra interpréter
    return {
        "mime_type": "image/png",
        "data": image_base64
    }
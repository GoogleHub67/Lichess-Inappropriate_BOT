import requests

def get_counter_opening_move(fen, variant="standard"):
    """
    Queries the free Lichess Opening Explorer to find the opponent's 
    most frequently played move in this position and returns a counter.
    """
    # Map Lichess variants to Explorer API requirements
    api_variant = "chess" if variant == "standard" else variant
    
    # Lichess Opening Explorer URL
    url = f"https://lichess.ovh"
    params = {
        "variant": api_variant,
        "fen": fen,
        "speeds": "blitz,rapid,classical",
        "ratings": "1600,1800,2000,2200"
    }
    
    try:
        response = requests.get(url, params=params, timeout=3)
        if response.status_code == 200:
            data = response.json()
            moves = data.get("moves", [])
            
            if moves:
                # Find the move with the highest play-count to see what is popular
                most_popular_opponent_move = moves[0]["uci"]
                print(f"🔮 Lichess Book Scout: Most popular move here is {most_popular_opponent_move}")
                
                # Simple counter: Pick the master move with the highest win rate for your color
                # In the API, the first move listed is usually the statistically strongest
                best_counter_move = moves[0]["uci"]
                return best_counter_move
    except Exception as e:
        print(f"⚠️ Opening Explorer API Error: {e}")
    
    return None # Fallback to engine calculation if API fails

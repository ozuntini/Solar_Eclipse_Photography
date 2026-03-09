#!/usr/bin/env python3
"""
Générateur de configuration d'éclipse automatique
"""
from datetime import datetime, time
from typing import List, Tuple

def generate_eclipse_config(
    c1: Tuple[int, int, int],
    c2: Tuple[int, int, int], 
    maximum: Tuple[int, int, int],
    c3: Tuple[int, int, int],
    c4: Tuple[int, int, int],
    location: str = "",
    date: str = ""
) -> str:
    """Génère configuration complète pour éclipse"""
    
    config_lines = [
        f"# Éclipse du {date} - {location}",
        f"# Généré le {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "#",
        
        # Configuration times
        f"Config,{c1[0]},{c1[1]},{c1[2]},{c2[0]},{c2[1]},{c2[2]},"
        f"{maximum[0]},{maximum[1]},{maximum[2]},{c3[0]},{c3[1]},{c3[2]},"
        f"{c4[0]},{c4[1]},{c4[2]},1",
        
        "",
        "# Vérifications pré-vol",
        "Verif,3,0,80,5000",
        "",
        
        "# Séquence photographique automatique",
        "Photo,C1,-,0,2,0,-,-,-,8,100,1,0",
        "Boucle,C2,-,0,1,0,-,0,0,10,5,5.6,400,0.002,0", 
        "Interval,C2,+,0,0,10,C3,-,0,0,10,20,2.8,1600,0.001,1000",
        "Photo,Max,-,-,-,-,-,-,-,4,800,2,2000",
        "Boucle,C3,-,0,0,30,+,0,1,0,10,5.6,400,0.002,0",
        "Photo,C4,-,0,2,0,-,-,-,8,100,1,0"
    ]
    
    return '\n'.join(config_lines)

# Exemple d'utilisation
if __name__ == "__main__":
    # Éclipse du 8 avril 2024 (exemple)
    config = generate_eclipse_config(
        c1=(18, 10, 29),
        c2=(19, 27, 3), 
        maximum=(19, 28, 23),
        c3=(19, 29, 43),
        c4=(20, 46, 31),
        location="Texas, USA",
        date="2024-04-08"
    )
    
    with open('eclipse_2024_04_08.txt', 'w') as f:
        f.write(config)
    
    print("✅ Configuration générée: eclipse_2024_04_08.txt")
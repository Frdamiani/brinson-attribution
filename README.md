# brinson-attribution

Outil d'attribution de performance pour un portefeuille multi-actifs (actions, obligations, monétaire).

Le modèle Brinson-Hood-Beebower décompose la surperformance ou sous-performance d'un portefeuille par rapport à son benchmark en trois effets :
- **Allocation** : l'impact des choix de pondération par classe d'actifs
- **Sélection** : l'impact du choix des titres au sein de chaque classe
- **Interaction** : l'effet combiné des deux

Les données de marché sont récupérées automatiquement via yfinance. L'interface permet de saisir les poids du portefeuille et du benchmark, de choisir la période d'analyse, et visualise les résultats sous forme de tableau et de graphiques.

## Lancement

```bash
pip install yfinance matplotlib numpy pandas
python attribution_performance.py
```

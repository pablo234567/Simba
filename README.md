# Cotes 1N2 → 120 min → Expected Points MPP

Outil pour parieurs / joueurs **MonPetitProno**.

1. Tu entres les **cotes 1N2** d'un match (temps réglementaire, 90 min).
2. L'app retire la marge du bookmaker et déduit les **probabilités réelles** 90 min.
3. Elle ajuste un **modèle de Poisson** (λ domicile / λ extérieur) puis **extrapole les
   probabilités sur 120 min** : la prolongation (30 min = ⅓ de match) ne se joue que
   sur les matchs nuls après 90 min, ce qui décante une partie des nuls.
4. Tu entres les **points MPP** par issue, et l'app calcule les **expected points**
   (`points × proba 120 min`) et te dit quel pari maximise l'espérance.

Tout le calcul se fait côté navigateur (instantané, aucune API).

## Lancer en local

```bash
pip install -r requirements.txt
python app.py
# http://localhost:5000
```

## Déploiement

Configuré pour Render (`render.yaml` / `Procfile`, via gunicorn).

## Modèle

- **Probabilités 90 min** : `p_i = (1/cote_i) / Σ(1/cote)` (normalisation proportionnelle).
- **Ajustement Poisson** : on cherche `λ_dom`, `λ_ext` tels que les issues 1/N/2 de deux
  Poisson indépendants reproduisent les probas 90 min (recherche sur grille + raffinage).
- **Prolongation** : mini-match de 30 min avec `λ × (30/90)`, ajustable via le facteur
  d'intensité. `P(1 à 120) = P(1) + P(N)·P(dom gagne la prolongation)`, idem pour 2,
  et `P(N à 120) = P(N)·P(prolongation nulle)` → tirs au but.

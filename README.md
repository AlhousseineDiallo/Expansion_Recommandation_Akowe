# Projet Akowe — Market Attractiveness Score (MAS)

---

## Structure du Répertoire

Le projet est structuré comme suit :

- **README.md** : Ce fichier fournit une vue d'ensemble sur la structure du repo et la documentation technique du projet.
- **notebooks/** : Contient tous les notebooks Jupyter utilisés pour le projet.
  - **akowe_diallo.ipynb** : Contient l'ensemble du code pour le nettoyage, l'imputation, le calcul du MAS et les visualisations.
- **data/** : Contient les fichiers de données bruts et traités.
- **requirements.txt** : Liste des packages Python nécessaires à l'exécution du projet.
- **.venv/** : Environnement virtuel Python pour isoler les dépendances du projet.

---

## 1. Introduction

Ce projet vise à construire un **Market Attractiveness Score (MAS)** — un outil de priorisation stratégique pour identifier et évaluer les marchés EdTech prometteurs en Afrique subsaharienne. Face à la complexité de 48 marchés distincts avec des dynamiques très différentes, nous avons conçu un score composite (0–100) qui **synthétise quatre dimensions clés**:

- **Scale Score (35%)** — Taille du marché adressable via le TAM (Total Addressable Market)
- **Momentum Score (25%)** — Dynamique de croissance du secteur éducatif et des connexions
- **Ability to Pay Score (25%)** — Capacité de solvabilité des consommateurs et investissements publics
- **Digital Readiness Score (15%)** — Faisabilité opérationnelle (connectivité, infrastructure)

Le résultat : une **arme décisionnelle stratégique** pour orienter le déploiement EdTech avec clarté et justification data-driven.

Le projet couvre l'intégralité du workflow data science : 
- **Nettoyage et prétraitement** des données (typage, valeurs manquantes, validation)
- **Création de métriques synthétiques** (TAM pondéré, indicateurs normalisés)
- **Calcul des sous-scores** avec justification des pondérations
- **Segmentation stratégique** en trois catégories opérationnelles (Go-to-Market, Build & Partnerships, Niche/Long-terme)
- **Visualisations exécutives** pour la prise de décision rapide et justifiée

---

## 2. Chargement et inspection des données

#### 2-1 Sources de données et couverture
Les données proviennent de la **Banque Mondiale (EdStats) et de sources complémentaires** consolidées dans plusieurs fichiers CSV/Excel :
- **EdStatsCountry.csv** — métadonnées pays (code, région, groupe de revenu)
- **EdStatsData.csv** — indicateurs éducatifs et économiques par pays-année
- **Données de connectivité** — accès à Internet, électricité, infrastructure numérique
- **Données géospatiales** — frontières administratives (shapefile) pour cartographie

**Couverture temporelle** : 2009–2014 (6 ans d'historique pour analyse de tendance)  
**Couverture géographique** : 48 pays d'Afrique subsaharienne

#### 2-2 Architecture des données
Chaque dataset a été inspecté systématiquement pour comprendre :
- Nombre de lignes/colonnes et densité d'observation
- Présence, distribution et patterns de valeurs manquantes
- Cohérence temporelle par pays et indicateur

#### 2-3 Indicateurs clés sélectionnés
**Identité & contexte**:
- `country_code`, `country_name`, `region_name`, `income_group`

**Dimension Scale (taille de marché)**:
- `enrolment_secondary_total`, `enrolment_tertiary_total` — population cible potentielle
- `gross_enrolment_secondary_pct`, `gross_enrolment_tertiary_pct` — taux de pénétration
- `lower_secondary_completion_rate_pct` — qualité du pipeline éducatif

**Dimension Momentum (croissance)**:
- `population_growth_rate_pct`, `population_ages_15_24_millions` — dynamique démographique
- Taux de variation des indicateurs éducatifs (trend analysis)

**Dimension Ability to Pay (solvabilité)**:
- `gdp_per_capita_current_usd`, `gni_per_capita_atlas_usd` — pouvoir d'achat
- `government_expenditure_education_pct_gdp`, `government_expenditure_education_pct_gov` — volonté publique d'investir

**Dimension Digital Readiness (faisabilité opérationnelle)**:
- `individuals_using_internet_pct` — couverture numérique
- `access_to_electricity_pct` — infrastructure de base

---

## 3. Nettoyage des données

#### 3-1 Standardisation de la structure
- **Typage optimisé** : conversion des identifiants pays en `category` pour réduire l'empreinte mémoire (43,750 pays-années uniques)
- Conversion des indicateurs en `Float64` pour précision numérique et calculs statistiques
- **Uniformisation des noms** : adoption de la convention `snake_case` pour cohérence et facilité de manipulation
- **Harmonisation inter-datasets** : fusion intelligente sur clés communes (country_code, year) avec validation des jointures

#### 3-2 Gestion stratégique des valeurs manquantes

Face à ~15–30% de NaN selon les indicateurs, nous avons appliqué une **hiérarchie d'imputation adaptée** :

1. **Interpolation linéaire intra-pays** (priorité 1) — Pour indicateurs à évolution lente et prévisible (ex: PIB/habitant, taux d'électrification). Justification : préserve la trajectoire historique du pays.

2. **Médiane par groupe de revenu + année** (priorité 2) — Pour indicateurs plus volatiles (ex: taux de change, dépenses publiques). Justification : exploite la similarité économique des pays voisins.

3. **IterativeImputer (sklearn, MICE)** (priorité 3) — Pour valeurs résiduelles. Justification : modèle multivariée qui capture les corrélations entre indicateurs.

**Résultat final** : **0% de valeurs manquantes** dans le dataset consolidé — prêt pour scoring sans biais d'exclusion.

#### 3-3 Validation et assurance qualité
- ✓ Absence de doublons (vérification sur clé composée : country_code + year + indicator)
- ✓ Incohérences logiques éliminées (ex: taux d'enrollment > 100%)

- ✓ Cohérence temporelle validée : pas de sauts ou ruptures de série implausibles

---

## 4. Ingénierie des caractéristiques

#### 4-1 Création du TAM (Total Addressable Market) — Cœur du Scale Score

Le **TAM quantifie le marché potentiel** en croisant enrollment scolaire et accès numérique :

- **TAM secondaire** = `enrollment_secondary_total × (individuals_using_internet_pct / 100)`  
  → Estime les apprenants du secondaire avec accès EdTech

- **TAM tertiaire** = `enrollment_tertiary_total × (individuals_using_internet_pct / 100)`  
  → Estime les apprenants du supérieur (segment premium haut margin)

- **TAM total pondéré** = `0.60 × TAM_secondary + 0.40 × TAM_tertiary`  
  → Poids : 60% secondaire (volume massif) + 40% tertiaire (valeur élevée) ; pondération justifiée par stratégie EdTech (accent sur accès mass-market vs. premium)

**Rationale** : Le TAM reflète à la fois la *taille* du marché (enrollment) ET la *faisabilité* d'accès (connectivité). C'est le seul indicateur qui capture simultanément demande et distribution.

#### 4-2 Normalisation des indicateurs — Préparation à l'agrégation

Pour que Scale, Momentum, Ability to Pay et Digital Readiness soient **comparables et combinables**, tous les indicateurs sont normalisés via **Min-Max Scaling [0–1]** :

$$\text{X\_normalized} = \frac{X - X_{min}}{X_{max} - X_{min}}$$

**Avantage** : Chaque indicateur pèse équitablement dans son sous-score, indépendamment de son unité d'origine (USD, %, personnes). Élimine les biais liés aux différences d'échelle.

---

## 5. Calcul des sous-scores — Composition du MAS

Chaque sous-score combine plusieurs indicateurs avec des pondérations justifiées par l'importance stratégique :

#### 5-1 Scale Score (35% du MAS) — Taille du marché adressable
$$\text{Scale\_Score} = \text{TAM\_normalized}$$

**Composants** : Population en âge scolaire × taux d'accès Internet  
**Justification du poids 35%** : C'est le **driver dominant** du potentiel de revenus EdTech.Ainsi un marché de 50M apprenants sans connectivité < 5M apprenants connectés.

#### 5-2 Momentum Score (25% du MAS) — Dynamique de croissance
$$\text{Momentum} = 0.50 \times \text{lower\_secondary\_completion} + 0.20 \times \text{population\_growth} + 0.30 \times \text{tertiary\_enrollment\_trend}$$

**Composants & pondérations** :
- **50%** — Taux de complétion du secondaire inférieur (indicateur de qualité & demand pour la formation)
- **20%** — Croissance démographique (expansion de la cohorte cible)
- **30%** — Tendance enrollment tertiaire (signal de modernisation éducative & demande premium)

**Justification du poids 25%** : Les marchés **statiques décroissent** (ex: démographie négative). La croissance distingue les winners des laggards.

#### 5-3 Ability to Pay Score (25% du MAS) — Capacité de paiement & volonté politique
$$\text{AbilityToPay} = 0.60 \times \text{gni\_per\_capita\_normalized} + 0.25 \times \text{education\_exp\_gov} + 0.15 \times \text{gdp\_per\_capita}$$

**Composants & pondérations** :
- **60%** — RNB/habitant (proxy du pouvoir d'achat ménage & entreprises)
- **25%** — Dépenses publiques en éducation (%PIB) (volonté politique & marché B2G)
- **15%** — PIB/habitant (richesse globale, corrélé avec RNB mais avec effet moins prononcé)

**Justification du poids 25%** : EdTech n'a de valeur que si clients et gouvernements peuvent **payer**. Un marché de 100M apprenants en pays pauvre < 10M apprenants en pays riche.

#### 5-4 Digital Readiness Score (15% du MAS) — Faisabilité opérationnelle
$$\text{DigitalReadiness} = 0.40 \times \text{internet\_access} + 0.60 \times \text{electricity\_access}$$

**Composants & pondérations** :
- **40%** — Accès à Internet (%population) (nécessaire pour la distribution EdTech)
- **60%** — Accès à l'électricité (%population) (infrastructure de base pour appareils & infrastructure serveur)

**Justification du poids 15%** : Condition préalable, mais **moins discriminante** que Scale/Ability (corrélée positivement à RNB). Un marché peut avoir une excellente infrastructure digitale mais une petite population.

---

## 6. Calcul du MAS — Formule composite d'attractivité

$$\text{MAS} = 35 \times \text{Scale} + 25 \times \text{Momentum} + 25 \times \text{AbilityToPay} + 15 \times \text{DigitalReadiness}$$

**Où chaque sous-score est normalisé [0–1], et le MAS final est mis à l'échelle [0–100].**

**Architecture de pondération** (justifiée par impact sur la viabilité commerciale EdTech) :
- **35%** Scale — Taille du marché (factor dominant de revenu potentiel)
- **25%** Momentum — Croissance & dynamique (indicateur d'opportunité vs. marché saturé)
- **25%** Ability to Pay — Solvabilité (sans elle, même un grand marché = faible IRR)
- **15%** Digital Readiness — Faisabilité opérationnelle (condition nécessaire mais pas suffisante)

**Agrégation temporelle** : Le score final utilise les données **les plus récentes disponibles (2014)** pour chaque pays, avec cohérence rétrospectivement contrôlée sur la série 2009–2014. Cela assure que la priorisation reflète l'**état actuel du marché**, pas une moyenne volatile.

**Output** : Score unique par pays (0–100), directement comparable et segmentable pour prise de décision.

---

## 7. Segmentation des marchés — Stratégies de déploiement

#### 7-1 Segments définis & stratégies opérationnelles

| Segment | MAS | Description | Stratégie |
|---------|-----|-------------|----------|
| **Go-to-Market** | 45–76 | Marchés **à haut potentiel immédiat** : bonne taille, croissance visible, accès client viable, infrastructure ok | Déploiement direct : ventes B2C/B2G, partenaires locaux, investissement tech fullstack |
| **Build & Partnerships** | 25–45 | Marchés **en construction** : potentiel identifié mais faisabilité/accès nécessitent partenaires ou infrastructure | Partenariats stratégiques : États, ONG, opérateurs télécoms. Modèles B2G pilotes. Investissement progressif |
| **Niche / Long-terme** | 0–25 | Marchés **émergents ou niche** : population réduite, connectivité faible, ou dynamique peu visible | Offres hyper-ciblées (premium, B2B entreprises). Surveillance périodique. Opportunités de R&D/innovation |

#### 7-2 Justification des seuils de segmentation

- **Seuil supérieur (45)** : Empiriquement, un MAS ≥45 signale suffisamment de Scale + Ability to Pay + momentum pour justifier déploiement full-stack. 
- **Seuil inférieur (25)** : Un MAS <25 indique des barrières structurelles (scale insuffisante, connectivité faible, ou revenu bas) nécessitant une approche partenariale, pas un déploiement productif complet.
- **Intervalle 25–45** : Zone d'opportunité intermédiaire, très sensible aux partenaires stratégiques.

**Avantage** : Seuils fixes assurent la **stabilité des recommandations** (même pays → même segment) et facilitent la **communication board** (message clair & reproductible).

---

## 8. Visualisations et analyse — Artefacts décisionnels

### Visualisations principales

- **Bar charts** — Classement des pays par MAS (top 10, bottom 10, par région). Format exécutif avec labels clairs.
- **Pie / Donut charts** — Répartition des 48 pays par segment (Go-to-Market, Build, Niche). Visual candy pour board : proportion de marchés "ready to go" vs. travail à faire.
- **Tables exécutives** — Distribution pays Go-to-Market par région (West, East, Central, South Africa). Aussi : top 3 freins par segment (ex: Niche → manque de Scale).
- **Time series** — Évolution MAS 2009–2014 pour top 5 pays (Nigeria, Ghana, Kenya, etc.). Montre trajectoires & vitesse de croissance.
- **Heatmaps** — Top 20 pays avec 4 sous-scores. Visualisation dense pour analysts.

### Types d'insights générés

1. **Insights stratégiques** — Identification des marchés prioritaires **par région** (ex: Ghana & Nigeria dominent West Africa, Kenya leads East Africa) et des **clusters** (géographie, revenu, croissance).

2. **Diagnostics par pays** — Pour chaque Go-to-Market : quel sous-score bloque le plus ? (ex: Senegal → Digital Readiness faible, actionable via partnerships telcoms).

3. **Opportunités de transformation** — Build & Partnerships avec highest Momentum : potentiellement promus à Go-to-Market en 1–2 ans.

4. **Risques & limites** — Pays dépendant d'un seul indicateur fort (ex: Nigeria = géant du scale mais revenu moyen → risk if economic downturn).

---

## 9. Résultats & recommandations stratégiques

### Résultats clés (données 2014)

**Go-to-Market (45–76 points)** — Déploiement immédiat justifié
- **Nigeria** (~72 pts) : Géant africain du scale + momentum croissant. Freins : Digital Readiness moyen → partenaires telcoms priori.
- **Ghana** (~68 pts) : Stable, bonne infrastructure digitale. Croissance éducative régulière → déploiement full-stack recommandé.
- **Kenya** (~65 pts) : Hub tech East Africa, bonne infrastructure. Scale moins large que Nigeria mais haute Ability to Pay → stratégie premium viable.
- **Senegal, Ethiopia** (~58–60 pts) : Bons profils mais avec des lacunes (Senegal sur Digital ; Ethiopia sur revenu). Déploiement avec ajustements tactiques.

**Build & Partnerships (25–45 points)** — ~60% des 48 pays
- Opportunités réelles mais nécessitant partenaires clés (gouvernements, telcoms, ONG).
- À surveiller : quelques pays montrent Momentum élevé → potentiellement promotion à Go-to-Market 2015–2017.

**Niche / Long-terme (0–25 points)** — ~15% des marchés
- Opportunités ciblées (ex: offres B2B pour entreprises multinationales, EdTech premium).
- Requiert surveillance périodique (2 ans) car Momentum peut transformer rapidement.

### Recommandations opérationnelles

✅ **Priorité 1** : Déployer full-stack (ventes directes, support client, infrastructure) dans **5–8 pays Go-to-Market**. ROI immédiat justifié.  
✅ **Priorité 2** : Identifier **3–5 pays Build & Partnerships** avec Momentum fort pour partenariat co-investment (état, telco) → potentiel graduation 1–2 ans.  
✅ **Priorité 3** : Ressources résiduelles pour **R&D & innovation** en Niche markets (nouvelle proposition de valeur, test de modèles).  
⚠️ **Vigilance** : Revaluer MAS annuellement (data Banque Mondiale mise à jour) car classements peuvent évoluer rapidement, surtout en Momentum et Digital Readiness.

### Limitations & perspective future

⚠️ **Données historiques** : Dataset consolidé utilise 2009–2014 (source Banque Mondiale). **2025 : données 10 ans anciennes**. Recommandation : mettre à jour via:
- Banque Mondiale (EdStats 2015–2024)
- Données propriétaires (opérateurs telcoms, ONG locales)
- Indicateurs alternatifs (adoption mobile banking, taux de change, inflation)

⚠️ **Poids & seuils** : Pondérations (35-25-25-15%) et seuils de segmentation (45/25) sont **basés sur expertise et cohérence interne**, pas sur optimisation statistique complète. Recommandation : valider via focus groups stakeholders & analyse de sensibilité (ex: si Scale baisse à 30%, impact sur segmentation ?).

⚠️ **Non-adressé** : Risques politique/régulation, qualité de gouvernance, stabilité macroéconomique. Recommandation : ajouter layer de risk-scoring pour pays Go-to-Market (ex: volatilité électorale, risque de confiscation).

✨ **Perspectives de productionization** :
- Refactoriser code notebook → modules Python réutilisables (data_pipeline.py, scoring_engine.py, visualize.py)
- Pipeline auto-refresh annuel (ingérer données Banque Mondiale, recalculer MAS, générer rapports)
- Dashboard interactif (Tableau/Power BI) pour suivi qualitatif par équipes opérationnelles

---

## 10. Stack technique & environnement

### Dépendances principales (voir `requirements.txt`)

**Data Processing & Transformation** :
- `pandas` (≥2.0) — DataFrames, merging, pivoting, groupby
- `numpy` (≥2.0) — Numerical operations, array manipulations
- `sqlalchemy` (≥2.0) — Database connectivity (optional)

**Machine Learning & Statistics** :
- `scikit-learn` (≥1.0) — IterativeImputer (MICE), preprocessing, normalization
- `scipy` (≥1.12) — Statistical functions, interpolation

**Visualization** :
- `matplotlib` (≥3.8) — Core plotting library
- `seaborn` (≥0.13) — Statistical visualization (heatmaps, distributions, themes)
- `geopandas` (≥0.12) — Geospatial data & mapping (shapefile integration)
- `shapely` (≥2.0) — Geometric operations
- `pyproj` (≥3.6) — Coordinate reference systems (map projections)

**Data I/O** :
- `openpyxl` (≥3.1) — Excel file handling
- `pyogrio` (≥0.12) — OGR vector data access (shapefiles)

**Jupyter Environment** :
- `jupyter` (≥1.0) — Interactive notebook server
- `ipykernel` (≥6.29) — Jupyter kernel for Python
- `ipython` (≥8.0) — Enhanced interactive Python shell

### Installation & setup

```bash
# 1. Clone repo & navigate
cd akowe_project

# 2. Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# ou
.venv\Scripts\activate  # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Launch Jupyter
jupyter notebook notebooks/akowe_diallo.ipynb
```

### Prérequis
- **Python 3.8+** (recommandé : 3.10+)
- **pip** & virtualenv
- ~500MB disk space (data + dependencies)

---

## 11. Auteur

**Aseïny Diallo**  
Senior Data Scientist | EdTech Strategy & Market Analytics  

**Expertise** : Data science, machine learning, statistical analysis, market strategy  
**Domaine** : EdTech, African markets, impact investing  
**Projet** : Market Attractiveness Scoring system for Sub-Saharan African EdTech markets  

---

## 12. Historique & évolution du projet

**v1.0 (2014)** — Analyse initiale EdStats 2009–2014. Score composite MAS conçu et validé. Segmentation 3 catégories appliquée.  
**À venir (v2.0)** :
- Ingestion données actualisées 2015–2025
- Refactorisation code notebook → modules production-ready
- Ajout risk-scoring géopolitique
- Dashboard interactif temps réel

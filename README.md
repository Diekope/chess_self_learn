# Chess Self-Learn ♟️

Une application d'échecs locale et professionnelle conçue pour l'apprentissage et le perfectionnement, propulsée par Python et le moteur Stockfish.

## ✨ Fonctionnalités

### 🧠 Apprentissage & Coaching
- **Mode Évaluation en temps réel** : Analyse instantanée de vos coups par Stockfish.
- **Icônes de Qualité** : Visualisez la force de vos coups (Brillant, Best, Book, Mistake, Blunder).
- **Flèches Correctives** : Affichage automatique du meilleur coup manqué en cas d'erreur.
- **Commentaires Intelligents** : Feedback textuel dynamique sur vos choix stratégiques.
- **Détection des Ouvertures** : Identification en temps réel de plus de 50 ouvertures et variantes célèbres.

### 🎮 Expérience de Jeu Pro
- **Moteur Stockfish Intégré** : Niveaux de difficulté allant de **200 ELO** à **3000+ ELO**.
- **Contrôles Intuitifs** : Drag-and-drop fluide avec visualisation de la pièce en mouvement.
- **Premove** : Préparez vos coups pendant que l'adversaire réfléchit.
- **Système de Promotion** : Dialogue interactif pour choisir votre pièce de promotion.
- **Historique PGN** : Liste complète des coups joués en notation algébrique.

### 🛠️ Outils Avancés
- **Mode Revue (Navigation temporelle)** : `Cmd + Z` pour remonter dans la partie et explorer des variantes sans affecter le score réel. `Esc` pour revenir au direct.
- **Analyse de Fin de Partie** : Rapport complet avec pourcentage de précision et décompte de la qualité des coups.
- **Flèches Personnalisées** : Clic droit + glisser pour dessiner vos propres plans tactiques.
- **Barre d'Évaluation** : Indicateur visuel de l'avantage matériel et positionnel.
- **Thèmes Visuels** : Choisissez entre plusieurs styles de plateaux (Classic, Wood, Blue, Dark).
- **Effets Sonores** : Sons immersifs pour les déplacements, captures, échecs et gaffes.

## 🚀 Installation

### Prérequis
- Python 3.9+
- Stockfish (installable via Homebrew sur Mac : `brew install stockfish`)

### Configuration
1. Clonez le dépôt :
   ```bash
   git clone https://github.com/VOTRE_NOM/chess_self_learn.git
   cd chess_self_learn
   ```
2. Créez et activez un environnement virtuel :
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Installez les dépendances :
   ```bash
   pip install -r requirements.txt
   ```

## 🏃 Lancement
```bash
python main.py
```

## 📝 Technologies
- **Logic** : `python-chess`
- **UI** : `PyQt6`
- **Engine** : `Stockfish`
- **Audio** : `QtMultimedia`

---
Développé avec ❤️ pour les passionnés d'échecs qui veulent progresser localement.

# Préparation pour l'oral

## Présentation des livrables

### Fonctionnalités principales
- **Authentification** :
  - Les utilisateurs peuvent se connecter avec un nom d'utilisateur et un mot de passe.
  - Les mots de passe sont sécurisés avec un hachage Argon2.
  - Utilisation de JWT pour gérer les sessions utilisateur.

- **Création de nouveaux utilisateurs** :
  - Les utilisateurs peuvent être créés par le département gestion.
  - Les rôles et permissions sont attribués automatiquement.

- **Lecture et modification des données** :
  - Les clients, contrats, et événements peuvent être consultés et modifiés via l'interface CLI.
  - Les permissions sont vérifiées avant chaque action.

---

## Démonstration technique

### Schéma de la base de données
- **Structure** :
  - Les modèles principaux sont `User`, `Customer`, `Contract`, et `Event`.
  - Les relations entre les modèles sont définies avec SQLAlchemy (ex. `User` -> `Customer`, `Contract` -> `Event`).

### Sécurité et bonnes pratiques
- **Protection contre les injections SQL** :
  - Utilisation de SQLAlchemy pour éviter les requêtes SQL brutes.

- **Validation des données utilisateur** :
  - Les données sont validées avant d'être insérées dans la base.

- **Gestion des permissions** :
  - Les permissions sont vérifiées avant chaque action critique.

- **Hachage des mots de passe** :
  - Les mots de passe sont salés et hachés avec Argon2 pour une sécurité optimale.

- **Gestion des jetons JWT** :
  - Les jetons sont signés et expirent après un délai défini.

---

## Réponses aux questions potentielles

### Pourquoi avoir choisi cette architecture ?
- **Séparation des responsabilités** :
  - Les services gèrent la logique métier.
  - Les repositories gèrent l'accès aux données.
  - L'interface CLI est responsable de l'interaction utilisateur.

- **Facilité de maintenance** :
  - Chaque couche est indépendante, ce qui facilite les modifications futures.

### Comment avez-vous sécurisé l'application ?
- **Mots de passe** :
  - Hachage avec Argon2.
- **Permissions** :
  - Vérification des permissions avant chaque action.
- **JWT** :
  - Utilisation de jetons pour l'authentification persistante.
- **Variables d'environnement** :
  - Les informations sensibles (ex. mots de passe DB) sont stockées dans un fichier `.env`.

### Quelles bonnes pratiques avez-vous suivies ?
- Respect des conventions PEP8.
- Tests unitaires avec `pytest`.
- Documentation des méthodes et classes.

---

## Conseils pour l'oral
- **Structure de la présentation** :
  - Commence par une introduction claire du projet.
  - Explique les fonctionnalités principales.
  - Décris les choix techniques et les bonnes pratiques suivies.

- **Démonstration** :
  - Prépare des exemples concrets (ex. création d'un utilisateur, lecture d'un contrat).
  - Montre le fonctionnement de l'authentification et des permissions.

- **Anticipe les questions** :
  - Prépare des réponses sur les choix techniques et les points de sécurité.

Bonne chance pour ton oral ! 🎉
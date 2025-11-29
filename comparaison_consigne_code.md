# Comparaison entre les consignes et le code

## Étape 1 : Mise en place de l'environnement SQL et Python
- **Consigne** : Utiliser PostgreSQL, SQLAlchemy, et un compte utilisateur non privilégié.
  - **Code** :
    - Utilisation de MySQL au lieu de PostgreSQL.
    - SQLAlchemy est bien utilisé comme ORM.
    - Les informations de connexion sont gérées via des variables d'environnement (fichier `.env`), ce qui respecte les bonnes pratiques.
  - **Manque** :
    - PostgreSQL n'est pas utilisé comme demandé.

## Étape 2 : Définir les modèles et implémentation dans la base
- **Consigne** : Créer des modèles pour les clients, contrats, et événements.
  - **Code** :
    - Les modèles `Customer`, `Contract`, et `Event` sont bien définis avec SQLAlchemy.
    - Les relations entre les modèles sont correctement établies.
  - **Manque** :
    - Aucun diagramme ERD n'est fourni.

## Étape 3 : Créer les comptes utilisateurs et permissions
- **Consigne** : Implémenter des rôles et permissions.
  - **Code** :
    - Les rôles (`Role`) et permissions (`Permission`) sont bien définis dans la base de données.
    - Les mots de passe sont salés et hachés avec Argon2.
  - **Manque** :
    - Les rôles sont bien implémentés, mais il n'y a pas de documentation claire sur leur utilisation.

## Étape 4 : Authentification et autorisation
- **Consigne** : Implémenter une authentification persistante avec JWT.
  - **Code** :
    - Utilisation de JWT pour l'authentification.
    - Les jetons sont créés avec une date d'expiration.
  - **Manque** :
    - Gestion des jetons expirés non implémentée.

## Étape 5 : Lecture des données
- **Consigne** : Permettre la lecture des clients, contrats, et événements.
  - **Code** :
    - Les services permettent de lire les données avec des permissions appropriées.
  - **Manque** :
    - Vérification des permissions parfois répétée dans plusieurs services.

## Étape 6 : Création et mise à jour des données
- **Consigne** : Permettre la création et la mise à jour des clients, contrats, et événements.
  - **Code** :
    - Les services gèrent correctement la création et la mise à jour.
    - Les validations sont effectuées avant l'écriture dans la base.
  - **Manque** :
    - Les validations pourraient être centralisées pour éviter les répétitions.

## Étape 7 : Interface en ligne de commande
- **Consigne** : Créer une interface CLI pour gérer les données.
  - **Code** :
    - L'interface CLI est bien implémentée avec `click`.
    - Les menus pour les utilisateurs, clients, contrats, et événements sont fonctionnels.
  - **Manque** :
    - Les messages d'erreur pourraient être plus explicites.

## Étape 8 : Journalisation avec Sentry
- **Consigne** : Ajouter la journalisation des erreurs avec Sentry.
  - **Code** :
    - Aucune implémentation de Sentry n'est présente.
  - **Manque** :
    - Ajouter Sentry pour capturer les erreurs et exceptions.

---

## Recommandations générales
- Ajouter un diagramme ERD pour mieux visualiser les relations entre les modèles.
- Implémenter la gestion des jetons expirés.
- Centraliser les validations pour éviter les répétitions.
- Ajouter Sentry pour la journalisation des erreurs.
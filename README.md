# Epic Events CRM

Application CRM CLI pour gérer des clients, contrats et événements. 
L'application est conçue pour être utilisée en ligne de commande (CLI) et intègre une gestion des utilisateurs avec rôles et permissions.

## Principales fonctionnalités

- **Interface CLI** : `cli.main` lance une réinitialisation complète de la base puis un menu principal piloté par les permissions (`PermissionService`) affichant les vues clients/contrats/évènements et la gestion des utilisateurs.
- **Domaines SQLAlchemy** : modèles `User`, `Role`, `Permission`, `Customer`, `Contract`, `Event` versionnés avec un mixin de timestamps. Les repositories exposent les opérations CRUD et restent agnostiques sur la logique métier.
- **Services applicatifs** : `CustomerService`, `ContractService`, `EventService`, `AuthService`, `PermissionService` orchestrent la validation (Pydantic), la vérification d'appartenance et les règles de gestion avant d'appeler les repositories.
- **Authentification & tokens** : `AuthService` sait créer/verifier des JWT (Argon2 + PyJWT) et sécuriser les mots de passe.
- **Base de données** : initialisation via `app.db.init_db` avec un seeding complet (rôles, permissions, utilisateurs, contrats, événements) et via la commande CLI qui droppe/crée/seed la base à chaque lancement.

## Stack technique
- Python 3.13
- SQLAlchemy + PyMySQL pour MySQL
- Click pour la CLI
- Pydantic (schemas) pour la validation des données
- Argon2 pour le hachage des mots de passe
- PyJWT pour la gestion des tokens JWT
- Sentry SDK pour capturer les erreurs
- Tests unitaires avec pytest (+ pytest-cov)

## Installation & configuration
1. Cloner le dépôt 

2. Installer les dépendances : `poetry install`

3. Créer un `.env` à la racine du projet et définir les variables suivantes :
	```env
	DB_HOST=localhost
	DB_PORT=3306
	DB_USER=root
	DB_PASS=...
	DB_NAME=epic_events
	JWT_SECRET=une_cle_secrete
	JWT_ALGORITHM=HS256
	JWT_EXP_SECONDS=3600
	```
4. Initialiser la base de données MySQL (créer la base `epic_events`).
Pour cela, vous pouvez utiliser un client MySQL ou la ligne de commande :
    ```sql
    CREATE DATABASE epic_events CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
    CREATE USER 'root'@'localhost' IDENTIFIED BY '...'; -- Remplacez '...' par votre mot de passe
    GRANT ALL PRIVILEGES ON epic_events.* TO 'root'@'localhost';
    FLUSH PRIVILEGES;
    ```

## Lancer l'application
1. Initialiser la base et démarrer l'interface :
	```bash
	poetry run python -m main run
	```
2. Se connecter avec l'un des comptes générés pendant le seed :
	- Management : `manager1` / `password`
	- Sales : `sales2` / `password`
	- Support : `support1` / `password`
	Chaque rôle verra les sections du menu qui correspondent à ses permissions (`PermissionService.available_menus_for_user`).

## Base de données & seed
- L'initialisation crée les tables SQLAlchemy, les rôles/permissions, trois sales, deux managers, deux supports, des clients, contrats et événements liés.
- Les seeds détaillés se trouvent dans `app.db.init_db.seed`, notamment la distribution des contrats/événements par utilisateur.
- La base de données est recréée à chaque lancement de l'application afin de garantir un état propre pour les tests et le développement.

## Testing
- Lancer la suite : `poetry run pytest`


## Structure utile
- `app/models` : définitions SQLAlchemy + mixins
- `app/repositories` : accès DB CRUD
- `app/services` : logique métier & validations
- `cli/views` : menus spécifiques (users/customers/contracts/events)
- `cli/crm_interface.py` : orchestration de l'interface (login, boucle de menu)
- `tests/units` : scénarios unitaires indépendants de la base réelle

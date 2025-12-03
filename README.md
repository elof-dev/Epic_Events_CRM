# Epic Events CRM

Application CLI minimaliste construite pour l'école ; elle permet d'explorer un CRM fictif couvrant les rôles management / sales / support et la chaîne clients → contrats → événements. L'accent est mis sur une architecture modulaire (models, repositories, services) et sur des permissions fines sans over-engineering.

## Principales briques
- **Interface CLI** : `cli.main` lance une réinitialisation complète de la base puis un menu principal piloté par les permissions (`PermissionService`) affichant les vues clients/contrats/évènements et la gestion des utilisateurs.
- **Domaines SQLAlchemy** : modèles `User`, `Role`, `Permission`, `Customer`, `Contract`, `Event` versionnés avec un mixin de timestamps. Les repositories exposent les opérations CRUD et restent agnostiques sur la logique métier.
- **Services applicatifs** : `CustomerService`, `ContractService`, `EventService`, `AuthService`, `PermissionService` orchestrent la validation (Pydantic), la vérification d'appartenance et les règles de gestion avant d'appeler les repositories.
- **Authentification & tokens** : `AuthService` sait créer/verifier des JWT (Argon2 + PyJWT) et sécuriser les mots de passe.
- **Base de données** : initialisation via `app.db.init_db` avec un seeding complet (rôles, permissions, utilisateurs, contrats, événements) et via la commande CLI qui droppe/crée/seed la base à chaque lancement.

## Stack technique
- Python 3.13
- SQLAlchemy + PyMySQL pour MySQL
- Click pour la CLI
- Pydantic pour valider les payloads (schemas)
- Argon2, PyJWT pour auth
- Sentry SDK (initialisé dans `cli.sentry`) pour capturer les erreurs
- Tests unitaires avec pytest (+ pytest-cov)

## Installation & configuration
1. Installer les dépendances : `poetry install`
2. Copier `.env.example` si présent (ou créer un `.env`) et définir les variables suivantes :
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
3. S'assurer que MySQL est accessible avec les identifiants fournis (gestion utilisateur + droits de DROP/CREATE).

## Lancer l'application
1. Réinitialiser la base et démarrer l'interface :
	```bash
	poetry run python -m cli.main run
	```
2. Le CLI réinitialise la base (DROP + CREATE + seed), puis charge Sentry et démarre l'interface.
	> **Remarque** : `cli.main.run` lève actuellement `RuntimeError('Erreur de test Sentry')` juste avant d'appeler `run_interface`. Il faut commenté cette ligne pour vraiment explorer l'interface.
3. Se connecter avec l'un des comptes générés pendant le seed :
	- Management : `manager1` / `password`
	- Sales : `sales2` / `password`
	- Support : `support1` / `password`
	Chaque rôle verra les sections du menu qui correspondent à ses permissions (`PermissionService.available_menus_for_user`).

## Base de données & seed
- L'initialisation crée les tables SQLAlchemy, les rôles/permissions, trois sales, deux managers, deux supports, quelques clients, contrats et événements liés.
- Les seeds détaillés se trouvent dans `app.db.init_db.seed`, notamment la distribution des contrats/événements par utilisateur.
- Le CLI supprime/crée également la base avant chaque lancement, ce qui est pratique pour l'école mais détruit les données : éviter en cas de besoin d'historique.

## Testing
- Lancer la suite : `poetry run pytest`
- Le dossier `tests/units` couvre les repositories, services et views pour s'assurer que les règles métiers fonctionnent.

## Structure utile
- `app/models` : définitions SQLAlchemy + mixins
- `app/repositories` : accès DB CRUD
- `app/services` : logique métier & validations
- `cli/views` : menus spécifiques (users/customers/contracts/events)
- `cli/crm_interface.py` : orchestration de l'interface (login, boucle de menu)
- `tests/units` : scénarios unitaires indépendants de la base réelle

## Prochaines étapes suggérées
1. Supprimer le `RuntimeError` pour explorer le CLI sans interruption.
2. Ajouter des fixtures fixtures/tests d'intégration (ex. avec la base MySQL).
3. Exporter un script SQL ou utiliser Docker pour rendre l'environnement MySQL plus reproductible.

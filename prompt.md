Je veux créer CRM interne à une entreprise (qui s’appelle epic_events) dans lequel on a des utilisateurs qui vont pouvoir se connecter, effectuer des actions CRUD sur des objets selon leur roles dans l’entreprise et les permissions qui sont attachées à ces roles. Ces données seront persistées dans MySql.
Tu vas parcourir les fichiers models.md, permissions.md, prompt.md et vues.md pour comprendre les modèles de données, les rôles et permissions, ainsi que les vues attendues dans l’application.
Tu vas d'abord relever les informations importantes dans ces fichiers, les incohérences et/ou incompréhensions (s'il y en a) puis tu vas me les résumer avant de commencer à coder l’application.
Tu vas me proposer une stack minimale, une architecture de projet adaptée à cette application CRM en Python, avec les bibliothèques et frameworks appropriés pour la gestion des modèles, de la base de données, de l’authentification, des permissions et de l’interface en ligne de commande (CLI).
Il faut que ce soit relativement simple et ce dont on peut attendre d"un élève qui débute en développement web backend en Python. Je veux que tout soit nommé en anglais (noms de fichiers, dossiers, classes, variables, fonctions, etc) sauf l'interface en ligne de commande (CLI) qui sera en français. Et je veux que tous les noms de variables ou fichiers soient explicites. Pas de noms abrégés ou de noms vagues.
C'est un projet d'école pour apprendre, donc il faut privilégier la clarté du code et la simplicité de l'architecture. Cette app ne participera pas à un système de production. Et elle ne sera pas déployée et n'évoluera pas. Cela dit, il faut quand même respecter les bonnes pratiques de développement.

Tu vas créer les modèles à l'aide du fichier models.md
Je veux un dossier app/ avec un sous-dossier models/ dans lequel tu vas créer les modèles SQLAlchemy pour les objets User, Role, Permission, Customer, Contract et Event, dans des fichiers séparés.

Ensuite tu vas créer la configuration de la base de données :
- Connexion à la base de données MySQL
- Création des tables
- Injection de données initiales (rôles, permissions, utilisateurs, clients, contrats, événements)
Voici le jeu de données :
- Rôles et permissions selon permissions.md
- 3 users dont le role est sales
- 2 users dont le role est management
- 2 users dont le role est support
- 3 clients, 6 contrats, 4 événements répartis comme suit :

- un user dont le role est sales et qui n'a pas de client

- un user dont le role est sales et qui a 2 clients :
    - un client sans contrat et sans événement
    - un client avec 4 contrats:
        - 1 contrat, créé par manager1, non signé, non payé
        - 1 contrat, créé par manager1, signé, partiellement payé, et sans événement
        - 1 contrat, créé par manager1, signé, totalement payé, et sans événement
        - 1 contrat, créé par manager1, signé, totalement payé, et 2 événements :
            - un événement sans support assigné
            - un événement avec un support assigné

- un user dont le role est sales et qui a 1 client :
    - un client avec 2 contrats :
        - 1 contrat, créé par manager2, signé, non payé, et sans événement
        - 1 contrat, créé par manager2, signé, totalement payé, et 2 événements :
            - un événement avec un autre support assigné
            - un événement sans support assigné

Pour éviter les migrations si je modifie les modèles, tu vas créer la base de données et les tables à chaque exécution du script. Donc tu vas supprimer la base de données si elle existe déjà avant de la recréer.

Tu vas créer un fichier de test pour vérifier que les données ont bien été insérées dans la base.

Ensuite tu vas coder ce qui va permettre l'authentification des utilisateurs et écrire les tests associés. Lorsque les utilisateurs vont se connecter, tu vas vérifier que leur mot de passe haché correspond bien au mot de passe haché stocké en base de données. Puis créer une session utilisateur pour les utilisateurs authentifiés avec JWT (JSON Web Token) et écrire les tests associés.

Pour la logique métier tu vas créer des services dans un dossier app/services/ pour gérer les permissions selon le rôle de l'utilisateur connecté, en te basant sur le fichier permissions.md.
Pour la couche d'accès aux données, tu vas créer des repository dans un dossier app/repositories/ pour chaque modèle (UserRepository, CustomerRepository, ContractRepository, EventRepository) qui vont interagir avec la base de données via SQLAlchemy.

Ensuite tu vas coder une interface en ligne de commande (CLI) dans un dossier cli/ avec les vues pour interagir avec le CRM et écrire les tests associés. J'ai essayé de te détailler au maximum les comportements attendus dans le fichier vues.md. Je me demande si on gère les vues par rôle utilisateur ou si on affiche toutes les vues et on gère l'accès aux données via les permissions. Tu vas me le préciser dans ton résumé avant de commencer à coder.

Quelques informations importantes : mots de passe hachés, principe du moindre privilège, validation côté application avant écriture en base, protection contre injections SQL via SQLAlchemy.

Pour la stack j'ai pensé à ça :
python 3.13
sqlalchemy
python-dotenv
cryptography
argon2-cffi
pyjwt
click
pymysql
coverage
sentry-sdk
flake8-html
pytest
pytest-cov

Pour la gestion des dépendances tu vas utiliser poetry.

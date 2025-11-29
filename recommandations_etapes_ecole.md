Recommandations étapes par l’école :
Etape 0 : Recommandations générales
Ce projet se fait en trois temps : 
1.	une partie d’initialisation et de définition (étapes 1 à 2) ;
2.	une partie de développement (étapes 3 à 7) ;
3.	une partie de finalisation (étapes 8 à 9).
Évitez de commencer les développements sans la partie de définition ; cela vous fera plus perdre du temps qu’autre chose. Bien que la partie développement soit la plus longue, veuillez ne pas négliger les parties de définition (avant le développement) et de journalisation et documentation (après le développement).


Etape 1 : Mise en place environnement SQL et Python
Résultat attendu :
•	avoir mis en place une base de données fonctionnelle et accessible.
Recommandations :
•	Choisir un moteur de base de données (PostgreSQL). 
•	Installer les outils d’administration associés (PgAdmin).
•	Créer un compte utilisateur pour l’application.
•	Créer une base de données pour l’application.
•	S’assurer que cet utilisateur dispose des droits nécessaires sur la base de données .
•	Installer une librairie ORM en Python (SQL Alchemy).
Points de vigilance :
•	Avant de démarrer le projet, familiarisez-vous avec ce qu’est un système Customer Relationship Management (CRM) – l’application que vous développerez.
•	N’oubliez pas d’utiliser un compte non privilégié pour la base de données.
•	Évitez de renseigner les informations de connexion à la base de données (y compris le mot de passe) en dur dans le code.


Etape 2 : Définir les modèles et implémentation dans la base
Résultat attendu :
•	avoir défini les classes Python des entités métiers 
o	pour les clients
o	les contrats
o	et les événements 
•	avoir modélisé les classes.
Recommandations :
•	Un diagramme entity-relationship (ERD) peut être utile pour mieux visualiser les relations entre les différents modèles
Points de vigilance :
•	Attention à définir les relations entre les différents modèles ;
•	Soyez conscient qu’il sera peut-être difficile d’implémenter les relations dans l’ORM.
Etape parallèle : bonnes pratiques
•	Après les étapes précédentes, vous aurez déjà initialisé la BDD et défini les modèles, c’est-à-dire que vous serez prêt à coder l’application. Nous avons découpé les tâches de développement de l’application dans les étapes suivantes en procédant d’abord au code des utilisateurs et de l’authentification, puis au code des opérations CRUD, et enfin au code de l’interface. 

•	Toutefois, il est possible de suivre un ordre différent, mais veuillez garder les étapes distinctes pour respecter la séparation des principes. Si vous voulez suivre un autre ordre, validez-le avec votre mentor.

•	Par ailleurs, nous vous conseillons de suivre cette étape parallèle ci-dessous tout au long de la partie de développement.

•	L’application va comporter de nombreux éléments interdépendants. Pour faciliter le processus de développement et rendre la maintenance du code plus facile sur le long terme, il faudra faire des choix sur l’architecture de l’application ; 
•	Il existe une collection de « bonnes solutions » aux problèmes courants, typiquement regroupées sous le nom de design patterns. Vous allez très certainement en utiliser plusieurs dans ce projet. Soyez sûr de vous familiariser avec les plus classiques.
o	Repository, DAO, Active Record… pour l’interface entre la base de données et la logique métier (data access layer, cf fichier design_patterns_database_layer.md) ;
o	MVC sera par exemple très utile pour « connecter » l’interface utilisateur à la logique métier.
•	Le code devra bien sûr suivre les bonnes pratiques de développement :
o	formatage et PEP8 (black, autopep8, flake8… ) ;
o	le code est couvert par des tests (unitaires et intégration). N’oubliez pas la couverture du code !
o	le code est documenté et bien organisé ;
o	tout au long du projet, gardez en tête que la sécurité de la plateforme est la principale préoccupation. Cela se traduira également dans le code !


Etape 3 : créer les comptes utilisateurs et permissions
Résultat attendu :
•	avoir codé les classes et les fonctions Python pour l’identification des utilisateurs.
Recommandations :
•	Réfléchir au stockage des mots de passe : ils doivent être salés et hachés.
•	Il est possible d’utiliser des librairies tierces (par exemple script ou argon2).
•	Tous les collaborateurs possèdent des éléments d’identification pertinents :
o	un numéro d’employé 
o	un nom 
o	une adresse email 
o	une affiliation à un département 
o	des permissions différentes suivant leur département.
Points de vigilance :
•	Respectez des bonnes pratiques de sécurité pour le stockage d’informations sensibles dans la base de données (obfuscation du mot de passe, salage, etc.).
•	Comprenez la différence entre autorisation et authentification.
•	Évitez l’implémentation des rôles « en dur » dans la table des comptes utilisateur au lieu de créer une relation vers un « rôle ».


Etape 4 : développer le code permettant l’authentification et l’autorisation des utilisateurs
Résultat attendu :
•	une fonction d’authentification permettant une authentification persistante des utilisateurs.
•	une fonction d’autorisation permettant de vérifier le niveau de permissions de l’utilisateur en cours.
Recommandations :
•	Il est possible d’utiliser des jetons JSON Web Token (JWT ; par exemple avec la librairie pyjwt). Faites attention au stockage du secret/à l’algorithme utilisé !
•	Après l’authentification, l’utilisateur reçoit un jeton qui lui permet d’accéder aux fonctionnalités auxquelles il a droit :
o	le jeton est stocké sur la machine et permet d’autoriser les actions dans l’application ;
o	par exemple, l’utilisateur pourrait s’authentifier en utilisant la commande : “python epicevents.py login”.
Points de vigilance :
•	La réalisation d’une authentification dans le terminal peut être une tâche ardue ;
•	Utilisez le fichier .netrc / _netrc peut être trop compliqué pour rendre l’application compatible avec d’autres plateformes : vous pouvez utiliser votre propre méthode (fichier dédié, variable d’environnement, argument en ligne de commande, etc.).
•	Les jetons ont une date d’expiration. Comment allez-vous gérer un jeton expiré ?


Etape 5 : développer les premiers éléments de code permettant la lecture de données dans la base
Résultat attendu :
•	avoir codé les classes et les fonctions Python permettant la lecture de données depuis la base.
Recommandations :
•	Le code doit permettre, au minimum, d’obtenir tous les instances des entités métiers ;
•	Il doit permettre : 
o	d’obtenir tous les clients,
o	d’obtenir tous les contrats,
o	d’obtenir tous les événements.
Points de vigilance :
•	Vérifiez les permissions avant de récupérer les données.
•	Assurez-vous que les utilisateurs doivent être authentifiés pour accéder aux données.
•	Ajoutez les relations entre les modèles « utilisateur » et les modèles métier.
o	Les modèles « utilisateur » sont ‘employé’ et les modèles métier sont ‘contrats’, ‘événements’, ou ‘clients’.


Etape 6 : développer le code permettant la création et la mise à jour de données dans la base
Résultat attendu :
•	avoir codé les classes et les fonctions Python permettant la création et la mise à jour d’informations dans la base de données.
Recommandations :
•	Le code doit permettre, au minimum, de :
o	créer un collaborateur ;
o	modifier un collaborateur (y compris son département) ;
o	créer un contrat ;
o	modifier un contrat (tous les champs, y compris relationnels) ;
o	créer un événement ;
o	modifier un événement (tous les champs, y compris relationnels) ;
o	les fonctionnalités ci-dessous doivent uniquement être accessibles aux utilisateurs qui y ont effectivement accès.
Points de vigilance :
•	Validez les données dans le code avant l’écriture dans la base ;
•	Vérifiez les permissions/rôles de l’utilisateur en cours avant la modification des données.


Etape 7 : développer l’interface en ligne de commande
Résultat attendu :
•	avoir codé l’interface utilisateur.
Recommandation :
•	Utilisez des librairies tierces pour faciliter l’implémentation du programme (par exemple: click ou rich).
Points de vigilance :
•	Il faut toujours valider les données utilisateur avant leur utilisation.
•	Il faut réutiliser (et si besoin, améliorer) le code développé à l’étape précédente pour assurer une bonne séparation des responsabilités (affichage vs manipulation des données).


Etape 8 : Ajouter la journalisation avec Sentry.io
Résultat attendu :
•	avoir ajouté la journalisation avec Sentry à l’application.
Recommandations :
•	Lire la documentation de Sentry pour Python.
•	Assurez-vous que les situations suivantes sont journalisées :
o	toutes les exceptions inattendues ;
o	chaque création/modification d’un collaborateur ;
o	la signature d’un contrat (pour l’option scénarisée).
Points de vigilance :
•	Soyez conscient de la difficulté à mettre en place le kit Sentry.
•	Soyez attentif aux problèmes de sécurité avec les clés Sentry (par exemple : publication sur GitHub, ou en dur dans le code).




Tous les choix possibles comportent un numéro de ligne et l'utilisateur choisi grâce à ce numéro de ligne

Menu d'accueil
- Message d’accueil
- Choix :
  - Se connecter
  - Quitter
Se connecter
- Saisie du username et du mot de passe
- Option de retour au menu d'accueil
Menu principal (après connexion)
- Choix du service (affiché selon les permissions de l'utilisateur) :
  - Gestion des utilisateurs (visible uniquement pour le management)
  - Gestion des clients
  - Gestion des contrats
  - Gestion des évènements
  - Déconnexion

=> Choix Gestion des utilisateurs
- Afficher tous les utilisateurs
- Filtrer par ID
- Retour
- Choix

=> Choix d'afficher la liste de tous les utilisateurs
Comportement de l'affichage : affichage en liste de tous les users (id, nom, prénom, username, rôle)
- Retour
- Choisir un utilisateur

        Affichage détail de l'utilisateur 
        Comportement de l'affichage : tous les champs de l'utilisateur
        - Modifier 
        - Supprimer 
        - Retour
        Choix

        Modification d'un utilisateur :
        Comportement de l'affichage : tous les champs de l'utilisateur
        Proposition des champs à modifier : uniquement les champs modifiables
        Comportement de l'affichage : une fois le choix modifié, réafficher la même vue avec les champs à jour. L'utilisateur peut modifier ainsi les champs un à un, et choisir retour à la gestion des utilisateurs ou déconnexion

        Suppression d'un utilisateur :
        Demander confirmation et retour à la gestion des utilisateurs

=> Choix de filtrer les utilisateurs par ID
- Saisie de l'ID
- Retour
- Choisir un utilisateur
        Reprendre logique Affichage détail de l'utilisateur

=> Choix gestion des clients
- Afficher tous les clients
- Mes clients (ceux qui sont assignés au user connecté, menu visible que par les sales) 
- Retour
- Choix

    => Choix d'afficher la liste de tous les clients
    Comportement de l'affichage : affichage en liste de tous les clients (id, nom, prénom, entreprise, user sales assigned)
    - Retour
    - Choisir un client

            Affichage détail du client :
            Comportement de l'affichage : tous les champs du client
            - Modifier : vue disponible uniquement si le user à le droit d'updater les clients ET s'il est assigné au client
            - Supprimer : vue disponible uniquement si le user à le droit d'updater les clients ET s'il est assigné au client
            - Retour
            Choix

            Modification d'un client :
            Comportement de l'affichage : tous les champs du client
            Proposition des champs à modifier : uniquement les champs modifiables
            Comportement de l'affichage : une fois le choix modifié, réafficher la même vue avec les champs à jour. L'utilisateur peut modifier ainsi les champs un à un, et choisir retour à la gestion des clients ou déconnexion

            Suppression d'un client :
            Demander confirmation et retour à la gestion des clients

    => Choix d'afficher la liste de ses clients
    Comportement de l'affichage : affichage en liste de tous les clients (id, nom, prénom, entreprise, user sales assigned), filtré where client user_sales_id = user connecté
    - Retour
    - Choisir un client
            Reprendre logique Affichage détail du client


=> Choix gestion des contrats
- Afficher tous les contrats
- Mes contrats (si user connecté est management, where user_management_id = user connecté, si user connecté est sales, afficher les contrats liés aux clients auxquels il est assigné, si user connecté est support, afficher ceux des clients liés aux évènements qu'il gère)
- Mes contrats non signés (si user connecté est management, where user_management_id = user connecté, si user connecté est sales, afficher les contrats liés aux clients auxquels il est assigné, si user connecté est support, il ne peut pas les voir puisque si le contrat n'est pas signé, il n'y a pas d'évènement lié)
- Mes contrats non payés (si user connecté est management, where user_management_id = user connecté, si user connecté est sales, afficher les contrats liés aux clients auxquels il est assigné, si user connecté est support, ceux des clients liés aux évènements qu'il gère)
- Retour
- Choix

    => Choix d'afficher la liste de tous les contrats
    Comportement de l'affichage : affichage en liste de tous les contrats (id, montant total, client lié, management assigned, sales assigned)
    - Retour
    - Choisir un contrat

            Affichage détail du contrat 
            Comportement de l'affichage : tous les champs du contrat
            - Modifier : vue disponible uniquement si le user à le droit d'updater les contrats ET si c'est un contrat lié à un de ses clients (pour les sales) ou tous les contrats (si user = management)
            - Supprimer : vue disponible uniquement si le user à le droit de supprimer les contrats 
            - Retour
            Choix

            Modification d'un contrat :
            Comportement de l'affichage : tous les champs du contrat
            Proposition des champs à modifier : uniquement les champs modifiables
            Comportement de l'affichage : une fois le choix modifié, réafficher la même vue avec les champs à jour. L'utilisateur peut modifier ainsi les champs un à un, et choisir retour à la gestion des contrats ou déconnexion

            Suppression d'un contrat :
            Demander confirmation et retour à la gestion des contrats
  
=> Choix d'afficher la liste de ses contrats
Comportement de l'affichage : affichage en liste de tous les contrats (id, montant total, client lié, management assigned, sales assigned), filtré :
  si role.user connecté = management : afficher les contrats qui lui sont assignés (where user_management_id = user connecté)
  si role.user connecté = sales : afficher les contrats liés aux clients auxquels il est assigné (where customer_id in (clients assignés par user connecté))
  si role.user connecté = support : afficher les contrats liés aux évènements qu'il gère (where contrat_id in (évènements gérés par user connecté))
- Retour 
- Choisir un contrat
        Reprendre logique d'affichage détail du contrat
        
=> Choix d'afficher la liste de ses contrats non signés
Comportement de l'affichage : affichage en liste de tous les contrats non signés (id, montant total, client lié, management assigned, sales assigned), filtré :
  si role.user connecté = management : afficher les contrats qui lui sont assignés et non signés (where user_management_id = user connecté AND signed = False)
  si role.user connecté = sales : afficher les contrats liés aux clients auxquels il est assigné et non signés (where customer_id in (clients assignés par user connecté) AND signed = False)
  si role.user connecté = support : ne rien afficher puisque si le contrat n'est pas signé, il n'y a pas d'évènement lié
- Retour
- Choisir un contrat
        Reprendre logique d'affichage détail du contrat


=> Choix d'afficher la liste de ses contrats non payés
Comportement de l'affichage : affichage en liste de tous les contrats non payés (id, montant total, balance due, client lié, management assigned, sales assigned), filtré :
  si role.user connecté = management : afficher les contrats qui lui sont assignés et non payés (where user_management_id = user connecté AND balance_due > 0)
  si role.user connecté = sales : afficher les contrats liés aux clients auxquels il est assigné et non payés (where customer_id in (clients assignés par user connecté) AND balance_due > 0)
  si role.user connecté = support : afficher les contrats liés aux évènements qu'il gère et non payés (where contrat_id in (évènements gérés par user connecté) AND balance_due > 0)
- Retour
- Choisir un contrat
        Reprendre logique d'affichage détail du contrat


=> Choix gestion des évènements
- Afficher tous les évènements
- Mes évènements : filtré :
   si user connecté = support : afficher les évènements qu'il gère
   sinon ne pas afficher cette option
- Evènements sans support assigned (visible uniquement par le management) : where user_support_id is NULL
- Retour
- Choix
    => Choix d'afficher la liste de tous les évènements
    Comportement de l'affichage : affichage en liste de tous les évènements (id, nom, client lié, support assigned)
    - Retour
    - Choisir un évènement

            Affichage détail de l'évènement 
            Comportement de l'affichage : tous les champs de l'évènement
            - Modifier : vue disponible uniquement si le user à le droit d'updater les évènements ET s'il est assigné à l'évènement (pour les support) ou tous les évènements (si user = management)
            - Supprimer : vue disponible uniquement si le user à le droit de supprimer les évènements 
            - Retour
            Choix

            Modification d'un évènement :
            Comportement de l'affichage : tous les champs de l'évènement
            Proposition des champs à modifier : uniquement les champs modifiables. Attention, le management ne peut modifier que le champs user_support_id
            Comportement de l'affichage : une fois le choix modifié, réafficher la même vue avec les champs à jour. L'utilisateur peut modifier ainsi les champs un à un, et choisir retour à la gestion des évènements ou déconnexion

            Suppression d'un évènement :
            Demander confirmation et retour à la gestion des évènements
  
    => Choix d'afficher la liste de ses évènements
    Comportement de l'affichage : affichage en liste de tous les évènements (id, nom, client lié, support assigned), filtré where user_support_id = user connecté
    - Retour
    - Choisir un évènement
            Reprendre logique Affichage détail de l'évènement
    => Choix d'afficher la liste des évènements sans support assigned
    Comportement de l'affichage : affichage en liste de tous les évènements (id, nom, client lié), filtré where user_support_id is NULL
    - Retour
    - Choisir un évènement
            Reprendre logique Affichage détail de l'évènement


        






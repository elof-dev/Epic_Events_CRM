# Cahier des charges – Epic Events

## Contexte

Epic Events est une entreprise qui organise des événements (fêtes, réunions professionnelles, manifestations hors les murs) pour ses clients.  
L’objectif est de développer un logiciel CRM (Customer Relationship Management) pour améliorer le travail interne.

Le CRM doit permettre de :
- collecter et traiter les données des clients et de leurs événements ;
- faciliter la communication entre les différents pôles de l'entreprise.

## Organisation interne

L’entreprise est divisée en trois départements :
- Département **commercial**
- Département **support**
- Département **gestion**

### Fonctionnement général
- Les commerciaux démarchent les clients et créent leurs profils sur la plateforme.  
- Lorsqu’un client veut organiser un événement, un membre du département gestion crée un contrat et l’associe au client.  
- Une fois le contrat signé, le commercial crée l’événement.  
- Le département gestion désigne ensuite un membre du support pour organiser et suivre l’événement.

---

## Exigences techniques et de sécurité

- Langage : **Python 3.13 ou plus récent**
- Application : **en ligne de commande**
- Protection contre les **injections SQL**
- Application du **principe du moindre privilège** (chaque utilisateur ne voit que ce qui le concerne)
- **Journalisation** des erreurs et exceptions avec **Sentry**
- MySQL comme base de données
- SQLAlchemy comme ORM
- Tests unitaires avec **pytest**



## Données à gérer

### Clients

Un client contient :
- Nom complet  
- Email  
- Téléphone  
- Nom de l’entreprise  
- Date de création (premier contact)  
- Dernière mise à jour/contact  
- Contact commercial chez Epic Events  

### Exemple
```
Nom complet : Kevin Casey
Email : kevin@startup.io
Téléphone : +678 123 456 78
Entreprise : Cool Startup LLC
Date de création : 18 avril 2021
Dernier contact : 29 mars 2023
Contact commercial : Bill Boquet
```

---

### Contrats

Un contrat contient :
- Identifiant unique  
- Informations sur le client  
- Contact commercial associé  
- Montant total  
- Montant restant à payer  
- Date de création  
- Statut (signé ou non)

---

### Événements

Un événement contient :
- Identifiant unique  
- Identifiant du contrat associé  
- Nom du client  
- Contact du client (email, téléphone)  
- Date et heure de début  
- Date et heure de fin  
- Contact support Epic Events  
- Lieu  
- Nombre de participants  
- Notes diverses

---

## Besoins et fonctionnalités

### Besoins généraux

- Chaque collaborateur doit avoir **ses identifiants**.  
- Chaque collaborateur appartient à **un rôle** (selon son département).  
- La plateforme doit permettre de **créer, lire, mettre à jour et supprimer** les informations des clients, contrats et événements.  
- Tous les collaborateurs doivent pouvoir **voir** (lecture seule) tous les clients, contrats et événements.

---

### Équipe gestion (management)

- Créer, mettre à jour et supprimer des collaborateurs.  
- Créer et modifier tous les contrats.  
- Filtrer les événements (ex : événements sans support associé).  
- Modifier un événement (associer un support).  

---

### Équipe commerciale (sales)

- Créer des clients (le client est automatiquement associé au commercial).  
- Mettre à jour les clients dont ils sont responsables.  
- Modifier les contrats des clients qu’ils gèrent.  
- Filtrer les contrats (ex : non signés ou non entièrement payés).  
- Créer un événement pour un client ayant un contrat signé.  

---

### Équipe support

- Filtrer les événements (voir uniquement ceux qui leur sont attribués).  
- Mettre à jour les événements dont ils sont responsables.

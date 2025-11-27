Toutes les PK, updated_at, created_by sont autoincrémentés et non modifiables.
Les clients sont créés par des users dont le rôle est sales et lui sont assignés.
Les contrats sont créés par des users dont le rôle est management et sont liés à des clients. Et donc indirectement à l'user sales qui est assigné au client.
Les évènements sont créés par des users dont le rôle est sales et sont liés à des contrats signés et à des clients. Ils sont ensuite assignés à un user dont le rôle est support.

User :
+ id: PK
+ role_id: FK de Role
+ user_first_name: str
+ user_last_name: str
+ email: str (unique)
+ phone_number: str (unique)
+ username: str (unique)
+ password_hash: str
+ created_at : datetime
+ updated_at : datetime

Role:
+ id: PK 
+ name: str unique
+ M2M Permission

Permission:
+ id: PK 
+ name: str unique
+ M2M Role


Customer :
+ id: PK
+ user_sales_id: FK de User
+ customer_first_name: str
+ customer_last_name: str
+ email: str unique
+ phone_number: str unique
+ company_name : str unique
+ created_at: datetime
+ updated_at: datetime

Contract :
+ id : PK
+ customer_id: FK de Customer
+ user_management_id: FK de User
+ contract_number: str (unique)
+ total_amount: numeric
+ balance_due: numeric
+ created_at: datetime
+ updated_at: datetime
+ signed : bool

Event:
+ id :PK
+ contract_id: FK de Contract
+ customer_id: FK de Customer
+ user_support_id: FK de User
+ event_name: str
+ event_number: str (unique)
+ start_datetime: datetime + heure
+ end_datetime: datetime + heure
+ location: str
+ attendees: int
+ note: text
+ created_at: datetime
+ updated_at: datetime


Relation entre ces objets :
User et Role :
- chaque user possède un role
- un role peut être associé à plusieurs users

Role et Permission :
- Une permission peut être affectée à plusieurs roles
- Un role peut posséder plusieurs permissions

User et Customer :
- un user dont le rôle est sales peut gérer plusieurs clients
- chaque client est géré par un user dont le role est sales

User et Contrat :
- un user dont le rôle est management peut gérer plusieurs contrats
- chaque contrat est géré par un seul user dont le role est management

User et Event :
- un user dont le role est support peut gérer plusieurs events
- chaque event est géré par un seul user dont le role est support

Contrat et Customer :
- un client peut posséder plusieurs contrats
- chaque contrat est lié à un seul client

Event et Customer :
- un client peut organiser plusieurs évènements
- Chaque évent est organisé par un seul client

Event et Contract :
- un contrat peut représenter plusieurs évènements
- chaque évent est organisé selon un seul contrat

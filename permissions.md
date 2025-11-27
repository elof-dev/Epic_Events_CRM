Les roles sont : Management, Sales et support et sont attribués
Les permissions sont celles du CRUD sur les objets User, Customer, Contract et Event.

Les users qui ont le rôle de management ont la permission de :
-	Sur l’objet 
o	User :create read update delete
o	Customer : read
o	Contract : create read update delete
o	Event : read, update (update only support._id)

Les users qui ont le rôle de sales ont la permission de
-	Sur l’objet :
o	User : aucun
o	Customer : create read update (update que les siens), delete (delete que les siens)
o	Contract : read update (update que ceux liés à ses clients)
o	Event : create (que pour ses clients et que quand le contrat est signé), read

Les users qui ont le rôle de support ont la permission de :
-	Sur l’objet :
o	User : aucun
o	Customer : read
o	Contract : read
o	Event : read, update (que ceux auxquels il est relié)


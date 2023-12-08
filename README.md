# sauvegardeur

Une application de sauvegarde externalisée.

## Contexte

L’objectif est de réaliser une application de sauvegarde externalisée, qui va faciliter la vie à l’utilisateur.

Il s’agit d’une application client-serveur en réseau, qui doit satisfaire aux règles suivantes :

- L’utilisateur choisi le nom du dossier à partir duquel il veut faire la sauvegarde, il entre l’adresse IP du serveur et la sauvegarde démarre.
- L’application cliente ne sauvegarde pas tous les fichiers du dossier, mais seulement ceux dont les propriétés (suffixes) sont décrites dans un fichier de paramètres, prédéfini. L’application, sauvegarde toute l’arborescence depuis le nom de dossier indiqué.
- L’application doit être en mesure de détecter si une première sauvegarde a déjà été faite : 
	- Si **non**, tous les fichiers correspondants aux critères seront envoyés au serveur
	- Si **oui**, on ne copie que les fichiers qui n’ont pas été sauvegardés ou qui ont été modifiés depuis la dernière sauvegarde.

En option : 

- Les flux de données transmis devront être sécurisés.
- Les données sauvegardées coté serveur devront être chiffrées
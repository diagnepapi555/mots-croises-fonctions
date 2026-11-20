LE DÉFI DES FONCTIONS — MOTS CROISÉS (VERSION RECONSTRUITE)

Le jeu conserve l'interface précédente. Modes solo et duo : le bouton Démarrer
est obligatoire après saisie du ou des noms. En duo, chaque tour dure 60 s.
Les réponses correctes restent verrouillées. L'espace enseignant est accessible
sur le même site avec le code PROF2026 (à remplacer avant publication publique).
Le serveur sauvegarde les progressions dans SQLite et le tableau enseignant se
rafraîchit automatiquement toutes les 5 secondes.

POUR TESTER SUR UN ORDINATEUR : Python 3.10+ requis. Lancer :
    python server.py
Puis ouvrir http://localhost:8000 dans le navigateur.

POUR LE SUIVI À DISTANCE : publier CE DOSSIER sur un hébergement qui exécute
Python en continu, conserve un disque persistant et expose le port défini par PORT.
Les élèves et le professeur ouvrent LA MÊME ADRESSE HTTPS.
Configurer TEACHER_CODE (secret) et DB_PATH (chemin sur disque persistant).
Une simple ouverture du fichier index.html en double-cliquant ne permet PAS
le suivi à distance. Aucun hébergement public n'est inclus dans ce ZIP.

Ne pas réutiliser l'URL du Coffre des fonctions : elle héberge une autre
application, avec d'autres API.

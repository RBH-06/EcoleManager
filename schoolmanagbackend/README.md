# Système de Gestion d'École de Formation – API Backend

## Présentation

Ceci est l'API backend pour le Système de Gestion d'École de Formation. Elle fournit des points de terminaison (endpoints) pour la gestion de l'authentification, des utilisateurs, des étudiants, des professeurs, des formations, des classes, des sessions, des inscriptions, des présences et des paiements.

- **URL de base :** `http://localhost:3000/api/`
- **Authentification :** JWT (jeton dans l'en-tête `Authorization: Bearer <token>`)
- **Base de données :** PostgreSQL (Dockerisé)

---

## Pour commencer

### 1. Configuration de l'environnement
- Copiez le fichier `.env.example` et renommez-le en `.env`, puis ajustez les valeurs si nécessaire.
- Assurez-vous que votre conteneur Docker Postgres est en cours d'exécution et accessible avec les identifiants présents dans `.env`.

### 2. Installation des dépendances
```sh
npm install
```

### 3. Exécuter la migration de la base de données
- Connectez-vous à votre base de données Postgres et exécutez le script de migration :

**En utilisant psql :**
```sh
psql -h localhost -U admin -d schoolmanagement -f db_schema.sql
```
- Entrez votre mot de passe (`admin`) lorsque vous y êtes invité.

### 4. Démarrer le serveur
```sh
npm start
```

---

## Authentification

- **Inscription (Admin uniquement, première fois) :**  
  `POST /api/auth/register`  
```json
  {
    "email": "admin@school.com",
    "password": "password123",
    "first_name": "Admin",
    "last_name": "User",
    "phone": "1234567890",
    "role": "admin"
  }
  ```

- **Connexion :**  
  `POST /api/auth/login`  
```json
  {
    "email": "admin@school.com",
    "password": "password123"
  }
  ```
  **Réponse :**  
```json
  {
    "token": "<JWT_TOKEN>",
    "user": { ... }
  }
  ```

- Utilisez le `token` retourné dans l'en-tête `Authorization` pour tous les points de terminaison protégés.

---

## Rôles des Utilisateurs

- **admin** : Accès complet (gérer les utilisateurs, étudiants, professeurs, formations, classes, etc.)
- **subadmin** : Accès de gestion limité
- **teacher** (professeur) : Accès à ses classes, ses étudiants, ses présences
- **student** (étudiant) : Accès à son propre profil, ses inscriptions, ses présences, ses paiements

---

## Points de terminaison (Endpoints) principaux

### Utilisateurs (Admin uniquement)
- `POST /api/users` – Créer un subadmin/teacher/student
- `GET /api/users` – Lister les utilisateurs
- `GET /api/users/:id` – Obtenir un utilisateur par son ID
- `PUT /api/users/:id` – Mettre à jour un utilisateur
- `DELETE /api/users/:id` – Supprimer un utilisateur

### Étudiants
- `POST /api/students`
- `GET /api/students`
- `GET /api/students/:id`
- `PUT /api/students/:id`
- `DELETE /api/students/:id`

### Professeurs
- `POST /api/teachers`
- `GET /api/teachers`
- `GET /api/teachers/:id`
- `PUT /api/teachers/:id`
- `DELETE /api/teachers/:id`

### Formations
- `POST /api/trainings`
- `GET /api/trainings`
- `GET /api/trainings/:id`
- `PUT /api/trainings/:id`
- `DELETE /api/trainings/:id`

### Classes
- `POST /api/classes`
- `GET /api/classes`
- `GET /api/classes/:id`
- `PUT /api/classes/:id`
- `DELETE /api/classes/:id`

### Sessions
- `POST /api/sessions`
- `GET /api/sessions`
- `GET /api/sessions/:id`
- `PUT /api/sessions/:id`
- `DELETE /api/sessions/:id`

### Inscriptions
- `POST /api/enrollments`
- `GET /api/enrollments`
- `GET /api/enrollments/:id`
- `PUT /api/enrollments/:id`
- `DELETE /api/enrollments/:id`

### Présences
- `POST /api/attendance`
- `GET /api/attendance`
- `GET /api/attendance/:id`
- `PUT /api/attendance/:id`
- `DELETE /api/attendance/:id`

### Paiements
- `POST /api/payments`
- `GET /api/payments`
- `GET /api/payments/:id`
- `PUT /api/payments/:id`
- `DELETE /api/payments/:id`

---

## En-têtes Communs

```http
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json
```

---

## Gestion des erreurs

- Toutes les erreurs retournent un JSON avec un champ `message`.
- 401 : Non autorisé (token invalide/manquant)
- 403 : Interdit (permissions insuffisantes)
- 404 : Introuvable
- 400 : Erreurs de validation

---

## Remarques

- Toutes les dates doivent être au format ISO 8601 (`YYYY-MM-DD`).
- Les ID sont des UUID.
- Pour les relations (par ex. les inscriptions), utilisez l'ID de l'entité référencée.

---

Pour toute question concernant les endpoints, les champs requis ou l'authentification, veuillez contacter l'équipe backend.
````</JWT_TOKEN></JWT_TOKEN>

# 🏫 EcoleManager

Application de gestion scolaire avec interface desktop **Tkinter**, backend **Node.js / Express** et base de données **PostgreSQL**.

---

## Fonctionnalités

| Module | Détail |
|---|---|
| Élèves | Inscription, profil, suivi |
| Enseignants | Gestion du personnel |
| Classes & Sessions | Organisation pédagogique |
| Inscriptions & Présences | Suivi des élèves |
| Paiements | Gestion des paiements par session |
| Authentification | Rôles admin / subadmin / enseignant / élève (JWT) |

---

## Stack technique

| Couche | Technologie |
|---|---|
| Interface desktop | Python · Tkinter (base locale SQLite) |
| Backend API REST | Node.js · Express · JWT · bcrypt |
| Base de données (backend) | PostgreSQL · PL/pgSQL |

> ℹ️ Le backend (Node.js) et l'interface Tkinter sont deux composants indépendants : le backend utilise PostgreSQL, l'interface Tkinter une base SQLite locale.

---

## Structure

```
EcoleManager/
├── schoolmanagbackend/   # API REST Node.js / Express
│   ├── index.js
│   ├── package.json
│   ├── db_schema.sql
│   └── src/
└── src/                  # Interface Tkinter (Python)
    └── app.py
```

---

## Installation

**Prérequis :** Node.js ≥ 18 · PostgreSQL ≥ 14 · Python ≥ 3.10

```bash
git clone https://github.com/RBH-06/EcoleManager.git
cd EcoleManager/schoolmanagbackend
npm install
```

> L'interface Tkinter (`src/`) n'utilise que des modules de la bibliothèque standard Python — aucune installation supplémentaire n'est nécessaire.

---

## Configuration

Créez un fichier `.env` dans `schoolmanagbackend/` :

```env
PORT=3000
DATABASE_URL=postgres://admin:admin@localhost:5432/school_db
JWT_SECRET=your_jwt_secret
```

Créez la base de données PostgreSQL puis importez le schéma :

```bash
psql -h localhost -U admin -d school_db -f db_schema.sql
```

---

## Lancement

```bash
# Backend (API REST sur http://localhost:3000)
cd schoolmanagbackend
npm start

# Interface Tkinter
cd ../src
python app.py
```

---

## API

| Méthode | Endpoint | Description |
|---|---|---|
| POST | `/api/auth/register` | Inscription (admin) |
| POST | `/api/auth/login` | Connexion (retourne un JWT) |
| GET/POST | `/api/students` | Élèves |
| GET/POST | `/api/teachers` | Enseignants |
| GET/POST | `/api/classes` | Classes |
| GET/POST | `/api/sessions` | Sessions |
| GET/POST | `/api/enrollments` | Inscriptions |
| GET/POST | `/api/attendance` | Présences |
| GET/POST | `/api/payments` | Paiements |
| GET/POST | `/api/trainings` | Formations |

---

## Contribuer

```bash
git checkout -b feature/ma-fonctionnalite
git commit -m "feat: description"
git push origin feature/ma-fonctionnalite
# → Ouvrir une Pull Request

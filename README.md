# 🏫 EcoleManager
 
Application de gestion scolaire avec interface desktop **Tkinter**, backend **Django REST, javascript** et base de données **PostgreSQL**.
 
---
 
## Fonctionnalités
 
| Module | Détail |
|---|---|
| 👨‍🎓 Élèves | Inscription, profil, suivi |
| 👩‍🏫 Enseignants | Gestion du personnel |
| 🏛️ Classes & Matières | Organisation pédagogique |
| 📊 Notes | Saisie et consultation |
| 🔐 Authentification | Rôles admin / enseignant / élève |
 
---
 
## Stack technique
 
| Couche | Technologie |
|---|---|
| Interface | Python · Tkinter |
| Backend | Python · Django · Javascript · Django REST Framework |
| Base de données | PostgreSQL · PLpgSQL |
 
---
 
## Structure
 
```
EcoleManager/
├── schoolmanagbackend/   # API REST Django
│   ├── manage.py
│   └── requirements.txt
└── src/                  # Interface Tkinter
```
 
---
 
## Installation
 
**Prérequis :** Python >= 3.10 · PostgreSQL >= 14
 
```bash
git clone https://github.com/RBH-06/EcoleManager.git
cd EcoleManager/schoolmanagbackend
 
python -m venv venv
source venv/bin/activate      # Windows : venv\Scripts\activate
pip install -r requirements.txt
```
 
---
 
## Configuration
 
Créez un fichier `.env` dans `schoolmanagbackend/` :
 
```env
SECRET_KEY=your_secret_key
DEBUG=True
DB_NAME=ecolemanager_db
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```
 
Créez la base de données PostgreSQL :
 
```sql
CREATE DATABASE ecolemanager_db;
GRANT ALL PRIVILEGES ON DATABASE ecolemanager_db TO postgres;
```
 
---
 
## Lancement
 
```bash
# Backend
cd schoolmanagbackend
python manage.py migrate
python manage.py createsuperuser   # optionnel
python manage.py runserver         # → http://localhost:8000
 
# Interface Tkinter
cd ../src
python main.py
```
 
---
 
## API
 
| Méthode | Endpoint | Description |
|---|---|---|
| GET/POST | `/api/students/` | Élèves |
| GET/POST | `/api/teachers/` | Enseignants |
| GET/POST | `/api/classes/` | Classes |
| GET/POST | `/api/grades/` | Notes |
| POST | `/api/auth/login/` | Connexion |
 
Admin Django : `http://localhost:8000/admin/`
 
---
 
## Contribuer
 
```bash
git checkout -b feature/ma-fonctionnalite
git commit -m "feat: description"
git push origin feature/ma-fonctionnalite
# → Ouvrir une Pull Request
```
 
---
 
> Développé par [RBH-06](https://github.com/RBH-06) · Licence MIT
 

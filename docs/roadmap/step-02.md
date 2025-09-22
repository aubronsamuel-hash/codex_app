# Step 02 - Backend Auth Skeleton (JWT + RBAC base)

## Goals
- Ajouter un squelette d’authentification stateless basé sur JWT (access + refresh tokens).
- Créer un modèle `User` minimal avec email unique, password_hash, is_active, created_at.
- Fournir les endpoints:
  - `POST /auth/signup` : créer un utilisateur
  - `POST /auth/login` : authentifier et renvoyer tokens
  - `GET /auth/me` : renvoyer l’utilisateur courant (Bearer token)
  - `POST /auth/refresh` : générer un nouveau token access à partir d’un refresh token
- Mettre en place une ébauche RBAC (tables Role et Permission vides ou minimales).
- Journaliser les évènements d’authentification (succès/échec) de manière simple (logs INFO/ERROR).

## Tasks
- **Modèles SQLAlchemy** :
  - User(id, email unique, password_hash, is_active, created_at)
  - Role(id, name) et Permission(id, name) comme squelette pour RBAC
- **Utilitaires sécurité** :
  - Hash/verify password (bcrypt/passlib-bcrypt)
  - JWT encode/decode avec exp/iat et secret
  - Settings: AUTH_SECRET, AUTH_ACCESS_TTL, AUTH_REFRESH_TTL
- **Migrations Alembic** :
  - Générer une révision pour User (+ tables role/permission basiques)
- **Routers FastAPI** :
  - `auth_router` avec /signup, /login, /me, /refresh
  - Dépendance `get_current_user()` pour protéger /me
- **Tests pytest** :
  - Unit tests : hash/verify password, jwt encode/decode
  - API tests : signup (201, email unique), login (200, tokens valides), me (401 sans token, 200 avec), refresh (200), cas erreurs (409 email déjà pris, 401 mauvais mot de passe)
- **README.md** :
  - Ajouter les variables d’environnement AUTH_SECRET, AUTH_ACCESS_TTL, AUTH_REFRESH_TTL
  - Expliquer comment lancer migrations et tester auth
- **Codex logs** :
  - Mettre à jour docs/codex/last_output.json
  - Ajouter réflexion courte dans docs/codex/reflections.md (<=200 mots)
  - Mettre à jour docs/codex/todo_next.md
  - Archiver sous docs/codex/history/*

## Acceptance Criteria
- `POST /auth/signup` crée un user actif, retourne 201 (sans exposer password)
- `POST /auth/login` retourne access_token + refresh_token valides
- `GET /auth/me` renvoie 401 sans token, 200 avec token valide
- `POST /auth/refresh` retourne un nouveau access_token valide
- Les migrations Alembic s’appliquent correctement en local
- Tests unitaires + API passent, couverture >= seuil défini dans policy.toml
- Logs d’auth basiques présents (succès/échec login)
- README mis à jour
- CI passe (guards + backend-tests + frontend-tests)

## Out of Scope
- Reset mot de passe, gestion email, providers sociaux
- RBAC avancé (attribution de rôles et permissions dynamiques)
- UI frontend (traité dans Step-03)

## Env (ajouter à .env.example)

# FF Tournament Platform

Complete starter project for a Free Fire tournament platform with:
- Flutter mobile frontend
- Flask REST API backend
- JWT auth
- Match listing, slot booking, wallet, leaderboard, admin panel
- Referral bonus and user stats

## Folder structure

- `backend/` Flask API, SQLite database, uploads, business logic
- `flutter_app/` Flutter mobile app with Provider state management

## Implemented features

### User side
- Email/password signup and login
- Google sign-in flow from Flutter to backend
- Profile photo upload
- Unique username
- Username lock after first match join
- Match list with entry fee, prize pool, total slots and spots left
- 50-slot booking grid like movie seat booking
- Entry fee deduction from wallet
- Room ID/password visible only to joined users once the match is full/live/completed
- Leaderboard and reward distribution display
- Wallet history
- Match history
- Basic win statistics
- Referral code bonus

### Admin side
- Create matches
- Update room details and status through API
- Submit results manually through API
- Automatic rank calculation based on score, then kills, then earliest join time
- Automatic reward distribution to wallet

## Backend setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
flask --app run.py db init
flask --app run.py db migrate -m "init"
flask --app run.py db upgrade
flask --app run.py seed
python run.py
```

Backend runs on `http://127.0.0.1:5000`

### Demo admin
- Email: `admin@ffarena.com`
- Password: `Admin@123`

## Flutter setup

```bash
cd flutter_app
flutter pub get
flutter run
```

Update `lib/core/constants.dart` if your backend host is different.
- Android emulator: `http://10.0.2.2:5000/api`
- Real device on same Wi-Fi: replace with your computer LAN IP like `http://192.168.1.5:5000/api`

## Important production notes

1. Google Sign-In requires platform setup in Firebase/Google Cloud and client IDs.
2. The backend `/api/auth/google` route is ready for integration, but you should verify Google identity tokens server-side before using it in production.
3. Add HTTPS, proper file storage, background jobs, rate limits, payment gateway, and push notifications before publishing.
4. For fairness, the current ranking logic sorts by score, then kills, then join time.
5. SQLite is included for easy local testing. Use PostgreSQL for production.

## Recommended next upgrades
- Firebase Cloud Messaging for push notifications
- Razorpay or another wallet top-up/payment gateway
- Real admin screens for result entry and match control
- Object storage for profile images
- Server-side Google token verification
- Pagination and search

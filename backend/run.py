import os
from app import create_app
from app.extensions import db
from app.seed import run_seed

app = create_app()

with app.app_context():
    db.create_all()
    run_seed()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
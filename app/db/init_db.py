from sqlalchemy.orm import Session

from app.db.base import Base
from app.db.session import engine
from app.services.seed import seed_admin_user, seed_demo_content


def init_db() -> None:
    Base.metadata.create_all(bind=engine)

    with Session(engine) as db:
        seed_admin_user(db)
        seed_demo_content(db)
        db.commit()

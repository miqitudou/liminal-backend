from sqlalchemy.orm import Session

from app.db.base import Base
from app.db.session import engine
from app.services.seed import seed_admin_user, seed_demo_content


def main() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    with Session(engine) as db:
        seed_admin_user(db)
        seed_demo_content(db)
        db.commit()

    print("Schema rebuilt successfully.")


if __name__ == "__main__":
    main()

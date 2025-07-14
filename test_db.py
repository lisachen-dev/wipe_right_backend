from sqlmodel import Session, select
from app.db.engine import engine
from app.models.provider import Provider

def seed_provider():
    new_provider = Provider(
        email= "gottacatchemall",
        phonenumber= 1234567890,
        user_id="2b07e53d-e98d-42d0-a2d3-d5c0f805f0fb"
    )
    with Session(engine) as session:
        session.add(new_provider)
        session.commit()
        session.refresh(new_provider)
        return new_provider

def select_providers():
    with Session(engine) as session:
        statement = select(Provider)
        results = session.exec(statement)
        providers = results.all()
        for provider in providers:
            print(provider)

if __name__ == "__main__":
    seed_provider()
    select_providers()
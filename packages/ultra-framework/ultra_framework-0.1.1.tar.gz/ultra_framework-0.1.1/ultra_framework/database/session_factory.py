"""session_factory module"""
from typing import Iterator

from sqlalchemy import Engine, text
from sqlalchemy.orm import sessionmaker, Session


class SessionFactory:
    """SessionFactory class"""

    def __init__(self, engine: Engine):
        self._session_maker = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def get_session(self) -> Iterator[Session]:
        """creates a session object from the session maker"""
        session = self._session_maker()

        try:
            yield session
        finally:
            session.close()

    def check_session(self, session: Session) -> tuple[Session, bool]:
        try:
            session.execute(text("select 1"))
            return next(self.get_session()), True
        except Exception:
            return session, False

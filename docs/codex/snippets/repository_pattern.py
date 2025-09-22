# Minimal repository pattern example (ASCII-only)

from typing import Optional, List

class Repository:
    def __init__(self, session):
        self.session = session

    def add(self, obj):
        self.session.add(obj)

    def get(self, model, id) -> Optional[object]:
        return self.session.get(model, id)

    def list(self, query) -> List[object]:
        return query.all()

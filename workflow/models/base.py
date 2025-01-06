from datetime import datetime

class BaseModel:
    def __init__(self):
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.is_active = True

    def save(self):
        self.updated_at = datetime.now()
        # Database save logic will be implemented here
        pass

    def delete(self):
        self.is_active = False
        self.save()

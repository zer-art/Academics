from typing import Dict, Optional
from datetime import datetime

class User:
    def __init__(self, id: int, email: str, name: str, provider: str, provider_id: str):
        self.id = id
        self.email = email
        self.name = name
        self.provider = provider
        self.provider_id = provider_id
        self.created_at = datetime.utcnow()

class UserDatabase:
    def __init__(self):
        self.users: Dict[str, User] = {}
        self.next_id = 1
    
    def create_user(self, email: str, name: str, provider: str, provider_id: str) -> User:
        """Create a new user or return existing one"""
        if email in self.users:
            return self.users[email]
        
        user = User(
            id=self.next_id,
            email=email,
            name=name,
            provider=provider,
            provider_id=provider_id
        )
        
        self.users[email] = user
        self.next_id += 1
        return user
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.users.get(email)
    
    def get_all_users(self) -> Dict[str, User]:
        """Get all users"""
        return self.users

# Global database instance (in production, use a real database)
user_db = UserDatabase()

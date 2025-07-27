from models import db
from datetime import datetime

class UserQuestion(db.Model):
    __tablename__ = 'user_questions'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    question = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), default='General')
    status = db.Column(db.String(20), default='pending')  # pending, answered, archived
    is_public = db.Column(db.Boolean, default=False)  # If answered, can be made public as FAQ
    answer = db.Column(db.Text, nullable=True)  # Admin answer
    answered_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    answered_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to user who answered (admin)
    answerer = db.relationship('User', backref='answered_questions', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'subject': self.subject,
            'question': self.question,
            'category': self.category,
            'status': self.status,
            'is_public': self.is_public,
            'answer': self.answer,
            'answered_by': self.answered_by,
            'answered_at': self.answered_at.isoformat() if self.answered_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<UserQuestion {self.id}: {self.subject}>'

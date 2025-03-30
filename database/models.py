from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
import json

db = SQLAlchemy()

class Session(db.Model):
    __tablename__ = 'sessions'
    
    id = db.Column(db.String(36), primary_key=True)
    scenario = db.Column(db.String(100), nullable=False)
    current_scene_id = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    partial_narrative = db.Column(db.Text, nullable=True)
    
    # Relationships
    narrative_data = relationship("NarrativeData", uselist=False, back_populates="session", cascade="all, delete-orphan")
    scene_prompts = relationship("ScenePrompt", uselist=False, back_populates="session", cascade="all, delete-orphan")
    media_urls = relationship("MediaUrl", uselist=False, back_populates="session", cascade="all, delete-orphan")
    
    @property
    def decision_history(self):
        if self.partial_narrative:
            partial_narrative_obj = json.loads(self.partial_narrative)
            return partial_narrative_obj.get('decision_history', [])
        return []
    
    @decision_history.setter
    def decision_history(self, value):
        if self.partial_narrative:
            partial_narrative_obj = json.loads(self.partial_narrative)
            partial_narrative_obj['decision_history'] = value
            self.partial_narrative = json.dumps(partial_narrative_obj)
        else:
            self.partial_narrative = json.dumps({
                'scenario': self.scenario,
                'last_narrative': None,
                'decision_history': value
            })

class NarrativeData(db.Model):
    __tablename__ = 'narrative_data'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(36), db.ForeignKey('sessions.id', ondelete='CASCADE'), unique=True)
    data = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    session = relationship("Session", back_populates="narrative_data")
    
    @property
    def narrative_obj(self):
        if self.data:
            return json.loads(self.data)
        return None
    
    @narrative_obj.setter
    def narrative_obj(self, value):
        self.data = json.dumps(value)

class ScenePrompt(db.Model):
    __tablename__ = 'scene_prompts'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(36), db.ForeignKey('sessions.id', ondelete='CASCADE'), unique=True)
    data = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    session = relationship("Session", back_populates="scene_prompts")
    
    @property
    def prompts_obj(self):
        if self.data:
            return json.loads(self.data)
        return None
    
    @prompts_obj.setter
    def prompts_obj(self, value):
        self.data = json.dumps(value)

class MediaUrl(db.Model):
    __tablename__ = 'media_urls'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(36), db.ForeignKey('sessions.id', ondelete='CASCADE'), unique=True)
    data = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    session = relationship("Session", back_populates="media_urls")
    
    @property
    def urls_obj(self):
        if self.data:
            return json.loads(self.data)
        return None
    
    @urls_obj.setter
    def urls_obj(self, value):
        self.data = json.dumps(value)

class SceneCache(db.Model):
    __tablename__ = 'scene_cache'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    scenario = db.Column(db.String(100), nullable=False)
    partial_narrative = db.Column(db.Text, nullable=False)
    next_narrative = db.Column(db.Text, nullable=False)
    next_scene_prompts = db.Column(db.Text, nullable=False)
    next_media_urls = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        db.UniqueConstraint('scenario', 'partial_narrative', name='uq_scenario_partial_narrative'),
    )
    
    @property
    def next_narrative_obj(self):
        if self.next_narrative:
            return json.loads(self.next_narrative)
        return None
    
    @next_narrative_obj.setter
    def next_narrative_obj(self, value):
        self.next_narrative = json.dumps(value)
    
    @property
    def next_scene_prompts_obj(self):
        if self.next_scene_prompts:
            return json.loads(self.next_scene_prompts)
        return None
    
    @next_scene_prompts_obj.setter
    def next_scene_prompts_obj(self, value):
        self.next_scene_prompts = json.dumps(value)
    
    @property
    def next_media_urls_obj(self):
        if self.next_media_urls:
            return json.loads(self.next_media_urls)
        return None
    
    @next_media_urls_obj.setter
    def next_media_urls_obj(self, value):
        self.next_media_urls = json.dumps(value)

class Video(db.Model):
    __tablename__ = 'videos'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    filename = db.Column(db.String(255), nullable=False, unique=True)
    url_path = db.Column(db.String(255), nullable=False)
    scene_id = db.Column(db.Integer, nullable=True)
    is_combined = db.Column(db.Boolean, default=False)
    original_prompt = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Video {self.id}: {self.url_path}>" 
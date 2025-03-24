import datetime
import hashlib
import json

import pytz
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy import func

from config import Config

db = SQLAlchemy()

TIMEZONE = pytz.timezone(Config.TIMEZONE)

class Workspace(db.Model):
    __tablename__ = 'workspaces'
    
    id = db.Column(db.String(40), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    nextNoteNum = db.Column(db.Integer, nullable=False)
    time = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    
    # Relationship with Notes
    notes = db.relationship('Notes', backref='workspace', lazy=True, cascade='all, delete-orphan')
    
    @staticmethod
    def get_by_wsName(wsName):
        key_id = hashlib.sha1(wsName.encode('ascii')).hexdigest()
        return Workspace.query.get(key_id)
    
    @staticmethod
    def create(wsName, nextNoteNum, time):
        key_id = hashlib.sha1(wsName.encode('ascii')).hexdigest()
        return Workspace(id=key_id, name=wsName, nextNoteNum=nextNoteNum, time=time)
    
    def localtime_str(self):
        local_datetime = pytz.utc.localize(self.time).astimezone(TIMEZONE)
        return local_datetime.strftime('%Y-%m-%d %H:%M:%S')
    
    def get_notes_list(self, request=None):
        dt = self.time
        load_time = request and request.args.get('time')
        
        if load_time:
            try:
                dt = datetime.datetime.strptime(load_time, '%Y-%m-%d %H:%M:%S')
                dt = TIMEZONE.localize(dt).astimezone(pytz.utc).replace(tzinfo=None)
            except ValueError:
                pass
        
        notes_entity = Notes.query.filter_by(
            workspace_id=self.id, 
            time=dt
        ).first()
        
        if notes_entity:
            return notes_entity.get_notes_json_array()
        return []


class Notes(db.Model):
    __tablename__ = 'notes'
    
    JSKEYS = ('id', 'xPos', 'yPos', 'height', 'width', 
              'bgcolor', 'zIndex', 'text')
    DBKEYS = ('noteid', 'xposition', 'yposition', 'height', 'width',
              'bgcolor', 'zindex', 'text')
    DB2JS = dict(zip(DBKEYS, JSKEYS))
    
    id = db.Column(db.Integer, primary_key=True)
    workspace_id = db.Column(db.String(40), db.ForeignKey('workspaces.id'), nullable=False)
    time = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    notes_json = db.Column(db.Text, nullable=False)
    
    def get_notes_json_array(self):
        return json.loads(self.notes_json)
    
    def set_notes_json_array(self, notes_array):
        self.notes_json = json.dumps(notes_array)
    
    def localtime_str(self):
        local_datetime = pytz.utc.localize(self.time).astimezone(TIMEZONE)
        return local_datetime.strftime('%Y-%m-%d %H:%M:%S')
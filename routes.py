import datetime
import hashlib
import json
import logging
import os
import time
import urllib.parse
from xml.dom.minidom import parseString

import pytz
from flask import Blueprint, current_app, render_template, request, redirect, Response, url_for
from lib import PyRSS2Gen

from models import db, Workspace, Notes
from config import Config

# Create blueprint
webnote_blueprint = Blueprint('webnote', __name__, url_prefix='/webnote')

# Constants
HELPEMAIL = Config.HELPEMAIL
NUM_DATES = Config.NUM_DATES
TIMEZONE = pytz.timezone(Config.TIMEZONE)
CUSTOMHEADER = """
<script>
(function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
(i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
})(window,document,'script','//www.google-analytics.com/analytics.js','ga');

ga('create', 'UA-105084-2', 'auto');
ga('send', 'pageview');
</script>
"""

# Routes
@webnote_blueprint.route('/')
def index():
    return redirect('/webnote/index.html')

@webnote_blueprint.route('/index.html')
def serve_index():
    return current_app.send_static_file('index.html')

@webnote_blueprint.route('/strings.js')
def serve_strings():
    # Detect language from request
    accept_language = request.headers.get('Accept-Language', 'en')
    lang = 'en'  # Default language
    
    for token in accept_language.split(','):
        language = token.split(';')[0].strip().lower()
        if language.startswith('de'):
            lang = 'de'
            break
        elif language.startswith('en'):
            lang = 'en'
            break
    
    # Serve the appropriate language file
    try:
        return current_app.send_static_file(f'strings.js.{lang}')
    except:
        return current_app.send_static_file('strings.js.en')

@webnote_blueprint.route('/save.py', methods=['POST'])
def save_workspace():
    dom = parseString(request.data)
    wsRoot = dom.getElementsByTagName('workspace').item(0)
    wsName = wsRoot.getAttribute('name')
    
    try:
        nextNoteNum = int(wsRoot.getAttribute('nextNoteNum'))
    except:
        nextNoteNum = 0
    
    notesJsonArray = []
    
    nlNotes = wsRoot.getElementsByTagName('note')
    for i in range(nlNotes.length):
        node = nlNotes.item(i)
        note = {}
        for j in range(node.attributes.length):
            attr = node.attributes.item(j)
            
            if attr.name in Notes.DBKEYS:  # Only use valid attributes
                note[Notes.DB2JS[attr.name]] = attr.nodeValue
        note['text'] = node.firstChild.nodeValue.strip()
        notesJsonArray.append(note)
    
    # Transaction to save workspace and notes
    nowtime = datetime.datetime.utcnow().replace(microsecond=0)
    workspace = Workspace.get_by_wsName(wsName)
    
    if not workspace:
        workspace = Workspace.create(wsName, nextNoteNum, nowtime)
        db.session.add(workspace)
    
    workspace.time = nowtime
    workspace.nextNoteNum = nextNoteNum
    
    # Create new Notes record
    notes = Notes(
        workspace_id=workspace.id,
        time=nowtime,
        notes_json=json.dumps(notesJsonArray)
    )
    
    db.session.add(notes)
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error saving workspace: {str(e)}")
        return Response('<return><status value="error"/></return>', 
                        content_type='text/xml')
    
    return Response(
        f'<return><status value="ok" update="{workspace.localtime_str()}"/></return>',
        content_type='text/xml'
    )

@webnote_blueprint.route('/getrecent.py')
def get_recent():
    name = request.args.get('name', '')
    if not name:
        return ''
    
    workspace = Workspace.get_by_wsName(name)
    if not workspace:
        return ''
    
    return workspace.localtime_str()

@webnote_blueprint.route('/getdates.py')
def get_dates():
    name = request.args.get('name', '')
    offset = request.args.get('offset', '0')
    
    if not name:
        return ''
    
    workspace = Workspace.get_by_wsName(name)
    if not workspace:
        return ''
    
    try:
        offset = int(offset)
    except:
        offset = 0
    
    notes = Notes.query.filter_by(workspace_id=workspace.id).order_by(
        Notes.time.desc()
    ).offset(offset).limit(11).all()
    
    return '|'.join(n.localtime_str() for n in notes)

@webnote_blueprint.route('/<name>.xml')
def get_rss(name):
    name = urllib.parse.unquote(name)
    
    workspace = Workspace.get_by_wsName(name)
    if workspace is None:
        return Response('Not Found', status=404)
    
    notes = workspace.get_notes_list(request)
    
    entries = []
    for note in notes:
        entries.append(PyRSS2Gen.RSSItem(
            title=urllib.parse.unquote(note.get('text', '')).strip().split('\n')[0][:60],
            description=urllib.parse.unquote(note.get('text', '')).strip(),
            guid=PyRSS2Gen.Guid('%s/webnote/%s#%s' % (
                request.host_url.rstrip('/'),
                urllib.parse.quote(urllib.parse.quote(workspace.name)),
                note.get('id', ''),
            ))
        ))
    
    # Put the recent entries first
    entries.reverse()
    
    rss = PyRSS2Gen.RSS2(
            title=urllib.parse.unquote(workspace.name),
            description='Webnote RSS feed',
            link='%s/webnote/%s' % (
                request.host_url.rstrip('/'),
                urllib.parse.quote(urllib.parse.quote(workspace.name))),
            lastBuildDate=workspace.time,
            items=entries)
    
    response = Response(content_type='text/xml')
    rss.write_xml(response.stream)
    return response

@webnote_blueprint.route('/<name>')
def load_workspace(name):
    name = urllib.parse.unquote(name)
    
    next_note_num = 0
    lasttime = ''
    notes = []
    
    workspace = Workspace.get_by_wsName(name)
    if workspace:
        next_note_num = workspace.nextNoteNum
        lasttime = workspace.localtime_str()
        
        notes = workspace.get_notes_list(request)
    
    template_values = {
        'debugOn': Config.DEBUG,
        'name': name,
        'lasttime': lasttime,
        'HELPEMAIL': HELPEMAIL,
        'NUM_DATES': NUM_DATES,
        'nextNoteNum': next_note_num,
        'newNoteText': '',  # TODO
        'CUSTOMHEADER': CUSTOMHEADER,
        'notes': json.dumps(notes),
    }
    
    return render_template('workspace.html', **template_values)
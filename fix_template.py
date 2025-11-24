"""
Quick script to fix the list_notes.html file with proper Quick Wins features
"""

# Read the original file
with open(r'd:\CSIT360 BLOCKCHAIN\Blocknotes\note_app\notes\templates\notes\list_notes.html.backup', 'r', encoding='utf-8') as f:
    content = f.read()

# Add view tabs after toolbar-left div opening
view_tabs_html = '''                <!-- View Filter Tabs -->
                <div class="view-tabs">
                    <a href="?view=all" class="view-tab {% if current_view == 'all' or not current_view %}active{% endif %}">
                        📝 All Notes
                    </a>
                    <a href="?view=archive" class="view-tab {% if current_view == 'archive' %}active{% endif %}">
                        📦 Archive
                    </a>
                    <a href="?view=trash" class="view-tab {% if current_view == 'trash' %}active{% endif %}">
                        🗑️ Trash
                    </a>
                </div>

'''

# Insert view tabs
content = content.replace(
    '            <div class="toolbar-left">\r\n                <!-- Search -->',
    f'            <div class="toolbar-left">\r\n{view_tabs_html}                <!-- Search -->'
)

# Add action buttons and update note card
action_buttons_html = '''
                <!-- Quick Actions Bar -->
                <div class="card-actions" onclick="event.stopPropagation();">
                    {% if current_view == 'trash' %}
                        <button class="action-btn restore-btn" data-note-id="{{ note.id }}" title="Restore from trash">
                            ↩️
                        </button>
                    {% elif current_view == 'archive' %}
                        <button class="action-btn unarchive-btn" data-note-id="{{ note.id }}" title="Unarchive">
                            📤
                        </button>
                        <button class="action-btn trash-btn" data-note-id="{{ note.id }}" title="Move to trash">
                            🗑️
                        </button>
                    {% else %}
                        <button class="action-btn pin-btn {% if note.is_pinned %}pinned{% endif %}" data-note-id="{{ note.id }}" title="{% if note.is_pinned %}Unpin{% else %}Pin{% endif %}">
                            📌
                        </button>
                        <button class="action-btn archive-btn" data-note-id="{{ note.id }}" title="Archive">
                            📦
                        </button>
                        <button class="action-btn trash-btn" data-note-id="{{ note.id }}" title="Move to trash">
                            🗑️
                        </button>
                        <div class="color-picker-wrapper">
                            <button class="action-btn color-btn" data-note-id="{{ note.id }}" title="Change color">
                                🎨
                            </button>
                            <div class="color-picker-menu" data-note-id="{{ note.id }}">
                                <button class="color-option" data-color="default" style="background: rgba(255,255,255,0.1);"></button>
                                <button class="color-option" data-color="red" style="background: #ff6b6b;"></button>
                                <button class="color-option" data-color="blue" style="background: #4ecdc4;"></button>
                                <button class="color-option" data-color="green" style="background: #95e1d3;"></button>
                                <button class="color-option" data-color="yellow" style="background: #f9ca24;"></button>
                                <button class="color-option" data-color="purple" style="background: #a29bfe;"></button>
                            </div>
                        </div>
                    {% endif %}
                </div>
'''

# Update note card opening tag
content = content.replace(
    '            <div class="note-card" data-note-id="{{ note.id }}" data-note-title="{{ note.title }}"\r\n                data-note-content="{{ note.content }}" data-note-created="{{ note.created_at|date:\'c\' }}"\r\n                data-note-has-receipt="{% if note.blockchain_receipt %}true{% else %}false{% endif %}">',
    f'''            <div class="note-card color-{{{{ note.color|default:'default' }}}}" data-note-id="{{{{ note.id }}}}" data-note-title="{{{{ note.title }}}}"
                data-note-content="{{{{ note.content }}}}" data-note-created="{{{{ note.created_at|date:'c' }}}}"
                data-note-has-receipt="{{% if note.blockchain_receipt %}}true{{% else %}}false{{% endif %}}" 
                data-note-color="{{{{ note.color|default:'default' }}}}" 
                data-note-pinned="{{{{ note.is_pinned|yesno:'true,false' }}}}" 
                data-note-archived="{{{{ note.is_archived|yesno:'true,false' }}}}">
{action_buttons_html}'''
)

# Add pin indicator
content = content.replace(
    '                <div class="card-header">\r\n                    <h3 class="card-title">{{ note.title }}</h3>',
    '''                <div class="card-header">
                    {% if note.is_pinned %}
                    <span class="pin-indicator" title="Pinned">📌</span>
                    {% endif %}
                    <h3 class="card-title">{{ note.title }}</h3>'''
)

# Write the modified content
with open(r'd:\CSIT360 BLOCKCHAIN\Blocknotes\note_app\notes\templates\notes\list_notes_fixed.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed HTML file created: list_notes_fixed.html")
print("Please review and then rename it to list_notes.html")

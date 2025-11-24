# Simple HTML Patch - Add Action Buttons to Note Cards
# Run this in PowerShell from the note_app directory

$file = "notes\templates\notes\list_notes.html"
$content = Get-Content $file -Raw

# Find the note card div and add action buttons after it
$oldPattern = '            <div class="note-card" data-note-id="{{ note.id }}" data-note-title="{{ note.title }}"
                data-note-content="{{ note.content }}" data-note-created="{{ note.created_at|date:''c'' }}"
                data-note-has-receipt="{% if note.blockchain_receipt %}true{% else %}false{% endif %}">

                <div class="card-header">'

$newPattern = '            <div class="note-card color-{{ note.color|default:''default'' }}" data-note-id="{{ note.id }}" data-note-title="{{ note.title }}"
                data-note-content="{{ note.content }}" data-note-created="{{ note.created_at|date:''c'' }}"
                data-note-has-receipt="{% if note.blockchain_receipt %}true{% else %}false{% endif %}"
                data-note-color="{{ note.color|default:''default'' }}"
                data-note-pinned="{{ note.is_pinned|yesno:''true,false'' }}"
                data-note-archived="{{ note.is_archived|yesno:''true,false'' }}">

                <!-- Quick Actions Bar -->
                <div class="card-actions">
                    {% if current_view == ''trash'' %}
                        <button class="action-btn restore-btn" data-note-id="{{ note.id }}" title="Restore from trash">
                            ↩️
                        </button>
                    {% elif current_view == ''archive'' %}
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

                <div class="card-header">
                    {% if note.is_pinned %}
                    <span class="pin-indicator" title="Pinned">📌</span>
                    {% endif %}'

$content = $content -replace [regex]::Escape($oldPattern), $newPattern

# Save the file
Set-Content $file -Value $content

Write-Host "✅ Action buttons added to note cards!"
Write-Host "Refresh your browser to see the changes."

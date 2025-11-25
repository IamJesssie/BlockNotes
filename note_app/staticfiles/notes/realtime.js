/**
 * BlockNotes Real-Time UI Module
 * Eliminates page reloads by updating the DOM directly after API calls
 */

(function () {
    'use strict';

    // ==================== CONFIGURATION ====================
    const CONFIG = {
        toastDuration: 3000,
        animationDuration: 300,
        debounceDelay: 150
    };

    // ==================== TOAST NOTIFICATION SYSTEM ====================

    let toastContainer = null;

    function initToastContainer() {
        toastContainer = document.querySelector('.toast-container');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.className = 'toast-container';
            document.body.appendChild(toastContainer);
        }
    }

    /**
     * Show a toast notification
     * @param {string} message - The message to display
     * @param {string} type - 'success', 'error', 'warning', 'info'
     * @param {number} duration - Duration in ms
     */
    window.showToast = function (message, type = 'success', duration = CONFIG.toastDuration) {
        if (!toastContainer) initToastContainer();

        const icons = {
            success: '✓',
            error: '✕',
            warning: '⚠',
            info: 'ℹ'
        };

        const titles = {
            success: 'Success',
            error: 'Error',
            warning: 'Warning',
            info: 'Info'
        };

        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.innerHTML = `
            <span class="toast-icon">${icons[type]}</span>
            <div class="toast-content">
                <p class="toast-title">${titles[type]}</p>
                <p class="toast-message">${message}</p>
            </div>
            <button class="toast-close" aria-label="Close">×</button>
        `;

        toastContainer.appendChild(toast);

        // Trigger animation
        requestAnimationFrame(() => {
            toast.classList.add('show');
        });

        // Close button handler
        toast.querySelector('.toast-close').addEventListener('click', () => {
            hideToast(toast);
        });

        // Auto-hide after duration
        setTimeout(() => {
            hideToast(toast);
        }, duration);

        return toast;
    };

    function hideToast(toast) {
        if (!toast || !toast.parentNode) return;
        toast.classList.remove('show');
        toast.classList.add('hiding');
        setTimeout(() => {
            if (toast.parentNode) toast.remove();
        }, CONFIG.animationDuration);
    }

    // ==================== UTILITY FUNCTIONS ====================

    function debounce(fn, delay) {
        let timer;
        return function (...args) {
            clearTimeout(timer);
            timer = setTimeout(() => fn.apply(this, args), delay);
        };
    }

    function updateNoteCount() {
        const noteCountEl = document.getElementById('note-count');
        if (noteCountEl) {
            const visibleCards = document.querySelectorAll('.note-card:not(.fade-out):not([style*="display: none"])');
            const count = visibleCards.length;
            noteCountEl.textContent = `${count} note${count !== 1 ? 's' : ''}`;
        }
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    function truncateText(text, maxLength) {
        if (!text) return '';
        if (text.length <= maxLength) return text;
        return text.substring(0, maxLength) + '...';
    }

    function getCSRFToken() {
        const input = document.querySelector('input[name="csrfmiddlewaretoken"]');
        if (input) return input.value;
        const meta = document.querySelector('meta[name="csrf-token"]');
        if (meta) return meta.content;
        return '';
    }

    // ==================== CARD REMOVAL WITH ANIMATION ====================

    function removeCardWithAnimation(noteId, callback) {
        const card = document.querySelector(`[data-note-id="${noteId}"]`);
        if (card) {
            card.classList.add('fade-out');
            setTimeout(() => {
                card.remove();
                updateNoteCount();
                checkEmptyState();
                if (callback) callback();
            }, CONFIG.animationDuration);
        }
    }

    function checkEmptyState() {
        const container = document.getElementById('notes-grid-container');
        if (!container) return;

        const remainingCards = container.querySelectorAll('.note-card');
        const existingEmpty = container.querySelector('.empty-state-grid:not(.search-empty-state)');

        if (remainingCards.length === 0 && !existingEmpty) {
            const emptyState = document.createElement('div');
            emptyState.className = 'empty-state-grid';
            emptyState.innerHTML = `
                <div class="empty-state-icon-wrapper">
                    <span style="font-size: 40px;">📝</span>
                </div>
                <h3>No notes yet</h3>
                <p>Create your first blockchain-secured note</p>
            `;
            container.appendChild(emptyState);
        }
    }

    // ==================== PIN/UNPIN HANDLER ====================

    function handlePin(noteId, btn) {
        const card = document.querySelector(`[data-note-id="${noteId}"]`);
        if (!card) return;

        // Optimistic UI update
        const wasPinned = card.dataset.notePinned === 'true';
        const newPinned = !wasPinned;

        card.dataset.notePinned = newPinned ? 'true' : 'false';
        btn.classList.toggle('pinned', newPinned);

        // Update pin indicator in card header
        const header = card.querySelector('.card-header');
        let pinIndicator = header.querySelector('.pin-indicator');

        if (newPinned && !pinIndicator) {
            pinIndicator = document.createElement('span');
            pinIndicator.className = 'pin-indicator';
            pinIndicator.title = 'Pinned';
            pinIndicator.textContent = '📌';
            header.insertBefore(pinIndicator, header.firstChild);
        } else if (!newPinned && pinIndicator) {
            pinIndicator.remove();
        }

        // Add loading state
        btn.classList.add('loading');

        fetch(`/notes/pin/${noteId}/`, {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: `csrfmiddlewaretoken=${getCSRFToken()}`
        })
            .then(res => res.json())
            .then(data => {
                btn.classList.remove('loading');
                if (data.success) {
                    showToast(data.message || (newPinned ? 'Note pinned' : 'Note unpinned'), 'success');
                    // Re-sort to move pinned notes to top
                    sortNotesClient(getCurrentSort());
                } else {
                    // Rollback on failure
                    card.dataset.notePinned = wasPinned ? 'true' : 'false';
                    btn.classList.toggle('pinned', wasPinned);
                    if (wasPinned && !header.querySelector('.pin-indicator')) {
                        const indicator = document.createElement('span');
                        indicator.className = 'pin-indicator';
                        indicator.textContent = '📌';
                        header.insertBefore(indicator, header.firstChild);
                    } else if (!wasPinned) {
                        const indicator = header.querySelector('.pin-indicator');
                        if (indicator) indicator.remove();
                    }
                    showToast('Failed to update pin status', 'error');
                }
            })
            .catch(err => {
                btn.classList.remove('loading');
                console.error('Pin failed:', err);
                // Rollback
                card.dataset.notePinned = wasPinned ? 'true' : 'false';
                btn.classList.toggle('pinned', wasPinned);
                showToast('Failed to update pin status', 'error');
            });
    }

    // ==================== ARCHIVE HANDLER ====================

    function handleArchive(noteId, btn) {
        const card = document.querySelector(`[data-note-id="${noteId}"]`);
        if (!card) return;

        const currentView = document.body.dataset.currentView || 'all';

        // Add loading state
        btn.classList.add('loading');

        fetch(`/notes/archive/${noteId}/`, {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: `csrfmiddlewaretoken=${getCSRFToken()}`
        })
            .then(res => res.json())
            .then(data => {
                btn.classList.remove('loading');
                if (data.success) {
                    // If we're in "all" view and note is archived, remove it
                    // If we're in "archive" view and note is unarchived, remove it
                    if ((currentView === 'all' && data.is_archived) ||
                        (currentView === 'archive' && !data.is_archived)) {
                        removeCardWithAnimation(noteId);
                    }

                    card.dataset.noteArchived = data.is_archived ? 'true' : 'false';
                    showToast(data.message || (data.is_archived ? 'Note archived' : 'Note unarchived'), 'success');
                } else {
                    showToast('Failed to archive note', 'error');
                }
            })
            .catch(err => {
                btn.classList.remove('loading');
                console.error('Archive failed:', err);
                showToast('Failed to archive note', 'error');
            });
    }

    // ==================== TRASH HANDLER ====================

    function handleTrash(noteId, btn) {
        const card = document.querySelector(`[data-note-id="${noteId}"]`);
        if (!card) return;

        // Add loading state
        btn.classList.add('loading');

        fetch(`/notes/trash/${noteId}/`, {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: `csrfmiddlewaretoken=${getCSRFToken()}`
        })
            .then(res => res.json())
            .then(data => {
                btn.classList.remove('loading');
                if (data.success) {
                    removeCardWithAnimation(noteId);
                    showToast(data.message || 'Note moved to trash', 'success');
                } else {
                    showToast('Failed to move note to trash', 'error');
                }
            })
            .catch(err => {
                btn.classList.remove('loading');
                console.error('Trash failed:', err);
                showToast('Failed to move note to trash', 'error');
            });
    }

    // ==================== RESTORE HANDLER ====================

    function handleRestore(noteId, btn) {
        const card = document.querySelector(`[data-note-id="${noteId}"]`);
        if (!card) return;

        // Add loading state
        btn.classList.add('loading');

        fetch(`/notes/restore/${noteId}/`, {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: `csrfmiddlewaretoken=${getCSRFToken()}`
        })
            .then(res => res.json())
            .then(data => {
                btn.classList.remove('loading');
                if (data.success) {
                    removeCardWithAnimation(noteId);
                    showToast(data.message || 'Note restored', 'success');
                } else {
                    showToast('Failed to restore note', 'error');
                }
            })
            .catch(err => {
                btn.classList.remove('loading');
                console.error('Restore failed:', err);
                showToast('Failed to restore note', 'error');
            });
    }

    // ==================== COLOR HANDLER ====================

    function handleColorChange(noteId, color, menu) {
        const card = document.querySelector(`[data-note-id="${noteId}"]`);
        if (!card) return;

        const oldColor = card.dataset.noteColor || 'default';

        // Optimistic UI update
        card.className = card.className.replace(/color-\w+/, `color-${color}`);
        card.dataset.noteColor = color;
        menu.classList.remove('show');

        const formData = new FormData();
        formData.append('color', color);
        formData.append('csrfmiddlewaretoken', getCSRFToken());

        fetch(`/notes/color/${noteId}/`, {
            method: 'POST',
            headers: { 'X-Requested-With': 'XMLHttpRequest' },
            body: formData
        })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    showToast('Color updated', 'success');
                } else {
                    // Rollback
                    card.className = card.className.replace(/color-\w+/, `color-${oldColor}`);
                    card.dataset.noteColor = oldColor;
                    showToast('Failed to update color', 'error');
                }
            })
            .catch(err => {
                console.error('Color update failed:', err);
                // Rollback
                card.className = card.className.replace(/color-\w+/, `color-${oldColor}`);
                card.dataset.noteColor = oldColor;
                showToast('Failed to update color', 'error');
            });
    }

    // ==================== CLIENT-SIDE SEARCH ====================

    function filterNotesClient(query) {
        const container = document.getElementById('notes-grid-container');
        if (!container) return;

        const cards = container.querySelectorAll('.note-card');
        const lowerQuery = (query || '').toLowerCase().trim();
        let visibleCount = 0;

        cards.forEach(card => {
            const title = (card.dataset.noteTitle || '').toLowerCase();
            const content = (card.dataset.noteContent || '').toLowerCase();

            if (!lowerQuery || title.includes(lowerQuery) || content.includes(lowerQuery)) {
                card.style.display = '';
                visibleCount++;
            } else {
                card.style.display = 'none';
            }
        });

        updateNoteCount();

        // Show/hide search empty state
        let searchEmpty = container.querySelector('.search-empty-state');
        if (visibleCount === 0 && cards.length > 0) {
            if (!searchEmpty) {
                searchEmpty = document.createElement('div');
                searchEmpty.className = 'empty-state-grid search-empty-state';
                searchEmpty.innerHTML = `
                    <div class="empty-state-icon-wrapper">
                        <span style="font-size: 40px;">🔍</span>
                    </div>
                    <h3>No notes found</h3>
                    <p>Try a different search term</p>
                `;
                container.appendChild(searchEmpty);
            }
        } else if (searchEmpty) {
            searchEmpty.remove();
        }

        // Update URL without reload
        const params = new URLSearchParams(window.location.search);
        if (lowerQuery) {
            params.set('q', query.trim());
        } else {
            params.delete('q');
        }
        const newUrl = window.location.pathname + (params.toString() ? ('?' + params.toString()) : '');
        try {
            window.history.replaceState({}, '', newUrl);
        } catch (err) {
            console.debug('history.replaceState failed', err);
        }
    }

    // ==================== CLIENT-SIDE SORTING ====================

    const SORT_OPTIONS = [
        { value: '-created_at', label: 'Newest' },
        { value: 'created_at', label: 'Oldest' },
        { value: 'title', label: 'A-Z' },
        { value: '-title', label: 'Z-A' }
    ];

    function getCurrentSort() {
        const params = new URLSearchParams(window.location.search);
        return params.get('sort') || '-created_at';
    }

    function sortNotesClient(mode) {
        const container = document.getElementById('notes-grid-container');
        if (!container) return;

        const items = Array.from(container.querySelectorAll('.note-card'));
        if (items.length === 0) return;

        const collator = new Intl.Collator(undefined, { sensitivity: 'base', numeric: true });

        // Separate pinned and unpinned notes
        const pinned = items.filter(card => card.dataset.notePinned === 'true');
        const unpinned = items.filter(card => card.dataset.notePinned !== 'true');

        const sortFn = (a, b) => {
            const aTitle = (a.dataset.noteTitle || '').trim();
            const bTitle = (b.dataset.noteTitle || '').trim();
            const aCreated = new Date(a.dataset.noteCreated || 0);
            const bCreated = new Date(b.dataset.noteCreated || 0);

            if (mode === '-created_at') return bCreated - aCreated;
            if (mode === 'created_at') return aCreated - bCreated;
            if (mode === 'title') return collator.compare(aTitle, bTitle);
            if (mode === '-title') return collator.compare(bTitle, aTitle);
            return 0;
        };

        pinned.sort(sortFn);
        unpinned.sort(sortFn);

        const frag = document.createDocumentFragment();
        pinned.forEach(it => frag.appendChild(it));
        unpinned.forEach(it => frag.appendChild(it));

        // Preserve empty states
        const emptyStates = container.querySelectorAll('.empty-state-grid');
        container.innerHTML = '';
        container.appendChild(frag);
        emptyStates.forEach(es => {
            if (items.length === 0) container.appendChild(es);
        });
    }

    // Make sortNotesClient available globally
    window.sortNotesClient = sortNotesClient;

    // ==================== EVENT DELEGATION ====================

    function initEventListeners() {
        // PIN/UNPIN
        document.addEventListener('click', function (e) {
            const btn = e.target.closest('.pin-btn');
            if (btn) {
                e.stopPropagation();
                handlePin(btn.dataset.noteId, btn);
            }
        });

        // ARCHIVE
        document.addEventListener('click', function (e) {
            const btn = e.target.closest('.archive-btn');
            if (btn) {
                e.stopPropagation();
                handleArchive(btn.dataset.noteId, btn);
            }
        });

        // TRASH
        document.addEventListener('click', function (e) {
            const btn = e.target.closest('.trash-btn');
            if (btn) {
                e.stopPropagation();
                handleTrash(btn.dataset.noteId, btn);
            }
        });

        // RESTORE
        document.addEventListener('click', function (e) {
            const btn = e.target.closest('.restore-btn');
            if (btn) {
                e.stopPropagation();
                handleRestore(btn.dataset.noteId, btn);
            }
        });

        // COLOR PICKER TOGGLE
        document.addEventListener('click', function (e) {
            const btn = e.target.closest('.color-btn');
            if (btn) {
                e.stopPropagation();
                const wrapper = btn.closest('.color-picker-wrapper');
                const menu = wrapper.querySelector('.color-picker-menu');

                // Close all other color pickers
                document.querySelectorAll('.color-picker-menu').forEach(m => {
                    if (m !== menu) m.classList.remove('show');
                });

                menu.classList.toggle('show');
            }
        });

        // COLOR SELECTION
        document.addEventListener('click', function (e) {
            const option = e.target.closest('.color-option');
            if (option) {
                e.stopPropagation();
                const menu = option.closest('.color-picker-menu');
                const noteId = menu.dataset.noteId;
                const color = option.dataset.color;
                handleColorChange(noteId, color, menu);
            }
        });

        // Close color picker when clicking outside
        document.addEventListener('click', function (e) {
            if (!e.target.closest('.color-picker-wrapper')) {
                document.querySelectorAll('.color-picker-menu').forEach(menu => {
                    menu.classList.remove('show');
                });
            }
        });

        // SEARCH INPUT
        const searchInput = document.getElementById('search-input');
        if (searchInput) {
            const debouncedFilter = debounce(function () {
                filterNotesClient(searchInput.value);
            }, CONFIG.debounceDelay);

            searchInput.addEventListener('input', debouncedFilter);
            searchInput.addEventListener('keydown', function (e) {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    filterNotesClient(searchInput.value);
                }
            });
        }

        // SORT DROPDOWN
        const dropdownWrapper = document.querySelector('.sort-dropdown');
        if (dropdownWrapper) {
            const current = dropdownWrapper.querySelector('#sort-current');
            const toggleBtn = dropdownWrapper.querySelector('#sort-dropdown-toggle');
            const initialSort = getCurrentSort();

            const selectedOpt = SORT_OPTIONS.find(o => o.value === initialSort) || SORT_OPTIONS[0];
            if (current) current.textContent = selectedOpt.label;

            if (toggleBtn) {
                let currentIndex = SORT_OPTIONS.findIndex(o => o.value === initialSort);
                if (currentIndex === -1) currentIndex = 0;

                toggleBtn.addEventListener('click', function (e) {
                    e.preventDefault();
                    e.stopPropagation();

                    currentIndex = (currentIndex + 1) % SORT_OPTIONS.length;
                    const next = SORT_OPTIONS[currentIndex];

                    if (current) current.textContent = next.label;
                    sortNotesClient(next.value);

                    const params = new URLSearchParams(window.location.search);
                    if (next.value) params.set('sort', next.value);
                    else params.delete('sort');
                    const newUrl = window.location.pathname + (params.toString() ? ('?' + params.toString()) : '');
                    try {
                        window.history.replaceState({}, '', newUrl);
                    } catch (err) {
                        console.debug('history.replaceState failed', err);
                    }
                });
            }
        }
    }

    // ==================== INITIALIZATION ====================

    function init() {
        initToastContainer();
        initEventListeners();

        // Initial sort
        sortNotesClient(getCurrentSort());

        // Store current view in body for reference
        const viewTab = document.querySelector('.view-tab.active');
        if (viewTab) {
            const href = viewTab.getAttribute('href') || '';
            if (href.includes('view=trash')) {
                document.body.dataset.currentView = 'trash';
            } else if (href.includes('view=archive')) {
                document.body.dataset.currentView = 'archive';
            } else {
                document.body.dataset.currentView = 'all';
            }
        }

        console.log('BlockNotes Real-Time UI initialized');
    }

    // Run on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();
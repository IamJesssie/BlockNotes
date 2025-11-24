// Quick Wins Features JavaScript
// This file handles pin, archive, trash, restore, and color picker functionality

document.addEventListener('DOMContentLoaded', function () {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    // Helper function to make API calls
    function makeQuickAction(url, successCallback) {
        fetch(url, {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: `csrfmiddlewaretoken=${csrfToken}`
        })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    if (successCallback) {
                        successCallback(data);
                    } else {
                        window.location.reload();
                    }
                } else {
                    console.error('Action failed:', data);
                    alert('Action failed. Please try again.');
                }
            })
            .catch(err => {
                console.error('Request failed:', err);
                alert('Request failed. Please try again.');
            });
    }

    // PIN/UNPIN Handler
    document.addEventListener('click', function (e) {
        const pinBtn = e.target.closest('.pin-btn');
        if (pinBtn) {
            e.stopPropagation();
            e.preventDefault();
            const noteId = pinBtn.dataset.noteId;
            makeQuickAction(`/notes/pin/${noteId}/`);
        }
    });

    // ARCHIVE Handler
    document.addEventListener('click', function (e) {
        const archiveBtn = e.target.closest('.archive-btn');
        if (archiveBtn) {
            e.stopPropagation();
            e.preventDefault();
            const noteId = archiveBtn.dataset.noteId;
            makeQuickAction(`/notes/archive/${noteId}/`);
        }
    });

    // UNARCHIVE Handler
    document.addEventListener('click', function (e) {
        const unarchiveBtn = e.target.closest('.unarchive-btn');
        if (unarchiveBtn) {
            e.stopPropagation();
            e.preventDefault();
            const noteId = unarchiveBtn.dataset.noteId;
            makeQuickAction(`/notes/archive/${noteId}/`); // Same endpoint, it toggles
        }
    });

    // TRASH Handler
    document.addEventListener('click', function (e) {
        const trashBtn = e.target.closest('.trash-btn');
        if (trashBtn) {
            e.stopPropagation();
            e.preventDefault();
            const noteId = trashBtn.dataset.noteId;

            if (!confirm('Move this note to trash?')) return;

            makeQuickAction(`/notes/trash/${noteId}/`);
        }
    });

    // RESTORE Handler
    document.addEventListener('click', function (e) {
        const restoreBtn = e.target.closest('.restore-btn');
        if (restoreBtn) {
            e.stopPropagation();
            e.preventDefault();
            const noteId = restoreBtn.dataset.noteId;
            makeQuickAction(`/notes/restore/${noteId}/`);
        }
    });

    // COLOR PICKER Toggle
    document.addEventListener('click', function (e) {
        const colorBtn = e.target.closest('.color-btn');
        if (colorBtn) {
            e.stopPropagation();
            e.preventDefault();
            const wrapper = colorBtn.closest('.color-picker-wrapper');
            const menu = wrapper.querySelector('.color-picker-menu');

            // Close all other color pickers
            document.querySelectorAll('.color-picker-menu').forEach(m => {
                if (m !== menu) m.classList.remove('show');
            });

            menu.classList.toggle('show');
        }
    });

    // COLOR SELECTION Handler
    document.addEventListener('click', function (e) {
        const colorOption = e.target.closest('.color-option');
        if (colorOption) {
            e.stopPropagation();
            e.preventDefault();
            const color = colorOption.dataset.color;
            const menu = colorOption.closest('.color-picker-menu');
            const noteId = menu.dataset.noteId;

            const formData = new FormData();
            formData.append('color', color);
            formData.append('csrfmiddlewaretoken', csrfToken);

            fetch(`/notes/color/${noteId}/`, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: formData
            })
                .then(res => res.json())
                .then(data => {
                    if (data.success) {
                        // Update card color class
                        const card = document.querySelector(`[data-note-id="${noteId}"]`);
                        if (card) {
                            card.className = card.className.replace(/color-\w+/, `color-${color}`);
                        }
                        menu.classList.remove('show');
                    }
                })
                .catch(err => console.error('Color update failed:', err));
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

    // Prevent card click when clicking action buttons
    document.querySelectorAll('.card-actions').forEach(actions => {
        actions.addEventListener('click', function (e) {
            e.stopPropagation();
        });
    });
});


document.addEventListener('DOMContentLoaded', () => {
    const state = {
        notes: [],
        currentView: 'home',
        selectedNoteId: null,
    };

    constSTORAGE_KEY = 'Notes.items';

    // DOM Elements
    const homeView = document.getElementById('home-view');
    const detailView = document.getElementById('detail-view');
    const settingsView = document.getElementById('settings-view');
    const notesList = document.getElementById('notes-list');
    const newNoteBtn = document.getElementById('new-note-btn');
    const noteForm = document.getElementById('note-form');
    const cancelBtn = document.getElementById('cancel-btn');
    const deleteNoteBtn = document.getElementById('delete-note-btn');
    const homeBtn = document.getElementById('home-btn');
    const settingsBtn = document.getElementById('settings-btn');
    const searchInput = document.getElementById('search-input');
    const importBtn = document.getElementById('import-btn');
    const importFile = document.getElementById('import-file');
    const exportBtn = document.getElementById('export-btn');
    const clearAllBtn = document.getElementById('clear-all-btn');

    // Utility Functions
    const generateUUID = () => crypto.randomUUID();
    const getCurrentTimestamp = () => new Date().toISOString();

    // Data Persistence
    const getNotes = () => {
        try {
            const notes = localStorage.getItem(STORAGE_KEY);
            return notes ? JSON.parse(notes) : [];
        } catch (e) {
            console.error('Error reading notes from localStorage', e);
            return [];
        }
    };

    const saveNotes = () => {
        try {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(state.notes));
        } catch (e) {
            console.error('Error saving notes to localStorage', e);
        }
    };

    // View Management
    const showView = (viewId) => {
        state.currentView = viewId;
        homeView.style.display = 'none';
        detailView.style.display = 'none';
        settingsView.style.display = 'none';
        document.getElementById(viewId).style.display = 'block';
    };

    // Render Functions
    const renderNotes = (notesToRender = state.notes) => {
        notesList.innerHTML = '';
        const sortedNotes = [...notesToRender].sort((a, b) => new Date(b.updatedAt) - new Date(a.updatedAt));
        sortedNotes.forEach(note => {
            const noteCard = document.createElement('div');
            noteCard.className = 'note-card';
            noteCard.dataset.id = note.id;
            noteCard.innerHTML = `
                <h3>${note.title}</h3>
                <p>${note.description.substring(0, 100)}...</p>
                <small>${new Date(note.updatedAt).toLocaleString()}</small>
            `;
            noteCard.addEventListener('click', () => {
                state.selectedNoteId = note.id;
                const selectedNote = state.notes.find(n => n.id === note.id);
                document.getElementById('note-id').value = selectedNote.id;
                document.getElementById('note-title').value = selectedNote.title;
                document.getElementById('note-description').value = selectedNote.description;
                document.getElementById('note-tags').value = selectedNote.tags.join(', ');
                document.getElementById('note-pinned').checked = selectedNote.pinned;
                showView('detail-view');
            });
            notesList.appendChild(noteCard);
        });
    };

    // Event Handlers
    newNoteBtn.addEventListener('click', () => {
        state.selectedNoteId = null;
        noteForm.reset();
        document.getElementById('note-id').value = '';
        showView('detail-view');
    });

    cancelBtn.addEventListener('click', () => {
        showView('home-view');
    });

    noteForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const id = document.getElementById('note-id').value;
        const title = document.getElementById('note-title').value;
        const description = document.getElementById('note-description').value;
        const tags = document.getElementById('note-tags').value.split(',').map(tag => tag.trim());
        const pinned = document.getElementById('note-pinned').checked;
        const now = getCurrentTimestamp();

        if (id) { // Update existing note
            const noteIndex = state.notes.findIndex(n => n.id === id);
            state.notes[noteIndex] = { ...state.notes[noteIndex], title, description, tags, pinned, updatedAt: now };
        } else { // Create new note
            const newNote = { id: generateUUID(), title, description, tags, pinned, createdAt: now, updatedAt: now };
            state.notes.push(newNote);
        }

        saveNotes();
        renderNotes();
        showView('home-view');
    });

    deleteNoteBtn.addEventListener('click', () => {
        if (state.selectedNoteId && confirm('Are you sure you want to delete this note?')) {
            state.notes = state.notes.filter(n => n.id !== state.selectedNoteId);
            saveNotes();
            renderNotes();
            showView('home-view');
        }
    });

    homeBtn.addEventListener('click', () => showView('home-view'));
    settingsBtn.addEventListener('click', () => showView('settings-view'));

    searchInput.addEventListener('input', (e) => {
        const query = e.target.value.toLowerCase();
        const filteredNotes = state.notes.filter(note =>
            note.title.toLowerCase().includes(query) ||
            note.description.toLowerCase().includes(query)
        );
        renderNotes(filteredNotes);
    });
    
    exportBtn.addEventListener('click', () => {
        const dataStr = JSON.stringify(state.notes, null, 2);
        const dataUri = 'data:application/json;charset=utf-8,' + encodeURIComponent(dataStr);
        const exportFileDefaultName = 'notes.json';
        const linkElement = document.createElement('a');
        linkElement.setAttribute('href', dataUri);
        linkElement.setAttribute('download', exportFileDefaultName);
        linkElement.click();
    });
    
    clearAllBtn.addEventListener('click', () => {
        if (confirm('Are you sure you want to delete all notes? This cannot be undone.')) {
            state.notes = [];
            saveNotes();
            renderNotes();
        }
    });

    importBtn.addEventListener('click', () => {
        importFile.click();
    });
    
    importFile.addEventListener('change', (event) => {
        const file = event.target.files[0];
        if (!file) {
            return;
        }
        const reader = new FileReader();
        reader.onload = (e) => {
            try {
                const importedNotes = JSON.parse(e.target.result);
                if (Array.isArray(importedNotes)) {
                    state.notes = [...state.notes, ...importedNotes.filter(n => n.id && n.title)];
                    saveNotes();
                    renderNotes();
                    alert('Notes imported successfully!');
                } else {
                    alert('Invalid file format.');
                }
            } catch (error) {
                alert('Error importing notes: ' + error.message);
            }
        };
        reader.readAsText(file);
    });

    // Init
    const init = () => {
        state.notes = getNotes();
        renderNotes();
        showView('home-view');
    };

    init();
});

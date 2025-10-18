
document.addEventListener('DOMContentLoaded', () => {
    // State
    let state = {
        logs: [],
        currentView: 'list',
        editingLogId: null,
        filter: {
            search: '',
            date: ''
        }
    };

    // DOM Elements
    const listView = document.getElementById('list-view');
    const detailView = document.getElementById('detail-view');
    const settingsView = document.getElementById('settings-view');
    const logList = document.getElementById('log-list');
    const logForm = document.getElementById('log-form');
    const newLogBtn = document.getElementById('new-log-btn');
    const navListBtn = document.getElementById('nav-list');
    const navSettingsBtn = document.getElementById('nav-settings');
    const cancelBtn = document.getElementById('cancel-btn');
    const addSetBtn = document.getElementById('add-set-btn');
    const searchInput = document.getElementById('search-input');
    const dateFilter = document.getElementById('date-filter');
    const importBtn = document.getElementById('import-btn');
    const importFile = document.getElementById('import-file');
    const exportBtn = document.getElementById('export-btn');
    const clearDataBtn = document.getElementById('clear-data-btn');
    const setsContainer = document.getElementById('sets-container');

    // Data Persistence
    const STORAGE_KEY = 'GymTracker.items';

    function loadLogs() {
        const logs = localStorage.getItem(STORAGE_KEY);
        return logs ? JSON.parse(logs) : [];
    }

    function saveLogs() {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(state.logs));
    }

    // Navigation
    function navigateTo(view) {
        state.currentView = view;
        listView.style.display = 'none';
        detailView.style.display = 'none';
        settingsView.style.display = 'none';

        if (view === 'list') {
            listView.style.display = 'block';
            renderLogList();
        } else if (view === 'detail') {
            detailView.style.display = 'block';
        } else if (view === 'settings') {
            settingsView.style.display = 'block';
        }
    }

    // Rendering
    function renderLogList() {
        logList.innerHTML = '';
        const filteredLogs = state.logs.filter(log => {
            const searchMatch = log.title.toLowerCase().includes(state.filter.search.toLowerCase());
            const dateMatch = !state.filter.date || log.workoutDate === state.filter.date;
            return searchMatch && dateMatch;
        });

        filteredLogs.forEach(log => {
            const li = document.createElement('li');
            li.innerHTML = `
                <div>
                    <strong>${log.title}</strong> - <span>${log.workoutDate}</span>
                </div>
                <div>
                    <span>Sets: ${log.repsPerSet.length}</span>
                    <span>Reps: ${log.repsPerSet.join('/')}</span>
                </div>
                <div>
                    <button class="edit-btn" data-id="${log.id}">Edit</button>
                    <button class="delete-btn" data-id="${log.id}">Delete</button>
                </div>
            `;
            logList.appendChild(li);
        });
    }

    function renderLogForm(log) {
        logForm.reset();
        document.getElementById('log-id').value = log ? log.id : '';
        document.getElementById('exercise-name').value = log ? log.title : '';
        document.getElementById('workout-date').value = log ? log.workoutDate : new Date().toISOString().split('T')[0];
        document.getElementById('notes').value = log ? log.description : '';
        
        setsContainer.innerHTML = '<label>Sets (reps):</label>';
        const reps = log ? log.repsPerSet : [10];
        reps.forEach(rep => {
            addSetInput(rep);
        });

        state.editingLogId = log ? log.id : null;
        navigateTo('detail');
    }

    function addSetInput(reps = '') {
        const div = document.createElement('div');
        div.innerHTML = `
            <input type="number" class="reps-input" value="${reps}" min="1" required>
            <button type="button" class="remove-set-btn">Remove</button>
        `;
        setsContainer.appendChild(div);
    }

    // Event Handlers
    newLogBtn.addEventListener('click', () => renderLogForm(null));
    navListBtn.addEventListener('click', () => navigateTo('list'));
    navSettingsBtn.addEventListener('click', () => navigateTo('settings'));
    cancelBtn.addEventListener('click', () => navigateTo('list'));
    addSetBtn.addEventListener('click', () => addSetInput());

    setsContainer.addEventListener('click', (e) => {
        if (e.target.classList.contains('remove-set-btn')) {
            e.target.parentElement.remove();
        }
    });
    
    logForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const id = document.getElementById('log-id').value || crypto.randomUUID();
        const title = document.getElementById('exercise-name').value;
        const workoutDate = document.getElementById('workout-date').value;
        const description = document.getElementById('notes').value;
        const repsPerSet = [...setsContainer.querySelectorAll('.reps-input')].map(input => parseInt(input.value));

        if (!title || !workoutDate || repsPerSet.some(isNaN)) {
            alert('Please fill out all required fields.');
            return;
        }

        const log = { id, title, workoutDate, description, repsPerSet, createdAt: new Date().toISOString(), updatedAt: new Date().toISOString() };

        if (state.editingLogId) {
            const index = state.logs.findIndex(l => l.id === state.editingLogId);
            state.logs[index] = { ...state.logs[index], ...log, updatedAt: new Date().toISOString() };
        } else {
            state.logs.unshift(log);
        }

        saveLogs();
        navigateTo('list');
    });

    logList.addEventListener('click', (e) => {
        const id = e.target.dataset.id;
        if (e.target.classList.contains('edit-btn')) {
            const log = state.logs.find(l => l.id === id);
            renderLogForm(log);
        } else if (e.target.classList.contains('delete-btn')) {
            if (confirm('Are you sure you want to delete this log?')) {
                state.logs = state.logs.filter(l => l.id !== id);
                saveLogs();
                renderLogList();
            }
        }
    });

    searchInput.addEventListener('input', (e) => {
        state.filter.search = e.target.value;
        renderLogList();
    });

    dateFilter.addEventListener('change', (e) => {
        state.filter.date = e.target.value;
        renderLogList();
    });

    importBtn.addEventListener('click', () => importFile.click());
    importFile.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (event) => {
                try {
                    const importedLogs = JSON.parse(event.target.result);
                    if (confirm('Merge with existing data? (Cancel to replace)')) {
                        state.logs = [...state.logs, ...importedLogs];
                    } else {
                        state.logs = importedLogs;
                    }
                    saveLogs();
                    navigateTo('list');
                } catch (error) {
                    alert('Invalid JSON file.');
                }
            };
            reader.readAsText(file);
        }
    });

    exportBtn.addEventListener('click', () => {
        const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(state.logs, null, 2));
        const downloadAnchorNode = document.createElement('a');
        downloadAnchorNode.setAttribute("href", dataStr);
        downloadAnchorNode.setAttribute("download", "GymTracker_export.json");
        document.body.appendChild(downloadAnchorNode);
        downloadAnchorNode.click();
        downloadAnchorNode.remove();
    });

    clearDataBtn.addEventListener('click', () => {
        if (confirm('Are you sure you want to delete all data? This cannot be undone.')) {
            state.logs = [];
            saveLogs();
            navigateTo('list');
        }
    });


    // Initialization
    function init() {
        state.logs = loadLogs();
        navigateTo('list');
    }

    init();
});

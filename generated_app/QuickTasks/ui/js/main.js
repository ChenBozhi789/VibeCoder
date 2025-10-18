
document.addEventListener('DOMContentLoaded', () => {
    // State
    let state = {
        tasks: [],
        currentView: 'main', // 'main', 'form', 'settings'
        editingTaskId: null,
        filter: 'all',
        searchTerm: ''
    };

    // DOM Elements
    const mainView = document.getElementById('main-view');
    const formView = document.getElementById('form-view');
    const settingsView = document.getElementById('settings-view');
    const taskList = document.getElementById('task-list');
    const taskForm = document.getElementById('task-form');
    const newTaskBtn = document.getElementById('new-task-btn');
    const settingsBtn = document.getElementById('settings-btn');
    const cancelBtn = document.getElementById('cancel-btn');
    const backToMainBtn = document.getElementById('back-to-main-btn');
    const searchBar = document.getElementById('search-bar');
    const filterButtons = document.querySelector('.filter-buttons');
    const exportBtn = document.getElementById('export-btn');
    const importBtn = document.getElementById('import-btn');
    const importFile = document.getElementById('import-file');
    const clearAllBtn = document.getElementById('clear-all-btn');

    // --- State Management and Data Persistence ---

    const saveState = () => {
        localStorage.setItem('quicktasks.tasks', JSON.stringify(state.tasks));
    };

    const loadState = () => {
        const tasks = localStorage.getItem('quicktasks.tasks');
        if (tasks) {
            state.tasks = JSON.parse(tasks);
        }
    };

    // --- Rendering ---

    const render = () => {
        // Render view
        mainView.classList.toggle('hidden', state.currentView !== 'main');
        formView.classList.toggle('hidden', state.currentView !== 'form');
        settingsView.classList.toggle('hidden', state.currentView !== 'settings');

        // Render tasks
        if (state.currentView === 'main') {
            renderTasks();
        }
    };

    const renderTasks = () => {
        taskList.innerHTML = '';
        const filteredTasks = state.tasks
            .filter(task => {
                if (state.filter === 'active') return !task.completed;
                if (state.filter === 'completed') return task.completed;
                return true;
            })
            .filter(task =>
                task.title.toLowerCase().includes(state.searchTerm.toLowerCase()) ||
                task.description.toLowerCase().includes(state.searchTerm.toLowerCase())
            );

        if (filteredTasks.length === 0) {
            taskList.innerHTML = '<p>No tasks found.</p>';
            return;
        }

        filteredTasks.forEach(task => {
            const taskItem = document.createElement('li');
            taskItem.className = `task-item ${task.completed ? 'completed' : ''}`;
            taskItem.dataset.id = task.id;

            taskItem.innerHTML = `
                <input type="checkbox" ${task.completed ? 'checked' : ''}>
                <div class="task-details">
                    <h3>${task.title}</h3>
                    <p>${task.description.substring(0, 100)}</p>
                </div>
                <div class="task-actions">
                    <button class="delete-btn">Delete</button>
                </div>
            `;
            taskList.appendChild(taskItem);
        });
    };

    // --- View Navigation ---

    const showView = (viewName) => {
        state.currentView = viewName;
        render();
    };

    // --- Task Management ---
    const generateUUID = () => crypto.randomUUID();
    
    const addTask = (title, description, tags) => {
        const newTask = {
            id: generateUUID(),
            title,
            description,
            tags: tags.split(',').map(tag => tag.trim()).filter(Boolean),
            completed: false,
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString()
        };
        state.tasks.unshift(newTask);
        saveState();
        showView('main');
    };

    const updateTask = (id, title, description, tags) => {
        const task = state.tasks.find(t => t.id === id);
        if (task) {
            task.title = title;
            task.description = description;
            task.tags = tags.split(',').map(tag => tag.trim()).filter(Boolean);
            task.updatedAt = new Date().toISOString();
            saveState();
        }
        showView('main');
    };

    const deleteTask = (id) => {
        if (confirm('Are you sure you want to delete this task?')) {
            state.tasks = state.tasks.filter(t => t.id !== id);
            saveState();
            render();
        }
    };

    const toggleCompleted = (id) => {
        const task = state.tasks.find(t => t.id === id);
        if (task) {
            task.completed = !task.completed;
            task.updatedAt = new Date().toISOString();
            saveState();
            render();
        }
    };

    const openEditForm = (id) => {
        const task = state.tasks.find(t => t.id === id);
        if (task) {
            state.editingTaskId = id;
            document.getElementById('task-id').value = task.id;
            document.getElementById('task-title').value = task.title;
            document.getElementById('task-description').value = task.description;
            document.getElementById('task-tags').value = task.tags.join(', ');
            showView('form');
        }
    };

    // --- Event Listeners ---

    newTaskBtn.addEventListener('click', () => {
        state.editingTaskId = null;
        taskForm.reset();
        document.getElementById('task-id').value = '';
        showView('form');
    });

    settingsBtn.addEventListener('click', () => showView('settings'));
    cancelBtn.addEventListener('click', () => showView('main'));
    backToMainBtn.addEventListener('click', () => showView('main'));

    taskForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const id = document.getElementById('task-id').value;
        const title = document.getElementById('task-title').value;
        const description = document.getElementById('task-description').value;
        const tags = document.getElementById('task-tags').value;

        if (id) {
            updateTask(id, title, description, tags);
        } else {
            addTask(title, description, tags);
        }
    });

    taskList.addEventListener('click', (e) => {
        const target = e.target;
        const taskItem = target.closest('.task-item');
        if (!taskItem) return;

        const id = taskItem.dataset.id;

        if (target.type === 'checkbox') {
            toggleCompleted(id);
        } else if (target.classList.contains('delete-btn')) {
            deleteTask(id);
        } else if (target.closest('.task-details')) {
            openEditForm(id);
        }
    });
    
    searchBar.addEventListener('input', (e) => {
        state.searchTerm = e.target.value;
        renderTasks();
    });

    filterButtons.addEventListener('click', (e) => {
        if (e.target.tagName === 'BUTTON') {
            state.filter = e.target.dataset.filter;
            document.querySelectorAll('.filter-btn').forEach(btn => btn.classList.remove('active'));
            e.target.classList.add('active');
            renderTasks();
        }
    });

    // --- Data Portability ---

    exportBtn.addEventListener('click', () => {
        const data = JSON.stringify(state.tasks, null, 2);
        const blob = new Blob([data], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'quicktasks.json';
        a.click();
        URL.revokeObjectURL(url);
    });

    importBtn.addEventListener('click', () => importFile.click());

    importFile.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (event) => {
                try {
                    const importedTasks = JSON.parse(event.target.result);
                    if (Array.isArray(importedTasks)) {
                         if (confirm('Replace existing tasks with imported tasks?')) {
                            state.tasks = importedTasks;
                            saveState();
                            showView('main');
                        }
                    } else {
                        alert('Invalid file format.');
                    }
                } catch (error) {
                    alert('Error parsing file.');
                }
            };
            reader.readAsText(file);
        }
    });

    clearAllBtn.addEventListener('click', () => {
        if (confirm('Are you sure you want to delete all tasks? This cannot be undone.')) {
            state.tasks = [];
            saveState();
            showView('main');
        }
    });

    // --- Initialization ---

    const init = () => {
        loadState();
        render();
    };

    init();
});

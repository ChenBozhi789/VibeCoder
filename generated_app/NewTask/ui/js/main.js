
document.addEventListener('DOMContentLoaded', () => {
    // State
    let state = {
        tasks: [],
        filter: 'all',
        searchTerm: ''
    };

    // DOM Elements
    const newTaskBtn = document.getElementById('new-task-btn');
    const settingsBtn = document.getElementById('settings-btn');
    const taskModal = document.getElementById('task-modal');
    const settingsModal = document.getElementById('settings-modal');
    const closeBtn = document.querySelector('.close-btn');
    const closeSettingsBtn = document.querySelector('.close-settings-btn');
    const taskForm = document.getElementById('task-form');
    const taskList = document.getElementById('task-list');
    const searchInput = document.getElementById('search-input');
    const filterSelect = document.getElementById('filter-select');
    const importBtn = document.getElementById('import-btn');
    const importFile = document.getElementById('import-file');
    const exportBtn = document.getElementById('export-btn');
    const clearDataBtn = document.getElementById('clear-data-btn');

    // Functions
    const generateId = () => '_' + Math.random().toString(36).substr(2, 9);

    const loadTasks = () => {
        const tasks = localStorage.getItem('NewTask.tasks');
        return tasks ? JSON.parse(tasks) : [];
    };

    const saveTasks = () => {
        localStorage.setItem('NewTask.tasks', JSON.stringify(state.tasks));
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

        filteredTasks.forEach(task => {
            const taskElement = document.createElement('li');
            taskElement.classList.add('task');
            if (task.completed) {
                taskElement.classList.add('completed');
            }
            taskElement.innerHTML = `
                <input type="checkbox" ${task.completed ? 'checked' : ''} data-id="${task.id}">
                <div class="task-details" data-id="${task.id}">
                    <strong>${task.title}</strong>
                    <p>${task.description}</p>
                </div>
                <button class="delete-btn" data-id="${task.id}">&times;</button>
            `;
            taskList.appendChild(taskElement);
        });
    };

    const openModal = (modal) => {
        modal.style.display = 'block';
    };

    const closeModal = (modal) => {
        modal.style.display = 'none';
    };

    const resetForm = () => {
        taskForm.reset();
        document.getElementById('task-id').value = '';
    };
    
    // Event Listeners
    newTaskBtn.addEventListener('click', () => {
        resetForm();
        openModal(taskModal);
    });

    settingsBtn.addEventListener('click', () => {
        openModal(settingsModal);
    });

    closeBtn.addEventListener('click', () => {
        closeModal(taskModal);
    });

    closeSettingsBtn.addEventListener('click', () => {
        closeModal(settingsModal);
    });

    window.addEventListener('click', (e) => {
        if (e.target === taskModal) {
            closeModal(taskModal);
        }
        if (e.target === settingsModal) {
            closeModal(settingsModal);
        }
    });

    taskForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const id = document.getElementById('task-id').value;
        const title = document.getElementById('task-title').value;
        const description = document.getElementById('task-description').value;
        const tags = document.getElementById('task-tags').value.split(',').map(tag => tag.trim());

        if (id) {
            // Update task
            const task = state.tasks.find(task => task.id === id);
            task.title = title;
            task.description = description;
            task.tags = tags;
            task.updatedAt = new Date().toISOString();
        } else {
            // Create new task
            const newTask = {
                id: generateId(),
                title,
                description,
                tags,
                completed: false,
                createdAt: new Date().toISOString(),
                updatedAt: new Date().toISOString(),
                completedAt: null
            };
            state.tasks.push(newTask);
        }

        saveTasks();
        renderTasks();
        closeModal(taskModal);
    });
    
    taskList.addEventListener('click', (e) => {
        const id = e.target.dataset.id;
        if (e.target.matches('.task-details, .task-details *')) {
            const task = state.tasks.find(task => task.id === id);
            if (task) {
                document.getElementById('task-id').value = task.id;
                document.getElementById('task-title').value = task.title;
                document.getElementById('task-description').value = task.description;
                document.getElementById('task-tags').value = task.tags.join(', ');
                openModal(taskModal);
            }
        }
        if (e.target.matches('.delete-btn')) {
            if (confirm('Are you sure you want to delete this task?')) {
                state.tasks = state.tasks.filter(task => task.id !== id);
                saveTasks();
                renderTasks();
            }
        }
        if (e.target.matches('input[type="checkbox"]')) {
            const task = state.tasks.find(task => task.id === id);
            task.completed = e.target.checked;
            task.completedAt = task.completed ? new Date().toISOString() : null;
            saveTasks();
            renderTasks();
        }
    });
    
    searchInput.addEventListener('input', (e) => {
        state.searchTerm = e.target.value;
        renderTasks();
    });

    filterSelect.addEventListener('change', (e) => {
        state.filter = e.target.value;
        renderTasks();
    });

    exportBtn.addEventListener('click', () => {
        const data = JSON.stringify(state.tasks, null, 2);
        const blob = new Blob([data], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'NewTask_export.json';
        a.click();
        URL.revokeObjectURL(url);
    });

    importBtn.addEventListener('click', () => {
        importFile.click();
    });
    
    importFile.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (e) => {
                try {
                    const importedTasks = JSON.parse(e.target.result);
                    if (Array.isArray(importedTasks)) {
                        if (confirm('Are you sure you want to import these tasks? This will overwrite your current tasks.')) {
                            state.tasks = importedTasks;
                            saveTasks();
                            renderTasks();
                            closeModal(settingsModal);
                        }
                    } else {
                        alert('Invalid JSON file.');
                    }
                } catch (error) {
                    alert('Error reading JSON file.');
                }
            };
            reader.readAsText(file);
        }
    });

    clearDataBtn.addEventListener('click', () => {
        if (confirm('Are you sure you want to clear all data? This cannot be undone.')) {
            state.tasks = [];
            saveTasks();
            renderTasks();
            closeModal(settingsModal);
        }
    });

    // Initial load
    state.tasks = loadTasks();
    renderTasks();
});

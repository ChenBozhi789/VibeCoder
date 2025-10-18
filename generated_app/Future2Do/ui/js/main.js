
document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const addTaskForm = document.getElementById('add-task-form');
    const taskTitleInput = document.getElementById('task-title');
    const taskDescInput = document.getElementById('task-desc');
    const taskDueDateInput = document.getElementById('task-due-date');
    const taskPriorityInput = document.getElementById('task-priority');
    const taskList = document.getElementById('task-list');
    const searchInput = document.getElementById('search');
    const filterStatusSelect = document.getElementById('filter-status');
    const sortBySelect = document.getElementById('sort-by');

    // Application State
    let tasks = [];
    let filters = {
        searchTerm: '',
        status: 'all',
        sortBy: 'priority'
    };

    // Load tasks from localStorage
    function loadTasks() {
        const storedTasks = localStorage.getItem('tasks');
        if (storedTasks) {
            tasks = JSON.parse(storedTasks);
        }
        renderTasks();
    }

    // Save tasks to localStorage
    function saveTasks() {
        localStorage.setItem('tasks', JSON.stringify(tasks));
    }

    // Render tasks based on filters and sorting
    function renderTasks() {
        let filteredTasks = [...tasks];

        // Filter by status
        if (filters.status === 'active') {
            filteredTasks = filteredTasks.filter(task => !task.completed);
        } else if (filters.status === 'completed') {
            filteredTasks = filteredTasks.filter(task => task.completed);
        }

        // Filter by search term
        if (filters.searchTerm) {
            const searchTerm = filters.searchTerm.toLowerCase();
            filteredTasks = filteredTasks.filter(task =>
                task.title.toLowerCase().includes(searchTerm) ||
                task.description.toLowerCase().includes(searchTerm)
            );
        }

        // Sort tasks
        if (filters.sortBy === 'priority') {
            const priorityOrder = { high: 1, medium: 2, low: 3 };
            filteredTasks.sort((a, b) => priorityOrder[a.priority] - priorityOrder[b.priority]);
        } else if (filters.sortBy === 'due-date') {
            filteredTasks.sort((a, b) => new Date(a.dueDate) - new Date(b.dueDate));
        }

        // Generate HTML for tasks
        taskList.innerHTML = filteredTasks.map(task => `
            <li class="task-item ${task.completed ? 'completed' : ''}" data-id="${task.id}" data-priority="${task.priority}">
                <div class="task-info">
                    <h3>${task.title}</h3>
                    <p>${task.description}</p>
                    <small>Due: ${task.dueDate || 'Not set'}</small>
                </div>
                <div class="task-actions">
                    <button class="toggle-btn">${task.completed ? 'Undo' : 'Complete'}</button>
                    <button class="delete-btn">Delete</button>
                </div>
            </li>
        `).join('');
    }

    // Add a new task
    function addTask(event) {
        event.preventDefault();
        const title = taskTitleInput.value.trim();
        if (!title) {
            alert('Task title is required.');
            return;
        }

        const newTask = {
            id: Date.now(),
            title,
            description: taskDescInput.value.trim(),
            dueDate: taskDueDateInput.value,
            priority: taskPriorityInput.value,
            completed: false
        };

        tasks.push(newTask);
        saveTasks();
        renderTasks();
        addTaskForm.reset();
    }

    // Handle clicks on the task list (for delete and toggle)
    function handleTaskListClick(event) {
        const target = event.target;
        const taskItem = target.closest('.task-item');
        if (!taskItem) return;

        const taskId = Number(taskItem.dataset.id);

        if (target.classList.contains('delete-btn')) {
            tasks = tasks.filter(task => task.id !== taskId);
        } else if (target.classList.contains('toggle-btn')) {
            const task = tasks.find(task => task.id === taskId);
            if (task) {
                task.completed = !task.completed;
            }
        }
        
        saveTasks();
        renderTasks();
    }

    // Event Listeners
    addTaskForm.addEventListener('submit', addTask);
    taskList.addEventListener('click', handleTaskListClick);
    
    searchInput.addEventListener('input', (e) => {
        filters.searchTerm = e.target.value;
        renderTasks();
    });

    filterStatusSelect.addEventListener('change', (e) => {
        filters.status = e.target.value;
        renderTasks();
    });

    sortBySelect.addEventListener('change', (e) => {
        filters.sortBy = e.target.value;
        renderTasks();
    });

    // Initial load
    loadTasks();
});

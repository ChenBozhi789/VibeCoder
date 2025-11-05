
const app = {
  tasks: [],
  settings: {},
  currentView: 'list',
  filter: {
    query: '',
    view: 'all'
  },
  init() {
    this.loadData();
    this.showView('list');
    this.addEventListeners();
  },
  loadData() {
    const tasks = localStorage.getItem('taskpromax.tasks');
    const settings = localStorage.getItem('taskpromax.settings');
    if (tasks) {
      this.tasks = JSON.parse(tasks);
    }
    if (settings) {
      this.settings = JSON.parse(settings);
    }
  },
  saveData() {
    localStorage.setItem('taskpromax.tasks', JSON.stringify(this.tasks));
    localStorage.setItem('taskpromax.settings', JSON.stringify(this.settings));
  },
  showView(view) {
    this.currentView = view;
    document.querySelectorAll('.view').forEach(v => v.style.display = 'none');
    document.getElementById(view + '-view').style.display = 'block';
    if (view === 'list') {
      this.filter.view = 'all';
      this.renderTasks();
    }
  },
  renderTasks() {
    const taskList = document.getElementById('task-list');
    taskList.innerHTML = '';
    let filteredTasks = this.tasks;

    if (this.filter.query) {
      filteredTasks = filteredTasks.filter(task => 
        task.title.toLowerCase().includes(this.filter.query.toLowerCase()) ||
        task.description.toLowerCase().includes(this.filter.query.toLowerCase())
      );
    }

    const today = new Date().toISOString().slice(0, 10);
    switch(this.filter.view) {
        case 'today':
            filteredTasks = filteredTasks.filter(task => task.dueDate === today);
            break;
        case 'upcoming':
            const upcomingDate = new Date();
            upcomingDate.setDate(upcomingDate.getDate() + 7);
            const upcoming = upcomingDate.toISOString().slice(0, 10);
            filteredTasks = filteredTasks.filter(task => task.dueDate > today && task.dueDate <= upcoming);
            break;
        case 'overdue':
            filteredTasks = filteredTasks.filter(task => task.dueDate < today && task.status === 'todo');
            break;
        case 'completed':
            filteredTasks = filteredTasks.filter(task => task.status === 'done');
            break;
    }
    
    filteredTasks.forEach(task => {
      const taskItem = document.createElement('li');
      taskItem.innerHTML = `
        <input type="checkbox" data-id="${task.id}" ${task.status === 'done' ? 'checked' : ''}>
        <span class="${task.status === 'done' ? 'completed' : ''}">${task.title}</span>
        <div>
          <button class="edit-btn" data-id="${task.id}">Edit</button>
          <button class="delete-btn" data-id="${task.id}">Delete</button>
        </div>
      `;
      taskList.appendChild(taskItem);
    });
  },
  addEventListeners() {
    document.getElementById('new-task-btn').addEventListener('click', () => this.showView('form'));
    document.getElementById('settings-link').addEventListener('click', () => this.showView('settings'));
    document.getElementById('cancel-btn').addEventListener('click', () => this.showView('list'));

    document.getElementById('task-form').addEventListener('submit', event => {
      event.preventDefault();
      const taskId = document.getElementById('task-id').value;
      const title = document.getElementById('task-title').value;
      if (title) {
          if (taskId) {
              const task = this.tasks.find(t => t.id === taskId);
              task.title = title;
              task.description = document.getElementById('task-description').value;
              task.tags = document.getElementById('task-tags').value.split(',');
              task.dueDate = document.getElementById('task-due-date').value;
              task.updatedAt = new Date().toISOString();
          } else {
            const newTask = {
              id: Date.now().toString(),
              title: title,
              description: document.getElementById('task-description').value,
              tags: document.getElementById('task-tags').value.split(','),
              dueDate: document.getElementById('task-due-date').value,
              status: 'todo',
              createdAt: new Date().toISOString(),
              updatedAt: new Date().toISOString(),
            };
            this.tasks.push(newTask);
          }
        this.saveData();
        this.showView('list');
        document.getElementById('task-form').reset();
        document.getElementById('task-id').value = '';
      }
    });

    document.getElementById('task-list').addEventListener('click', event => {
      if (event.target.classList.contains('edit-btn')) {
        const taskId = event.target.dataset.id;
        const task = this.tasks.find(t => t.id === taskId);
        if (task) {
          document.getElementById('task-id').value = task.id;
          document.getElementById('task-title').value = task.title;
          document.getElementById('task-description').value = task.description;
          document.getElementById('task-tags').value = task.tags.join(',');
          document.getElementById('task-due-date').value = task.dueDate;
          this.showView('form');
        }
      }
      if (event.target.classList.contains('delete-btn')) {
        const taskId = event.target.dataset.id;
        this.tasks = this.tasks.filter(t => t.id !== taskId);
        this.saveData();
        this.renderTasks();
      }
      if (event.target.type === 'checkbox') {
        const taskId = event.target.dataset.id;
        const task = this.tasks.find(t => t.id === taskId);
        if(task){
            task.status = event.target.checked ? 'done' : 'todo';
            this.saveData();
            this.renderTasks();
        }
      }
    });

    document.getElementById('import-btn').addEventListener('click', () => {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = '.json';
        input.onchange = e => {
            const file = e.target.files[0];
            const reader = new FileReader();
            reader.onload = readerEvent => {
                const content = readerEvent.target.result;
                try {
                    const data = JSON.parse(content);
                    if (data.tasks) {
                        this.tasks = data.tasks;
                        this.saveData();
                        this.showView('list');
                        alert('Data imported successfully!');
                    } else {
                        alert('Invalid JSON format for import.');
                    }
                } catch (error) {
                    alert('Error parsing JSON file.');
                }
            }
            reader.readAsText(file);
        }
        input.click();
    });

    document.getElementById('export-btn').addEventListener('click', () => {
        const data = {
            tasks: this.tasks,
            settings: this.settings
        };
        const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(data, null, 2));
        const downloadAnchorNode = document.createElement('a');
        downloadAnchorNode.setAttribute("href", dataStr);
        downloadAnchorNode.setAttribute("download", "taskpromax_data.json");
        document.body.appendChild(downloadAnchorNode);
        downloadAnchorNode.click();
        downloadAnchorNode.remove();
    });

    
// Generated code for task_manager - confirmation_modal
// Requirements: The application needs to handle a confirmation modal for clearing data. The modal should be displayed when the 'Clear All Data' button is clicked. The modal has two buttons: 'Yes' and 'No'. If 'Yes' is clicked, the data should be cleared. If 'No' is clicked, the modal should be hidden.

// TODO: Implement confirmation_modal for task_manager
// This is a placeholder - implement the actual functionality based on requirements

    
    document.getElementById('search-box').addEventListener('input', (e) => {
        this.filter.query = e.target.value;
        this.renderTasks();
    });
    
    document.getElementById('all-tasks-link').addEventListener('click', (e) => {
        e.preventDefault();
        this.filter.view = 'all';
        this.renderTasks();
    });

    document.getElementById('today-view-link').addEventListener('click', (e) => {
        e.preventDefault();
        this.filter.view = 'today';
        this.renderTasks();
    });

    document.getElementById('upcoming-view-link').addEventListener('click', (e) => {
        e.preventDefault();
        this.filter.view = 'upcoming';
        this.renderTasks();
    });

    document.getElementById('overdue-view-link').addEventListener('click', (e) => {
        e.preventDefault();
        this.filter.view = 'overdue';
        this.renderTasks();
    });

    document.getElementById('completed-view-link').addEventListener('click', (e) => {
        e.preventDefault();
        this.filter.view = 'completed';
        this.renderTasks();
    });
  }
};

document.addEventListener('DOMContentLoaded', () => {
  app.init();
});


document.addEventListener('DOMContentLoaded', () => {
    // --- STATE MANAGEMENT ---
    let state = {
        goals: [],
        editingGoalId: null,
        filterBy: {
            status: 'all',
            searchTerm: ''
        },
        sortBy: 'updatedAt-desc',
        confirmation: {
            isVisible: false,
            message: '',
            onConfirm: null,
        },
    };

    const STORAGE_KEY = 'GoalSetter.goals';

    // --- DOM ELEMENTS ---
    const listView = document.getElementById('list-view');
    const formView = document.getElementById('form-view');
    const settingsModal = document.getElementById('settings-modal');
    const confirmModal = document.getElementById('confirm-modal');

    const newGoalBtn = document.getElementById('new-goal-btn');
    const settingsBtn = document.getElementById('settings-btn');
    const goalList = document.getElementById('goal-list');
    const goalForm = document.getElementById('goal-form');

    // Filter and Sort controls
    const searchInput = document.getElementById('search-input');
    const filterStatus = document.getElementById('filter-status');
    const sortBy = document.getElementById('sort-by');
    
    // Form fields
    const goalIdInput = document.getElementById('goal-id');
    const titleInput = document.getElementById('title');
    const descriptionInput = document.getElementById('description');
    const tagsInput = document.getElementById('tags');
    const targetDateInput = document.getElementById('targetDate');
    const progressInput = document.getElementById('progress');
    const progressValueSpan = document.getElementById('progress-value');
    const achievedCheckbox = document.getElementById('achieved');

    // Buttons
    const cancelBtn = document.getElementById('cancel-btn');
    const deleteBtn = document.getElementById('delete-btn');
    
    // Settings Modal
    const importBtn = document.getElementById('import-btn');
    const importFileInput = document.getElementById('import-file');
    const exportBtn = document.getElementById('export-btn');
    const clearDataBtn = document.getElementById('clear-data-btn');

    // Confirmation Modal
    const confirmMessage = document.getElementById('confirm-message');
    const confirmYesBtn = document.getElementById('confirm-yes-btn');
    const confirmNoBtn = document.getElementById('confirm-no-btn');

    // --- DATA PERSISTENCE ---
    function saveState() {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(state.goals));
    }

    function loadState() {
        const storedGoals = localStorage.getItem(STORAGE_KEY);
        state.goals = storedGoals ? JSON.parse(storedGoals) : [];
    }

    // --- UTILITY FUNCTIONS ---
    function generateUUID() {
        return ([1e7]+-1e3+-4e3+-8e3+-1e11).replace(/[018]/g, c =>
            (c ^ crypto.getRandomValues(new Uint8Array(1))[0] & 15 >> c / 4).toString(16)
        );
    }
    
    function formatDate(isoDate) {
        if (!isoDate) return 'N/A';
        const date = new Date(isoDate);
        return date.toLocaleDateString(undefined, { year: 'numeric', month: 'long', day: 'numeric' });
    }
    
    function daysUntil(isoDate) {
        if (!isoDate) return '';
        const target = new Date(isoDate);
        target.setHours(0,0,0,0);
        const today = new Date();
        today.setHours(0,0,0,0);
        const diffTime = target - today;
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
        if (diffDays < 0) return `<span class="overdue">${Math.abs(diffDays)} days overdue</span>`;
        if (diffDays === 0) return `<span class="due-soon">Due today</span>`;
        return `${diffDays} days remaining`;
    }

    // --- VIEW MANAGEMENT ---
    function showListView() {
        listView.classList.remove('hidden');
        formView.classList.add('hidden');
        state.editingGoalId = null;
        render();
    }

    function showFormView(goalId = null) {
        listView.classList.add('hidden');
        formView.classList.remove('hidden');
        state.editingGoalId = goalId;
        goalForm.reset();
        progressValueSpan.textContent = '0%';
        deleteBtn.classList.toggle('hidden', !goalId);
        
        if (goalId) {
            const goal = state.goals.find(g => g.id === goalId);
            if (goal) {
                goalIdInput.value = goal.id;
                titleInput.value = goal.title;
                descriptionInput.value = goal.description;
                tagsInput.value = goal.tags ? goal.tags.join(', ') : '';
                targetDateInput.value = goal.targetDate;
                progressInput.value = goal.progress;
                progressValueSpan.textContent = `${goal.progress}%`;
                achievedCheckbox.checked = goal.achieved;
            }
        }
    }

    function toggleSettingsModal(show = true) {
        settingsModal.classList.toggle('hidden', !show);
    }
    
    function showConfirmation(message, onConfirmCallback) {
        state.confirmation.message = message;
        state.confirmation.onConfirm = onConfirmCallback;
        confirmMessage.textContent = message;
        confirmModal.classList.remove('hidden');
    }

    function hideConfirmation() {
        confirmModal.classList.add('hidden');
        state.confirmation.onConfirm = null;
    }

    // --- RENDER ---
    function render() {
        renderGoalList();
    }

    function renderGoalList() {
        goalList.innerHTML = '';
        const filteredAndSortedGoals = getVisibleGoals();

        if (filteredAndSortedGoals.length === 0) {
            goalList.innerHTML = '<li><p>No goals yet. Create one!</p></li>';
            return;
        }

        filteredAndSortedGoals.forEach(goal => {
            const li = document.createElement('li');
            li.className = `goal-item ${goal.achieved ? 'achieved' : ''} ${!goal.achieved && new Date(goal.targetDate) < new Date() ? 'overdue' : ''}`;
            li.dataset.id = goal.id;
            
            li.innerHTML = `
                <h3 class="goal-title">${goal.title}</h3>
                <div class="goal-actions">
                    <button class="btn btn-secondary btn-sm edit-btn">Edit</button>
                    <button class="btn btn-danger btn-sm delete-goal-btn">Delete</button>
                </div>
                <div class="goal-progress-bar">
                    <div class="goal-progress-bar-fill" style="width: ${goal.progress}%;"></div>
                </div>
                <div class="goal-details">
                    <span>Target: ${formatDate(goal.targetDate)} (${daysUntil(goal.targetDate)})</span>
                    <span>${goal.achieved ? `Achieved on ${formatDate(goal.achievedAt)}` : `Progress: ${goal.progress}%`}</span>
                </div>
            `;
            goalList.appendChild(li);
        });
    }

    function getVisibleGoals() {
        let goals = [...state.goals];

        // Filter
        if (state.filterBy.status === 'active') {
            goals = goals.filter(g => !g.achieved);
        } else if (state.filterBy.status === 'achieved') {
            goals = goals.filter(g => g.achieved);
        }
        
        if(state.filterBy.searchTerm) {
            const searchTerm = state.filterBy.searchTerm.toLowerCase();
            goals = goals.filter(g => 
                g.title.toLowerCase().includes(searchTerm) || 
                g.description.toLowerCase().includes(searchTerm)
            );
        }

        // Sort
        const [key, direction] = state.sortBy.split('-');
        goals.sort((a, b) => {
            let valA = a[key];
            let valB = b[key];
            if (key === 'targetDate' || key.includes('At')) {
                valA = new Date(valA);
                valB = new Date(valB);
            }
            if (valA < valB) return direction === 'asc' ? -1 : 1;
            if (valA > valB) return direction === 'asc' ? 1 : -1;
            return 0;
        });

        return goals;
    }

    // --- EVENT HANDLERS ---
    function handleFormSubmit(e) {
        e.preventDefault();
        const now = new Date().toISOString();
        const tags = tagsInput.value.split(',').map(t => t.trim()).filter(Boolean);

        const goalData = {
            id: state.editingGoalId || generateUUID(),
            title: titleInput.value,
            description: descriptionInput.value,
            tags: tags,
            targetDate: targetDateInput.value,
            progress: parseInt(progressInput.value, 10),
            achieved: achievedCheckbox.checked,
            updatedAt: now,
            createdAt: state.editingGoalId ? state.goals.find(g => g.id === state.editingGoalId).createdAt : now,
            achievedAt: achievedCheckbox.checked ? (state.goals.find(g => g.id === state.editingGoalId)?.achievedAt || now) : null
        };

        if (state.editingGoalId) {
            state.goals = state.goals.map(g => g.id === state.editingGoalId ? goalData : g);
        } else {
            state.goals.push(goalData);
        }

        saveState();
        showListView();
    }

    function handleGoalListClick(e) {
        const target = e.target;
        const goalItem = target.closest('.goal-item');
        if (!goalItem) return;

        const goalId = goalItem.dataset.id;

        if (target.classList.contains('edit-btn') || target.classList.contains('goal-title')) {
            showFormView(goalId);
        } else if (target.classList.contains('delete-goal-btn')) {
            showConfirmation('Are you sure you want to delete this goal?', () => {
                state.goals = state.goals.filter(g => g.id !== goalId);
                saveState();
                render();
                hideConfirmation();
            });
        }
    }
    
    function handleSettings() {
        exportBtn.onclick = () => {
            const dataStr = JSON.stringify(state.goals, null, 2);
            const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
            
            const exportFileDefaultName = 'GoalSetter_backup.json';
            
            let linkElement = document.createElement('a');
            linkElement.setAttribute('href', dataUri);
            linkElement.setAttribute('download', exportFileDefaultName);
            linkElement.click();
        };

        importBtn.onclick = () => importFileInput.click();
        importFileInput.onchange = (e) => {
            const file = e.target.files[0];
            if (!file) return;

            const reader = new FileReader();
            reader.onload = (event) => {
                try {
                    const importedGoals = JSON.parse(event.target.result);
                    // Basic validation
                    if (Array.isArray(importedGoals)) {
                        showConfirmation('This will replace all your current goals. Are you sure?', () => {
                            state.goals = importedGoals;
                            saveState();
                            render();
                            toggleSettingsModal(false);
                            hideConfirmation();
                        });
                    } else {
                        alert('Invalid file format.');
                    }
                } catch (error) {
                    alert('Error reading or parsing the file.');
                }
            };
            reader.readAsText(file);
            importFileInput.value = ''; // Reset for next import
        };

        clearDataBtn.onclick = () => {
             showConfirmation('This will delete all your goals permanently. Are you sure?', () => {
                state.goals = [];
                saveState();
                render();
                toggleSettingsModal(false);
                hideConfirmation();
            });
        };

        settingsModal.querySelector('.close-btn').onclick = () => toggleSettingsModal(false);
    }

    // --- INITIALIZATION ---
    function init() {
        // Event Listeners Setup
        newGoalBtn.addEventListener('click', () => showFormView());
        settingsBtn.addEventListener('click', () => toggleSettingsModal(true));
        goalForm.addEventListener('submit', handleFormSubmit);
        cancelBtn.addEventListener('click', showListView);
        deleteBtn.addEventListener('click', () => {
            showConfirmation('Are you sure you want to delete this goal?', () => {
                state.goals = state.goals.filter(g => g.id !== state.editingGoalId);
                saveState();
                showListView();
                hideConfirmation();
            });
        });
        goalList.addEventListener('click', handleGoalListClick);
        
        // Filters and Sort
        searchInput.addEventListener('input', e => {
            state.filterBy.searchTerm = e.target.value;
            render();
        });
        filterStatus.addEventListener('change', e => {
            state.filterBy.status = e.target.value;
            render();
        });
        sortBy.addEventListener('change', e => {
            state.sortBy = e.target.value;
            render();
        });
        
        // Progress bar display
        progressInput.addEventListener('input', e => {
            progressValueSpan.textContent = `${e.target.value}%`;
        });
        
        achievedCheckbox.addEventListener('change', e => {
            if (e.target.checked) {
                progressInput.value = 100;
                progressValueSpan.textContent = `100%`;
            }
        });

        // Modals
        confirmYesBtn.addEventListener('click', () => {
            if (state.confirmation.onConfirm) {
                state.confirmation.onConfirm();
            }
        });
        confirmNoBtn.addEventListener('click', hideConfirmation);
        document.querySelector('#settings-modal .close-btn').addEventListener('click', () => toggleSettingsModal(false));


        loadState();
        showListView(); // Initial view
        handleSettings();
    }

    init();
});

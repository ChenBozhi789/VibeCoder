
// --- Core Infrastructure ---
const STORAGE_KEY = 'MyRecipeBox.recipes';
const storage = {
    load: () => JSON.parse(localStorage.getItem(STORAGE_KEY)) || [],
    save: (data) => localStorage.setItem(STORAGE_KEY, JSON.stringify(data)),
};
const utils = {
    uid: () => `r-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
};

// --- Global State ---
let state = {
    recipes: [],
    currentView: 'list',
    filter: { search: '', tag: '' },
    sort: 'newest',
    modal: { isOpen: false, title: '', message: '', onConfirm: null },
    status: { message: '', type: 'info', timer: null },
};

// --- DOMContentLoaded ---
document.addEventListener('DOMContentLoaded', () => {
    state.recipes = storage.load();
    setupEventListeners();
    renderApp();
});

// --- Main Render Function ---
function renderApp() {
    renderCurrentView();
    renderListView();
    renderStatus();
    renderModal();
}

// --- View Management ---
function showView(viewId) {
    state.currentView = viewId;
    renderCurrentView();
}

function renderCurrentView() {
    document.querySelectorAll('main > section').forEach(section => {
        section.style.display = section.id === `${state.currentView}-view` ? '' : 'none';
    });
}

// --- List View ---
function renderListView() {
    const listEl = document.getElementById('recipe-list');
    const emptyEl = document.getElementById('list-empty');
    const filteredRecipes = applyFiltersAndSort();

    if (filteredRecipes.length === 0) {
        listEl.innerHTML = '';
        emptyEl.style.display = 'block';
        return;
    }

    emptyEl.style.display = 'none';
    listEl.innerHTML = filteredRecipes.map(recipe => `
        <div class="recipe-card" data-id="${recipe.id}">
            <h3>${recipe.title}</h3>
            <p>${(recipe.instructions[0] || recipe.description || '').substring(0, 100)}...</p>
            <div class="card-footer">
                <small>${new Date(recipe.createdAt).toLocaleDateString()}</small>
                <button class="delete-recipe-btn danger" data-id="${recipe.id}">Delete</button>
            </div>
        </div>
    `).join('');

    document.querySelectorAll('.recipe-card').forEach(card => {
        card.addEventListener('click', (e) => {
            if (!e.target.classList.contains('delete-recipe-btn')) {
                openRecipe(card.dataset.id);
            }
        });
    });
    
    document.querySelectorAll('.delete-recipe-btn').forEach(button => {
        button.addEventListener('click', (e) => {
            e.stopPropagation();
            confirmDelete(button.dataset.id);
        });
    });
}

function applyFiltersAndSort() {
    let recipes = [...state.recipes];
    const searchTerm = state.filter.search.toLowerCase();
    const tagTerm = state.filter.tag.toLowerCase();

    if (searchTerm) {
        recipes = recipes.filter(r => 
            r.title.toLowerCase().includes(searchTerm) ||
            r.ingredients.some(i => i.name.toLowerCase().includes(searchTerm)) ||
            r.instructions.some(s => s.toLowerCase().includes(searchTerm))
        );
    }

    if (tagTerm) {
        recipes = recipes.filter(r => r.tags.some(t => t.toLowerCase().includes(tagTerm)));
    }

    switch (state.sort) {
        case 'oldest': recipes.sort((a, b) => new Date(a.createdAt) - new Date(b.createdAt)); break;
        case 'title': recipes.sort((a, b) => a.title.localeCompare(b.title)); break;
        default: recipes.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt)); break;
    }
    return recipes;
}


// --- Form View ---
function startNewRecipe() {
    resetForm();
    showView('form');
}

function openRecipe(id) {
    const recipe = state.recipes.find(r => r.id === id);
    if (!recipe) return;

    resetForm();
    document.getElementById('recipe-id').value = recipe.id;
    document.getElementById('title-input').value = recipe.title;
    document.getElementById('description-input').value = recipe.description;
    document.getElementById('tags-input').value = recipe.tags.join(', ');
    
    recipe.ingredients.forEach(addIngredientRowFromData);
    recipe.instructions.forEach(addStepRowFromData);

    document.getElementById('delete-btn').style.display = 'inline-block';
    showView('form');
}

function resetForm() {
    document.getElementById('recipe-form').reset();
    document.getElementById('recipe-id').value = '';
    document.getElementById('ingredients-list').innerHTML = '';
    document.getElementById('instructions-list').innerHTML = '';
    document.getElementById('delete-btn').style.display = 'none';
    document.getElementById('title-hint').style.display = 'none';
}

function addIngredientRow() { addIngredientRowFromData({ name: '', quantity: '', unit: '' }); }
function addIngredientRowFromData(data) {
    const div = document.createElement('div');
    div.className = 'dynamic-row';
    div.innerHTML = `
        <input type="text" class="ingredient-name" placeholder="Name" value="${data.name}">
        <input type="text" class="ingredient-quantity" placeholder="Quantity" value="${data.quantity}">
        <input type="text" class="ingredient-unit" placeholder="Unit" value="${data.unit}">
        <button type="button" class="remove-row-btn">×</button>
    `;
    document.getElementById('ingredients-list').appendChild(div);
}

function addStepRow() { addStepRowFromData(''); }
function addStepRowFromData(data) {
    const div = document.createElement('div');
    div.className = 'dynamic-row';
    div.innerHTML = `
        <input type="text" class="instruction-step" value="${data}">
        <button type="button" class="remove-row-btn">×</button>
    `;
    document.getElementById('instructions-list').appendChild(div);
}

function handleFormSubmit(event) {
    event.preventDefault();
    const title = document.getElementById('title-input').value.trim();
    if (!title) {
        document.getElementById('title-hint').style.display = 'block';
        return;
    }
    document.getElementById('title-hint').style.display = 'none';
    
    const id = document.getElementById('recipe-id').value || utils.uid();
    const now = new Date().toISOString();
    
    const recipe = {
        id,
        title,
        description: document.getElementById('description-input').value.trim(),
        tags: document.getElementById('tags-input').value.split(',').map(t => t.trim()).filter(Boolean),
        ingredients: Array.from(document.querySelectorAll('#ingredients-list .dynamic-row')).map(row => ({
            name: row.querySelector('.ingredient-name').value.trim(),
            quantity: row.querySelector('.ingredient-quantity').value.trim(),
            unit: row.querySelector('.ingredient-unit').value.trim(),
        })),
        instructions: Array.from(document.querySelectorAll('#instructions-list .dynamic-row')).map(row => 
            row.querySelector('.instruction-step').value.trim()
        ),
        createdAt: state.recipes.find(r => r.id === id)?.createdAt || now,
        updatedAt: now,
    };
    
    const index = state.recipes.findIndex(r => r.id === id);
    if (index > -1) {
        state.recipes[index] = recipe;
    } else {
        state.recipes.push(recipe);
    }
    
    storage.save(state.recipes);
    setStatus('Recipe saved successfully!', 'success');
    showView('list');
    renderListView();
}

function confirmDelete(id) {
    showModal('Delete Recipe', 'Are you sure you want to delete this recipe?', () => {
        state.recipes = state.recipes.filter(r => r.id !== id);
        storage.save(state.recipes);
        setStatus('Recipe deleted.', 'success');
        if (state.currentView === 'form') {
            showView('list');
        }
        renderListView();
    });
}


// --- Settings View ---
function exportData() {
    const dataStr = JSON.stringify(state.recipes, null, 2);
    const blob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'my-recipe-box.json';
    a.click();
    URL.revokeObjectURL(url);
    setStatus('Data exported.', 'success');
}

function importData(event) {
    const file = event.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (e) => {
        try {
            const importedRecipes = JSON.parse(e.target.result);
            // Basic validation
            if (Array.isArray(importedRecipes)) {
                state.recipes = importedRecipes;
                storage.save(state.recipes);
                setStatus('Data imported successfully!', 'success');
                showView('list');
                renderListView();
            } else {
                setStatus('Invalid file format.', 'error');
            }
        } catch (error) {
            setStatus('Could not parse file.', 'error');
        }
    };
    reader.readAsText(file);
    // Reset file input
    event.target.value = '';
}


// --- Modal ---
function showModal(title, message, onConfirm) {
    state.modal = { isOpen: true, title, message, onConfirm };
    renderModal();
}

function hideModal() {
    state.modal = { isOpen: false, title: '', message: '', onConfirm: null };
    renderModal();
}

function renderModal() {
    const modal = document.getElementById('modal');
    if (!state.modal.isOpen) {
        modal.style.display = 'none';
        return;
    }
    modal.style.display = 'flex';
    document.getElementById('modal-title').textContent = state.modal.title;
    document.getElementById('modal-message').textContent = state.modal.message;
}


// --- Status Bar ---
function setStatus(message, type = 'info', duration = 3000) {
    if (state.status.timer) clearTimeout(state.status.timer);
    state.status = { message, type, timer: null };
    renderStatus();
    state.status.timer = setTimeout(() => {
        state.status.message = '';
        renderStatus();
    }, duration);
}

function renderStatus() {
    const statusEl = document.getElementById('status');
    if (!state.status.message) {
        statusEl.style.display = 'none';
        return;
    }
    statusEl.textContent = state.status.message;
    statusEl.className = `status-bar ${state.status.type}`;
    statusEl.style.display = 'block';
}


// --- Event Listeners ---
function setupEventListeners() {
    // Navigation
    document.getElementById('nav-list').addEventListener('click', () => showView('list'));
    document.getElementById('nav-new').addEventListener('click', startNewRecipe);
    document.getElementById('nav-settings').addEventListener('click', () => showView('settings'));
    document.getElementById('add-recipe-link').addEventListener('click', startNewRecipe);

    // List View
    document.getElementById('search-input').addEventListener('input', (e) => {
        state.filter.search = e.target.value;
        renderListView();
    });
    document.getElementById('sort-select').addEventListener('change', (e) => {
        state.sort = e.target.value;
        renderListView();
    });
    document.getElementById('tag-filter-input').addEventListener('input', (e) => {
        state.filter.tag = e.target.value;
        renderListView();
    });
    
    // Form View
    document.getElementById('recipe-form').addEventListener('submit', handleFormSubmit);
    document.getElementById('cancel-btn').addEventListener('click', () => showView('list'));
    document.getElementById('delete-btn').addEventListener('click', () => confirmDelete(document.getElementById('recipe-id').value));
    document.getElementById('add-ingredient-btn').addEventListener('click', addIngredientRow);
    document.getElementById('add-step-btn').addEventListener('click', addStepRow);
    
    document.getElementById('ingredients-list').addEventListener('click', (e) => {
        if (e.target.classList.contains('remove-row-btn')) {
            e.target.closest('.dynamic-row').remove();
        }
    });
    document.getElementById('instructions-list').addEventListener('click', (e) => {
        if (e.target.classList.contains('remove-row-btn')) {
            e.target.closest('.dynamic-row').remove();
        }
    });

    // Settings View
    document.getElementById('export-btn').addEventListener('click', exportData);
    document.getElementById('import-btn').addEventListener('click', () => document.getElementById('import-file').click());
    document.getElementById('import-file').addEventListener('change', importData);
    document.getElementById('clear-btn').addEventListener('click', () => {
        showModal('Clear All Data', 'Are you sure you want to permanently delete all recipes?', () => {
            state.recipes = [];
            storage.save(state.recipes);
            setStatus('All data cleared.', 'success');
            renderListView();
            hideModal();
        });
    });

    // Modal
    document.getElementById('modal-cancel').addEventListener('click', hideModal);
    document.getElementById('modal-confirm').addEventListener('click', () => {
        if (state.modal.onConfirm) state.modal.onConfirm();
        hideModal();
    });
}

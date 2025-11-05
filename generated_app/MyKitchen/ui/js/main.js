
const app = {
    state: {
        recipes: [],
        currentView: 'list',
        selectedRecipeId: null,
    },

    init: function() {
        this.loadRecipes();
        this.render();
        this.attachEventListeners();
    },

    loadRecipes: function() {
        const recipes = localStorage.getItem('MyKitchen.recipes');
        if (recipes) {
            this.state.recipes = JSON.parse(recipes);
        }
    },

    saveRecipes: function() {
        localStorage.setItem('MyKitchen.recipes', JSON.stringify(this.state.recipes));
    },

    render: function() {
        const listView = document.getElementById('list-view');
        const formView = document.getElementById('form-view');
        const settingsView = document.getElementById('settings-view');

        listView.classList.toggle('hidden', this.state.currentView !== 'list');
        formView.classList.toggle('hidden', this.state.currentView !== 'form');
        settingsView.classList.toggle('hidden', this.state.currentView !== 'settings');

        if (this.state.currentView === 'list') {
            this.renderListView();
        } else if (this.state.currentView === 'form') {
            this.renderFormView();
        }
    },

    renderListView: function() {
        const recipeList = document.getElementById('recipe-list');
        recipeList.innerHTML = '';
        this.state.recipes.forEach(recipe => {
            const item = document.createElement('div');
            item.className = 'recipe-item';
            item.innerHTML = `
                <span>${recipe.title}</span>
                <div>
                    <button class="edit-btn" data-id="${recipe.id}">Edit</button>
                    <button class="delete-btn" data-id="${recipe.id}">Delete</button>
                </div>
            `;
            recipeList.appendChild(item);
        });
    },

    renderFormView: function() {
        const formTitle = document.getElementById('form-title');
        const recipeForm = document.getElementById('recipe-form');
        const deleteBtn = document.getElementById('delete-btn');

        if (this.state.selectedRecipeId) {
            formTitle.textContent = 'Edit Recipe';
            deleteBtn.classList.remove('hidden');
            const recipe = this.state.recipes.find(r => r.id === this.state.selectedRecipeId);
            document.getElementById('recipe-id').value = recipe.id;
            document.getElementById('title').value = recipe.title;
            document.getElementById('description').value = recipe.description;
            document.getElementById('instructions').value = recipe.instructions;
            document.getElementById('tags').value = recipe.tags.join(', ');
            document.getElementById('favorite').checked = recipe.favorite;
        } else {
            formTitle.textContent = 'Create Recipe';
            deleteBtn.classList.add('hidden');
            recipeForm.reset();
            document.getElementById('recipe-id').value = '';
        }
    },

    attachEventListeners: function() {
        document.getElementById('new-recipe-btn').addEventListener('click', () => this.showView('form'));
        document.getElementById('cancel-btn').addEventListener('click', () => this.showView('list'));
        document.getElementById('settings-btn').addEventListener('click', () => this.showView('settings'));
        document.getElementById('close-settings-btn').addEventListener('click', () => this.showView('list'));
        document.getElementById('recipe-form').addEventListener('submit', (e) => this.handleFormSubmit(e));
        document.getElementById('recipe-list').addEventListener('click', (e) => this.handleListClick(e));
        document.getElementById('delete-btn').addEventListener('click', () => this.handleDeleteRecipe());
    },

    showView: function(view, recipeId = null) {
        this.state.currentView = view;
        this.state.selectedRecipeId = recipeId;
        this.render();
    },

    handleFormSubmit: function(e) {
        e.preventDefault();
        const recipe = {
            id: document.getElementById('recipe-id').value || crypto.randomUUID(),
            title: document.getElementById('title').value,
            description: document.getElementById('description').value,
            instructions: document.getElementById('instructions').value,
            tags: document.getElementById('tags').value.split(',').map(tag => tag.trim()),
            favorite: document.getElementById('favorite').checked,
        };

        if (document.getElementById('recipe-id').value) {
            this.updateRecipe(recipe);
        } else {
            this.addRecipe(recipe);
        }
        this.showView('list');
    },

    handleListClick: function(e) {
        if (e.target.classList.contains('edit-btn')) {
            const recipeId = e.target.dataset.id;
            this.showView('form', recipeId);
        }
        if (e.target.classList.contains('delete-btn')) {
            const recipeId = e.target.dataset.id;
            if (confirm('Are you sure you want to delete this recipe?')) {
                this.deleteRecipe(recipeId);
                this.render();
            }
        }
    },
    
    handleDeleteRecipe: function() {
        if (confirm('Are you sure you want to delete this recipe?')) {
            this.deleteRecipe(this.state.selectedRecipeId);
            this.showView('list');
        }
    },

    addRecipe: function(recipe) {
        this.state.recipes.push(recipe);
        this.saveRecipes();
    },

    updateRecipe: function(updatedRecipe) {
        const index = this.state.recipes.findIndex(r => r.id === updatedRecipe.id);
        if (index > -1) {
            this.state.recipes[index] = updatedRecipe;
            this.saveRecipes();
        }
    },

    deleteRecipe: function(id) {
        this.state.recipes = this.state.recipes.filter(r => r.id !== id);
        this.saveRecipes();
    },
};

document.addEventListener('DOMContentLoaded', () => app.init());

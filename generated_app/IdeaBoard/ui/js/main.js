
document.addEventListener('DOMContentLoaded', () => {
    const app = {
        ideas: [],
        currentView: 'idea-list-view',
        init() {
            this.ideas = JSON.parse(localStorage.getItem('IdeaBoard.ideas')) || [];
            this.showView(this.currentView);
            this.renderIdeas();
            this.attachEventListeners();
        },
        showView(viewId) {
            document.querySelectorAll('.view').forEach(view => {
                view.style.display = 'none';
            });
            document.getElementById(viewId).style.display = 'block';
            this.currentView = viewId;
        },
        renderIdeas() {
            const ideaList = document.getElementById('idea-list');
            ideaList.innerHTML = '';
            const searchQuery = document.getElementById('search-bar').value.toLowerCase();
            const filterTags = document.getElementById('filter-tags').value.toLowerCase().split(',').map(tag => tag.trim()).filter(tag => tag);

            const filteredIdeas = this.ideas.filter(idea => {
                const titleMatch = idea.title.toLowerCase().includes(searchQuery);
                const descriptionMatch = idea.description.toLowerCase().includes(searchQuery);
                const tagsMatch = filterTags.length === 0 || filterTags.some(tag => idea.tags.map(t => t.toLowerCase()).includes(tag));
                return (titleMatch || descriptionMatch) && tagsMatch;
            });

            filteredIdeas.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));

            filteredIdeas.forEach(idea => {
                const li = document.createElement('li');
                li.className = 'idea-item';
                li.dataset.id = idea.id;
                li.innerHTML = `
                    <h3>${idea.title}</h3>
                    <p>${idea.description.substring(0, 100)}...</p>
                    <small>Created: ${new Date(idea.createdAt).toLocaleString()}</small>
                `;
                li.addEventListener('click', () => this.editIdea(idea.id));
                ideaList.appendChild(li);
            });
        },
        saveIdeas() {
            localStorage.setItem('IdeaBoard.ideas', JSON.stringify(this.ideas));
        },
        addIdea(title, description, tags) {
            const newIdea = {
                id: crypto.randomUUID(),
                title,
                description,
                tags,
                createdAt: new Date().toISOString(),
                updatedAt: new Date().toISOString(),
            };
            this.ideas.push(newIdea);
            this.saveIdeas();
            this.renderIdeas();
            this.showView('idea-list-view');
        },
        updateIdea(id, title, description, tags) {
            const idea = this.ideas.find(idea => idea.id === id);
            if (idea) {
                idea.title = title;
                idea.description = description;
                idea.tags = tags;
                idea.updatedAt = new Date().toISOString();
                this.saveIdeas();
                this.renderIdeas();
                this.showView('idea-list-view');
            }
        },
        deleteIdea(id) {
            if (confirm('Are you sure you want to delete this idea?')) {
                this.ideas = this.ideas.filter(idea => idea.id !== id);
                this.saveIdeas();
                this.renderIdeas();
                this.showView('idea-list-view');
            }
        },
        editIdea(id) {
            const idea = this.ideas.find(idea => idea.id === id);
            if (idea) {
                document.getElementById('idea-id').value = idea.id;
                document.getElementById('idea-title').value = idea.title;
                document.getElementById('idea-description').value = idea.description;
                document.getElementById('idea-tags').value = idea.tags.join(', ');
                document.getElementById('delete-btn').style.display = 'inline-block';
                this.showView('idea-form-view');
            }
        },
        importIdeas(file) {
            const reader = new FileReader();
            reader.onload = (event) => {
                try {
                    const importedIdeas = JSON.parse(event.target.result);
                    if (Array.isArray(importedIdeas)) {
                        this.ideas = importedIdeas;
                        this.saveIdeas();
                        this.renderIdeas();
                        alert('Ideas imported successfully!');
                    } else {
                        alert('Invalid JSON file.');
                    }
                } catch (error) {
                    alert('Error importing ideas: ' + error.message);
                }
            };
            reader.readAsText(file);
        },
        exportIdeas() {
            const data = JSON.stringify(this.ideas, null, 2);
            const blob = new Blob([data], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'ideaboard.json';
            a.click();
            URL.revokeObjectURL(url);
        },
        clearAllData() {
            if (confirm('Are you sure you want to clear all data?')) {
                this.ideas = [];
                this.saveIdeas();
                this.renderIdeas();
            }
        },
        attachEventListeners() {
            document.getElementById('new-idea-btn').addEventListener('click', () => {
                document.getElementById('idea-form').reset();
                document.getElementById('idea-id').value = '';
                document.getElementById('delete-btn').style.display = 'none';
                this.showView('idea-form-view');
            });

            document.getElementById('cancel-btn').addEventListener('click', () => {
                this.showView('idea-list-view');
            });
            
             document.getElementById('cancel-settings-btn').addEventListener('click', () => {
                this.showView('idea-list-view');
            });

            document.getElementById('settings-btn').addEventListener('click', () => {
                this.showView('settings-view');
            });

            document.getElementById('idea-form').addEventListener('submit', (event) => {
                event.preventDefault();
                const id = document.getElementById('idea-id').value;
                const title = document.getElementById('idea-title').value;
                const description = document.getElementById('idea-description').value;
                const tags = document.getElementById('idea-tags').value.split(',').map(tag => tag.trim()).filter(tag => tag);

                if (id) {
                    this.updateIdea(id, title, description, tags);
                } else {
                    this.addIdea(title, description, tags);
                }
            });

            document.getElementById('delete-btn').addEventListener('click', () => {
                const id = document.getElementById('idea-id').value;
                this.deleteIdea(id);
            });

            document.getElementById('search-bar').addEventListener('input', () => this.renderIdeas());
            document.getElementById('filter-tags').addEventListener('input', () => this.renderIdeas());

            document.getElementById('import-btn').addEventListener('click', () => {
                document.getElementById('import-file').click();
            });

            document.getElementById('import-file').addEventListener('change', (event) => {
                const file = event.target.files[0];
                if (file) {
                    this.importIdeas(file);
                }
            });

            document.getElementById('export-btn').addEventListener('click', () => this.exportIdeas());
            document.getElementById('clear-all-btn').addEventListener('click', () => this.clearAllData());
        }
    };

    app.init();
});


const app = {
    cards: [],
    currentView: 'list-view',
    currentCardIndex: null,
    studySession: {
        cards: [],
        currentIndex: 0,
        filter: 'all'
    },
    init() {
        this.loadData();
        this.render();
        this.addEventListeners();
    },
    render() {
        const views = document.querySelectorAll('.view');
        views.forEach(view => view.style.display = 'none');
        document.getElementById(this.currentView).style.display = 'block';

        if (this.currentView === 'list-view') {
            this.renderCardList();
        }
    },
    addEventListeners() {
        // Navigation
        document.getElementById('new-card-btn').addEventListener('click', () => this.showView('form-view'));
        document.getElementById('cancel-btn').addEventListener('click', () => this.showView('list-view'));
        document.querySelectorAll('[data-view]').forEach(btn => {
            btn.addEventListener('click', () => this.showView(btn.dataset.view));
        });

        // Card form
        document.getElementById('card-form').addEventListener('submit', (e) => {
            e.preventDefault();
            const question = document.getElementById('question').value;
            const answer = document.getElementById('answer').value;
            const tags = document.getElementById('tags').value.split(',').map(tag => tag.trim()).filter(tag => tag);
            
            if (this.currentCardIndex !== null) {
                this.updateCard(this.cards[this.currentCardIndex].id, question, answer, tags);
            } else {
                this.addCard(question, answer, tags);
            }
            document.getElementById('card-form').reset();
            this.showView('list-view');
        });

        // Settings
        document.getElementById('export-btn').addEventListener('click', () => this.exportData());
        document.getElementById('import-btn').addEventListener('click', () => document.getElementById('import-file').click());
        document.getElementById('import-file').addEventListener('change', (e) => this.importData(e.target.files[0]));
        document.getElementById('clear-data-btn').addEventListener('click', () => this.clearData());

        // Study
        document.getElementById('start-study-btn').addEventListener('click', () => this.startStudySession());
        document.getElementById('show-answer-btn').addEventListener('click', () => document.getElementById('study-answer').style.display = 'block');
        document.getElementById('next-card-btn').addEventListener('click', () => this.showNextCard());
        document.getElementById('known-btn').addEventListener('click', () => this.markCardAsKnown());
        document.getElementById('unknown-btn').addEventListener('click', () => this.markCardAsUnknown());

        // Search and filter
        document.getElementById('search-bar').addEventListener('input', (e) => this.renderCardList(e.target.value));
        document.getElementById('filter-status').addEventListener('change', (e) => this.renderCardList(document.getElementById('search-bar').value, e.target.value));
    },
    showView(viewId) {
        this.currentView = viewId;
        if (viewId === 'form-view' && this.currentCardIndex === null) {
            document.getElementById('card-form').reset();
            document.getElementById('delete-btn').style.display = 'none';
        } else {
            document.getElementById('delete-btn').style.display = 'inline-block';
        }
        this.render();
    },
    // Data Persistence
    saveData() {
        localStorage.setItem('SmartCards.cards', JSON.stringify(this.cards));
    },
    loadData() {
        const data = localStorage.getItem('SmartCards.cards');
        if (data) {
            this.cards = JSON.parse(data);
        }
    },
    // CRUD
    addCard(question, answer, tags) {
        const newCard = {
            id: this.generateUUID(),
            question,
            answer,
            tags,
            status: 'unknown',
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString()
        };
        this.cards.push(newCard);
        this.saveData();
        this.renderCardList();
    },
    updateCard(id, question, answer, tags) {
        const card = this.getCardById(id);
        if (card) {
            card.question = question;
            card.answer = answer;
            card.tags = tags;
            card.updatedAt = new Date().toISOString();
            this.saveData();
            this.renderCardList();
        }
        this.currentCardIndex = null;
    },
    deleteCard(id) {
        if (confirm('Are you sure you want to delete this card?')) {
            this.cards = this.cards.filter(card => card.id !== id);
            this.saveData();
            this.renderCardList();
        }
    },
    getCardById(id) {
        return this.cards.find(card => card.id === id);
    },
    // Study
    startStudySession() {
        const filter = document.getElementById('study-filter').value;
        this.studySession.filter = filter;
        if (filter === 'all') {
            this.studySession.cards = [...this.cards];
        } else {
            this.studySession.cards = this.cards.filter(card => card.status === filter);
        }
        this.studySession.currentIndex = 0;
        if (this.studySession.cards.length > 0) {
            this.showStudyCard();
            this.showView('study-view');
        } else {
            alert('No cards to study in this filter.');
        }
    },
    showStudyCard() {
        const card = this.studySession.cards[this.studySession.currentIndex];
        document.getElementById('study-question').textContent = card.question;
        document.getElementById('study-answer').textContent = card.answer;
        document.getElementById('study-answer').style.display = 'none';
        document.getElementById('progress').textContent = `${this.studySession.currentIndex + 1} / ${this.studySession.cards.length}`;
    },
    showNextCard() {
        if (this.studySession.currentIndex < this.studySession.cards.length - 1) {
            this.studySession.currentIndex++;
            this.showStudyCard();
        } else {
            alert('Study session complete!');
            this.showView('list-view');
        }
    },
    markCardAsKnown() {
        const card = this.studySession.cards[this.studySession.currentIndex];
        card.status = 'known';
        this.saveData();
        this.showNextCard();
    },
    markCardAsUnknown() {
        const card = this.studySession.cards[this.studySession.currentIndex];
        card.status = 'unknown';
        this.saveData();
        this.showNextCard();
    },
    // Settings
    exportData() {
        const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(this.cards, null, 2));
        const downloadAnchorNode = document.createElement('a');
        downloadAnchorNode.setAttribute("href", dataStr);
        downloadAnchorNode.setAttribute("download", "smartcards.json");
        document.body.appendChild(downloadAnchorNode);
        downloadAnchorNode.click();
        downloadAnchorNode.remove();
    },
    importData(file) {
        if (file) {
            const reader = new FileReader();
            reader.onload = (e) => {
                try {
                    const importedCards = JSON.parse(e.target.result);
                    if (Array.isArray(importedCards)) {
                        if (confirm('Merge with existing cards or replace? OK for merge, Cancel for replace.')) {
                            this.cards = [...this.cards, ...importedCards];
                        } else {
                            this.cards = importedCards;
                        }
                        this.saveData();
                        this.renderCardList();
                        alert('Data imported successfully!');
                    } else {
                        alert('Invalid JSON file format.');
                    }
                } catch (error) {
                    alert('Error parsing JSON file.');
                }
            };
            reader.readAsText(file);
        }
    },
    clearData() {
        if (confirm('Are you sure you want to clear all data? This cannot be undone.')) {
            this.cards = [];
            this.saveData();
            this.renderCardList();
        }
    },
    // Rendering
    renderCardList(searchTerm = '', statusFilter = 'all') {
        const cardList = document.getElementById('card-list');
        cardList.innerHTML = '';
        let filteredCards = this.cards;

        if (searchTerm) {
            filteredCards = filteredCards.filter(card =>
                card.question.toLowerCase().includes(searchTerm.toLowerCase()) ||
                card.answer.toLowerCase().includes(searchTerm.toLowerCase())
            );
        }

        if (statusFilter !== 'all') {
            filteredCards = filteredCards.filter(card => card.status === statusFilter);
        }

        filteredCards.forEach((card, index) => {
            const cardItem = document.createElement('div');
            cardItem.className = 'card-item';
            cardItem.innerHTML = `
                <div class="card-item-question">${card.question}</div>
                <div class="card-item-status ${card.status}">${card.status}</div>
                <div class="card-item-actions">
                    <button class="edit-btn">Edit</button>
                    <button class="delete-btn">Delete</button>
                </div>
            `;
            cardItem.querySelector('.edit-btn').addEventListener('click', () => {
                this.currentCardIndex = this.cards.findIndex(c => c.id === card.id);
                document.getElementById('question').value = card.question;
                document.getElementById('answer').value = card.answer;
                document.getElementById('tags').value = card.tags.join(', ');
                this.showView('form-view');
            });
            cardItem.querySelector('.delete-btn').addEventListener('click', () => this.deleteCard(card.id));
            cardList.appendChild(cardItem);
        });
    },
    // Utility
    generateUUID() {
        return ([1e7]+-1e3+-4e3+-8e3+-1e11).replace(/[018]/g, c =>
            (c ^ crypto.getRandomValues(new Uint8Array(1))[0] & 15 >> c / 4).toString(16)
        );
    }
};

document.addEventListener('DOMContentLoaded', () => {
    app.init();
});

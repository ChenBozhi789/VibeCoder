
document.addEventListener('DOMContentLoaded', () => {
    // --- STATE MANAGEMENT ---
    let state = {
        books: [],
        currentView: 'home',
        editingBookId: null,
        filter: {
            status: 'all',
            search: ''
        }
    };

    // --- DOM ELEMENTS ---
    const homeView = document.getElementById('home-view');
    const formView = document.getElementById('form-view');
    const settingsView = document.getElementById('settings-view');
    const bookList = document.getElementById('book-list');
    const bookForm = document.getElementById('book-form');
    const formTitle = document.getElementById('form-title');
    const deleteBtn = document.getElementById('delete-btn');
    const searchBar = document.getElementById('search-bar');
    const filterStatus = document.getElementById('filter-status');
    const importBtn = document.getElementById('import-btn');
    const importFile = document.getElementById('import-file');
    const exportBtn = document.getElementById('export-btn');
    const clearDataBtn = document.getElementById('clear-data-btn');

    // --- DATA PERSISTENCE ---
    const STORAGE_KEY = 'BookTrackr.books';

    function getBooks() {
        const books = localStorage.getItem(STORAGE_KEY);
        return books ? JSON.parse(books) : [];
    }

    function saveBooks() {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(state.books));
    }

    // --- UUID Generator ---
    function generateUUID() {
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
            var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
            return v.toString(16);
        });
    }

    // --- RENDER FUNCTIONS ---
    function render() {
        renderBookList();
        showView(state.currentView);
    }

    function showView(view) {
        homeView.classList.add('hidden');
        formView.classList.add('hidden');
        settingsView.classList.add('hidden');

        if (view === 'home') {
            homeView.classList.remove('hidden');
        } else if (view === 'form') {
            formView.classList.remove('hidden');
        } else if (view === 'settings') {
            settingsView.classList.remove('hidden');
        }
    }

    function renderBookList() {
        const { books, filter } = state;
        let filteredBooks = books;

        if (filter.status !== 'all') {
            filteredBooks = filteredBooks.filter(book => book.status === filter.status);
        }

        if (filter.search) {
            const searchTerm = filter.search.toLowerCase();
            filteredBooks = filteredBooks.filter(book =>
                book.title.toLowerCase().includes(searchTerm) ||
                book.author.toLowerCase().includes(searchTerm)
            );
        }

        bookList.innerHTML = '';
        if (filteredBooks.length === 0) {
            bookList.innerHTML = '<p>No books found. Add one to get started!</p>';
            return;
        }

        filteredBooks.forEach(book => {
            const progressPercent = book.totalPages ? (book.currentPage / book.totalPages) * 100 : 0;
            const bookItem = document.createElement('div');
            bookItem.className = 'book-item';
            bookItem.innerHTML = `
                <h3>${book.title}</h3>
                <p class="author">by ${book.author}</p>
                <div class="progress-bar">
                    <div class="progress" style="width: ${progressPercent}%"></div>
                </div>
                <p>Status: <strong>${book.status.charAt(0).toUpperCase() + book.status.slice(1)}</strong></p>
                <div class="book-actions">
                    <button class="btn" data-id="${book.id}" data-action="edit">Edit</button>
                    <button class="btn btn-danger" data-id="${book.id}" data-action="delete">Delete</button>
                    <button class="btn" data-id="${book.id}" data-action="increment">+1 Page</button>
                    <button class="btn" data-id="${book.id}" data-action="finish">Finish</button>
                </div>
            `;
            bookList.appendChild(bookItem);
        });
    }

    // --- EVENT HANDLERS ---
    document.getElementById('nav-home').addEventListener('click', (e) => {
        e.preventDefault();
        state.currentView = 'home';
        render();
    });

    document.getElementById('nav-new-book').addEventListener('click', (e) => {
        e.preventDefault();
        state.currentView = 'form';
        state.editingBookId = null;
        formTitle.textContent = 'Add a New Book';
        bookForm.reset();
        deleteBtn.classList.add('hidden');
        render();
    });

    document.getElementById('nav-settings').addEventListener('click', (e) => {
        e.preventDefault();
        state.currentView = 'settings';
        render();
    });

    document.getElementById('cancel-btn').addEventListener('click', () => {
        state.currentView = 'home';
        render();
    });

    bookForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const formData = new FormData(bookForm);
        const bookData = {
            title: formData.get('title'),
            author: formData.get('author'),
            totalPages: formData.get('totalPages') ? parseInt(formData.get('totalPages')) : null,
            currentPage: formData.get('currentPage') ? parseInt(formData.get('currentPage')) : 0,
            description: formData.get('description'),
            tags: formData.get('tags').split(',').map(tag => tag.trim()).filter(tag => tag),
        };

        if (state.editingBookId) {
            const bookIndex = state.books.findIndex(book => book.id === state.editingBookId);
            if (bookIndex > -1) {
                state.books[bookIndex] = { ...state.books[bookIndex], ...bookData, updatedAt: new Date().toISOString() };
            }
        } else {
            bookData.id = generateUUID();
            bookData.createdAt = new Date().toISOString();
            bookData.updatedAt = new Date().toISOString();
            bookData.status = 'reading';
            state.books.push(bookData);
        }

        saveBooks();
        state.currentView = 'home';
        render();
    });

    bookList.addEventListener('click', (e) => {
        const { id, action } = e.target.dataset;
        if (!id || !action) return;

        const bookIndex = state.books.findIndex(book => book.id === id);
        if (bookIndex === -1) return;

        const book = state.books[bookIndex];

        switch (action) {
            case 'edit':
                state.currentView = 'form';
                state.editingBookId = id;
                formTitle.textContent = 'Edit Book';
                deleteBtn.classList.remove('hidden');

                bookForm.elements.title.value = book.title;
                bookForm.elements.author.value = book.author;
                bookForm.elements.totalPages.value = book.totalPages;
                bookForm.elements.currentPage.value = book.currentPage;
                bookForm.elements.description.value = book.description;
                bookForm.elements.tags.value = book.tags.join(', ');
                render();
                break;
            case 'delete':
                if (confirm('Are you sure you want to delete this book?')) {
                    state.books.splice(bookIndex, 1);
                    saveBooks();
                    render();
                }
                break;
            case 'increment':
                if (book.currentPage < book.totalPages) {
                    book.currentPage++;
                    book.updatedAt = new Date().toISOString();
                    saveBooks();
                    render();
                }
                break;
            case 'finish':
                book.status = 'finished';
                if (book.totalPages) {
                    book.currentPage = book.totalPages;
                }
                book.finishedAt = new Date().toISOString();
                book.updatedAt = new Date().toISOString();
                saveBooks();
                render();
                break;
        }
    });

    deleteBtn.addEventListener('click', () => {
        if (state.editingBookId && confirm('Are you sure you want to delete this book?')) {
            state.books = state.books.filter(book => book.id !== state.editingBookId);
            saveBooks();
            state.currentView = 'home';
            render();
        }
    });

    searchBar.addEventListener('input', (e) => {
        state.filter.search = e.target.value;
        render();
    });

    filterStatus.addEventListener('change', (e) => {
        state.filter.status = e.target.value;
        render();
    });

    importBtn.addEventListener('click', () => {
        importFile.click();
    });

    importFile.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = (e) => {
            try {
                const importedBooks = JSON.parse(e.target.result);
                if (Array.isArray(importedBooks)) {
                    // Simple merge: add new books, don't update existing ones
                    const existingIds = new Set(state.books.map(b => b.id));
                    const newBooks = importedBooks.filter(b => !existingIds.has(b.id));
                    state.books.push(...newBooks);
                    saveBooks();
                    render();
                    alert('Books imported successfully!');
                } else {
                    alert('Invalid file format.');
                }
            } catch (error) {
                alert('Error parsing file.');
            }
        };
        reader.readAsText(file);
    });

    exportBtn.addEventListener('click', () => {
        const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(state.books, null, 2));
        const downloadAnchorNode = document.createElement('a');
        downloadAnchorNode.setAttribute("href", dataStr);
        downloadAnchorNode.setAttribute("download", "BookTrackr_export.json");
        document.body.appendChild(downloadAnchorNode); // required for firefox
        downloadAnchorNode.click();
        downloadAnchorNode.remove();
    });

    clearDataBtn.addEventListener('click', () => {
        if (confirm('Are you sure you want to delete all your data? This action cannot be undone.')) {
            state.books = [];
            saveBooks();
            render();
        }
    });


    // --- INITIAL LOAD ---
    state.books = getBooks();
    render();
});

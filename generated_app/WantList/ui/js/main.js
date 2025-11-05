
document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const newItemBtn = document.getElementById('new-item-btn');
    const itemModal = document.getElementById('item-modal');
    const closeModalBtn = document.getElementById('close-modal-btn');
    const cancelBtn = document.getElementById('cancel-btn');
    const itemForm = document.getElementById('item-form');
    const itemList = document.getElementById('item-list');
    const totalItems = document.getElementById('total-items');
    const totalPrice = document.getElementById('total-price');
    const searchInput = document.getElementById('search-input');
    const filterSelect = document.getElementById('filter-select');
    const modalTitle = document.getElementById('modal-title');
    const itemId = document.getElementById('item-id');
    const itemTitle = document.getElementById('item-title');
    const itemPrice = document.getElementById('item-price');
    const itemDescription = document.getElementById('item-description');
    const itemTags = document.getElementById('item-tags');
    const importBtn = document.getElementById('import-btn');
    const exportBtn = document.getElementById('export-btn');
    const clearBtn = document.getElementById('clear-btn');

    let items = JSON.parse(localStorage.getItem('WantList.items')) || [];

    // --- Data Functions ---
    const saveItems = () => {
        localStorage.setItem('WantList.items', JSON.stringify(items));
    };

    const renderItems = () => {
        const searchTerm = searchInput.value.toLowerCase();
        const filterValue = filterSelect.value;

        const filteredItems = items.filter(item => {
            const titleMatch = item.title.toLowerCase().includes(searchTerm);
            if (filterValue === 'with-price') {
                return titleMatch && item.price !== null && item.price !== undefined && item.price > 0;
            }
            if (filterValue === 'without-price') {
                return titleMatch && (item.price === null || item.price === undefined || item.price <= 0);
            }
            return titleMatch;
        });

        itemList.innerHTML = '';
        filteredItems.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt)).forEach(item => {
            const li = document.createElement('li');
            li.className = 'item';
            li.dataset.id = item.id;
            li.innerHTML = `
                <div class="item-details" data-id="${item.id}">
                    <div class="item-title">${item.title}</div>
                    <div class="item-price">${item.price ? '$' + item.price.toFixed(2) : '—'}</div>
                </div>
                <div class="item-actions">
                    <button class="delete-btn" data-id="${item.id}">Delete</button>
                </div>
            `;
            itemList.appendChild(li);
        });
        updateSummary();
    };

    const updateSummary = () => {
        totalItems.textContent = items.length;
        const total = items.reduce((sum, item) => sum + (item.price || 0), 0);
        totalPrice.textContent = total.toFixed(2);
    };

    // --- Modal Functions ---
    const openModal = (item = null) => {
        itemForm.reset();
        if (item) {
            modalTitle.textContent = 'Edit Item';
            itemId.value = item.id;
            itemTitle.value = item.title;
            itemPrice.value = item.price;
            itemDescription.value = item.description;
            itemTags.value = item.tags.join(', ');
        } else {
            modalTitle.textContent = 'New Item';
            itemId.value = '';
        }
        itemModal.style.display = 'block';
    };

    const closeModal = () => {
        itemModal.style.display = 'none';
    };

    // --- Event Listeners ---
    newItemBtn.addEventListener('click', () => openModal());
    closeModalBtn.addEventListener('click', closeModal);
    cancelBtn.addEventListener('click', closeModal);
    window.addEventListener('click', (e) => {
        if (e.target === itemModal) {
            closeModal();
        }
    });

    itemForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const id = itemId.value;
        const title = itemTitle.value.trim();
        const price = parseFloat(itemPrice.value) || null;
        const description = itemDescription.value.trim();
        const tags = itemTags.value.split(',').map(tag => tag.trim()).filter(Boolean);

        if (!title) {
            alert('Title is required.');
            return;
        }

        if (id) {
            // Update existing item
            const item = items.find(item => item.id === id);
            item.title = title;
            item.price = price;
            item.description = description;
            item.tags = tags;
            item.updatedAt = new Date().toISOString();
        } else {
            // Create new item
            items.push({
                id: crypto.randomUUID(),
                title,
                price,
                description,
                tags,
                createdAt: new Date().toISOString(),
                updatedAt: new Date().toISOString()
            });
        }
        saveItems();
        renderItems();
        closeModal();
    });

    itemList.addEventListener('click', (e) => {
        const id = e.target.closest('.item').dataset.id;
        if (e.target.classList.contains('delete-btn')) {
            if (confirm('Are you sure you want to delete this item?')) {
                items = items.filter(item => item.id !== id);
                saveItems();
                renderItems();
            }
        } else if (e.target.closest('.item-details')) {
             const item = items.find(item => item.id === id);
             openModal(item);
        }
    });

    searchInput.addEventListener('input', renderItems);
    filterSelect.addEventListener('change', renderItems);
    
    // --- Data Portability ---
    exportBtn.addEventListener('click', () => {
        const dataStr = JSON.stringify(items, null, 2);
        const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
        const exportFileDefaultName = 'WantList_export.json';
        let linkElement = document.createElement('a');
        linkElement.setAttribute('href', dataUri);
        linkElement.setAttribute('download', exportFileDefaultName);
        linkElement.click();
    });

    importBtn.addEventListener('click', () => {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = '.json';
        input.onchange = e => {
            const file = e.target.files[0];
            const reader = new FileReader();
            reader.onload = readerEvent => {
                const content = readerEvent.target.result;
                try {
                    const importedItems = JSON.parse(content);
                    if (Array.isArray(importedItems)) {
                         if (confirm('Do you want to merge with existing data? (Cancel to replace)')) {
                            items = [...items, ...importedItems];
                         } else {
                            items = importedItems;
                         }
                        saveItems();
                        renderItems();
                        alert('Data imported successfully!');
                    } else {
                        alert('Invalid JSON format.');
                    }
                } catch (error) {
                    alert('Error importing data: ' + error.message);
                }
            };
            reader.readAsText(file, 'UTF-8');
        };
        input.click();
    });

    clearBtn.addEventListener('click', () => {
        if (confirm('Are you sure you want to clear all data? This cannot be undone.')) {
            items = [];
            saveItems();
            renderItems();
        }
    });


    // Initial Render
    renderItems();
});


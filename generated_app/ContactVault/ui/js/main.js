
document.addEventListener('DOMContentLoaded', () => {
    // DOM elements
    const homeBtn = document.getElementById('home-btn');
    const settingsBtn = document.getElementById('settings-btn');
    const newContactBtn = document.getElementById('new-contact-btn');
    const saveContactBtn = document.getElementById('save-contact-btn');
    const cancelBtn = document.getElementById('cancel-btn');
    const deleteContactBtn = document.getElementById('delete-contact-btn');
    const importBtn = document.getElementById('import-btn');
    const exportBtn = document.getElementById('export-btn');
    const clearAllBtn = document.getElementById('clear-all-btn');
    const searchBar = document.getElementById('search-bar');

    const listView = document.getElementById('list-view');
    const detailView = document.getElementById('detail-view');
    const settingsView = document.getElementById('settings-view');
    const contactList = document.getElementById('contact-list');
    const contactForm = document.getElementById('contact-form');
    const importFileInput = document.getElementById('import-file');

    let contacts = [];
    let currentContactId = null;

    // Data persistence
    function loadContacts() {
        const contactsJSON = localStorage.getItem('ContactVault.contacts');
        contacts = contactsJSON ? JSON.parse(contactsJSON) : [];
    }

    function saveContacts() {
        localStorage.setItem('ContactVault.contacts', JSON.stringify(contacts));
    }

    // Navigation
    function showListView() {
        listView.classList.remove('hidden');
        detailView.classList.add('hidden');
        settingsView.classList.add('hidden');
        renderContactList();
    }

    function showDetailView(contact) {
        listView.classList.add('hidden');
        detailView.classList.remove('hidden');
        settingsView.classList.add('hidden');
        if (contact) {
            currentContactId = contact.id;
            document.getElementById('contact-id').value = contact.id;
            document.getElementById('name').value = contact.name;
            document.getElementById('phone').value = contact.phone;
            document.getElementById('email').value = contact.email;
            document.getElementById('notes').value = contact.notes;
            document.getElementById('tags').value = contact.tags.join(', ');
            deleteContactBtn.classList.remove('hidden');
        } else {
            currentContactId = null;
            contactForm.reset();
            document.getElementById('contact-id').value = '';
            deleteContactBtn.classList.add('hidden');
        }
    }

    function showSettingsView() {
        listView.classList.add('hidden');
        detailView.classList.add('hidden');
        settingsView.classList.remove('hidden');
    }

    // Rendering
    function renderContactList(filteredContacts = contacts) {
        contactList.innerHTML = '';
        filteredContacts.sort((a, b) => a.name.localeCompare(b.name));
        filteredContacts.forEach(contact => {
            const li = document.createElement('li');
            li.innerHTML = `
                <div>
                    <strong>${contact.name}</strong>
                    <small>${contact.phone || contact.email}</small>
                </div>
                <button class="edit-btn">Edit</button>
            `;
            li.querySelector('.edit-btn').addEventListener('click', (e) => {
                e.stopPropagation();
                showDetailView(contact);
            });
            li.addEventListener('click', () => showDetailView(contact));
            contactList.appendChild(li);
        });
    }

    // CRUD operations
    function saveContact() {
        const id = document.getElementById('contact-id').value;
        const name = document.getElementById('name').value.trim();
        const phone = document.getElementById('phone').value.trim();
        const email = document.getElementById('email').value.trim();
        const notes = document.getElementById('notes').value.trim();
        const tags = document.getElementById('tags').value.split(',').map(tag => tag.trim()).filter(tag => tag);

        if (!name) {
            alert('Name is required.');
            return;
        }
        if (email && !/\S+@\S+\.\S+/.test(email)) {
            alert('Invalid email format.');
            return;
        }

        const now = new Date().toISOString();
        if (id) {
            const index = contacts.findIndex(c => c.id == id);
            if (index !== -1) {
                contacts[index] = { ...contacts[index], name, phone, email, notes, tags, updatedAt: now };
            }
        } else {
            const newContact = { id: Date.now().toString(), name, phone, email, notes, tags, createdAt: now, updatedAt: now };
            contacts.push(newContact);
        }
        saveContacts();
        showListView();
    }

    function deleteContact() {
        if (currentContactId && confirm('Are you sure you want to delete this contact?')) {
            contacts = contacts.filter(c => c.id !== currentContactId);
            saveContacts();
            showListView();
        }
    }

    // Search and filter
    function searchContacts() {
        const searchTerm = searchBar.value.toLowerCase();
        const filteredContacts = contacts.filter(contact =>
            contact.name.toLowerCase().includes(searchTerm) ||
            contact.phone.toLowerCase().includes(searchTerm) ||
            contact.email.toLowerCase().includes(searchTerm)
        );
        renderContactList(filteredContacts);
    }

    // Data portability
    function exportContacts() {
        const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(contacts, null, 2));
        const downloadAnchorNode = document.createElement('a');
        downloadAnchorNode.setAttribute("href", dataStr);
        downloadAnchorNode.setAttribute("download", "ContactVault_export.json");
        document.body.appendChild(downloadAnchorNode);
        downloadAnchorNode.click();
        downloadAnchorNode.remove();
    }

    function importContacts() {
        importFileInput.click();
    }

    function handleImportFile(event) {
        const file = event.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function (e) {
                try {
                    const importedContacts = JSON.parse(e.target.result);
                    if (Array.isArray(importedContacts) && confirm('Are you sure you want to replace all contacts with the imported data?')) {
                        contacts = importedContacts;
                        saveContacts();
                        showListView();
                    } else {
                        alert('Invalid file format.');
                    }
                } catch (error) {
                    alert('Error parsing JSON file.');
                }
            };
            reader.readAsText(file);
        }
    }

    function clearAllData() {
        if (confirm('Are you sure you want to delete all contacts? This action cannot be undone.')) {
            contacts = [];
            saveContacts();
            showListView();
        }
    }

    // Event Listeners
    homeBtn.addEventListener('click', showListView);
    settingsBtn.addEventListener('click', showSettingsView);
    newContactBtn.addEventListener('click', () => showDetailView(null));
    cancelBtn.addEventListener('click', showListView);
    contactForm.addEventListener('submit', (e) => {
        e.preventDefault();
        saveContact();
    });
    deleteContactBtn.addEventListener('click', deleteContact);
    importBtn.addEventListener('click', importContacts);
    importFileInput.addEventListener('change', handleImportFile);
    exportBtn.addEventListener('click', exportContacts);
    clearAllBtn.addEventListener('click', clearAllData);
    searchBar.addEventListener('input', searchContacts);

    // Initial load
    loadContacts();
    showListView();
});

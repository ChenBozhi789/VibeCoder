
// EasyBook - A simple booking management app
// (c) 2023-2024, MIT License

// --- STATE MANAGEMENT ---
let state = {
  bookings: [],
  filters: {
    searchTerm: '',
    status: 'all',
    dateRange: 'all'
  },
  editingBookingId: null,
  pagination: {
    currentPage: 1,
    itemsPerPage: 10
  }
};

const STORAGE_KEY = 'EasyBook.bookings';

// --- DOM ELEMENTS ---
const DOMElements = {
    bookingList: document.getElementById('booking-list'),
    bookingModal: document.getElementById('booking-modal'),
    importExportModal: document.getElementById('import-export-modal'),
    bookingForm: document.getElementById('booking-form'),
    btnAdd: document.getElementById('btn-add'),
    closeButtons: document.querySelectorAll('.close-button'),
    pageIndicator: document.getElementById('page-indicator'),
    prevPage: document.getElementById('prev-page'),
    nextPage: document.getElementById('next-page'),
    search: document.getElementById('search'),
    statusFilter: document.getElementById('status-filter'),
    dateRange: document.getElementById('date-range'),
    btnImport: document.getElementById('btn-import'),
    btnExport: document.getElementById('btn-export'),
    modalTitle: document.getElementById('booking-modal-title'),
    bookingId: document.getElementById('bk-id'),
    bookingTitle: document.getElementById('bk-title'),
    bookingDate: document.getElementById('bk-date'),
    bookingTime: document.getElementById('bk-time'),
    bookingStatus: document.getElementById('bk-status'),
    bookingNotes: document.getElementById('bk-notes'),
    btnExportJson: document.getElementById('btn-export-json'),
    btnImportApply: document.getElementById('btn-import-apply'),
    importFile: document.getElementById('import-file'),
    importMode: document.getElementById('import-mode'),
};

// --- DATA PERSISTENCE ---
function loadState() {
  const data = localStorage.getItem(STORAGE_KEY);
  if (data) {
    state.bookings = JSON.parse(data);
  }
  render();
}

function saveState() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(state.bookings));
}

// --- UTILITY FUNCTIONS ---
function nextId() {
  return `bk_${new Date().getTime()}`;
}

// --- RENDER FUNCTION ---
function render() {
  const { bookings, filters, pagination } = state;
  const { bookingList, pageIndicator, prevPage, nextPage } = DOMElements;

  // Apply filters
  let filteredBookings = bookings.filter(booking => {
    const searchTerm = filters.searchTerm.toLowerCase();
    const titleMatch = booking.title.toLowerCase().includes(searchTerm);
    const notesMatch = booking.description && booking.description.toLowerCase().includes(searchTerm);
    const statusMatch = filters.status === 'all' || booking.status === filters.status;
    return (titleMatch || notesMatch) && statusMatch;
  });

  // Apply date range filter
    const now = new Date();
    const today = now.toISOString().split('T')[0];
    if (filters.dateRange === 'today') {
        filteredBookings = filteredBookings.filter(b => b.date === today);
    } else if (filters.dateRange === 'this-week') {
        const firstDay = new Date(now.setDate(now.getDate() - now.getDay()));
        const lastDay = new Date(now.setDate(now.getDate() - now.getDay() + 6));
        filteredBookings = filteredBookings.filter(b => {
            const bookingDate = new Date(b.date);
            return bookingDate >= firstDay && bookingDate <= lastDay;
        });
    }


  // Sort by date
  filteredBookings.sort((a, b) => new Date(a.date) - new Date(b.date));

  // Pagination
  const totalPages = Math.ceil(filteredBookings.length / pagination.itemsPerPage);
  pagination.currentPage = Math.min(pagination.currentPage, totalPages || 1);
  const startIndex = (pagination.currentPage - 1) * pagination.itemsPerPage;
  const endIndex = startIndex + pagination.itemsPerPage;
  const paginatedBookings = filteredBookings.slice(startIndex, endIndex);

  // Render bookings
  bookingList.innerHTML = paginatedBookings.map(booking => `
    <div class="booking-item" data-id="${booking.id}">
        <h3>${booking.title}</h3>
        <p>${booking.date} at ${booking.time}</p>
        <p>Status: <span class="status-${booking.status}">${booking.status}</span></p>
        <p>${booking.description || ''}</p>
        <button class="btn-edit">Edit</button>
        <button class="btn-delete">Delete</button>
    </div>
  `).join('') || '<p>No bookings found.</p>';

  // Update pagination controls
  pageIndicator.textContent = `Page ${pagination.currentPage} of ${totalPages || 1}`;
  prevPage.disabled = pagination.currentPage === 1;
  nextPage.disabled = pagination.currentPage === totalPages || totalPages === 0;

  // Add event listeners for edit and delete buttons
  document.querySelectorAll('.btn-edit').forEach(btn => btn.addEventListener('click', (e) => openEditModal(e.target.closest('.booking-item').dataset.id)));
  document.querySelectorAll('.btn-delete').forEach(btn => btn.addEventListener('click', (e) => deleteBooking(e.target.closest('.booking-item').dataset.id)));
}

// --- MODAL MANAGEMENT ---
function openModal(modal) {
    modal.style.display = 'block';
}

function closeModal(modal) {
    modal.style.display = 'none';
}

// --- BOOKING MANAGEMENT ---
function openCreateModal() {
    DOMElements.modalTitle.textContent = 'New Booking';
    DOMElements.bookingForm.reset();
    DOMElements.bookingId.value = '';
    state.editingBookingId = null;
    openModal(DOMElements.bookingModal);
}

function openEditModal(id) {
    const booking = state.bookings.find(b => b.id === id);
    if (booking) {
        DOMElements.modalTitle.textContent = 'Edit Booking';
        DOMElements.bookingId.value = booking.id;
        DOMElements.bookingTitle.value = booking.title;
        DOMElements.bookingDate.value = booking.date;
        DOMElements.bookingTime.value = booking.time;
        DOMElements.bookingStatus.value = booking.status;
        DOMElements.bookingNotes.value = booking.description;
        state.editingBookingId = id;
        openModal(DOMElements.bookingModal);
    }
}

function handleFormSubmit(e) {
    e.preventDefault();
    const id = DOMElements.bookingId.value;
    const bookingData = {
        id: id || nextId(),
        title: DOMElements.bookingTitle.value,
        date: DOMElements.bookingDate.value,
        time: DOMElements.bookingTime.value,
        status: DOMElements.bookingStatus.value,
        description: DOMElements.bookingNotes.value,
        createdAt: id ? state.bookings.find(b => b.id === id).createdAt : new Date().toISOString(),
        updatedAt: new Date().toISOString()
    };

    if (checkForConflict(bookingData.date, bookingData.time, bookingData.id)) {
        if (!confirm('There is a booking at this time. Are you sure you want to proceed?')) {
            return;
        }
    }

    if (id) {
        // Update
        const index = state.bookings.findIndex(b => b.id === id);
        state.bookings[index] = bookingData;
    } else {
        // Create
        state.bookings.push(bookingData);
    }

    saveState();
    render();
    closeModal(DOMElements.bookingModal);
}

function deleteBooking(id) {
    if (confirm('Are you sure you want to delete this booking?')) {
        state.bookings = state.bookings.filter(b => b.id !== id);
        saveState();
        render();
    }
}

function checkForConflict(date, time, excludeId) {
    return state.bookings.some(b => b.id !== excludeId && b.date === date && b.time === time && b.status !== 'cancelled');
}

// --- DATA PORTABILITY ---
function handleExport() {
    const dataStr = JSON.stringify(state.bookings, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
    const exportFileDefaultName = 'easybook_backup.json';
    let linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
}

function handleImport() {
    const file = DOMElements.importFile.files[0];
    if (!file) {
        alert('Please select a file to import.');
        return;
    }

    const reader = new FileReader();
    reader.onload = function(event) {
        try {
            const importedBookings = JSON.parse(event.target.result);
            const mode = DOMElements.importMode.value;

            if (mode === 'replace') {
                if (confirm('Are you sure you want to replace all existing bookings?')) {
                    state.bookings = importedBookings;
                }
            } else { // merge
                importedBookings.forEach(importedBooking => {
                    const existingIndex = state.bookings.findIndex(b => b.id === importedBooking.id);
                    if (existingIndex !== -1) {
                        state.bookings[existingIndex] = importedBooking;
                    } else {
                        state.bookings.push(importedBooking);
                    }
                });
            }

            saveState();
            render();
            closeModal(DOMElements.importExportModal);
        } catch (error) {
            alert('Error importing file. Please make sure it is a valid JSON file.');
        }
    };
    reader.readAsText(file);
}

// --- EVENT LISTENERS ---
DOMElements.btnAdd.addEventListener('click', openCreateModal);
DOMElements.btnImport.addEventListener('click', () => openModal(DOMElements.importExportModal));
DOMElements.btnExport.addEventListener('click', handleExport); // Direct export
DOMElements.btnExportJson.addEventListener('click', handleExport);
DOMElements.btnImportApply.addEventListener('click', handleImport);

DOMElements.closeButtons.forEach(btn => btn.addEventListener('click', (e) => closeModal(e.target.closest('.modal'))));
DOMElements.bookingForm.addEventListener('submit', handleFormSubmit);
DOMElements.search.addEventListener('input', (e) => {
    state.filters.searchTerm = e.target.value;
    render();
});
DOMElements.statusFilter.addEventListener('change', (e) => {
    state.filters.status = e.target.value;
    render();
});
DOMElements.dateRange.addEventListener('change', (e) => {
    state.filters.dateRange = e.target.value;
    render();
});
DOMElements.prevPage.addEventListener('click', () => {
    if (state.pagination.currentPage > 1) {
        state.pagination.currentPage--;
        render();
    }
});
DOMElements.nextPage.addEventListener('click', () => {
    const totalPages = Math.ceil(state.bookings.length / state.pagination.itemsPerPage);
    if (state.pagination.currentPage < totalPages) {
        state.pagination.currentPage++;
        render();
    }
});


// --- INITIALIZATION ---
document.addEventListener('DOMContentLoaded', () => {
  loadState();
});

// Alias for initialization
function init() {
    loadState();
}

// Start the app
init();

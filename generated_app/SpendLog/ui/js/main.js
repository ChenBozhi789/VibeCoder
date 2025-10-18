
document.addEventListener('DOMContentLoaded', () => {
    const expenseForm = document.getElementById('expense-form');
    const expenseNameInput = document.getElementById('expense-name');
    const expenseAmountInput = document.getElementById('expense-amount');
    const expenseCategoryInput = document.getElementById('expense-category');
    const expenseList = document.getElementById('expense-list');
    const totalExpensesSpan = document.getElementById('total-expenses');
    const categorySummaryList = document.getElementById('category-summary');

    let expenses = getExpenses();

    function getExpenses() {
        const expenses = localStorage.getItem('expenses');
        return expenses ? JSON.parse(expenses) : [];
    }

    function saveExpenses() {
        localStorage.setItem('expenses', JSON.stringify(expenses));
    }

    function render() {
        renderExpenses();
        updateSummary();
    }

    function renderExpenses() {
        expenseList.innerHTML = '';
        if (expenses.length === 0) {
            expenseList.innerHTML = '<p>No expenses added yet.</p>';
            return;
        }
        expenses.forEach((expense, index) => {
            const li = document.createElement('li');
            li.innerHTML = `
                <div class="expense-item">
                    <span>${expense.name}</span> - $${expense.amount.toFixed(2)} <em>(${expense.category})</em>
                </div>
                <button class="delete-btn" data-index="${index}">Delete</button>
            `;
            expenseList.appendChild(li);
        });
    }

    function updateSummary() {
        const total = expenses.reduce((sum, expense) => sum + expense.amount, 0);
        totalExpensesSpan.textContent = total.toFixed(2);

        const categoryTotals = expenses.reduce((acc, expense) => {
            acc[expense.category] = (acc[expense.category] || 0) + expense.amount;
            return acc;
        }, {});
        
        categorySummaryList.innerHTML = '';
        if (Object.keys(categoryTotals).length === 0) {
            categorySummaryList.innerHTML = '<li>No expenses by category.</li>';
        } else {
            for (const category in categoryTotals) {
                const li = document.createElement('li');
                li.textContent = `${category}: $${categoryTotals[category].toFixed(2)}`;
                categorySummaryList.appendChild(li);
            }
        }
    }

    function addExpense(name, amount, category) {
        if (name.trim() === '' || isNaN(amount) || amount <= 0 || category === '') {
            alert('Please fill in all fields with valid data.');
            return;
        }
        expenses.push({ name, amount, category });
        saveExpenses();
        render();
    }
    
    function deleteExpense(index) {
        expenses.splice(index, 1);
        saveExpenses();
        render();
    }

    expenseForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const name = expenseNameInput.value;
        const amount = parseFloat(expenseAmountInput.value);
        const category = expenseCategoryInput.value;
        
        addExpense(name, amount, category);
        
        expenseForm.reset();
    });

    expenseList.addEventListener('click', (e) => {
        if (e.target.classList.contains('delete-btn')) {
            const index = parseInt(e.target.getAttribute('data-index'), 10);
            deleteExpense(index);
        }
    });

    // Initial render
    render();
});

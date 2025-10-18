
// State management
let state = {
    feeds: [],
    selectedFeedId: null,
};

// DOM elements
const addFeedForm = document.getElementById('add-feed-form');
const feedUrlInput = document.getElementById('feed-url');
const feedList = document.getElementById('feed-list');
const articlesContainer = document.getElementById('articles-container');

// Data persistence
function saveState() {
    localStorage.setItem('feedboxState', JSON.stringify(state));
}

function loadState() {
    const savedState = localStorage.getItem('feedboxState');
    if (savedState) {
        state = JSON.parse(savedState);
    }
}

// Render functions
function renderFeeds() {
    feedList.innerHTML = '';
    state.feeds.forEach(feed => {
        const li = document.createElement('li');
        li.textContent = feed.title;
        li.dataset.feedId = feed.id;
        li.classList.add('feed-item');
        if (feed.id === state.selectedFeedId) {
            li.classList.add('selected');
        }

        const deleteButton = document.createElement('button');
        deleteButton.textContent = 'Delete';
        deleteButton.classList.add('delete-feed-btn');
        deleteButton.dataset.feedId = feed.id;
        li.appendChild(deleteButton);

        feedList.appendChild(li);
    });
}

function renderArticles() {
    const selectedFeed = state.feeds.find(feed => feed.id === state.selectedFeedId);
    if (selectedFeed) {
        articlesContainer.innerHTML = '';
        selectedFeed.articles.forEach((article, index) => {
            const articleDiv = document.createElement('div');
            articleDiv.classList.add('article');
            if (article.read) {
                articleDiv.classList.add('read');
            }
            articleDiv.innerHTML = `
                <h2><a href="${article.link}" target="_blank">${article.title}</a></h2>
                <p>${article.description}</p>
                <button class="toggle-read-btn" data-article-index="${index}">${article.read ? 'Mark as Unread' : 'Mark as Read'}</button>
            `;
            articlesContainer.appendChild(articleDiv);
        });
    } else {
        articlesContainer.innerHTML = '<p>Select a feed to see articles.</p>';
    }
}

// Event listeners
addFeedForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const url = feedUrlInput.value;
    feedUrlInput.value = '';

    try {
        const response = await fetch(`https://api.rss2json.com/v1/api.json?rss_url=${encodeURIComponent(url)}`);
        const data = await response.json();

        if (data.status === 'ok') {
            const newFeed = {
                id: Date.now().toString(),
                url: url,
                title: data.feed.title,
                articles: data.items.map(item => ({
                    title: item.title,
                    link: item.link,
                    description: item.description,
                    pubDate: item.pubDate,
                    read: false
                }))
            };
            state.feeds.push(newFeed);
            saveState();
            renderFeeds();
        } else {
            alert('Could not fetch or parse the feed.');
        }
    } catch (error) {
        console.error('Error fetching feed:', error);
        alert('Error fetching feed. Check the console for details.');
    }
});

feedList.addEventListener('click', (e) => {
    if (e.target.classList.contains('feed-item')) {
        const feedId = e.target.dataset.feedId;
        state.selectedFeedId = feedId;
        saveState();
        renderFeeds();
        renderArticles();
    }
    if (e.target.classList.contains('delete-feed-btn')) {
        const feedId = e.target.dataset.feedId;
        state.feeds = state.feeds.filter(feed => feed.id !== feedId);
        if (state.selectedFeedId === feedId) {
            state.selectedFeedId = null;
        }
        saveState();
        renderFeeds();
        renderArticles();
    }
});

articlesContainer.addEventListener('click', (e) => {
    if (e.target.classList.contains('toggle-read-btn')) {
        const articleIndex = parseInt(e.target.dataset.articleIndex, 10);
        const selectedFeed = state.feeds.find(feed => feed.id === state.selectedFeedId);
        if (selectedFeed) {
            selectedFeed.articles[articleIndex].read = !selectedFeed.articles[articleIndex].read;
            saveState();
            renderArticles();
        }
    }
});

// Initialization
function init() {
    loadState();
    renderFeeds();
    renderArticles();
}

init();

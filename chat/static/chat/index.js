document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('search');
    const searchResults = document.getElementById('search-results');

    // Handle input in the search bar
    searchInput.addEventListener('input', async () => {
        const query = searchInput.value;
        if (query.trim() === '') {
            searchResults.innerHTML = '';
            return;
        }

        // Fetch users matching the search query
        const response = await fetch(`/search_users/?query=${query}`);
        const users = await response.json();

        // Display user search results
        searchResults.innerHTML = users.map(user => `
            <div class="list-group-item">
                <a href="#" data-user-id="${user.id}">${user.username}</a>
            </div>
        `).join('');
    });

    // Handle clicks on search results to start a chat
    searchResults.addEventListener('click', event => {
        if (event.target.tagName === 'A') {
            const userId = event.target.getAttribute('data-user-id');
            window.location.href = `/start_chat/${userId}/`;
        }
    });
});


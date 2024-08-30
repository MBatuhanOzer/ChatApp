document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('search');
    const searchResults = document.getElementById('search-results');

    searchInput.addEventListener('input', async () => {
        const query = searchInput.value;
        if (query.length < 3) {
            searchResults.innerHTML = '';
            return;
        }

        const response = await fetch(`/search_users/?query=${query}`);
        const users = await response.json();

        searchResults.innerHTML = users.map(user => `
            <div>
                <a href="#" data-user-id="${user.id}">${user.username}</a>
            </div>
        `).join('');
    });

    searchResults.addEventListener('click', event => {
        if (event.target.tagName === 'A') {
            const userId = event.target.getAttribute('data-user-id');
            window.location.href = `/start_chat/${userId}/`;
        }
    });
});

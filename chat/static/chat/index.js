document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('search');
    const searchResults = document.getElementById('search-results');

    searchInput.addEventListener('input', async () => {
        const query = searchInput.value;
        
        if (query.trim() === '') {
            searchResults.innerHTML = '';
            searchResults.classList.add('d-none');  
            return;
        }

        try {
            const response = await fetch(`/search_users/?query=${query}`);
            const users = await response.json();

            if (users.length > 0) {
                searchResults.innerHTML = users.map(user => `
                    <div class="card mb-2">
                        <div class="card-body">
                            <a href="#" data-user-id="${user.id}" class="card-link">${user.username}</a>
                        </div>
                    </div>
                `).join('');

                searchResults.classList.remove('d-none');  
            } else {
                searchResults.innerHTML = '<p class="text-muted">No users found.</p>';
                searchResults.classList.remove('d-none');  
            }
        } catch (error) {
            console.error("Error fetching search results:", error);
            searchResults.innerHTML = '<p class="text-danger">An error occurred while searching. Please try again.</p>';
            searchResults.classList.remove('d-none');  
        }
    });

    searchResults.addEventListener('click', event => {
        if (event.target.tagName === 'A') {
            const userId = event.target.getAttribute('data-user-id');
            window.location.href = `/start_chat/${userId}/`;
        }
    });
});

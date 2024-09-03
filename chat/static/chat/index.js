document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('search');
    const searchResults = document.getElementById('search-results');

    searchInput.addEventListener('input', async () => {
        const query = searchInput.value;
        
        // Check if the query is empty
        if (query.trim() === '') {
            searchResults.innerHTML = '';
            searchResults.classList.add('d-none');  // Hide search results if query is empty
            return;
        }

        try {
            // Fetch users matching the search query
            const response = await fetch(`/search_users/?query=${query}`);
            const users = await response.json();

            // If users are found, display them; otherwise, hide the results
            if (users.length > 0) {
                searchResults.innerHTML = users.map(user => `
                    <div class="card mb-2">
                        <div class="card-body">
                            <a href="#" data-user-id="${user.id}" class="card-link">${user.username}</a>
                        </div>
                    </div>
                `).join('');

                searchResults.classList.remove('d-none');  // Show search results
            } else {
                searchResults.innerHTML = '<p class="text-muted">No users found.</p>';
                searchResults.classList.remove('d-none');  // Show message if no users are found
            }
        } catch (error) {
            console.error("Error fetching search results:", error);
            searchResults.innerHTML = '<p class="text-danger">An error occurred while searching. Please try again.</p>';
            searchResults.classList.remove('d-none');  // Show error message
        }
    });

    // Handle clicks on search results to start a chat
    searchResults.addEventListener('click', event => {
        if (event.target.tagName === 'A') {
            const userId = event.target.getAttribute('data-user-id');
            window.location.href = `/start_chat/${userId}/`;
        }
    });
});

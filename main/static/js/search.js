document.addEventListener('DOMContentLoaded', function() {

    const searchInput = document.getElementById('search-input');
    const suggestionsBox = document.getElementById('suggestions');
    let desktopAbortController = null;

    function highlightMatch(text, query) {
        const lowerText = text.toLowerCase();
        const lowerQuery = query.toLowerCase();
        const startIndex = lowerText.indexOf(lowerQuery);
        if (startIndex === -1) {
            return text;
        }
        const before = text.substring(0, startIndex);
        const match = text.substring(startIndex, startIndex + query.length);
        const after = text.substring(startIndex + query.length);
        return `${before}<span class="font-semibold text-indigo-600">${match}</span>${after}`;
    }

    if (searchInput && suggestionsBox && typeof AUTOCOMPLETE_URL !== 'undefined') {
        searchInput.addEventListener('input', function() {
            const query = this.value.trim();

            if (desktopAbortController) {
                desktopAbortController.abort();
            }
            desktopAbortController = new AbortController();
            const signal = desktopAbortController.signal;

            if (query.length > 0) {
                const url = `${AUTOCOMPLETE_URL}?q=${encodeURIComponent(query)}`;

                fetch(url, { signal }) 
                    .then(response => {
                        if (signal.aborted) { 
                            throw new DOMException('Aborted', 'AbortError');
                        }
                        if (!response.ok) {
                            throw new Error('Network response was not ok');
                        }
                        return response.json();
                    })
                    .then(data => {
                        suggestionsBox.innerHTML = '';

                        if (data.length > 0) {
                            data.forEach(item => {
                                const div = document.createElement('div');
                                div.className = 'px-4 py-3 text-sm text-gray-700 border-b border-gray-100 hover:bg-indigo-50 hover:text-indigo-700 cursor-pointer transition-colors duration-150 ease-in-out';
                                div.innerHTML = highlightMatch(item.name, query);
                                div.onclick = () => {
                                    window.location.href = item.url;
                                };
                                suggestionsBox.appendChild(div);
                            });
                            if (suggestionsBox.lastChild) {
                                suggestionsBox.lastChild.classList.remove('border-b', 'border-gray-100');
                            }
                            suggestionsBox.classList.remove('hidden');
                        } else {
                            const noResultsDiv = document.createElement('div');
                            noResultsDiv.className = 'px-4 py-3 text-sm text-gray-500';
                            noResultsDiv.textContent = 'Схоже, нічого не знайдено...';
                            suggestionsBox.appendChild(noResultsDiv);
                            suggestionsBox.classList.remove('hidden');
                        }
                    })
                    .catch(error => {
                        if (error.name === 'AbortError') {
                            console.log('Fetch aborted for desktop');
                        } else {
                            console.error('Error fetching autocomplete suggestions:', error);
                            suggestionsBox.innerHTML = ''; 
                            suggestionsBox.classList.add('hidden');
                        }
                    });
            } else {
                suggestionsBox.innerHTML = ''; 
                suggestionsBox.classList.add('hidden');
                if (desktopAbortController) { 
                    desktopAbortController.abort();
                    desktopAbortController = null;
                }
            }
        });

        document.addEventListener('click', function(event) {
            if (!searchInput.contains(event.target) && !suggestionsBox.contains(event.target)) {
                suggestionsBox.classList.add('hidden');
            }
        });

    } else {
    }

    // Логіка для мобільного пошуку 
    const mobileSearchInput = document.getElementById('mobile-search-input');
    const mobileSuggestionsBox = document.getElementById('mobile-suggestions');
    let mobileAbortController = null;

    if (mobileSearchInput && mobileSuggestionsBox && typeof AUTOCOMPLETE_URL !== 'undefined') {
        mobileSearchInput.addEventListener('input', function() {
            const query = this.value.trim();

            if (mobileAbortController) {
                mobileAbortController.abort();
            }
            mobileAbortController = new AbortController();
            const signal = mobileAbortController.signal;
            
            if (query.length > 0) {
                const url = `${AUTOCOMPLETE_URL}?q=${encodeURIComponent(query)}`;
                fetch(url, { signal })
                    .then(response => {
                        if (signal.aborted) {
                             throw new DOMException('Aborted', 'AbortError');
                        }
                        if (!response.ok) {
                            throw new Error('Network response was not ok for mobile');
                        }
                        return response.json();
                    })
                    .then(data => {
                        mobileSuggestionsBox.innerHTML = '';
                        if (data.length > 0) {
                            data.forEach(item => {
                                const div = document.createElement('div');
                                div.className = 'px-4 py-3 text-sm text-gray-700 border-b border-gray-100 hover:bg-indigo-50 hover:text-indigo-700 cursor-pointer transition-colors duration-150 ease-in-out';
                                div.innerHTML = highlightMatch(item.name, query);
                                div.onclick = () => {
                                    window.location.href = item.url;
                                };
                                mobileSuggestionsBox.appendChild(div);
                            });
                            if (mobileSuggestionsBox.lastChild) {
                                mobileSuggestionsBox.lastChild.classList.remove('border-b', 'border-gray-100');
                            }
                            mobileSuggestionsBox.classList.remove('hidden');
                        } else {
                            const noResultsDiv = document.createElement('div');
                            noResultsDiv.className = 'px-4 py-3 text-sm text-gray-500';
                            noResultsDiv.textContent = 'Схоже, нічого не знайдено...';
                            mobileSuggestionsBox.appendChild(noResultsDiv);
                            mobileSuggestionsBox.classList.remove('hidden');
                        }
                    })
                    .catch(error => {
                        if (error.name === 'AbortError') {
                            console.log('Fetch aborted for mobile');
                        } else {
                            console.error('Error fetching mobile autocomplete suggestions:', error);
                            mobileSuggestionsBox.innerHTML = '';
                            mobileSuggestionsBox.classList.add('hidden');
                        }
                    });
            } else {
                mobileSuggestionsBox.innerHTML = '';
                mobileSuggestionsBox.classList.add('hidden');
                if (mobileAbortController) {
                    mobileAbortController.abort();
                    mobileAbortController = null;
                }
            }
        });

        document.addEventListener('click', function(event) {
            if (mobileSuggestionsBox && !mobileSearchInput.contains(event.target) && !mobileSuggestionsBox.contains(event.target)) {
                 mobileSuggestionsBox.classList.add('hidden');
            }
        });
    }
});
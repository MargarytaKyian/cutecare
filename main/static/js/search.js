document.addEventListener('DOMContentLoaded', () => {
    const input = document.getElementById('search-input');
    const suggBox = document.getElementById('suggestions');
    const url = AUTOCOMPLETE_URL;
    let timer = null;
  
    input.addEventListener('input', () => {
      const term = input.value.trim();
      clearTimeout(timer);
      if (term.length < 2) {
        suggBox.innerHTML = '';
        return;
      }
      timer = setTimeout(() => {
        fetch(`${url}?q=${encodeURIComponent(term)}`)
          .then(resp => {
            if (!resp.ok) throw new Error(resp.statusText);
            return resp.json();
          })
          .then(data => {
            console.log('autocomplete:', term, data);
            suggBox.innerHTML = data.length
              ? data.map(item =>
                  `<a href="${item.url}"
                      class="list-group-item list-group-item-action">
                     ${item.name}
                   </a>`
                ).join('')
              : `<div class="list-group-item">Нічого не знайдено</div>`;
          })
          .catch(err => {
            console.error('Autocomplete error:', err);
            suggBox.innerHTML = '';
          });
      }, 300);
    });
  
    document.addEventListener('click', e => {
      if (!input.contains(e.target) && !suggBox.contains(e.target)) {
        suggBox.innerHTML = '';
      }
    });
  });
  
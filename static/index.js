
const playlistList = document.getElementById('playlist-list');
const playlistData = JSON.parse('{{ playlist | tojson }}');

// Create list items and add them to the playlist
playlistData.tracks.forEach((track, index) => {
  const listItem = document.createElement('li');
  listItem.textContent = track;

  // Add the number before the song link
  const number = document.createElement('span');
  number.textContent = `${index + 1}. `;
  listItem.prepend(number);

  playlistList.appendChild(listItem);
});

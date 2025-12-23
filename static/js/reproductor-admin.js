document.addEventListener('DOMContentLoaded', function() {
    // Estas variables se obtienen del objeto CONFIG definido en el HTML (admin_players.html)
    const defaultImageUrl = CONFIG.defaultImageUrl;
    const songsData = CONFIG.songsData;
    const currentSongId = CONFIG.currentSongId;
    const audioPlayer = document.getElementById('audio-player');
    const sedeId = CONFIG.sedeId;

    if (!audioPlayer || !songsData || songsData.length === 0) {
        console.log("Player o canciones no encontradas. Saliendo.");
        return;
    }

    // Encuentra el índice de la canción actual
    let currentSongIndex = 0;
    if (currentSongId !== null) {
        const initialIndex = songsData.findIndex(song => song.id == currentSongId);
        if (initialIndex !== -1) {
            currentSongIndex = initialIndex;
        }
    }

    const playPauseBtn = document.getElementById('play-pause-btn');
    const playIcon = document.getElementById('play-icon');
    const pauseIcon = document.getElementById('pause-icon');
    const nextBtn = document.getElementById('next-btn');
    const prevBtn = document.getElementById('prev-btn');
    const progressBarContainer = document.getElementById('progress-bar-container');
    const progressBarFill = progressBarContainer ? progressBarContainer.querySelector('#progress-bar-fill') : null;
    const currentTimeEl = document.getElementById('current-time');
    const durationEl = document.getElementById('duration');
    const volumeBar = document.getElementById('volume-bar');

    // Elementos de la UI que se actualizan
    const ui = {
        currentSongImage: document.getElementById('current-song-image'),
        currentSongTitle: document.getElementById('current-song-title'),
        currentSongArtist: document.getElementById('current-song-artist'),
        playerImage: document.getElementById('player-image'),
        playerTitle: document.getElementById('player-title'),
        playerArtist: document.getElementById('player-artist')
    };

    function loadSong(songIndex, shouldPlay = true) {
        const song = songsData[songIndex];
        const imageUrl = song.imagen ? song.imagen : defaultImageUrl;
        
        audioPlayer.src = song.audio;
        try { 
            audioPlayer.load(); 
        } catch (e) { 
            console.warn('audio.load() failed', e); 
        }

        // Actualizar UI principal
        if (ui.currentSongImage) ui.currentSongImage.src = imageUrl;
        if (ui.currentSongTitle) ui.currentSongTitle.textContent = song.titulo;
        if (ui.currentSongArtist) ui.currentSongArtist.textContent = song.artista;

        // Actualizar UI del reproductor inferior
        if (ui.playerImage) ui.playerImage.src = imageUrl;
        if (ui.playerTitle) ui.playerTitle.textContent = song.titulo;
        if (ui.playerArtist) ui.playerArtist.textContent = song.artista;

        currentSongIndex = songIndex;
        
        if (shouldPlay) {
            audioPlayer.play().catch(e => console.error("Error playing song:", e));
        }
    }

    function formatTime(seconds) {
        if (!seconds || isNaN(seconds)) return "0:00";
        const minutes = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${minutes}:${secs < 10 ? '0' : ''}${secs}`;
    }

    // --- Event Listeners ---
    if (nextBtn) {
        nextBtn.addEventListener('click', () => {
            currentSongIndex = (currentSongIndex + 1) % songsData.length;
            loadSong(currentSongIndex);
        });
    }

    if (prevBtn) {
        prevBtn.addEventListener('click', () => {
            currentSongIndex = (currentSongIndex - 1 + songsData.length) % songsData.length;
            loadSong(currentSongIndex);
        });
    }

    audioPlayer.addEventListener('timeupdate', () => {
        const { currentTime, duration } = audioPlayer;
        if (duration) {
            const progressPercent = (currentTime / duration) * 100;
            if (progressBarFill) progressBarFill.style.width = `${progressPercent}%`;
            if (durationEl) durationEl.textContent = formatTime(duration);
        }
        if (currentTimeEl) currentTimeEl.textContent = formatTime(currentTime);
    });

    if (progressBarContainer) {
        progressBarContainer.addEventListener('click', (e) => {
            const width = progressBarContainer.clientWidth;
            const clickX = e.offsetX;
            const duration = audioPlayer.duration;
            if (duration) {
                audioPlayer.currentTime = (clickX / width) * duration;
            }
        });
    }

    if (volumeBar) {
        volumeBar.addEventListener('input', (e) => {
            audioPlayer.volume = e.target.value / 100;
        });
    }

    audioPlayer.addEventListener('ended', () => {
        if (nextBtn) nextBtn.click();
    });

    // --- Clic en la lista de reproducción ---
    document.querySelectorAll('.playlist-item').forEach(item => {
        item.addEventListener('click', function() {
            const songId = this.dataset.songId;
            const songIndex = songsData.findIndex(song => song.id == songId);
            if (songIndex !== -1) {
                loadSong(songIndex);
            }
        });
    });

    // --- Comunicación con el Servidor (Status) ---
    function updateSedeStatus(url, data) {
        if (sedeId === null) return;
        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': CONFIG.csrfToken,
            },
            body: JSON.stringify(data),
        })
        .catch(err => console.error('Admin Player Status Error:', err));
    }

    audioPlayer.addEventListener('play', () => {
        if (sedeId !== null) {
            const activeSong = songsData[currentSongIndex];
            if (activeSong) {
                updateSedeStatus(CONFIG.playSignalUrl, { 
                    sede_id: sedeId, 
                    song_id: activeSong.id 
                });
            }
        }
    });

    audioPlayer.addEventListener('pause', () => {
        if (sedeId !== null) {
            updateSedeStatus(CONFIG.stopSignalUrl, { sede_id: sedeId });
        }
    });

    // Heartbeat cada 30 segundos
    setInterval(() => {
        if (!audioPlayer.paused && sedeId !== null) {
            const activeSong = songsData[currentSongIndex];
            if (activeSong) {
                updateSedeStatus(CONFIG.playSignalUrl, { 
                    sede_id: sedeId, 
                    song_id: activeSong.id 
                });
            }
        }
    }, 30000);

    // Backup: desactivar al cerrar pestaña
    window.addEventListener('beforeunload', () => {
        if (sedeId !== null && !audioPlayer.paused) {
             const data = { sede_id: sedeId };
             const blob = new Blob([JSON.stringify(data)], { type: 'application/json' });
             navigator.sendBeacon(CONFIG.stopSignalUrl, blob);
        }
    });

    // Carga inicial
    loadSong(currentSongIndex, false);
});
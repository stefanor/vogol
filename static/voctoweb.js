'use strict';

const updateIntervals = [];

function startup() {
    const previews = document.getElementsByClassName('preview');
    for (const preview of previews) {
        updateIntervals.push(setInterval(updatePreview, 2000, preview));
        setTimeout(updatePreview, 0, preview);
    }

    const buttons = document.getElementsByTagName('button');
    for (const button of buttons) {
        button.onclick = actionButton;
    }
    updateIntervals.push(setInterval(updateState, 5000));
    setTimeout(updateState, 0);
}

function updatePreview(img) {
    const source = img.dataset.source;
    const url = '/preview/' + source;
    fetch(url, {
        credentials: 'same-origin',
    }).then(checkResponse)
    .then(response => response.blob())
    .then(response => {
        if (response) {
            const objectURL = URL.createObjectURL(response);
            img.src = objectURL;
            updateTimestamp();
        }
    }).catch(error => {
        // FIXME
        //console.error('Failed to fetch', source);
        //img.src = URL.createObjectURL('');
    });
}

function updateTimestamp() {
    const last_updated = document.getElementById('last-update');
    last_updated.innerHTML = new Date();
}

function checkResponse(response) {
    if (response.status == 403) {
        showLoginDialog();
    }
    if (!response.ok) {
        throw new Error('Failed to get ' + response.url);
    }
    return response;
}

// We're not logged in:
function showLoginDialog() {
    // Stop hitting the server
    while(updateIntervals.length > 0) {
        const interval = updateIntervals.shift();
        clearInterval(interval);
    }
    $('#login-modal').modal();
}

// Handle an action click
function actionButton(event) {
    const button = event.target;
    fetch('/action', {
        credentials: 'same-origin',
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(button.dataset),
    }).then(checkResponse)
    .then(response => response.json())
    .then(receivedState);
}

// Request state from Voctomix
function updateState() {
    fetch('/state', {
        credentials: 'same-origin',
        method: 'GET',
    }).then(checkResponse)
    .then(response => response.json())
    .then(receivedState);
}

// Received state from Voctomix
function receivedState(state) {
    setCurrentVideo(state.video_a, 'a');
    setCurrentVideo(state.video_b, 'b');
    setCompositeMode(state.composite_mode);
    setStreamStatus(state.stream_status);
    setAudioStatus(state.audio);
}

// Put the A / B label on the right source
function setCurrentVideo(source, slot) {
    const tag = document.getElementById('video-' + slot);
    if (tag) {
        if (tag.dataset.source == source) {
            return;
        } else {
            tag.remove();
        }
    }
    const parent = document.getElementById('header-' + source);
    const badge = document.createElement('div');
    badge.id = 'video-' + slot;
    if (slot == 'a') {
        badge.className = 'selected-source badge badge-warning';
    } else {
        badge.className = 'selected-source badge badge-info';
    }
    badge.dataset.source = source;
    badge.appendChild(document.createTextNode(slot.toUpperCase()));
    parent.appendChild(badge);
}

function setCompositeMode(mode) {
    const composite_mode = document.getElementById('composite-mode');
    if (mode == 'fullscreen') {
        composite_mode.innerHTML = 'Full Screen';
    } else if (mode == 'side_by_side_equal') {
        composite_mode.innerHTML = 'Side by Side';
    } else if (mode == 'side_by_side_preview') {
        composite_mode.innerHTML = 'Side by Side Preview';
    } else if (mode == 'picture_in_picture') {
        composite_mode.innerHTML = 'Picture in Picture';
    }
}

function setStreamStatus(status) {
    const stream_status = document.getElementById('stream-status');
    if (status == 'live') {
        stream_status.className = 'badge badge-success';
    } else {
        stream_status.className = 'badge badge-danger';
    }
    stream_status.innerHTML = status;
}

function setAudioStatus(status) {
    for (const source in status) {
        const volume = status[source];
        const element = document.getElementById('audio-' + source);
        const intVolume = Math.trunc(volume * 100) + '%';
        if (volume > 0.2) {
            element.className = 'badge badge-success';
            element.innerHTML = '🔊 ' + intVolume;
        } else {
            element.className = 'badge badge-danger';
            element.innerHTML = '🔇 ' + intVolume;
        }
    }
}

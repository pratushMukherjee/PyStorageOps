// CloudForge Dashboard — Frontend Application
const API = window.location.origin.replace(':3000', ':8080');
const AI_API = window.location.origin.replace(':3000', ':8081');

let selectedAppId = null;

// --- API Helpers ---
async function api(method, path, body = null) {
    const opts = { method, headers: { 'Content-Type': 'application/json' } };
    if (body) opts.body = JSON.stringify(body);
    const res = await fetch(`${API}${path}`, opts);
    if (res.status === 204) return null;
    return res.json();
}

// --- Apps ---
async function loadApps() {
    const data = await api('GET', '/api/v1/apps');
    const list = document.getElementById('apps-list');
    list.innerHTML = '';

    (data.apps || []).forEach(app => {
        const el = document.createElement('div');
        el.className = `list-item${app.id === selectedAppId ? ' active' : ''}`;
        el.innerHTML = `
            <div class="name">${app.name}</div>
            <div class="meta">
                <span class="status status-${app.status}">${app.status}</span>
                &middot; ${app.language}
            </div>`;
        el.onclick = () => selectApp(app.id);
        list.appendChild(el);
    });
}

async function selectApp(id) {
    selectedAppId = id;
    document.getElementById('deploy-btn').disabled = false;
    document.getElementById('rollback-btn').disabled = false;
    document.getElementById('delete-btn').disabled = false;

    const data = await api('GET', `/api/v1/apps/${id}`);
    const app = data.app;
    document.getElementById('detail-title').textContent = app.name;
    document.getElementById('app-info').innerHTML = `
        <span class="label">Status</span><span class="status status-${app.status}">${app.status}</span>
        <span class="label">Language</span><span>${app.language}</span>
        <span class="label">Port</span><span>${app.port || 'auto'}</span>
        <span class="label">ID</span><span>${app.id.slice(0, 8)}...</span>`;

    loadDeployments(id);
    loadLogs(id);
    loadApps();
}

// --- Deployments ---
async function loadDeployments(appId) {
    const data = await api('GET', `/api/v1/apps/${appId}/deployments`);
    const list = document.getElementById('deployments-list');
    list.innerHTML = '';

    (data.deployments || []).forEach(dep => {
        const el = document.createElement('div');
        el.className = 'list-item';
        el.innerHTML = `
            <div class="name">v${dep.version} <span class="status status-${dep.status}">${dep.status}</span></div>
            <div class="meta">${dep.image} &middot; ${new Date(dep.created_at).toLocaleString()}</div>`;
        list.appendChild(el);
    });
}

// --- Logs ---
async function loadLogs(appId) {
    const data = await api('GET', `/api/v1/apps/${appId}/logs?limit=20`);
    const container = document.getElementById('logs-container');
    container.innerHTML = '';

    (data.logs || []).forEach(log => {
        const el = document.createElement('div');
        el.className = `log-entry log-${log.level}`;
        el.textContent = `[${log.timestamp}] [${log.level.toUpperCase()}] ${log.message}`;
        container.appendChild(el);
    });
}

// --- Create App ---
document.getElementById('create-app-btn').onclick = () => {
    document.getElementById('create-modal').classList.remove('hidden');
};
document.getElementById('cancel-modal').onclick = () => {
    document.getElementById('create-modal').classList.add('hidden');
};
document.getElementById('create-form').onsubmit = async (e) => {
    e.preventDefault();
    const name = document.getElementById('app-name').value;
    const language = document.getElementById('app-language').value;
    await api('POST', '/api/v1/apps', { name, language });
    document.getElementById('create-modal').classList.add('hidden');
    document.getElementById('app-name').value = '';
    loadApps();
};

// --- Deploy / Rollback / Delete ---
document.getElementById('deploy-btn').onclick = async () => {
    if (!selectedAppId) return;
    await api('POST', `/api/v1/apps/${selectedAppId}/deploy`);
    setTimeout(() => selectApp(selectedAppId), 2000);
};
document.getElementById('rollback-btn').onclick = async () => {
    if (!selectedAppId) return;
    await api('POST', `/api/v1/apps/${selectedAppId}/rollback`);
    selectApp(selectedAppId);
};
document.getElementById('delete-btn').onclick = async () => {
    if (!selectedAppId) return;
    await api('DELETE', `/api/v1/apps/${selectedAppId}`);
    selectedAppId = null;
    document.getElementById('detail-title').textContent = 'Select an app';
    document.getElementById('app-info').innerHTML = '';
    document.getElementById('deployments-list').innerHTML = '';
    document.getElementById('logs-container').innerHTML = '';
    document.getElementById('deploy-btn').disabled = true;
    document.getElementById('rollback-btn').disabled = true;
    document.getElementById('delete-btn').disabled = true;
    loadApps();
};

// --- AI Chat ---
document.getElementById('chat-send').onclick = sendChat;
document.getElementById('chat-input').onkeydown = (e) => { if (e.key === 'Enter') sendChat(); };

async function sendChat() {
    const input = document.getElementById('chat-input');
    const msg = input.value.trim();
    if (!msg) return;
    input.value = '';

    addChatMessage(msg, 'user');

    try {
        const res = await fetch(`${AI_API}/api/v1/ai/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: msg }),
        });
        const data = await res.json();
        addChatMessage(data.reply, 'ai');
    } catch {
        addChatMessage('AI service unavailable. Check that the AI service is running on port 8081.', 'ai');
    }
}

function addChatMessage(text, role) {
    const container = document.getElementById('chat-messages');
    const el = document.createElement('div');
    el.className = `chat-msg chat-${role}`;
    el.textContent = text;
    container.appendChild(el);
    container.scrollTop = container.scrollHeight;
}

// --- Init ---
loadApps();
addChatMessage('Welcome! I can help you deploy apps, diagnose errors, and optimize your configurations.', 'ai');

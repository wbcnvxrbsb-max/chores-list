// API Client for Chores App

const api = {
    // Auth
    async pinExists() {
        const res = await fetch('/api/auth/pin-exists');
        return res.json();
    },

    async verifyPin(pin) {
        const res = await fetch('/api/auth/verify-pin', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ pin })
        });
        return { ok: res.ok, data: await res.json() };
    },

    async setPin(pin, currentPin = null) {
        const body = { pin };
        if (currentPin) body.current_pin = currentPin;

        const res = await fetch('/api/auth/set-pin', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body)
        });
        return { ok: res.ok, data: await res.json() };
    },

    // Children
    async getChildren() {
        const res = await fetch('/api/children');
        return res.json();
    },

    async createChild(name) {
        const res = await fetch('/api/children', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name })
        });
        return res.json();
    },

    async updateChild(id, data) {
        const res = await fetch(`/api/children/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        return res.json();
    },

    async deleteChild(id) {
        const res = await fetch(`/api/children/${id}`, {
            method: 'DELETE'
        });
        return res.json();
    },

    // Chores
    async getChores(childId) {
        const res = await fetch(`/api/children/${childId}/chores`);
        return res.json();
    },

    async createChore(childId, title, frequency = 'daily') {
        const res = await fetch(`/api/children/${childId}/chores`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title, frequency })
        });
        return res.json();
    },

    async updateChore(choreId, data) {
        const res = await fetch(`/api/chores/${choreId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        return res.json();
    },

    async deleteChore(choreId) {
        const res = await fetch(`/api/chores/${choreId}`, {
            method: 'DELETE'
        });
        return res.json();
    },

    async completeChore(choreId) {
        const res = await fetch(`/api/chores/${choreId}/complete`, {
            method: 'POST'
        });
        return res.json();
    },

    async uncompleteChore(choreId) {
        const res = await fetch(`/api/chores/${choreId}/complete`, {
            method: 'DELETE'
        });
        return res.json();
    },

    // History
    async getHistory(days = 7, childId = null) {
        let url = `/api/history?days=${days}`;
        if (childId) url += `&child_id=${childId}`;
        const res = await fetch(url);
        return res.json();
    }
};

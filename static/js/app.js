// Main Chores App

function choresApp() {
    return {
        // View state
        currentView: 'home',
        parentTab: 'children',

        // Data
        children: [],
        chores: [],
        selectedChild: null,
        editingChild: null,
        editingChildChores: [],
        report: [],
        reportDays: 7,

        // Auth state
        isAuthenticated: false,
        needsSetup: false,
        showPinModal: false,
        pinInput: '',
        pinError: '',

        // Prompt modal
        showPrompt: false,
        promptTitle: '',
        promptValue: '',
        promptResolve: null,

        // Confirm modal
        showConfirm: false,
        confirmTitle: '',
        confirmMessage: '',
        confirmResolve: null,

        // Add chore modal
        showAddChore: false,
        newChoreTitle: '',
        newChoreFrequency: '',

        // Settings
        currentPin: '',
        newPin: '',

        async init() {
            // Check if PIN needs to be set up
            const { exists } = await api.pinExists();
            this.needsSetup = !exists;

            // Load children
            await this.loadChildren();
        },

        async loadChildren() {
            this.children = await api.getChildren();
        },

        // Navigation
        goHome() {
            this.currentView = 'home';
            this.selectedChild = null;
            this.chores = [];
            this.isAuthenticated = false;
            this.loadChildren();
        },

        async selectChild(child) {
            this.selectedChild = child;
            this.chores = await api.getChores(child.id);
            this.currentView = 'child';
        },

        // Filter chores by frequency for grouped display
        choresByFrequency(frequency) {
            return this.chores.filter(c => (c.frequency || 'daily') === frequency);
        },

        // Chore completion (kid view)
        async toggleChore(chore) {
            if (chore.completed) {
                // Can't un-complete from kid view
                return;
            }

            const result = await api.completeChore(chore.id);
            if (result.success) {
                chore.completed = true;
                chore.completed_at = result.completed_at;
            }
        },

        // PIN handling
        async enterPin(digit) {
            if (this.pinInput.length >= 4) return;

            this.pinInput += digit;
            this.pinError = '';

            if (this.pinInput.length === 4) {
                if (this.needsSetup) {
                    // Setting up new PIN
                    const result = await api.setPin(this.pinInput);
                    if (result.ok) {
                        this.needsSetup = false;
                        this.isAuthenticated = true;
                        this.showPinModal = false;
                        this.pinInput = '';
                        this.currentView = 'parent';
                    } else {
                        this.pinError = result.data.error || 'Failed to set PIN';
                        this.pinInput = '';
                    }
                } else {
                    // Verifying PIN
                    const result = await api.verifyPin(this.pinInput);
                    if (result.ok && result.data.valid) {
                        this.isAuthenticated = true;
                        this.showPinModal = false;
                        this.pinInput = '';
                        this.currentView = 'parent';
                    } else {
                        this.pinError = 'Incorrect PIN';
                        this.pinInput = '';
                    }
                }
            }
        },

        logout() {
            this.isAuthenticated = false;
            this.goHome();
        },

        // Prompt helper
        prompt(title, defaultValue = '') {
            return new Promise((resolve) => {
                this.promptTitle = title;
                this.promptValue = defaultValue;
                this.promptResolve = resolve;
                this.showPrompt = true;

                // Focus input after render
                this.$nextTick(() => {
                    this.$refs.promptInput?.focus();
                    this.$refs.promptInput?.select();
                });
            });
        },

        confirmPrompt() {
            if (this.promptResolve) {
                this.promptResolve(this.promptValue);
            }
            this.showPrompt = false;
            this.promptValue = '';
            this.promptResolve = null;
        },

        cancelPrompt() {
            if (this.promptResolve) {
                this.promptResolve(null);
            }
            this.showPrompt = false;
            this.promptValue = '';
            this.promptResolve = null;
        },

        // Confirm helper
        confirm(title, message) {
            return new Promise((resolve) => {
                this.confirmTitle = title;
                this.confirmMessage = message;
                this.confirmResolve = resolve;
                this.showConfirm = true;
            });
        },

        doConfirm() {
            if (this.confirmResolve) {
                this.confirmResolve(true);
            }
            this.showConfirm = false;
            this.confirmResolve = null;
        },

        cancelConfirm() {
            if (this.confirmResolve) {
                this.confirmResolve(false);
            }
            this.showConfirm = false;
            this.confirmResolve = null;
        },

        // Child management
        async renameChild(child) {
            const name = await this.prompt('Enter new name', child.name);
            if (name && name.trim() && name !== child.name) {
                await api.updateChild(child.id, { name: name.trim() });
                await this.loadChildren();
            }
        },

        // Chore management
        async editChildChores(child) {
            this.editingChild = child;
            this.editingChildChores = await api.getChores(child.id);
        },

        // Add chore modal handlers
        addChore() {
            this.newChoreTitle = '';
            this.newChoreFrequency = '';
            this.showAddChore = true;
            this.$nextTick(() => {
                this.$refs.choreInput?.focus();
            });
        },

        cancelAddChore() {
            this.showAddChore = false;
            this.newChoreTitle = '';
            this.newChoreFrequency = '';
        },

        async confirmAddChore() {
            if (!this.newChoreTitle.trim() || !this.newChoreFrequency) {
                return;
            }

            await api.createChore(this.editingChild.id, this.newChoreTitle.trim(), this.newChoreFrequency);
            this.editingChildChores = await api.getChores(this.editingChild.id);
            this.showAddChore = false;
            this.newChoreTitle = '';
            this.newChoreFrequency = '';
        },

        async renameChore(chore) {
            const title = await this.prompt('Enter new name', chore.title);
            if (title && title.trim() && title !== chore.title) {
                await api.updateChore(chore.id, { title: title.trim() });
                this.editingChildChores = await api.getChores(this.editingChild.id);
            }
        },

        async deleteChore(chore) {
            const confirmed = await this.confirm(
                'Delete this chore?',
                'The chore "' + chore.title + '" will be removed.'
            );
            if (confirmed) {
                await api.deleteChore(chore.id);
                this.editingChildChores = await api.getChores(this.editingChild.id);
            }
        },

        // Report (formerly History)
        async loadReport() {
            const result = await api.getHistory(this.reportDays);
            this.report = result.history || [];
        },

        // For backwards compatibility with HTML that uses 'history'
        get history() {
            return this.report;
        },

        get historyDays() {
            return this.reportDays;
        },

        set historyDays(value) {
            this.reportDays = value;
        },

        // Settings
        async changePin() {
            if (!this.currentPin || !this.newPin) {
                alert('Please enter both current and new PIN');
                return;
            }
            if (this.newPin.length < 4) {
                alert('New PIN must be at least 4 digits');
                return;
            }

            const result = await api.setPin(this.newPin, this.currentPin);
            if (result.ok) {
                alert('PIN updated successfully');
                this.currentPin = '';
                this.newPin = '';
            } else {
                alert(result.data.error || 'Failed to update PIN');
            }
        },

        // Formatting helpers
        formatDate(dateStr) {
            const date = new Date(dateStr + 'T00:00:00');
            const today = new Date();
            today.setHours(0, 0, 0, 0);

            const yesterday = new Date(today);
            yesterday.setDate(yesterday.getDate() - 1);

            if (date.getTime() === today.getTime()) {
                return 'Today';
            } else if (date.getTime() === yesterday.getTime()) {
                return 'Yesterday';
            } else {
                return date.toLocaleDateString('en-US', {
                    weekday: 'long',
                    month: 'short',
                    day: 'numeric'
                });
            }
        },

        formatTime(timestamp) {
            if (!timestamp) return '';
            const date = new Date(timestamp);
            return date.toLocaleTimeString('en-US', {
                hour: 'numeric',
                minute: '2-digit'
            });
        },

        formatFrequency(freq) {
            const labels = {
                'daily': 'Daily',
                'weekly': 'Weekly',
                'monthly': 'Monthly',
                'oneoff': 'One-off'
            };
            return labels[freq] || freq || 'Daily';
        }
    };
}

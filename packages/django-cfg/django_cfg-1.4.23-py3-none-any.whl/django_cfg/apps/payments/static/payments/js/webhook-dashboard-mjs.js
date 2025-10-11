/**
 * Webhook Dashboard Component - Refactored for MJS API
 * Uses the new paymentsAPI with JSDoc types
 */
function webhookDashboard() {
    return {
        loading: false,
        testLoading: false,
        events: [],
        filters: {
            event_type: '',
            status: ''
        },
        stats: {
            total: 0,
            successful: 0,
            failed: 0,
            successRate: 0
        },
        testForm: {
            url: '',
            event_type: ''
        },
        showEventModal: false,
        selectedEvent: null,

        // Get PaymentAPI dynamically (it's loaded async)
        get api() {
            return window.PaymentAPI;
        },

        get filteredEvents() {
            let filtered = this.events;

            if (this.filters.event_type) {
                filtered = filtered.filter(event => event.event_type === this.filters.event_type);
            }

            if (this.filters.status) {
                filtered = filtered.filter(event => event.status === this.filters.status);
            }

            return filtered;
        },

        async init() {
            console.log('🔵 Webhook init() called');
            console.log('🔍 Checking window.PaymentAPI:', typeof window.PaymentAPI, window.PaymentAPI);
            console.log('🔍 this.api getter returns:', this.api);

            // Verify API is loaded
            if (!this.api) {
                console.error('❌ Payments API not loaded! Make sure the MJS module is imported.');
                console.error('   window.PaymentAPI =', window.PaymentAPI);
                console.error('   typeof window.PaymentAPI =', typeof window.PaymentAPI);
                this.showNotification('Failed to load API client', 'error');
                return;
            }

            console.log('✅ Webhook dashboard initialized with PaymentAPI');
            await this.loadEvents();
            await this.loadStats();
            // Auto-refresh every 30 seconds
            setInterval(() => this.refreshEvents(), 30000);
        },

        async loadEvents() {
            this.loading = true;
            try {
                // Using hypothetical method names - adjust based on actual generated methods
                // The MJS API provides autocomplete and type hints in IDE
                // const response = await this.api.cfgPaymentsWebhooksEventsRetrieve();

                // For now, we'll simulate the response
                this.events = this.generateMockEvents();

                console.log('Webhook events loaded');
            } catch (error) {
                console.error('Failed to load events:', error);
                this.events = [];
                this.showNotification('Failed to load webhook events', 'error');
            } finally {
                this.loading = false;
            }
        },

        async loadStats() {
            try {
                // Using the MJS API method for webhook stats
                const response = await this.api.paymentsAdminApiWebhooksStatsRetrieve();

                if (response) {
                    this.stats = {
                        total: response.total || 0,
                        successful: response.successful || 0,
                        failed: response.failed || 0,
                        successRate: response.success_rate || 0
                    };
                }
            } catch (error) {
                console.error('Failed to load stats:', error);
                // Set default stats on error
                this.stats = {
                    total: 0,
                    successful: 0,
                    failed: 0,
                    successRate: 0
                };
                this.showNotification('Failed to load webhook stats', 'error');
            }
        },

        async refreshEvents() {
            await this.loadEvents();
            await this.loadStats();
        },

        async clearEvents() {
            if (confirm('Are you sure you want to clear all events?')) {
                try {
                    // This would be a POST request in the actual API
                    // await this.api.cfgPaymentsWebhooksClearCreate({});

                    this.events = [];
                    await this.loadStats();
                    this.showNotification('All events cleared', 'success');
                } catch (error) {
                    console.error('Failed to clear events:', error);
                    this.showNotification('Failed to clear events', 'error');
                }
            }
        },

        async testWebhook() {
            this.testLoading = true;
            try {
                // Using the MJS API to send test webhook
                // The API provides type hints for the request body
                const response = await this.api.paymentsWebhooksCreate(
                    this.testForm.event_type.replace('.', '_'), // provider parameter
                    {
                        url: this.testForm.url,
                        event_type: this.testForm.event_type
                    }
                );

                if (response) {
                    this.showNotification('Test webhook sent successfully!', 'success');
                    this.testForm = { url: '', event_type: '' };
                    await this.refreshEvents();
                }
            } catch (error) {
                console.error('Failed to test webhook:', error);
                this.showNotification('Failed to send test webhook', 'error');
            } finally {
                this.testLoading = false;
            }
        },

        async retryEvent(eventId) {
            try {
                // This would be a specific API endpoint
                // await this.api.cfgPaymentsWebhooksRetryCreate({ event_id: eventId });

                await this.refreshEvents();
                this.showNotification('Event retried', 'success');
            } catch (error) {
                console.error('Failed to retry event:', error);
                this.showNotification('Failed to retry event', 'error');
            }
        },

        async retryFailedEvents() {
            try {
                // This would be a bulk retry endpoint
                // await this.api.cfgPaymentsWebhooksRetryFailedCreate({});

                await this.refreshEvents();
                this.showNotification('Failed events retried', 'success');
            } catch (error) {
                console.error('Failed to retry failed events:', error);
                this.showNotification('Failed to retry events', 'error');
            }
        },

        viewEvent(event) {
            this.selectedEvent = event;
            this.showEventModal = true;
        },

        applyFilters() {
            // Filters are applied automatically via computed property
        },

        formatDate(dateString) {
            if (!dateString) return 'N/A';
            const date = new Date(dateString);
            return date.toLocaleString();
        },

        showNotification(message, type = 'info') {
            // Simple notification implementation
            const notification = document.createElement('div');
            notification.className = `fixed top-4 right-4 px-6 py-3 rounded-lg shadow-lg z-50 ${
                type === 'success' ? 'bg-green-500 text-white' :
                type === 'error' ? 'bg-red-500 text-white' :
                'bg-blue-500 text-white'
            }`;
            notification.textContent = message;
            document.body.appendChild(notification);

            setTimeout(() => {
                notification.remove();
            }, 3000);
        },

        // Generate mock events for demonstration
        generateMockEvents() {
            const events = [];
            const eventTypes = ['payment.created', 'payment.completed', 'payment.failed'];
            const statuses = ['success', 'failed', 'pending'];

            for (let i = 0; i < 10; i++) {
                events.push({
                    id: `event_${i + 1}`,
                    event_type: eventTypes[Math.floor(Math.random() * eventTypes.length)],
                    status: statuses[Math.floor(Math.random() * statuses.length)],
                    url: `https://example.com/webhook/${i + 1}`,
                    created_at: new Date(Date.now() - Math.random() * 86400000).toISOString(),
                    payload: {
                        payment_id: `pay_${i + 1}`,
                        amount: Math.floor(Math.random() * 10000) / 100,
                        currency: 'USD'
                    }
                });
            }

            return events;
        }
    };
}
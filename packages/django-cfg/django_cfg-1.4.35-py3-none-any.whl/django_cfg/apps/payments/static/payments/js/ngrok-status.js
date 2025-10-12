/**
 * Ngrok Status Component
 * Handles ngrok tunnel status monitoring and control
 */
function ngrokStatus() {
    return {
        loading: false,
        status: {
            active: false,
            public_url: '',
            webhook_url: '',
            error: null,
            region: 'us',
            proto: 'https'
        },

        async init() {
            await this.refreshStatus();
            // Don't auto-refresh since endpoint doesn't exist
            // setInterval(() => this.refreshStatus(), 10000);
        },

        async refreshStatus() {
            this.loading = true;
            try {
                // Webhook health endpoint doesn't exist, so just show as inactive
                this.status = {
                    active: false,
                    public_url: '',
                    webhook_url: '',
                    error: 'Ngrok tunnel not active. Run server with: python manage.py runserver_ngrok',
                    region: 'us',
                    proto: 'https'
                };
            } catch (error) {
                console.error('Failed to fetch ngrok status:', error);
                this.status.active = false;
                this.status.error = error.message || 'Connection failed';
            } finally {
                this.loading = false;
            }
        },

        copyUrl() {
            if (this.status.public_url) {
                PaymentAPI.utils.copyToClipboard(this.status.public_url);
            }
        },

        copyWebhookUrl() {
            if (this.status.webhook_url) {
                PaymentAPI.utils.copyToClipboard(this.status.webhook_url);
            }
        },

        openTunnel() {
            if (this.status.public_url) {
                window.open(this.status.public_url, '_blank');
            }
        }
    };
}

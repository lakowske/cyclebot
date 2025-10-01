/**
 * Main application logic for WebSocket and JSON-RPC communication
 */

class App {
    constructor() {
        this.ws = null;
        this.chatLog = document.getElementById('chatLog');
        this.promptInput = document.getElementById('promptInput');
        this.statusEl = document.getElementById('status');
        this.requestId = 0;
        this.pendingRequests = new Map();

        this.setupEventListeners();
        this.connect();
    }

    setupEventListeners() {
        this.promptInput.addEventListener('run', (e) => {
            this.handleRun(e.detail.content, e.detail.options);
        });

        this.promptInput.addEventListener('clear', () => {
            this.chatLog.clear();
        });
    }

    connect() {
        this.updateStatus('connecting', 'Connecting to server...');

        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws`;

        this.ws = new WebSocket(wsUrl);

        this.ws.onopen = () => {
            this.updateStatus('connected', '✓ Connected to server');
            this.promptInput.setDisabled(false);
        };

        this.ws.onclose = () => {
            this.updateStatus('disconnected', '✗ Disconnected from server');
            this.promptInput.setDisabled(true);

            // Attempt to reconnect after 3 seconds
            setTimeout(() => this.connect(), 3000);
        };

        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            this.updateStatus('disconnected', '✗ Connection error');
        };

        this.ws.onmessage = (event) => {
            this.handleMessage(event.data);
        };
    }

    updateStatus(status, message) {
        this.statusEl.className = `status ${status}`;
        this.statusEl.textContent = message;
    }

    handleRun(content, options) {
        if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
            alert('Not connected to server');
            return;
        }

        // Add prompt to chat log
        this.chatLog.addPrompt(content);

        // Clear input
        this.promptInput.clear();

        // Disable input during execution
        this.promptInput.setDisabled(true);

        // Create JSON-RPC request
        const id = ++this.requestId;
        const request = {
            jsonrpc: '2.0',
            method: 'prompt',
            params: {
                content: content,
                options: options || {}
            },
            id: id
        };

        // Store request for tracking
        this.pendingRequests.set(id, { content, timestamp: Date.now() });

        // Send request
        this.ws.send(JSON.stringify(request));
    }

    handleMessage(data) {
        try {
            const message = JSON.parse(data);

            // Handle JSON-RPC notification (streaming message)
            if (message.method === 'message' && message.params) {
                this.handleStreamMessage(message.params);
                return;
            }

            // Handle JSON-RPC response (final result)
            if (message.id !== undefined) {
                this.handleResponse(message);
                return;
            }

        } catch (error) {
            console.error('Error parsing message:', error, data);
        }
    }

    handleStreamMessage(params) {
        const { type, data } = params;
        this.chatLog.addMessage(type, data);
    }

    handleResponse(response) {
        const request = this.pendingRequests.get(response.id);

        if (!request) {
            console.warn('Received response for unknown request:', response.id);
            return;
        }

        this.pendingRequests.delete(response.id);

        if (response.error) {
            // Show error in chat log
            this.chatLog.addMessage('error', {
                code: response.error.code,
                message: response.error.message,
                data: response.error.data
            });
            console.error('JSON-RPC error:', response.error);
        } else if (response.result) {
            console.log('Request completed:', response.result);
        }

        // Re-enable input
        this.promptInput.setDisabled(false);
    }
}

// Initialize app when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => new App());
} else {
    new App();
}

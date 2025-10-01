/**
 * Chat log web component for displaying messages with color-coded types
 */
class ChatLog extends HTMLElement {
    constructor() {
        super();
        this.attachShadow({ mode: 'open' });
        this.messages = [];
        this.render();
    }

    connectedCallback() {
        // Component is connected to DOM
    }

    render() {
        this.shadowRoot.innerHTML = `
            <style>
                :host {
                    display: flex;
                    flex-direction: column;
                    flex: 1;
                    overflow: hidden;
                    background: #1e1e1e;
                    border: 1px solid #3e3e42;
                    border-radius: 6px;
                    margin-bottom: 1rem;
                }

                .messages {
                    flex: 1;
                    overflow-y: auto;
                    padding: 1rem;
                    display: flex;
                    flex-direction: column;
                    gap: 0.75rem;
                }

                .message {
                    padding: 0.75rem 1rem;
                    border-radius: 4px;
                    border-left: 4px solid;
                    font-size: 0.875rem;
                    line-height: 1.5;
                    word-wrap: break-word;
                }

                .message-header {
                    font-weight: 600;
                    margin-bottom: 0.5rem;
                    display: flex;
                    align-items: center;
                    gap: 0.5rem;
                }

                .message-type {
                    font-size: 0.75rem;
                    opacity: 0.8;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                }

                .message-content {
                    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
                    white-space: pre-wrap;
                }

                .message.assistant {
                    background: #1e2a3a;
                    border-left-color: #569cd6;
                }

                .message.user {
                    background: #2a2a1e;
                    border-left-color: #dcdcaa;
                }

                .message.system {
                    background: #2a1e2a;
                    border-left-color: #c586c0;
                }

                .message.result {
                    background: #1e3a1e;
                    border-left-color: #4ec9b0;
                }

                .message.error {
                    background: #3a1e1e;
                    border-left-color: #f48771;
                }

                .message.prompt {
                    background: #2d2d30;
                    border-left-color: #858585;
                }

                .tool-use {
                    background: #252526;
                    padding: 0.5rem;
                    margin: 0.5rem 0;
                    border-radius: 4px;
                    border: 1px solid #3e3e42;
                }

                .tool-name {
                    color: #dcdcaa;
                    font-weight: 600;
                    margin-bottom: 0.25rem;
                }

                .tool-input {
                    color: #ce9178;
                    font-size: 0.8125rem;
                    margin-left: 1rem;
                }

                .tool-result {
                    background: #252526;
                    padding: 0.5rem;
                    margin: 0.5rem 0;
                    border-radius: 4px;
                    border: 1px solid #3e3e42;
                    color: #4ec9b0;
                }

                .result-summary {
                    display: grid;
                    grid-template-columns: auto 1fr;
                    gap: 0.5rem 1rem;
                    font-size: 0.8125rem;
                }

                .result-label {
                    color: #858585;
                }

                .result-value {
                    color: #4ec9b0;
                    font-weight: 500;
                }

                .empty-state {
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    height: 100%;
                    color: #858585;
                    font-size: 0.875rem;
                }

                /* Scrollbar styling */
                .messages::-webkit-scrollbar {
                    width: 8px;
                }

                .messages::-webkit-scrollbar-track {
                    background: #1e1e1e;
                }

                .messages::-webkit-scrollbar-thumb {
                    background: #3e3e42;
                    border-radius: 4px;
                }

                .messages::-webkit-scrollbar-thumb:hover {
                    background: #4e4e52;
                }
            </style>
            <div class="messages" id="messages">
                <div class="empty-state">Enter a prompt below to get started</div>
            </div>
        `;
    }

    addMessage(type, data) {
        this.messages.push({ type, data, timestamp: Date.now() });
        this.updateMessages();
    }

    addPrompt(content) {
        this.addMessage('prompt', { content });
    }

    clear() {
        this.messages = [];
        this.updateMessages();
    }

    updateMessages() {
        const container = this.shadowRoot.getElementById('messages');

        if (this.messages.length === 0) {
            container.innerHTML = '<div class="empty-state">Enter a prompt below to get started</div>';
            return;
        }

        container.innerHTML = this.messages.map(msg => this.renderMessage(msg)).join('');
        container.scrollTop = container.scrollHeight;
    }

    renderMessage({ type, data }) {
        switch (type) {
            case 'prompt':
                return `
                    <div class="message prompt">
                        <div class="message-header">
                            <span class="message-type">Prompt</span>
                        </div>
                        <div class="message-content">${this.escapeHtml(data.content)}</div>
                    </div>
                `;

            case 'assistant':
                const contentHtml = data.content.map(block => {
                    if (block.type === 'text') {
                        return `<div class="message-content">${this.escapeHtml(block.text)}</div>`;
                    } else if (block.type === 'tool_use') {
                        return `
                            <div class="tool-use">
                                <div class="tool-name">🔧 ${this.escapeHtml(block.name)}</div>
                                <div class="tool-input">${this.escapeHtml(JSON.stringify(block.input, null, 2))}</div>
                            </div>
                        `;
                    }
                    return '';
                }).join('');

                return `
                    <div class="message assistant">
                        <div class="message-header">
                            <span class="message-type">Assistant</span>
                            <span style="opacity: 0.6; font-size: 0.75rem;">Turn ${data.turn}</span>
                        </div>
                        ${contentHtml}
                    </div>
                `;

            case 'user':
                const userContentHtml = data.content.map(block => {
                    if (block.type === 'text') {
                        return `<div class="message-content">${this.escapeHtml(block.text)}</div>`;
                    } else if (block.type === 'tool_result') {
                        const resultClass = block.is_error ? 'error' : '';
                        return `
                            <div class="tool-result ${resultClass}">
                                ${this.escapeHtml(JSON.stringify(block.content, null, 2))}
                            </div>
                        `;
                    }
                    return '';
                }).join('');

                return `
                    <div class="message user">
                        <div class="message-header">
                            <span class="message-type">Tool Response</span>
                        </div>
                        ${userContentHtml}
                    </div>
                `;

            case 'system':
                return `
                    <div class="message system">
                        <div class="message-header">
                            <span class="message-type">System Info</span>
                        </div>
                        <div class="result-summary">
                            <span class="result-label">Model:</span>
                            <span class="result-value">${this.escapeHtml(data.model || 'N/A')}</span>
                            <span class="result-label">Session:</span>
                            <span class="result-value">${this.escapeHtml(data.session_id || 'N/A')}</span>
                            <span class="result-label">Working Directory:</span>
                            <span class="result-value">${this.escapeHtml(data.cwd || 'N/A')}</span>
                            <span class="result-label">Permission Mode:</span>
                            <span class="result-value">${this.escapeHtml(data.permission_mode || 'N/A')}</span>
                        </div>
                    </div>
                `;

            case 'result':
                const errorClass = data.is_error ? 'error' : 'result';
                return `
                    <div class="message ${errorClass}">
                        <div class="message-header">
                            <span class="message-type">${data.is_error ? 'Error' : 'Completed'}</span>
                        </div>
                        <div class="result-summary">
                            <span class="result-label">Turns:</span>
                            <span class="result-value">${data.num_turns}</span>
                            <span class="result-label">API Duration:</span>
                            <span class="result-value">${data.duration_api_ms}ms</span>
                            <span class="result-label">Total Duration:</span>
                            <span class="result-value">${data.duration_ms}ms</span>
                            <span class="result-label">Cost:</span>
                            <span class="result-value">$${data.total_cost_usd.toFixed(4)}</span>
                        </div>
                    </div>
                `;

            default:
                return `
                    <div class="message">
                        <div class="message-header">
                            <span class="message-type">Unknown</span>
                        </div>
                        <div class="message-content">${this.escapeHtml(JSON.stringify(data))}</div>
                    </div>
                `;
        }
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

customElements.define('chat-log', ChatLog);

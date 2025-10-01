/**
 * Prompt input web component with text area and run button
 */
class PromptInput extends HTMLElement {
    constructor() {
        super();
        this.attachShadow({ mode: 'open' });
        this.disabled = false;
        this.render();
    }

    connectedCallback() {
        this.setupEventListeners();
    }

    render() {
        this.shadowRoot.innerHTML = `
            <style>
                :host {
                    display: flex;
                    flex-direction: column;
                    gap: 0.75rem;
                }

                .input-container {
                    display: flex;
                    gap: 0.75rem;
                    align-items: flex-end;
                }

                textarea {
                    flex: 1;
                    min-height: 80px;
                    padding: 0.75rem;
                    background: #2d2d30;
                    border: 1px solid #3e3e42;
                    border-radius: 4px;
                    color: #d4d4d4;
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                    font-size: 0.875rem;
                    line-height: 1.5;
                    resize: vertical;
                    transition: border-color 0.2s;
                }

                textarea:focus {
                    outline: none;
                    border-color: #569cd6;
                }

                textarea:disabled {
                    opacity: 0.5;
                    cursor: not-allowed;
                }

                button {
                    padding: 0.75rem 1.5rem;
                    background: #0e639c;
                    border: none;
                    border-radius: 4px;
                    color: white;
                    font-size: 0.875rem;
                    font-weight: 600;
                    cursor: pointer;
                    transition: background-color 0.2s;
                    height: 40px;
                    min-width: 100px;
                }

                button:hover:not(:disabled) {
                    background: #1177bb;
                }

                button:active:not(:disabled) {
                    background: #0d5a8f;
                }

                button:disabled {
                    background: #3e3e42;
                    cursor: not-allowed;
                    opacity: 0.6;
                }

                .options-toggle {
                    background: transparent;
                    border: 1px solid #3e3e42;
                    color: #d4d4d4;
                    padding: 0.5rem 1rem;
                    font-size: 0.8125rem;
                }

                .options-toggle:hover:not(:disabled) {
                    background: #3e3e42;
                }

                .options-panel {
                    display: none;
                    background: #2d2d30;
                    border: 1px solid #3e3e42;
                    border-radius: 4px;
                    padding: 1rem;
                    gap: 0.75rem;
                    flex-direction: column;
                }

                .options-panel.visible {
                    display: flex;
                }

                .option-row {
                    display: flex;
                    gap: 1rem;
                    align-items: center;
                }

                label {
                    font-size: 0.8125rem;
                    color: #cccccc;
                    min-width: 120px;
                }

                input[type="text"],
                input[type="number"],
                select {
                    flex: 1;
                    padding: 0.5rem;
                    background: #1e1e1e;
                    border: 1px solid #3e3e42;
                    border-radius: 4px;
                    color: #d4d4d4;
                    font-size: 0.8125rem;
                }

                input[type="text"]:focus,
                input[type="number"]:focus,
                select:focus {
                    outline: none;
                    border-color: #569cd6;
                }

                .button-group {
                    display: flex;
                    gap: 0.5rem;
                }

                .clear-button {
                    background: #3a1e1e;
                    min-width: 80px;
                }

                .clear-button:hover:not(:disabled) {
                    background: #4a2e2e;
                }
            </style>

            <div class="input-container">
                <textarea
                    id="prompt"
                    placeholder="Enter your prompt here..."
                    rows="3"
                ></textarea>
                <div class="button-group">
                    <button id="optionsBtn" class="options-toggle">⚙️ Options</button>
                    <button id="clearBtn" class="clear-button">Clear</button>
                    <button id="runBtn">Run</button>
                </div>
            </div>

            <div id="optionsPanel" class="options-panel">
                <div class="option-row">
                    <label for="systemPrompt">System Prompt:</label>
                    <input type="text" id="systemPrompt" placeholder="Optional system prompt">
                </div>
                <div class="option-row">
                    <label for="maxTurns">Max Turns:</label>
                    <input type="number" id="maxTurns" min="1" max="100" value="10">
                </div>
                <div class="option-row">
                    <label for="permissionMode">Permission Mode:</label>
                    <select id="permissionMode">
                        <option value="default">Default</option>
                        <option value="enabled">Enabled</option>
                        <option value="disabled">Disabled</option>
                    </select>
                </div>
                <div class="option-row">
                    <label for="allowedTools">Allowed Tools:</label>
                    <input type="text" id="allowedTools" placeholder="Comma-separated tool names (optional)">
                </div>
            </div>
        `;
    }

    setupEventListeners() {
        const textarea = this.shadowRoot.getElementById('prompt');
        const runBtn = this.shadowRoot.getElementById('runBtn');
        const clearBtn = this.shadowRoot.getElementById('clearBtn');
        const optionsBtn = this.shadowRoot.getElementById('optionsBtn');
        const optionsPanel = this.shadowRoot.getElementById('optionsPanel');

        runBtn.addEventListener('click', () => this.handleRun());
        clearBtn.addEventListener('click', () => this.handleClear());
        optionsBtn.addEventListener('click', () => {
            optionsPanel.classList.toggle('visible');
        });

        // Submit on Ctrl+Enter or Cmd+Enter
        textarea.addEventListener('keydown', (e) => {
            if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                e.preventDefault();
                this.handleRun();
            }
        });
    }

    handleRun() {
        const textarea = this.shadowRoot.getElementById('prompt');
        const content = textarea.value.trim();

        if (!content || this.disabled) {
            return;
        }

        // Gather options
        const options = this.getOptions();

        // Dispatch custom event
        this.dispatchEvent(new CustomEvent('run', {
            detail: { content, options },
            bubbles: true,
            composed: true
        }));
    }

    handleClear() {
        this.dispatchEvent(new CustomEvent('clear', {
            bubbles: true,
            composed: true
        }));
    }

    getOptions() {
        const systemPrompt = this.shadowRoot.getElementById('systemPrompt').value.trim();
        const maxTurns = parseInt(this.shadowRoot.getElementById('maxTurns').value);
        const permissionMode = this.shadowRoot.getElementById('permissionMode').value;
        const allowedToolsStr = this.shadowRoot.getElementById('allowedTools').value.trim();

        const options = {};

        if (systemPrompt) {
            options.system_prompt = systemPrompt;
        }

        if (maxTurns && maxTurns > 0) {
            options.max_turns = maxTurns;
        }

        if (permissionMode) {
            options.permission_mode = permissionMode;
        }

        if (allowedToolsStr) {
            options.allowed_tools = allowedToolsStr.split(',').map(t => t.trim()).filter(t => t);
        }

        return Object.keys(options).length > 0 ? options : null;
    }

    getValue() {
        return this.shadowRoot.getElementById('prompt').value;
    }

    setValue(value) {
        this.shadowRoot.getElementById('prompt').value = value;
    }

    clear() {
        this.setValue('');
    }

    setDisabled(disabled) {
        this.disabled = disabled;
        const textarea = this.shadowRoot.getElementById('prompt');
        const runBtn = this.shadowRoot.getElementById('runBtn');
        const clearBtn = this.shadowRoot.getElementById('clearBtn');
        const optionsBtn = this.shadowRoot.getElementById('optionsBtn');

        textarea.disabled = disabled;
        runBtn.disabled = disabled;
        clearBtn.disabled = disabled;
        optionsBtn.disabled = disabled;

        if (disabled) {
            runBtn.textContent = 'Running...';
        } else {
            runBtn.textContent = 'Run';
        }
    }
}

customElements.define('prompt-input', PromptInput);

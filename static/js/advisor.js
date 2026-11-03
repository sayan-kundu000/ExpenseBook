// ==========================================================================
// Doom-GPT 4o: Latverian Imperial AI Financial Consigliere (ChatGPT Engine)
// Dedicated Financial Advice for Dr. Victor Von Doom
// ==========================================================================

document.addEventListener('DOMContentLoaded', () => {
    const chatMessages = document.getElementById('advisorChatMessages');
    const chatInput = document.getElementById('advisorChatInput');
    const sendBtn = document.getElementById('advisorSendBtn');
    const chips = document.querySelectorAll('.prompt-chips .chip');
    const clearChatBtn = document.getElementById('clearChatBtn');

    // Keep an initial snapshot of the welcome message for reset
    const initialWelcomeHTML = chatMessages ? chatMessages.innerHTML : '';

    // Helper: Escape HTML
    function escapeHtml(str) {
        return str.replace(/[&<>'"]/g, 
            tag => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[tag] || tag)
        );
    }

    // Advanced Markdown Formatter for ChatGPT responses
    function formatMarkdown(text) {
        if (!text) return '';
        
        let html = text;

        // Blockquotes (> text)
        html = html.replace(/^> (.*$)/gim, '<blockquote style="border-left: 3px solid #10b981; background: rgba(16,185,129,0.08); padding: 8px 14px; margin: 12px 0; border-radius: 0 8px 8px 0; color: #e2e8f0; font-style: italic;">$1</blockquote>');

        // Headers
        html = html.replace(/^### (.*$)/gim, '<h3 style="color: #34d399; font-size: 16px; font-weight: 800; margin: 14px 0 6px 0; display: flex; align-items: center; gap: 6px;">$1</h3>');
        html = html.replace(/^#### (.*$)/gim, '<h4 style="color: #67e8f9; font-size: 14px; font-weight: 700; margin: 12px 0 6px 0; text-transform: uppercase; letter-spacing: 0.5px;">$1</h4>');
        html = html.replace(/^## (.*$)/gim, '<h2 style="color: #fff; font-size: 18px; font-weight: 800; margin: 16px 0 8px 0;">$1</h2>');

        // Bold and Italic
        html = html.replace(/\*\*(.*?)\*\*/gim, '<strong style="color: #fff; font-weight: 700;">$1</strong>');
        html = html.replace(/\*(.*?)\*/gim, '<em>$1</em>');

        // Inline Code `code`
        html = html.replace(/`([^`]+)`/gim, '<code style="background: rgba(0,0,0,0.4); border: 1px solid rgba(255,255,255,0.1); padding: 2px 6px; border-radius: 4px; font-family: var(--font-mono); font-size: 12px; color: #34d399;">$1</code>');

        // Numbered Lists (1. item)
        html = html.replace(/^\d+\.\s+(.*$)/gim, '<li style="margin-bottom: 6px; padding-left: 4px;">$1</li>');

        // Bulleted Lists (- item)
        html = html.replace(/^-\s+(.*$)/gim, '<li style="margin-bottom: 6px; padding-left: 4px;">$1</li>');

        // Paragraph breaks
        html = html.replace(/\n\n/gim, '<div style="height: 10px;"></div>');
        html = html.replace(/\n/gim, '<br/>');

        return html;
    }

    // Helper: Append a message to the chat
    function appendMessage(sender, rawHtml, meta = null) {
        if (!chatMessages) return null;
        const bubble = document.createElement('div');
        bubble.className = `chat-bubble ${sender}`;

        const activeUserName = window.currentUserName || 'You';
        const activeModelName = (meta && meta.model_name) || window.advisorModelName || 'AI Financial Advisor';

        if (sender === 'user') {
            bubble.style.cssText = 'align-self: flex-end; background: linear-gradient(135deg, #059669 0%, #047857 100%); color: #fff; max-width: 85%; padding: 14px 18px; border-radius: 14px 14px 2px 14px; box-shadow: 0 4px 14px rgba(5,150,105,0.3);';
            bubble.innerHTML = `
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px; font-size: 11px; font-weight: 700; color: #a7f3d0; text-transform: uppercase;">
                    <i data-feather="user" style="width: 13px; height: 13px;"></i>
                    <span>${escapeHtml(activeUserName)}</span>
                </div>
                ${rawHtml}
            `;
        } else {
            bubble.style.cssText = 'align-self: flex-start; background: #111b2e; border: 1px solid rgba(16, 185, 129, 0.35); color: var(--text-primary); max-width: 95%; border-radius: 14px 14px 14px 2px; padding: 18px 22px; box-shadow: 0 6px 20px rgba(0,0,0,0.3);';
            let headerHtml = `
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 12px; font-size: 11px; font-weight: 700; color: #34d399; text-transform: uppercase; letter-spacing: 0.5px;">
                    <i data-feather="cpu" style="width: 14px; height: 14px;"></i>
                    <span>${escapeHtml(activeModelName.toUpperCase())} &bull; FINANCIAL ADVISOR</span>
                    ${meta && meta.intent ? `<span style="margin-left: auto; background: rgba(16,185,129,0.18); padding: 2px 8px; border-radius: 9999px; color: #34d399; font-size: 10px; border: 1px solid rgba(16,185,129,0.3);">${meta.intent} (${meta.confidence}%)</span>` : ''}
                </div>
            `;
            bubble.innerHTML = headerHtml + `<div class="msg-content">${rawHtml}</div>`;
        }

        chatMessages.appendChild(bubble);
        chatMessages.scrollTop = chatMessages.scrollHeight;

        if (window.feather) feather.replace();
        return bubble;
    }

    // Helper: Show typing indicator
    function showTyping() {
        const typing = document.createElement('div');
        typing.className = 'chat-bubble ai typing-indicator';
        typing.id = 'typingIndicator';
        typing.style.cssText = 'align-self: flex-start; background: #111b2e; border: 1px solid rgba(16,185,129,0.25); border-radius: 12px; padding: 14px 20px;';
        const modelName = window.advisorModelName || 'AI Financial Advisor';
        typing.innerHTML = `
            <div style="display: flex; align-items: center; gap: 10px; color: var(--text-secondary); font-size: 13px;">
                <span style="width: 16px; height: 16px; border: 2px solid #10b981; border-top-color: transparent; border-radius: 50%; display: inline-block; animation: spin 0.7s linear infinite;"></span>
                <span style="color: #34d399; font-weight: 600;">${escapeHtml(modelName)} is analyzing financial, economic & accounting parameters...</span>
            </div>
        `;
        chatMessages.appendChild(typing);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function removeTyping() {
        const typing = document.getElementById('typingIndicator');
        if (typing) typing.remove();
    }

    // ChatGPT Streaming Typewriter Effect
    function streamResponse(targetElement, fullFormattedHtml, onComplete) {
        // Fast streaming by chunking the text or injecting smoothly
        targetElement.innerHTML = '';
        const container = document.createElement('div');
        container.innerHTML = fullFormattedHtml;

        // Render with rapid streaming simulation
        let cursor = document.createElement('span');
        cursor.className = 'streaming-cursor';
        cursor.textContent = '▌';
        cursor.style.cssText = 'color: #10b981; animation: blink 0.8s infinite; display: inline-block; margin-left: 2px;';

        targetElement.appendChild(cursor);

        // Divide into words for typewriter pacing
        const words = fullFormattedHtml.split(' ');
        let currentIdx = 0;
        const totalWords = words.length;
        const batchSize = Math.max(3, Math.floor(totalWords / 25)); // Smooth ~500ms duration

        const interval = setInterval(() => {
            currentIdx += batchSize;
            if (currentIdx >= totalWords) {
                clearInterval(interval);
                targetElement.innerHTML = fullFormattedHtml;
                if (chatMessages) chatMessages.scrollTop = chatMessages.scrollHeight;
                if (onComplete) onComplete();
            } else {
                targetElement.innerHTML = words.slice(0, currentIdx).join(' ') + ' <span style="color: #10b981;">▌</span>';
                if (chatMessages) chatMessages.scrollTop = chatMessages.scrollHeight;
            }
        }, 20);
    }

    // Send query to Local AI Financial Advisor
    async function handleSendQuery(queryText) {
        const text = (queryText || (chatInput ? chatInput.value : '')).trim();
        if (!text) return;

        appendMessage('user', `<p style="margin: 0; line-height: 1.5; font-size: 14px;">${escapeHtml(text)}</p>`);
        if (chatInput) {
            chatInput.value = '';
            chatInput.disabled = true;
        }
        if (sendBtn) sendBtn.disabled = true;

        showTyping();

        try {
            const res = await fetch('/api/ai/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ question: text })
            });
            const data = await res.json();
            removeTyping();

            if (data && data.reply) {
                let formatted = formatMarkdown(data.reply);
                
                // Add suggested action steps if present as interactive pills
                let actionsHtml = '';
                if (data.suggested_actions && data.suggested_actions.length > 0) {
                    actionsHtml = `
                        <div style="margin-top: 16px; padding-top: 14px; border-top: 1px solid rgba(255,255,255,0.08);">
                            <div style="font-size: 11px; font-weight: 800; color: #10b981; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.5px;">
                                🎯 Tactical Action Directives (Click to Execute):
                            </div>
                            <div style="display: flex; flex-wrap: wrap; gap: 8px;">
                                ${data.suggested_actions.map(act => `
                                    <button class="action-directive-pill btn btn-sm" data-action="${escapeHtml(act)}" style="background: rgba(16,185,129,0.15); border: 1px solid rgba(16,185,129,0.35); color: #34d399; font-size: 12px; padding: 4px 10px; border-radius: 9999px; cursor: pointer; transition: all 0.2s;">
                                        ⚡ ${escapeHtml(act)}
                                    </button>
                                `).join('')}
                            </div>
                        </div>
                    `;
                }

                // Add message utility bar (Copy decree, timestamp)
                const utilBarHtml = `
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 14px; padding-top: 10px; border-top: 1px solid rgba(255,255,255,0.05); font-size: 11px; color: var(--text-muted);">
                        <span>Sovereign Core &bull; Latverian Imperial Encryption</span>
                        <div style="display: flex; gap: 10px;">
                            <button class="copy-decree-btn" style="background: transparent; border: none; color: var(--text-secondary); cursor: pointer; display: flex; align-items: center; gap: 4px; font-size: 11px;" title="Copy this advice">
                                <i data-feather="copy" style="width: 12px; height: 12px;"></i>
                                <span>Copy Advice</span>
                            </button>
                        </div>
                    </div>
                `;

                // Create container bubble
                const bubble = appendMessage('ai', '', { intent: data.intent, confidence: data.confidence });
                if (bubble) {
                    const contentDiv = bubble.querySelector('.msg-content');
                    if (contentDiv) {
                        streamResponse(contentDiv, formatted + actionsHtml + utilBarHtml, () => {
                            if (window.feather) feather.replace();
                            
                            // Attach copy handlers
                            const copyBtn = bubble.querySelector('.copy-decree-btn');
                            if (copyBtn) {
                                copyBtn.addEventListener('click', () => {
                                    navigator.clipboard.writeText(data.reply).then(() => {
                                        copyBtn.innerHTML = '<span style="color: #10b981;">✓ Decree Copied!</span>';
                                        setTimeout(() => {
                                            copyBtn.innerHTML = '<i data-feather="copy" style="width: 12px; height: 12px;"></i><span>Copy Advice</span>';
                                            if (window.feather) feather.replace();
                                        }, 2000);
                                    });
                                });
                            }

                            // Attach interactive directive pills
                            bubble.querySelectorAll('.action-directive-pill').forEach(pill => {
                                pill.addEventListener('click', () => {
                                    const actionText = pill.getAttribute('data-action');
                                    if (actionText) handleSendQuery(actionText);
                                });
                            });
                        });
                    }
                }
            } else {
                appendMessage('ai', '<p>My Lord Doom, the neural matrix encountered a brief telemetry fluctuation. Please restate your directive.</p>');
            }
        } catch (err) {
            removeTyping();
            appendMessage('ai', '<p style="color: #f43f5e;">Sub-quantum neural core connection timed out. Latverian internal defenses remain intact.</p>');
            console.error("Doom-GPT chat error:", err);
        } finally {
            if (chatInput) {
                chatInput.disabled = false;
                chatInput.focus();
            }
            if (sendBtn) sendBtn.disabled = false;
        }
    }

    if (sendBtn) {
        sendBtn.addEventListener('click', () => handleSendQuery());
    }

    if (chatInput) {
        chatInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSendQuery();
            }
        });
    }

    // Attach Prompt Chips
    chips.forEach(chip => {
        chip.addEventListener('click', () => {
            const prompt = chip.getAttribute('data-prompt');
            if (prompt) handleSendQuery(prompt);
        });
    });

    // Clear Chat / New Session
    if (clearChatBtn) {
        clearChatBtn.addEventListener('click', () => {
            if (chatMessages && initialWelcomeHTML) {
                chatMessages.innerHTML = initialWelcomeHTML;
                if (window.feather) feather.replace();
            }
        });
    }

    // Transformer Self-Attention Live Tester Visualizer
    const testInput = document.getElementById('attnTestInput');
    const testBtn = document.getElementById('attnTestBtn');
    const pillWrap = document.getElementById('attnPillWrap');
    const resultCat = document.getElementById('attnResultCat');

    async function runAttentionTest() {
        if (!testInput || !pillWrap) return;
        const text = testInput.value.trim();
        if (!text) return;

        pillWrap.innerHTML = '<span style="color: var(--text-muted); font-size: 12px;">Computing Transformer self-attention weights...</span>';

        try {
            const res = await fetch('/api/ai/predict-category', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ description: text })
            });
            const data = await res.json();
            
            if (resultCat) {
                resultCat.innerHTML = `Predicted: <strong style="color: #10b981;">${data.category}</strong> (${data.confidence}% confidence)`;
            }

            if (data.attention_tokens && data.attention_tokens.length > 0) {
                pillWrap.innerHTML = data.attention_tokens.map(item => {
                    const alpha = Math.min(1.0, Math.max(0.18, item.weight * 2.8));
                    return `
                        <div class="token-pill" style="background: rgba(16, 185, 129, ${alpha}); border-color: rgba(16, 185, 129, ${alpha + 0.2}); color: #fff; font-weight: 600;">
                            <span>${item.token}</span>
                            <span style="font-size: 10px; opacity: 0.85; margin-left: 3px;">${item.weight}</span>
                        </div>
                    `;
                }).join('');
            } else {
                pillWrap.innerHTML = '<span style="color: var(--text-muted);">No tokens extracted.</span>';
            }
        } catch (err) {
            pillWrap.innerHTML = '<span style="color: #f43f5e;">Inference error.</span>';
        }
    }

    if (testBtn) testBtn.addEventListener('click', runAttentionTest);
    if (testInput) {
        testInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                runAttentionTest();
            }
        });
    }
});

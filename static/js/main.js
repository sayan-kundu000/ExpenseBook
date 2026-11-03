// ==========================================================================
// ExpenseBook Main Interactive Logic
// ==========================================================================

document.addEventListener('DOMContentLoaded', () => {
    // 1. Initialize Feather / Lucide icons if available
    if (window.feather) {
        feather.replace();
    }

    // 2. Sidebar Toggle (Collapsible Navigation & Drawer)
    const sidebarToggleBtn = document.getElementById('sidebarToggleBtn');
    const mobileMenuBtn = document.getElementById('mobileMenuToggle');
    const sidebarCloseBtn = document.getElementById('sidebarCloseBtn');
    const sidebarBackdrop = document.getElementById('sidebarBackdrop');
    const sidebar = document.getElementById('appSidebar') || document.querySelector('.sidebar');
    const mainContent = document.getElementById('appMainContent') || document.querySelector('.main-content');

    function openSidebarDrawer() {
        if (!sidebar) return;
        sidebar.classList.add('open');
        if (sidebarBackdrop) sidebarBackdrop.style.display = 'block';
        if (sidebarCloseBtn) sidebarCloseBtn.style.display = 'inline-block';
    }

    function closeSidebarDrawer() {
        if (!sidebar) return;
        sidebar.classList.remove('open');
        if (sidebarBackdrop) sidebarBackdrop.style.display = 'none';
        if (sidebarCloseBtn) sidebarCloseBtn.style.display = 'none';
    }

    function toggleSidebar() {
        if (!sidebar) return;
        if (sidebar.classList.contains('collapsed')) {
            // It is in collapsed/hidden mode (e.g. on Doom GPT / Advisor)
            if (sidebar.classList.contains('open')) {
                closeSidebarDrawer();
            } else {
                openSidebarDrawer();
            }
        } else {
            // Standard page mode: toggle full-width collapse
            sidebar.classList.toggle('collapsed');
            if (mainContent) mainContent.classList.toggle('full-width');
        }
    }

    if (sidebarToggleBtn) sidebarToggleBtn.addEventListener('click', toggleSidebar);
    if (mobileMenuBtn) mobileMenuBtn.addEventListener('click', toggleSidebar);
    if (sidebarCloseBtn) sidebarCloseBtn.addEventListener('click', closeSidebarDrawer);
    if (sidebarBackdrop) sidebarBackdrop.addEventListener('click', closeSidebarDrawer);

    // Also close drawer on ESC key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && sidebar && sidebar.classList.contains('open')) {
            closeSidebarDrawer();
        }
    });

    // 3. Theme Toggle (Obsidian Dark / Crisp Light)
    const themeToggleBtn = document.getElementById('themeToggleBtn');
    const savedTheme = localStorage.getItem('expensebook_theme') || 'dark';
    if (savedTheme === 'light') {
        document.body.classList.add('light-theme');
    }

    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', () => {
            document.body.classList.toggle('light-theme');
            const isLight = document.body.classList.contains('light-theme');
            localStorage.setItem('expensebook_theme', isLight ? 'light' : 'dark');
        });
    }

    // 4. Modal Open & Close Handler
    const modalOpenTriggers = document.querySelectorAll('[data-modal-target]');
    const modalCloseTriggers = document.querySelectorAll('[data-modal-close]');

    modalOpenTriggers.forEach(btn => {
        btn.addEventListener('click', () => {
            const targetId = btn.getAttribute('data-modal-target');
            const modal = document.getElementById(targetId);
            if (modal) {
                modal.classList.add('active');
            }
        });
    });

    modalCloseTriggers.forEach(btn => {
        btn.addEventListener('click', () => {
            const modal = btn.closest('.modal-backdrop');
            if (modal) {
                modal.classList.remove('active');
            }
        });
    });

    // Close modal on outside click
    document.querySelectorAll('.modal-backdrop').forEach(modal => {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.classList.remove('active');
            }
        });
    });

    // 5. Real-Time AI Transformer Expense Auto-Categorizer
    const descInputs = document.querySelectorAll('.ai-predict-input');
    descInputs.forEach(input => {
        let debounceTimer;
        input.addEventListener('input', () => {
            clearTimeout(debounceTimer);
            const text = input.value.trim();
            const badgeContainer = input.closest('form').querySelector('.ai-prediction-badge-wrap');
            const catSelect = input.closest('form').querySelector('select[name="category_id"]');

            if (!badgeContainer || text.length < 3) {
                if (badgeContainer) badgeContainer.innerHTML = '';
                return;
            }

            debounceTimer = setTimeout(async () => {
                try {
                    const response = await fetch('/api/ai/predict-category', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ description: text })
                    });
                    const data = await response.json();
                    if (data && data.category) {
                        badgeContainer.innerHTML = `
                            <div class="category-badge" style="background: rgba(6, 182, 212, 0.15); border: 1px solid rgba(6, 182, 212, 0.4); color: #06b6d4; margin-top: 8px;">
                                <i data-feather="cpu" style="width: 14px; height: 14px;"></i>
                                <span>AI Transformer: <strong>${data.category}</strong> (${data.confidence}%)</span>
                            </div>
                        `;
                        if (window.feather) feather.replace();

                        // Auto-select in dropdown if 'auto' or unselected
                        if (catSelect && (catSelect.value === '' || catSelect.value === 'auto')) {
                            Array.from(catSelect.options).forEach(opt => {
                                if (opt.text.toLowerCase().includes(data.category.toLowerCase())) {
                                    catSelect.value = opt.value;
                                }
                            });
                        }
                    }
                } catch (err) {
                    console.error("AI auto-categorizer error:", err);
                }
            }, 300);
        });
    });
});

// ==========================================================================
// ExpenseBook Dashboard Charts
// ==========================================================================

document.addEventListener('DOMContentLoaded', async () => {
    const trendCtx = document.getElementById('monthlyTrendChart');
    const catCtx = document.getElementById('categoryPieChart');

    if (!trendCtx && !catCtx) return;

    try {
        const response = await fetch('/api/analytics/charts');
        const data = await response.json();

        // 1. Monthly Spending Trend Line Chart
        if (trendCtx && data.trend) {
            const ctx = trendCtx.getContext('2d');
            
            // Gradient fill
            const gradient = ctx.createLinearGradient(0, 0, 0, 300);
            gradient.addColorStop(0, 'rgba(99, 102, 241, 0.4)');
            gradient.addColorStop(1, 'rgba(99, 102, 241, 0.0)');

            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: data.trend.labels,
                    datasets: [{
                        label: 'Monthly Spending',
                        data: data.trend.data,
                        borderColor: '#6366f1',
                        borderWidth: 3,
                        backgroundColor: gradient,
                        fill: true,
                        tension: 0.4,
                        pointBackgroundColor: '#818cf8',
                        pointBorderColor: '#ffffff',
                        pointBorderWidth: 2,
                        pointRadius: 5,
                        pointHoverRadius: 7
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false },
                        tooltip: {
                            backgroundColor: '#1e293b',
                            titleColor: '#f8fafc',
                            bodyColor: '#cbd5e1',
                            borderColor: 'rgba(255, 255, 255, 0.1)',
                            borderWidth: 1,
                            padding: 12,
                            callbacks: {
                                label: (ctx) => ` Spent: ${window.userCurrency || '₹'}${ctx.raw.toLocaleString()}`
                            }
                        }
                    },
                    scales: {
                        x: {
                            grid: { color: 'rgba(255, 255, 255, 0.05)' },
                            ticks: { color: '#94a3b8', font: { family: 'Plus Jakarta Sans' } }
                        },
                        y: {
                            grid: { color: 'rgba(255, 255, 255, 0.05)' },
                            ticks: {
                                color: '#94a3b8',
                                font: { family: 'Plus Jakarta Sans' },
                                callback: (val) => `${window.userCurrency || '₹'}${val}`
                            }
                        }
                    }
                }
            });
        }

        // 2. Category Distribution Doughnut Chart
        if (catCtx && data.categories) {
            new Chart(catCtx.getContext('2d'), {
                type: 'doughnut',
                data: {
                    labels: data.categories.labels,
                    datasets: [{
                        data: data.categories.data,
                        backgroundColor: data.categories.colors,
                        borderColor: '#0f172a',
                        borderWidth: 3,
                        hoverOffset: 6
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    cutout: '72%',
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                color: '#94a3b8',
                                boxWidth: 12,
                                padding: 14,
                                font: { family: 'Plus Jakarta Sans', size: 12 }
                            }
                        },
                        tooltip: {
                            backgroundColor: '#1e293b',
                            titleColor: '#f8fafc',
                            bodyColor: '#cbd5e1',
                            borderColor: 'rgba(255, 255, 255, 0.1)',
                            borderWidth: 1,
                            padding: 12,
                            callbacks: {
                                label: (ctx) => ` ${ctx.label}: ${window.userCurrency || '₹'}${ctx.raw.toLocaleString()}`
                            }
                        }
                    }
                }
            });
        }

    } catch (err) {
        console.error("Error loading dashboard charts:", err);
    }
});

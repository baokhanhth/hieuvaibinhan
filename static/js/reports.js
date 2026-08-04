document.addEventListener("DOMContentLoaded", () => {
    let revenueChart, bestChart, slowChart;

    const radioFilters = document.querySelectorAll('input[name="filter"]');
    const fromDateInput = document.getElementById("from-date");
    const toDateInput = document.getElementById("to-date");
    const btnApply = document.getElementById("btn-apply");

    const todayStr = new Date().toISOString().split("T")[0];
    if (fromDateInput) fromDateInput.max = todayStr;
    if (toDateInput) toDateInput.max = todayStr;

    if (fromDateInput && toDateInput) {
        fromDateInput.addEventListener("change", () => {
            if (fromDateInput.value) toDateInput.min = fromDateInput.value;
        });
        toDateInput.addEventListener("change", () => {
            if (toDateInput.value) fromDateInput.max = toDateInput.value;
        });
    }

    radioFilters.forEach(radio => {
        radio.addEventListener("change", (e) => {
            if (fromDateInput) fromDateInput.value = "";
            if (toDateInput) toDateInput.value = "";
            
            fetchReportData(e.target.value);
        });
    });

    if (btnApply) {
        btnApply.addEventListener("click", () => {
            const fromDate = fromDateInput ? fromDateInput.value : "";
            const toDate = toDateInput ? toDateInput.value : "";

            if (!fromDate || !toDate) {
                alert("Vui lòng chọn đầy đủ cả Từ ngày và Đến ngày!");
                return;
            }

            if (fromDate > toDate) {
                alert("Từ ngày không thể lớn hơn Đến ngày!");
                return;
            }

            radioFilters.forEach(radio => radio.checked = false);

            fetchReportData("custom", fromDate, toDate);
        });
    }

    async function fetchReportData(filterType, fromDate = "", toDate = "") {
        let url = `data/?filter=${filterType}`;
        if (filterType === "custom") {
            url += `&from_date=${fromDate}&to_date=${toDate}`;
        }

        try {
            const response = await fetch(url);
            const result = await response.json();

            if (result.success) {
                updateKPIs(result.total_revenue, result.total_orders);
                updateCharts(result.chart, result.best_sellers, result.slow_sellers);
            }
        } catch (error) {
            console.error("Lỗi tải dữ liệu báo cáo:", error);
        }
    }

    function updateKPIs(revenue, orders) {
        const revEl = document.getElementById("total-revenue");
        const ordEl = document.getElementById("total-orders");
        if (revEl) revEl.innerText = Number(revenue).toLocaleString("vi-VN") + " đ";
        if (ordEl) ordEl.innerText = Number(orders).toLocaleString("vi-VN");
    }

    function updateCharts(chartData, bestSellers, slowSellers) {
        const colorPalette = [
            '#2f88c6', '#16a34a', '#e65f5f', '#f59e0b', '#8b5cf6', 
            '#ec4899', '#14b8a6', '#f97316', '#6366f1', '#84cc16'
        ];

        // Biểu đồ doanh thu
        const ctxRevenue = document.getElementById("revenue-chart")?.getContext("2d");
        if (ctxRevenue) {
            if (revenueChart) revenueChart.destroy();
            revenueChart = new Chart(ctxRevenue, {
                type: 'bar',
                data: {
                    labels: chartData.labels,
                    datasets: [{
                        label: 'Doanh thu',
                        data: chartData.revenue,
                        orderCount: chartData.orders,
                        backgroundColor: 'rgba(47, 136, 198, 0.75)',
                        borderColor: '#2f88c6',
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    let revenueVal = context.raw || 0;
                                    let orderVal = context.dataset.orderCount[context.dataIndex] || 0;
                                    let formattedRevenue = Number(revenueVal).toLocaleString("vi-VN");
                                    return [
                                        ` Tổng doanh thu: ${formattedRevenue} đ`,
                                        ` Tổng hóa đơn: ${orderVal} đơn`
                                    ];
                                }
                            }
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                precision: 0,
                                callback: function(value) {
                                    return Number(value).toLocaleString("vi-VN");
                                }
                            }
                        }
                    }
                }
            });
        }

        // Biểu đồ Top 5 bán chạy
        const ctxBest = document.getElementById("best-chart")?.getContext("2d");
        if (ctxBest) {
            if (bestChart) bestChart.destroy();
            bestChart = new Chart(ctxBest, {
                type: 'bar',
                data: {
                    labels: bestSellers.map(item => item.product_name),
                    datasets: [{
                        label: 'Số lượng bán (m)',
                        data: bestSellers.map(item => item.total_qty),
                        backgroundColor: bestSellers.map((_, index) => colorPalette[index % colorPalette.length])
                    }]
                },
                options: { 
                    responsive: true, 
                    maintainAspectRatio: false,
                    indexAxis: 'y', 
                    plugins: { legend: { display: false } },
                    scales: { x: { beginAtZero: true } }
                }
            });
        }

        // Biểu đồ Top 5 bán chậm
        const ctxSlow = document.getElementById("slow-chart")?.getContext("2d");
        if (ctxSlow) {
            if (slowChart) slowChart.destroy();
            slowChart = new Chart(ctxSlow, {
                type: 'bar',
                data: {
                    labels: slowSellers.map(item => item.product_name),
                    datasets: [{
                        label: 'Số lượng bán (m)',
                        data: slowSellers.map(item => item.total_qty),
                        backgroundColor: slowSellers.map((_, index) => colorPalette[(index + 3) % colorPalette.length])
                    }]
                },
                options: { 
                    responsive: true, 
                    maintainAspectRatio: false,
                    indexAxis: 'y',
                    plugins: { legend: { display: false } },
                    scales: { x: { beginAtZero: true } }
                }
            });
        }
    }

    // Mặc định tự động tải báo cáo 30 ngày gần nhất khi mở trang
    fetchReportData("30days");
});
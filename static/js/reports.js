document.addEventListener("DOMContentLoaded", () => {
    let revenueChart, bestChart, slowChart;

    const radioFilters = document.querySelectorAll('input[name="filter"]');
    const customDateContainer = document.querySelector('.custom-date');
    const fromDateInput = document.getElementById("from-date");
    const toDateInput = document.getElementById("to-date");
    const btnApply = document.getElementById("btn-apply");

    // Xử lý ẩn/hiện khung chọn ngày tùy chọn
    radioFilters.forEach(radio => {
        radio.addEventListener("change", (e) => {
            if (e.target.value === "custom") {
                customDateContainer.style.display = "flex";
            } else {
                customDateContainer.style.display = "none";
                fetchReportData(e.target.value);
            }
        });
    });

    btnApply.addEventListener("click", () => {
        const fromDate = fromDateInput.value;
        const toDate = toDateInput.value;
        if (!fromDate || !toDate) {
            alert("Vui lòng chọn đầy đủ từ ngày và đến ngày!");
            return;
        }
        fetchReportData("custom", fromDate, toDate);
    });

    // Hàm gọi dữ liệu từ Backend API
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
        document.getElementById("total-revenue").innerText = Number(revenue).toLocaleString("vi-VN");
        document.getElementById("total-orders").innerText = Number(orders).toLocaleString("vi-VN");
    }

    function updateCharts(chartData, bestSellers, slowSellers) {
        // Danh sách các màu sắc đẹp và sinh động để gán cho các mặt hàng
        const colorPalette = [
            '#2f88c6', '#16a34a', '#e65f5f', '#f59e0b', '#8b5cf6', 
            '#ec4899', '#14b8a6', '#f97316', '#6366f1', '#84cc16'
        ];

        // 1. Biểu đồ doanh thu: Cột dọc (bar) kèm Tooltip hiển thị Doanh thu và Số đơn
        const ctxRevenue = document.getElementById("revenue-chart").getContext("2d");
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
                                    ` Tổng doanh thu: ${formattedRevenue}`,
                                    ` Tổng hóa đơn: ${orderVal} đơn`
                                ];
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        // Thêm dòng này để ép các bước nhảy trên trục y phải là số nguyên (tránh bị chia nhỏ thành số lẻ 0.1, 0.2 đ)
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

        // 2. Biểu đồ Top mặt hàng bán chạy: Mỗi cột một màu khác nhau
        const ctxBest = document.getElementById("best-chart").getContext("2d");
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
                indexAxis: 'y', // Cột nằm ngang
                plugins: {
                    legend: { display: false } // Ẩn chú thích màu thừa nếu muốn gọn
                },
                scales: { x: { beginAtZero: true } }
            }
        });

        // 3. Biểu đồ Top mặt hàng bán chậm: Mỗi cột một màu khác nhau
        const ctxSlow = document.getElementById("slow-chart").getContext("2d");
        if (slowChart) slowChart.destroy();
        slowChart = new Chart(ctxSlow, {
            type: 'bar',
            data: {
                labels: slowSellers.map(item => item.product_name),
                datasets: [{
                    label: 'Số lượng bán (m)',
                    data: slowSellers.map(item => item.total_qty),
                    // Tự động lấy màu ngược lại hoặc dùng bảng màu tương tự
                    backgroundColor: slowSellers.map((_, index) => colorPalette[(index + 3) % colorPalette.length])
                }]
            },
            options: { 
                responsive: true, 
                maintainAspectRatio: false,
                indexAxis: 'y', // Cột nằm ngang
                plugins: {
                    legend: { display: false }
                },
                scales: { x: { beginAtZero: true } }
            }
        });
    }
    fetchReportData("today");
});
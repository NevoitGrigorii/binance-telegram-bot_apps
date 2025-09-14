// Чекаємо, поки сторінка повністю завантажиться
document.addEventListener('DOMContentLoaded', function() {
    // Ініціалізуємо Telegram Web App API
    const tg = window.Telegram.WebApp;
    tg.expand(); // Розширюємо вікно на весь екран

    const chartContainer = document.getElementById('chart-container');

    // Налаштування вигляду графіка, схожого на Binance
    const chart = LightweightCharts.createChart(chartContainer, {
        width: chartContainer.clientWidth,
        height: chartContainer.clientHeight,
        layout: {
            backgroundColor: '#131722',
            textColor: 'rgba(255, 255, 255, 0.9)',
        },
        grid: {
            vertLines: { color: '#334158' },
            horzLines: { color: '#334158' },
        },
        crosshair: { mode: LightweightCharts.CrosshairMode.Normal },
        timeScale: { timeVisible: true, secondsVisible: false },
    });

    // Створюємо серію для свічного графіка
    const candleSeries = chart.addCandlestickSeries({
      upColor: '#26a69a',
      downColor: '#ef5350',
      borderDownColor: '#ef5350',
      borderUpColor: '#26a69a',
      wickDownColor: '#ef5350',
      wickUpColor: '#26a69a',
    });

    // Функція для завантаження даних з Binance
    async function loadChartData(symbol, interval = '1d') {
        try {
            // Робимо запит до публічного API Binance
            const response = await fetch(`https://api.binance.com/api/v3/klines?symbol=${symbol}&interval=${interval}&limit=200`);
            const data = await response.json();

            // Форматуємо дані для бібліотеки графіків
            const formattedData = data.map(candle => ({
                time: candle[0] / 1000, // час (timestamp)
                open: parseFloat(candle[1]),
                high: parseFloat(candle[2]),
                low: parseFloat(candle[3]),
                close: parseFloat(candle[4]),
            }));

            candleSeries.setData(formattedData);

        } catch (error) {
            console.error('Помилка завантаження даних:', error);
        }
    }

    // Отримуємо символ з параметрів URL, переданих з кнопки бота
    const urlParams = new URLSearchParams(window.location.search);
    const symbol = urlParams.get('symbol') || 'BTCUSDT'; // Якщо символ не передано, показуємо BTCUSDT

    // Завантажуємо дані при старті
    loadChartData(symbol, '1d');

    // Обробник зміни розміру вікна, щоб графік адаптувався
    window.addEventListener('resize', () => {
        chart.resize(chartContainer.clientWidth, chartContainer.clientHeight);
    });
});
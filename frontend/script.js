document.addEventListener('DOMContentLoaded', function() {
    // --- Ініціалізація ---
    const tg = window.Telegram.WebApp;
    tg.expand();

    const chartContainer = document.getElementById('chart-container');
    const chart = LightweightCharts.createChart(chartContainer, { /* ...налаштування з минулого разу... */ });
    const candleSeries = chart.addCandlestickSeries({ /* ...налаштування з минулого разу... */ });

    // Посилання на елементи керування
    const symbolInput = document.getElementById('symbol-input');
    const searchButton = document.getElementById('search-button');
    const intervalButtons = document.querySelectorAll('.interval-btn');

    let currentSymbol = 'BTCUSDT';
    let currentInterval = '1d';
    let socket = null;

    // --- Функції ---

    // 1. Функція завантаження початкових даних
    async function loadInitialData(symbol, interval) {
        try {
            const response = await fetch(`https://api.binance.com/api/v3/klines?symbol=${symbol.toUpperCase()}&interval=${interval}&limit=200`);
            const data = await response.json();

            if (data.code) { // Перевірка на помилку від Binance
                alert('Помилка: ' + data.msg);
                return;
            }

            const formattedData = data.map(candle => ({
                time: candle[0] / 1000,
                open: parseFloat(candle[1]),
                high: parseFloat(candle[2]),
                low: parseFloat(candle[3]),
                close: parseFloat(candle[4]),
            }));
            candleSeries.setData(formattedData);
        } catch (error) {
            console.error('Помилка завантаження даних:', error);
            alert('Не вдалося завантажити дані. Перевірте символ.');
        }
    }

    // 2. Функція для підключення WebSocket
    function connectWebSocket(symbol, interval) {
        // Закриваємо старе з'єднання, якщо воно є
        if (socket) socket.close();

        // Створюємо нове з'єднання
        socket = new WebSocket(`wss://stream.binance.com:9443/ws/${symbol.toLowerCase()}@kline_${interval}`);

        socket.onmessage = function(event) {
            const message = JSON.parse(event.data);
            const kline = message.k;

            // Оновлюємо останню свічку на графіку
            candleSeries.update({
                time: kline.t / 1000,
                open: parseFloat(kline.o),
                high: parseFloat(kline.h),
                low: parseFloat(kline.l),
                close: parseFloat(kline.c),
            });
        };
    }

    // 3. Головна функція для оновлення графіка
    async function updateChart(symbol, interval) {
        currentSymbol = symbol;
        currentInterval = interval;
        symbolInput.value = symbol; // Оновлюємо поле вводу

        // Виділяємо активну кнопку таймфрейму
        intervalButtons.forEach(btn => {
            btn.classList.toggle('active', btn.dataset.interval === interval);
        });

        await loadInitialData(symbol, interval);
        connectWebSocket(symbol, interval);
    }

    // --- Обробники подій ---

    // Пошук по кнопці або Enter
    searchButton.addEventListener('click', () => updateChart(symbolInput.value, currentInterval));
    symbolInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') updateChart(symbolInput.value, currentInterval);
    });

    // Кнопки таймфреймів
    intervalButtons.forEach(button => {
        button.addEventListener('click', () => {
            const newInterval = button.dataset.interval;
            updateChart(currentSymbol, newInterval);
        });
    });

    // --- Перший запуск ---
    const urlParams = new URLSearchParams(window.location.search);
    const initialSymbol = urlParams.get('symbol') || 'BTCUSDT';
    updateChart(initialSymbol, '1d');

    // Адаптація розміру графіка
    window.addEventListener('resize', () => chart.resize(chartContainer.clientWidth, chartContainer.clientHeight));
});
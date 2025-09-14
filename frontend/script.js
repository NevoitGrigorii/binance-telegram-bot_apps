document.addEventListener('DOMContentLoaded', function() {
    // --- Ініціалізація ---
    const tg = window.Telegram.WebApp;
    tg.expand(); // Розширюємо вікно на весь екран

    const chartContainer = document.getElementById('chart-container');

    // Налаштування вигляду графіка
    const chart = LightweightCharts.createChart(chartContainer, {
        width: chartContainer.clientWidth,
        height: chartContainer.clientHeight,
        layout: { backgroundColor: '#131722', textColor: 'rgba(255, 255, 255, 0.9)' },
        grid: { vertLines: { color: '#334158' }, horzLines: { color: '#334158' } },
        crosshair: { mode: LightweightCharts.CrosshairMode.Normal },
        timeScale: { timeVisible: true, secondsVisible: false },
    });

    // Налаштування вигляду свічок
    const candleSeries = chart.addCandlestickSeries({
      upColor: '#26a69a', downColor: '#ef5350', borderDownColor: '#ef5350',
      borderUpColor: '#26a69a', wickDownColor: '#ef5350', wickUpColor: '#26a69a',
    });

    // Посилання на елементи керування
    const symbolInput = document.getElementById('symbol-input');
    const searchButton = document.getElementById('search-button');
    const intervalButtons = document.querySelectorAll('.interval-btn');

    let currentSymbol = 'BTCUSDT';
    let currentInterval = '1d';
    let socket = null;

    // --- Функції ---

    // 1. Функція завантаження початкових даних (історії)
    async function loadInitialData(symbol, interval) {
        try {
            // Завантажуємо 200 останніх свічок для історії
            const response = await fetch(`https://api.binance.com/api/v3/klines?symbol=${symbol.toUpperCase()}&interval=${interval}&limit=200`);
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            const data = await response.json();

            if (!Array.isArray(data) || data.length === 0) {
                 alert('Помилка: Не знайдено даних для символу ' + symbol);
                 return;
            }

            const formattedData = data.map(candle => ({
                time: candle[0] / 1000, open: parseFloat(candle[1]), high: parseFloat(candle[2]),
                low: parseFloat(candle[3]), close: parseFloat(candle[4]),
            }));
            candleSeries.setData(formattedData);
        } catch (error) {
            console.error('Помилка завантаження даних:', error);
            alert('Не вдалося завантажити дані. Перевірте правильність символу.');
        }
    }

    // 2. Функція для підключення WebSocket для даних в реальному часі
    function connectWebSocket(symbol, interval) {
        if (socket) socket.close(); // Закриваємо старе з'єднання

        socket = new WebSocket(`wss://stream.binance.com:9443/ws/${symbol.toLowerCase()}@kline_${interval}`);

        socket.onmessage = function(event) {
            const message = JSON.parse(event.data);
            const kline = message.k;

            candleSeries.update({
                time: kline.t / 1000, open: parseFloat(kline.o), high: parseFloat(kline.h),
                low: parseFloat(kline.l), close: parseFloat(kline.c),
            });
        };
    }

    // 3. Головна функція для оновлення всього графіка
    async function updateChart(symbol, interval) {
        currentSymbol = symbol;
        currentInterval = interval;
        symbolInput.value = symbol;

        intervalButtons.forEach(btn => {
            btn.classList.toggle('active', btn.dataset.interval === interval);
        });

        await loadInitialData(symbol, interval);
        connectWebSocket(symbol, interval);
    }

    // --- Обробники подій ---

    searchButton.addEventListener('click', () => updateChart(symbolInput.value, currentInterval));
    symbolInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') updateChart(symbolInput.value, currentInterval);
    });

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

    window.addEventListener('resize', () => chart.resize(chartContainer.clientWidth, chartContainer.clientHeight));
});
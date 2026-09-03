const form = document.getElementById("search-form");
const cityInput = document.getElementById("city-input");
const loading = document.getElementById("loading");
const error = document.getElementById("error");
const weatherSection = document.getElementById("weather");

const currentIcon = (code) => `https://openweathermap.org/img/wn/${code}@2x.png`;
const formatDate = (d) =>
    new Date(d + "T00:00:00").toLocaleDateString(undefined, {
        weekday: "short",
        month: "short",
        day: "numeric",
    });

function showLoading(show) {
    loading.classList.toggle("hidden", !show);
    weatherSection.classList.add("hidden");
}

function showError(msg) {
    error.textContent = msg;
    error.classList.remove("hidden");
    setTimeout(() => error.classList.add("hidden"), 5000);
}

function renderWeather(data) {
    const c = data.current;

    document.getElementById("city-name").textContent = c.city;
    document.getElementById("current-icon").src = currentIcon(c.icon);
    document.getElementById("current-icon").alt = c.description;
    document.getElementById("current-temp").textContent = `${c.temp}°C`;
    document.getElementById("current-desc").textContent = c.description;
    document.getElementById("feels-like").textContent = `Feels like ${c.feels_like}°C`;
    document.getElementById("humidity").textContent = `Humidity ${c.humidity}%`;
    document.getElementById("wind").textContent = `Wind ${c.wind_speed} m/s`;
    document.getElementById("pressure").textContent = `Pressure ${c.pressure} hPa`;

    const grid = document.getElementById("forecast-grid");
    grid.innerHTML = "";
    data.forecast.forEach((f) => {
        const card = document.createElement("div");
        card.className = "forecast-card";
        card.innerHTML = `
            <div class="date">${formatDate(f.date)}</div>
            <img src="${currentIcon(f.icon)}" alt="${f.description}">
            <div class="temp">${f.temp}°C</div>
            <div class="desc">${f.description}</div>
        `;
        grid.appendChild(card);
    });

    weatherSection.classList.remove("hidden");
}

form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const city = cityInput.value.trim();
    if (!city) return;

    error.classList.add("hidden");
    showLoading(true);

    try {
        const resp = await fetch(`/api/weather?city=${encodeURIComponent(city)}`);
        const data = await resp.json();
        if (!resp.ok) throw new Error(data.error || "Something went wrong");
        renderWeather(data);
    } catch (err) {
        showError(err.message);
    } finally {
        showLoading(false);
    }
});

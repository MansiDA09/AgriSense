import requests
import pandas as pd

# =====================================================
# AGRISENSE
# Historical Agriculture Data + Live Open-Meteo Data
# =====================================================

# -----------------------------------------------------
# 1. LOCATION
# -----------------------------------------------------

CITY = "Bhiwani"
STATE = "Haryana"

LATITUDE = 28.793
LONGITUDE = 76.139791

# -----------------------------------------------------
# 2. READ HISTORICAL AGRICULTURE DATA
# -----------------------------------------------------

historical_file = "data/agridata.csv"

agri_df = pd.read_csv(historical_file)

print("Historical agriculture dataset loaded.")
print(f"Rows: {len(agri_df)}")
print(f"Columns: {list(agri_df.columns)}")

# -----------------------------------------------------
# 3. OPEN-METEO API
# -----------------------------------------------------

url = "https://api.open-meteo.com/v1/forecast"

params = {
    "latitude": LATITUDE,
    "longitude": LONGITUDE,
    "timezone": "Asia/Kolkata",

    "current": [
        "temperature_2m",
        "relative_humidity_2m",
        "rain",
        "wind_speed_10m",
        "soil_temperature_0cm",
        "soil_moisture_0_to_1cm"
    ],

    "daily": [
        "temperature_2m_max",
        "temperature_2m_min",
        "temperature_2m_mean",
        "rain_sum",
        "et0_fao_evapotranspiration",
        "wind_speed_10m_max"
    ],

    "forecast_days": 7
}

response = requests.get(url, params=params, timeout=30)
response.raise_for_status()

weather_data = response.json()

# -----------------------------------------------------
# 4. CURRENT WEATHER
# -----------------------------------------------------

current = weather_data["current"]

current_df = pd.DataFrame([{
    "city": CITY,
    "state": STATE,
    "updated_at": current["time"],
    "temperature_c": current["temperature_2m"],
    "humidity_percent": current["relative_humidity_2m"],
    "rain_mm": current["rain"],
    "wind_kmh": current["wind_speed_10m"],
    "soil_temperature_c": current["soil_temperature_0cm"],
    "soil_moisture": current["soil_moisture_0_to_1cm"]
}])

# -----------------------------------------------------
# 5. 7-DAY FORECAST
# -----------------------------------------------------

daily = weather_data["daily"]

forecast_df = pd.DataFrame({
    "date": daily["time"],
    "max_temp_c": daily["temperature_2m_max"],
    "min_temp_c": daily["temperature_2m_min"],
    "mean_temp_c": daily["temperature_2m_mean"],
    "rainfall_mm": daily["rain_sum"],
    "et0_mm": daily["et0_fao_evapotranspiration"],
    "max_wind_kmh": daily["wind_speed_10m_max"]
})

# -----------------------------------------------------
# 6. HISTORICAL CROP SUMMARY
# -----------------------------------------------------

# Keep the historical dataset untouched.
# This creates a separate summary for analysis.

crop_summary_df = (
    agri_df.groupby("crop", as_index=False)
    .agg(
        records=("crop", "size"),
        total_area=("area", "sum"),
        total_production=("production", "sum"),
        average_yield=("yield", "mean")
    )
    .sort_values("total_production", ascending=False)
)

# -----------------------------------------------------
# 7. BASIC CROP SUITABILITY
# -----------------------------------------------------

temperature = current["temperature_2m"]
soil_moisture = current["soil_moisture_0_to_1cm"]

# Crop rules used only as a prototype.
crop_rules = {
    "Rice": {
        "min_temp": 20,
        "max_temp": 35,
        "min_moisture": 0.20
    },

    "Wheat": {
        "min_temp": 15,
        "max_temp": 25,
        "min_moisture": 0.15
    },

    "Mustard": {
        "min_temp": 10,
        "max_temp": 25,
        "min_moisture": 0.10
    },

    "Cotton": {
        "min_temp": 21,
        "max_temp": 35,
        "min_moisture": 0.10
    },

    "Bajra": {
        "min_temp": 25,
        "max_temp": 35,
        "min_moisture": 0.08
    }
}

# Find which crops from our rules actually exist
# in the historical agriculture dataset.

historical_crops = set(
    agri_df["crop"]
    .dropna()
    .astype(str)
    .str.strip()
    .str.lower()
)

recommendations = []

for crop, rule in crop_rules.items():

    crop_exists = crop.lower() in historical_crops

    temperature_match = (
        rule["min_temp"] <= temperature <= rule["max_temp"]
    )

    moisture_match = soil_moisture >= rule["min_moisture"]

    if crop_exists and temperature_match and moisture_match:

        recommendations.append({
            "city": CITY,
            "state": STATE,
            "crop": crop,
            "status": "Suitable",
            "temperature_c": temperature,
            "soil_moisture": soil_moisture,
            "reason": (
                "Current temperature and soil moisture "
                "match the predefined prototype range."
            )
        })

# -----------------------------------------------------
# 8. CREATE RECOMMENDATION DATAFRAME
# -----------------------------------------------------

if recommendations:

    recommendation_df = pd.DataFrame(recommendations)

else:

    recommendation_df = pd.DataFrame([{
        "city": CITY,
        "state": STATE,
        "crop": "No matching crop",
        "status": "No recommendation",
        "temperature_c": temperature,
        "soil_moisture": soil_moisture,
        "reason": (
            "Current conditions did not match "
            "the predefined prototype ranges."
        )
    }])

# -----------------------------------------------------
# 9. SAVE OUTPUT FILES
# -----------------------------------------------------

current_df.to_csv(
    "data/live_weather.csv",
    index=False
)

forecast_df.to_csv(
    "data/7_day_forecast.csv",
    index=False
)

crop_summary_df.to_csv(
    "data/historical_crop_summary.csv",
    index=False
)

recommendation_df.to_csv(
    "data/crop_recommendation.csv",
    index=False
)

# -----------------------------------------------------
# 10. DISPLAY RESULT
# -----------------------------------------------------

print()
print("==============================================")
print("AGRISENSE UPDATE")
print("==============================================")

print(f"Location: {CITY}, {STATE}")
print(f"Updated: {current['time']}")
print(f"Temperature: {temperature} °C")
print(f"Humidity: {current['relative_humidity_2m']} %")
print(f"Rain: {current['rain']} mm")
print(f"Soil moisture: {soil_moisture}")

print()
print("Crop Suitability:")
print(recommendation_df.to_string(index=False))

print()
print("AgriSense data updated successfully.")

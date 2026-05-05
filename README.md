# 🚢 EU Maritime Compliance Calculator

---

## 📌 Overview

The **EU Maritime Compliance Calculator** is an interactive Streamlit-based application designed to compute **FuelEU Maritime compliance metrics** and **EU ETS (Emissions Trading System) liabilities** for shipping voyages.

The application allows users to input voyage-level fuel consumption data and calculates:
- Compliance balance under FuelEU regulations
- Well-to-Wake (WtW) emission intensities
- EU ETS emission allowances (EUA)
- Estimated penalties for non-compliance

It also integrates **fuel price data** to provide additional cost visibility.

---

## 🎯 Key Features

- 🚢 Voyage-level fuel consumption input
- 🌱 Biofuel blending support
- ⚙️ LNG engine emission configurations
- ❄️ Ice-class adjustment calculations
- 📊 FuelEU compliance balance computation
- 💰 EU ETS (EUA) emissions calculation
- 📉 Penalty estimation based on emissions
- ⛽ Live fuel price table (via daily scraped data)

---

## ⚙️ Tech Stack

- **Python**
- **Streamlit** – Interactive UI
- **Pandas / NumPy** – Data processing
- **Logging** – Application tracking

---

## 🔄 How It Works

1. User inputs voyage details:
   - Fuel types and consumption
   - Biofuel blends
   - LNG engine configurations
   - Ice-class conditions

2. Application processes:
   - Energy consumption (MJ)
   - Emission factors (WtT, TtW)

3. Outputs generated:
   - **Well-to-Tank (WtT) intensity**
   - **Tank-to-Wake (TtW) intensity**
   - **Well-to-Wake (WtW) emissions**
   - **Compliance balance**
   - **Penalty estimation**
   - **EU ETS allowances (EUA)**

---

## 📊 Outputs

- Total Energy in Scope  
- Fuel-wise consumption breakdown  
- GHG intensity metrics (WtT, TtW, WtW)  
- Compliance balance (FuelEU)  
- Estimated penalty (€)  
- EU ETS total EUA  
- Fuel price reference table  

---

## 📁 How to Run

### 🔹 1. Clone Repository
```bash
git clone https://github.com/tanmaymelanta/EUEmissions.git
cd EUEmissions
```

### 🔹 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 🔹 3. Run Application
```bash
streamlit run app.py
```

---

## 📌 Future Enhancements
- Automate fuel price scraping pipeline
- Add scenario comparison (multiple voyages)
- Integrate real-time emissions data sources
- Deploy on cloud (AWS / Streamlit Cloud)
- Add export (PDF / Excel reports)

---

## 👤 Author
Tanmay Melanta
Data Scientist | Data Engineer | Cloud Enthusiast

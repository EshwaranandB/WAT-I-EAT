# WatiEat - India's AI Food Companion 🍲

**WatiEat** is an intelligent, highly-personalized AI food companion built specifically for the Indian context (hostel budgets, regional thalis, street food culture, and diverse dietary needs). 

It was built during the AMD Slingshot Regional Ideathon 2025.

### Features
1. **Hyper Personalization:** Tailors every recommendation based on your region, mood, budget, and goal.
2. **Snap & Know:** Instantly analyzes any Indian food photo, calculating a custom `NourishScore™` and macro breakdown.
3. **Swiggy Interceptor:** Ranks restaurant menu items based on your health goals.
4. **Mood-Food Engine:** Detects your current emotional state and offers healthy swap alternatives for your cravings.
5. **My Thali Builder:** Generates a full 4-meal daily meal plan within your exact ₹ budget constraint.

### Tech Stack
- **Frontend:** Streamlit, Custom CSS (Glassmorphism, Poppins font)
- **AI Brain:** Google Gemini 1.5 Flash (Vision & Text)
- **Data Visualization:** Plotly
- **Hardware Config:** Designed for AMD AI Inference

### How to Run Locally

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Set up your API key:
   Create a `.env` file in the root directory and add:
   ```
   GOOGLE_API_KEY=your_gemini_api_key_here
   ```
3. Run the app:
   ```bash
   streamlit run app.py
   ```

### Demo Mode 🎯
For pitch presenters: You can hit the "🎯 Demo Mode" button in the top right to instantly populate a test user persona and execute a fluid 10-second end-to-end presentation of the product's image analysis engine.

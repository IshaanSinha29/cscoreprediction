# 🏏 T20 Cricket Score Predictor

A web application that predicts the final score of a T20 cricket match using machine learning and Django. The model considers real-time match data such as current score, overs, wickets, and recent performance to project the final score and visualize match progression.

## 📌 Features

- User authentication (Login & Registration)
- Input match data and get score predictions
- Visualizations:
  - Current vs Predicted Score
  - Run Rate Comparison
  - Projected Run Progression Chart
- Model trained using historical T20 match data
- Data preprocessed and passed through a machine learning pipeline

## 🛠️ Tech Stack

- **Backend**: Django
- **Frontend**: HTML, CSS, Bootstrap, Matplotlib
- **Machine Learning**: scikit-learn, Pandas
- **Visualization**: Matplotlib
- **Authentication**: Django Auth


## 🧠 How it Works

1. Users enter match conditions (team, overs, wickets, last 5 overs run).
2. The app processes input and predicts final score using a trained ML model (`pipe.pkl`).
3. Outputs are visualized using Matplotlib.

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Virtualenv (recommended)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/t20-cricket-score-predictor.git
cd t20-cricket-score-predictor

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Run the app
python manage.py runserver

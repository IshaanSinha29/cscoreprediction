from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import urllib, base64
import pickle
import pandas as pd

# Predefined lists of teams and cities
teams = [
    'Australia', 'India', 'Bangladesh', 'New Zealand', 'South Africa',
    'England', 'West Indies', 'Afghanistan', 'Pakistan', 'Sri Lanka'
]

cities = [
    'Colombo', 'Mirpur', 'Johannesburg', 'Dubai', 'Auckland', 'Cape Town',
    'London', 'Pallekele', 'Barbados', 'Sydney', 'Melbourne', 'Durban',
    'St Lucia', 'Wellington', 'Lauderhill', 'Hamilton', 'Centurion',
    'Manchester', 'Abu Dhabi', 'Mumbai', 'Nottingham', 'Southampton',
    
    'Mount Maunganui', 'Chittagong', 'Kolkata', 'Lahore', 'Delhi',
    'Nagpur', 'Chandigarh', 'Adelaide', 'Bangalore', 'St Kitts', 'Cardiff',
    'Christchurch', 'Trinidad'
]

def index(request):
    next_url = request.GET.get('next') or request.POST.get('next') or 'predictor'
    print(">>> next URL received:", next_url)  # Debug print
    
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            print(f">>> Logging in, redirecting to: {next_url}")  # Debug print
            return redirect(next_url)
        else:
            print(">>> Invalid credentials")  # Debug print
            return render(request, "index.html", {"error": "Invalid credentials", "next": next_url})

    return render(request, 'index.html', {'next': next_url})


def registration(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if User.objects.filter(username=username).exists():
            return render(request, 'registration.html', {'error': "Username already exists. Please choose a different one."})
        
        if User.objects.filter(email=email).exists():
            return render(request, 'registration.html', {'error': "Email already registered. Try logging in."})

        try:
            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()
            return redirect('login')
        except IntegrityError:
            return render(request, 'registration.html', {'error': "An error occurred during registration. Try again."})

    return render(request, 'registration.html')

def contact(request):
    return render(request, 'contact.html')

@login_required(login_url='login')
def predictor(request):
    prediction = None
    error_message = None
    chart = None
    runrate_chart = None
    projection_chart = None

    # Default values
    batting_team = ''
    bowling_team = ''
    city = ''
    current_score = 0
    overs = 0.0
    wickets = 0
    last_five = 0

    if request.method == 'POST':
        try:
            # Load model inside the view (optional)
            with open('pipe.pkl', 'rb') as f:
                pipe = pickle.load(f)

            # Get form data
            batting_team = request.POST.get('batting_team')
            bowling_team = request.POST.get('bowling_team')
            city = request.POST.get('city')
            current_score = request.POST.get('current_score', '').strip()
            overs = request.POST.get('overs', '').strip()
            wickets = request.POST.get('wickets', '').strip()
            last_five = request.POST.get('last_five', '').strip()

            # Convert and validate inputs
            current_score = int(current_score) if current_score else 0
            overs = float(overs) if overs else 0.0
            wickets = int(wickets) if wickets else 0
            last_five = int(last_five) if last_five else 0

            if overs <= 0 or overs > 20:
                raise ValueError("Overs must be between 1 and 20.")
            if wickets < 0 or wickets > 10:
                raise ValueError("Wickets must be between 0 and 10.")
            if current_score < 0:
                raise ValueError("Score must be non-negative.")

            # Feature engineering
            balls_left = 120 - int(overs * 6)
            wicket_left = 10 - wickets
            current_run_rate = current_score / overs if overs > 0 else 0

            if current_run_rate > 36:
                error_message = "Can't score that many runs in the given overs."
            else:
                input_df = pd.DataFrame({
                    'batting_team': [batting_team],
                    'bowling_team': [bowling_team],
                    'city': [city],
                    'current_score': [current_score],
                    'balls_left': [balls_left],
                    'wicket_left': [wicket_left],
                    'current_run_rate': [current_run_rate],
                    'last_five': [last_five]
                })

                if wickets == 10 or overs == 20:
                    prediction = current_score
                else:
                    # ML model prediction
                    ml_pred = pipe.predict(input_df)[0]
                    ml_pred = int(ml_pred)

                    # Heuristic projection based on run rate and wickets
                    wickets_factor = 1 - (wickets * 0.05)
                    wickets_factor = max(0.5, wickets_factor)  # min 50%

                    heuristic_proj = int(current_score + (current_run_rate * balls_left / 6) * wickets_factor)

                    max_possible_score = current_score + (balls_left // 6) * 36  # max 36 runs/over

                    # Combine predictions intelligently
                    if ml_pred < current_score:
                        prediction = heuristic_proj
                    elif ml_pred > max_possible_score:
                        prediction = int((ml_pred + heuristic_proj) / 2)
                    else:
                        prediction = int((ml_pred + heuristic_proj) / 2)

                    prediction = max(prediction, current_score)

                # Generate Chart 1: Current vs Predicted Score
                fig, ax = plt.subplots()
                ax.bar(['Current Score', 'Predicted Score'], [current_score, prediction], color=['blue', 'green'])
                ax.set_ylabel('Runs')
                ax.set_title(f'{batting_team} Score Projection')
                plt.tight_layout()
                buf = io.BytesIO()
                plt.savefig(buf, format='png')
                plt.close(fig)
                buf.seek(0)
                chart = urllib.parse.quote(base64.b64encode(buf.read()))

                # Generate Chart 2: Run Rate Comparison
                fig2, ax2 = plt.subplots()
                ax2.bar(['Current RR', 'Projected RR'], [current_run_rate, prediction / 20], color=['orange', 'red'])
                ax2.set_ylabel('Runs per Over')
                ax2.set_title('Run Rate Comparison')
                plt.tight_layout()
                buf2 = io.BytesIO()
                plt.savefig(buf2, format='png')
                plt.close(fig2)
                buf2.seek(0)
                runrate_chart = urllib.parse.quote(base64.b64encode(buf2.read()))

                # Generate Chart 3: Projected Run Progression
                fig3, ax3 = plt.subplots()
                overs_done = int(overs)
                remaining_overs = 20 - overs_done

                if overs >= 20 or wickets >= 10:
                    projected_scores = [current_score if i >= overs_done else None for i in range(1, 21)]
                else:
                    run_pattern = [0.04, 0.05, 0.05, 0.05, 0.06, 0.06, 0.07, 0.07, 0.08, 0.08,
                                0.09, 0.09, 0.1, 0.1, 0.11, 0.11, 0.12, 0.13, 0.14, 0.15]

                    future_pattern = run_pattern[overs_done:]
                    pattern_sum = sum(future_pattern)
                    run_diff = prediction - current_score
                    scaled_runs = [(p / pattern_sum) * run_diff for p in future_pattern]

                    cumulative_score = current_score
                    projected_scores = []
                    for i in range(1, 21):
                        if i <= overs_done:
                            projected_scores.append(None)
                        else:
                            cumulative_score += scaled_runs[i - overs_done - 1]
                            projected_scores.append(int(cumulative_score))

                ax3.plot(range(1, 21), projected_scores, marker='o', linestyle='--', color='purple')
                ax3.axvline(x=overs_done, color='gray', linestyle='--', label='Current Over')
                ax3.set_xlabel('Over')
                ax3.set_ylabel('Projected Score')
                ax3.set_title('Projected Run Progression')
                ax3.legend()
                plt.tight_layout()
                buf3 = io.BytesIO()
                plt.savefig(buf3, format='png')
                plt.close(fig3)
                buf3.seek(0)
                projection_chart = urllib.parse.quote(base64.b64encode(buf3.read()))

        except ValueError as e:
            error_message = str(e)
        except Exception as e:
            error_message = "An unexpected error occurred. Please try again."

    return render(request, "predictor.html", {
        'teams': sorted(teams),
        'cities': sorted(cities),
        'batting_team': batting_team,
        'bowling_team': bowling_team,
        'selected_city': city,
        'current_score': current_score,
        'overs': overs,
        'wickets': wickets,
        'last_five': last_five,
        'prediction': prediction,
        'chart': chart if chart else None,
        'runrate_chart': runrate_chart if runrate_chart else None,
        'projection_chart': projection_chart if projection_chart else None,
        'error_message': error_message,
    })

def about(request):
    return render(request, 'about.html')

def home(request):
    return render(request, 'home.html')

def logout_view(request):
    logout(request)
    return redirect("home")

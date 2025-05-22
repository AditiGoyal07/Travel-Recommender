from flask import Flask, render_template, request
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from geopy.distance import geodesic

app = Flask(__name__)

# Load the dataset
df = pd.read_csv('travel.csv')

# Assume user's current location for distance calculation
user_location = (28.6139, 77.2090)  # Example: Delhi, India

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/recommendation', methods=['POST'])
def recommendation():
    # Get user inputs from the form
    budget = int(request.form['budget'])
    spiritual = int(request.form['spiritual'])
    nightlife = int(request.form['nightlife'])
    crowded = int(request.form['crowded'])
    nature = int(request.form['nature'])

    # Validate the ratings and preferences
    if not (1 <= spiritual <= 5) or not (1 <= nightlife <= 5) or not (1 <= crowded <= 5) or not (1 <= nature <= 5):
        return "Please rate your interests from 1 to 5."

    # Assign ratings and preferences to specific interests
    user_interests = {
        'Spiritual': spiritual,
        'Nightlife': nightlife,
        'Crowded': crowded,
        'Nature': nature
    }
    # ...

#   Filter destinations based on budget
    filtered_destinations = df[df['Average Budget'].between(budget - 1500, budget + 1500)].copy()

#   Check if there are destinations after filtering
    if filtered_destinations.empty:
        return "No destinations found within your budget and preferences."

# ... (continue with the rest of the code)

# Calculate preference score based on user ratings
    filtered_destinations['Preference Score'] = (
        user_interests['Spiritual'] * filtered_destinations['Spiritual'] +
        user_interests['Nightlife'] * filtered_destinations['Nightlife'] +
        user_interests['Crowded'] * filtered_destinations['Crowded'] +
        user_interests['Nature'] * filtered_destinations['Nature']
)

# ... (continue with the rest of the code)

   

    # Use cosine similarity for content-based filtering
    features = filtered_destinations[['Spiritual', 'Nightlife', 'Crowded', 'Nature']]
    user_features = [user_interests['Spiritual'], user_interests['Nightlife'], user_interests['Crowded'],
                     user_interests['Nature']]
    filtered_destinations['Cosine Similarity'] = cosine_similarity(features, [user_features]).flatten()

    # Calculate distance from the user's location
    destination_locations = list(zip(filtered_destinations['Latitude'], filtered_destinations['Longitude']))
    filtered_destinations['Distance'] = [geodesic(user_location, loc).kilometers for loc in destination_locations]

    # Normalize distance and add as a factor
    filtered_destinations['Distance Score'] = 1 / (1 + filtered_destinations['Distance'])
    filtered_destinations['Distance Score'] = (filtered_destinations['Distance Score'] - filtered_destinations['Distance Score'].min()) / (
            filtered_destinations['Distance Score'].max() - filtered_destinations['Distance Score'].min())

    # Combine all scores for final recommendation
    filtered_destinations['Final Score'] = (
        0.5 * filtered_destinations['Preference Score'] +
        0.2 * filtered_destinations['Cosine Similarity'] +
        0.1 * filtered_destinations['Distance Score']
    )

    # Display recommendations sorted by the final score
    if not filtered_destinations.empty:
        top_recommendation = filtered_destinations.sort_values(by='Final Score', ascending=False).iloc[0]
        return render_template('recommendation.html', recommendation=top_recommendation.to_dict())
    else:
        return "No destinations found within your budget and preferences."

if __name__ == '__main__':
    app.run(debug=True, port=5001)


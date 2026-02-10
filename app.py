from flask import Flask, render_template, request, jsonify
import re

app = Flask(__name__)

# Disease Knowledge Base
DISEASE_DATABASE = {
    'common cold': {
        'symptoms': ['runny nose', 'sneezing', 'cough', 'sore throat', 'mild fever', 'congestion', 'headache'],
        'info': 'A viral infection affecting the upper respiratory tract.',
        'recommendations': 'Rest, stay hydrated, use over-the-counter cold medications, and consider vitamin C. Symptoms typically resolve in 7-10 days.',
        'severity': 'mild'
    },
    'flu': {
        'symptoms': ['high fever', 'body aches', 'fatigue', 'chills', 'cough', 'headache', 'weakness', 'muscle pain'],
        'info': 'Influenza is a viral infection that attacks the respiratory system.',
        'recommendations': 'Rest, drink plenty of fluids, take antiviral medications if prescribed within 48 hours, and monitor temperature. Seek medical attention if symptoms worsen.',
        'severity': 'moderate'
    },
    'migraine': {
        'symptoms': ['severe headache', 'nausea', 'light sensitivity', 'sound sensitivity', 'visual disturbances', 'throbbing pain', 'aura'],
        'info': 'A neurological condition causing intense headaches.',
        'recommendations': 'Rest in a dark, quiet room, apply cold compress, stay hydrated, and consider prescribed migraine medication. Identify and avoid triggers.',
        'severity': 'moderate'
    },
    'food poisoning': {
        'symptoms': ['nausea', 'vomiting', 'diarrhea', 'stomach cramps', 'stomach pain', 'fever', 'weakness', 'abdominal pain'],
        'info': 'Illness caused by consuming contaminated food or water.',
        'recommendations': 'Stay hydrated with clear fluids, rest, avoid solid foods initially, and gradually reintroduce bland foods. Seek medical help if symptoms persist beyond 48 hours.',
        'severity': 'moderate'
    },
    'allergies': {
        'symptoms': ['sneezing', 'runny nose', 'itchy eyes', 'watery eyes', 'congestion', 'rash', 'itching', 'hives'],
        'info': 'An immune system response to allergens in the environment.',
        'recommendations': 'Identify and avoid allergens, use antihistamines, keep windows closed during high pollen times, and consider allergy testing.',
        'severity': 'mild'
    },
    'strep throat': {
        'symptoms': ['severe sore throat', 'painful swallowing', 'fever', 'swollen lymph nodes', 'white patches on tonsils', 'headache', 'red throat'],
        'info': 'A bacterial infection causing throat inflammation.',
        'recommendations': 'See a doctor for antibiotic treatment, rest, drink warm liquids, gargle with salt water, and take pain relievers as needed.',
        'severity': 'moderate'
    },
    'asthma': {
        'symptoms': ['wheezing', 'shortness of breath', 'chest tightness', 'coughing', 'difficulty breathing', 'rapid breathing'],
        'info': 'A chronic respiratory condition causing airway inflammation.',
        'recommendations': 'Use prescribed inhalers, avoid triggers, monitor peak flow, and develop an asthma action plan with your doctor.',
        'severity': 'moderate'
    },
    'gastritis': {
        'symptoms': ['stomach pain', 'nausea', 'bloating', 'indigestion', 'burning sensation', 'loss of appetite', 'heartburn'],
        'info': 'Inflammation of the stomach lining.',
        'recommendations': 'Eat smaller meals, avoid spicy and acidic foods, reduce stress, limit alcohol, and consider antacids. See a doctor if symptoms persist.',
        'severity': 'mild'
    },
    'sinusitis': {
        'symptoms': ['facial pain', 'nasal congestion', 'thick nasal discharge', 'headache', 'pressure around eyes', 'reduced sense of smell', 'postnasal drip'],
        'info': 'Inflammation of the sinuses often caused by infection.',
        'recommendations': 'Use saline nasal spray, apply warm compress, stay hydrated, use decongestants, and see a doctor if symptoms last more than 10 days.',
        'severity': 'mild'
    },
    'anxiety': {
        'symptoms': ['excessive worry', 'restlessness', 'rapid heartbeat', 'sweating', 'trembling', 'difficulty concentrating', 'sleep problems', 'panic'],
        'info': 'A mental health condition characterized by persistent worry and fear.',
        'recommendations': 'Practice relaxation techniques, exercise regularly, maintain a healthy sleep schedule, consider therapy or counseling, and speak with a mental health professional.',
        'severity': 'moderate'
    },
    'bronchitis': {
        'symptoms': ['persistent cough', 'mucus production', 'chest discomfort', 'fatigue', 'shortness of breath', 'wheezing', 'low fever'],
        'info': 'Inflammation of the bronchial tubes in the lungs.',
        'recommendations': 'Rest, drink plenty of fluids, use a humidifier, avoid lung irritants, and consider cough suppressants. See a doctor if symptoms persist beyond 3 weeks.',
        'severity': 'mild'
    },
    'urinary tract infection': {
        'symptoms': ['burning urination', 'frequent urination', 'urgent urination', 'cloudy urine', 'pelvic pain', 'blood in urine', 'strong-smelling urine'],
        'info': 'A bacterial infection affecting the urinary system.',
        'recommendations': 'Drink plenty of water, see a doctor for antibiotics, avoid caffeine and alcohol, and urinate frequently. Do not delay treatment.',
        'severity': 'moderate'
    }
}

# Emergency Symptoms
EMERGENCY_SYMPTOMS = [
    'chest pain',
    'difficulty breathing',
    'severe bleeding',
    'loss of consciousness',
    'confusion',
    'sudden severe headache',
    'paralysis',
    'stroke symptoms',
    'heart attack',
    'severe allergic reaction',
    'suicide thoughts',
    'suicidal',
    'severe burn',
    'choking',
    'seizure',
    'poisoning',
    'severe injury',
    'can\'t breathe',
    'cannot breathe',
    'crushing chest pain',
    'slurred speech'
]


@app.route('/')
def index():
    """Render the main chatbot page"""
    return render_template('index.html')


@app.route('/chat', methods=['POST'])
def chat():
    """Process user symptoms and return diagnosis"""
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip().lower()
        
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400
        
        # Check for emergency symptoms
        is_emergency = check_emergency(user_message)
        
        if is_emergency:
            return jsonify({
                'type': 'emergency',
                'message': 'I\'ve detected symptoms that may require immediate medical attention.',
                'emergency_info': {
                    'title': 'EMERGENCY - Seek Immediate Help',
                    'instructions': [
                        'Call 911 or your local emergency number immediately',
                        'Go to the nearest emergency room',
                        'Do NOT wait or try to treat this at home',
                        'If you\'re experiencing a mental health crisis, call 988 (Suicide & Crisis Lifeline)'
                    ]
                }
            })
        
        # Analyze symptoms and find matching diseases
        diagnosis = analyze_symptoms(user_message)
        
        if diagnosis:
            return jsonify({
                'type': 'diagnosis',
                'disease': diagnosis['disease'],
                'info': diagnosis['info'],
                'recommendations': diagnosis['recommendations'],
                'severity': diagnosis['severity'],
                'match_count': diagnosis['match_count']
            })
        else:
            return jsonify({
                'type': 'no_match',
                'message': 'I couldn\'t match your symptoms to a specific condition in my database.',
                'suggestions': [
                    'Monitor your symptoms for any changes',
                    'Keep track of when symptoms started and their severity',
                    'Consider scheduling an appointment with your doctor',
                    'Call your healthcare provider if symptoms worsen'
                ]
            })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def check_emergency(message):
    """Check if message contains emergency symptoms"""
    for symptom in EMERGENCY_SYMPTOMS:
        if symptom in message:
            return True
    return False


def analyze_symptoms(message):
    """Analyze user symptoms and match with disease database"""
    matches = []
    
    for disease_name, disease_data in DISEASE_DATABASE.items():
        match_count = 0
        
        for symptom in disease_data['symptoms']:
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(symptom) + r'\b'
            if re.search(pattern, message):
                match_count += 1
        
        if match_count > 0:
            matches.append({
                'disease': disease_name,
                'match_count': match_count,
                'info': disease_data['info'],
                'recommendations': disease_data['recommendations'],
                'severity': disease_data['severity']
            })
    
    # Sort by match count (highest first)
    matches.sort(key=lambda x: x['match_count'], reverse=True)
    
    # Return the best match
    return matches[0] if matches else None


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
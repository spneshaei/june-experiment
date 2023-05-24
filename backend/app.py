from flask import Flask, jsonify, request 
from flask import url_for, redirect
from flask_cors import CORS
import json
from types import SimpleNamespace
import threading
import time
import openai

case = """Jeder weiß, wie herausfordernd die Organisation eines Ski-Ausflugs mit Freunden sein kann. Die Planung wird oft schon beim ersten Versuch der Terminfindung verworfen. Um diesen Organisationsprozess zu vereinfachen und die belastenden Aspekte eines Ausflugs zu beseitigen, haben wir Alp-Us ins Leben gerufen. Diese App ist die große Neuheit der letzten Jahre im Bereich des Wintersport-Tourismus.

Mit Alp-Us können Sie alle wichtigen Aspekte Ihres Skiurlaubs zentral über eine einzige App planen und organisieren. Sie ist das perfekte Tool, um effizient und schnell den idealen Ausflug für Wintersportbegeisterte zu gestalten. Egal ob Sie einen Ausflug für die Familie, eine Gruppe von Freunden oder im Rahmen eines Firmenevents planen.

In der App können persönliche Gruppen durch einen Einladungslink, der von einem Gruppenleiter bereitgestellt wird, erstellt werden. Nach Erhalt des Einladungslinks registrieren sich die einzelnen Teilnehmer, was nur wenige Minuten dauert. Während der Registrierung werden alle nötigen Informationen, wie beispielsweise Verfügbarkeit, Skigebiet-Präferenzen oder Mobilitätsoptionen der einzelnen Gruppenmitglieder individuell abgefragt. Dies dient als Grundlage für optimale Vorschläge der Buchungs-Module durch Alp-Us.

Auf Basis dieser Daten erstellt Alp-Us kombinierbare Vorschläge bezüglich Skigebieten, Unterkünften, Gastronomie und dem Transport zur An- und Abreise, welche direkt in der App durch den vorbestimmten Gruppenleiter zusammengestellt und gebucht werden können. Es ist zudem möglich, dass Sie lediglich Skigebiet, Unterkunft und Gastronomie über Alp-Us buchen und den Transport eigenständig organisieren, beispielsweise mit dem eigenen Fahrzeug.

Alle Buchungen und Tickets, welche heute noch ohne Alp-Us über verschiedene Plattformen und Anbieter organisiert werden müssen, können zentral über Alp-Us gebucht und jederzeit über das Mobiltelefon jedes Gruppenmitglieds abgerufen werden.

Für teilnehmende Unternehmen wie Hotels, Skigebiete oder Restaurants bietet sich die Möglichkeit, sich nicht nur über einen weiteren Kanal zu präsentieren, sondern auch spezifische Kundensegmente effizienter zu erreichen als über traditionelle Kanäle. Zudem besteht die Möglichkeit, spezielle Angebote gegen Bezahlung prominenter zu platzieren und somit eine höhere Conversion Rate durch Reservierungen und Buchungen zu erreichen.

Unser Ziel ist es, ein vollends befriedigendes Gesamtergebnis für den Kunden zu bieten. Dadurch ermöglichen wir das optimale Matching zwischen Kunden und Partnerunternehmen über unsere Plattform und generieren Netzwerkeffekte für alle Beteiligten. Je mehr Leistungen schlussendlich gebucht werden, desto mehr Gebühren fließen an die Plattform zurück. Deshalb ist das grundlegende Ziel von Alp-Us, möglichst optimale Vorschläge zu generieren, so dass möglichst viele Teilleistungen des Service-Angebots gebucht werden."""
       

with open("api_key.txt", "r") as f:
    openai.api_key = f.read().strip()

lock = threading.Lock()

app = Flask(__name__, static_url_path='/static')
CORS(app)

def load_data_from_file(file_name):
    with open(file_name + "-writingtheory.json", "r") as f:
        return json.loads(f.read(), object_hook = lambda d: SimpleNamespace(**d))

def save_data_to_file(file_name, data):
    with open(file_name + "-writingtheory.json", "w") as f:
        f.write(json.dumps(data, default=lambda o: o.__dict__, indent=4))

def save_error_log(error):
    error_data = load_data_from_file("errors")
    error_data.append({"error": error, "time": int(time.time())})
    save_data_to_file("error", error_data)

def getIdeationFromGPT(review):
    global case
    msg = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        max_tokens=40,
        temperature=0,
        messages=[
            {"role": "system", "content": "You provide one example idea per response. Give only the idea without any preamble or comment. Be as brief as possible."},
            {"role": "user", "content": "I need an idea on what to include in my review of this business case: " + case},
            {"role": "assistant", "content": "The feedback may include an evaluation of aspects like the effectiveness of the app in simplifying and streamlining the organization of ski trips."},
            {"role": "user", "content": "Give me another idea."},
            {"role": "assistant", "content": "The feedback may question how well the app integrates with various booking platforms and providers to offer a seamless experience for users."},
            {"role": "user", "content": "Give me another idea that I have not used yet. This is the review so far:" + str(review)},
            {"role": "system", "content": "All responses must be in German now."},
        ]
    )
    result = msg['choices'][0]['message']['content']
    return result

def getEvaluationFromGPT(review):
    global case
    msg = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        max_tokens=40,
        temperature=0,
        # top_p=0,
        messages=[
            {"role": "system", "content": "You evaluate text and give one suggestion for improvement. Give only the suggestion without any preamble or comment. Be as brief as possible."},
            {"role": "user", "content": "I need a feedback suggestion to improve my review of this business case: " + case},
            {"role": "assistant", "content": "Avoid repetition. Instead consolidate similar points for greater clarity and conciseness."},
            {"role": "user", "content": "Do the same but with a new suggestion."},
            {"role": "assistant", "content": "Try to rephrase your feedback in a more measured way. Talk about the case instead of how you personally feel about it."},
            {"role": "user", "content": "Do the same but with a new suggestion. This is the review so far:" + str(review)},
            {"role": "system", "content": "All responses must be in German now."},
        ]
    )
    return msg['choices'][0]['message']['content']

def getGoalSettingFromGPT(review):
    global case
    msg = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    max_tokens=40,
    temperature=0,
    # top_p=0,
    messages=[
        {"role": "system", "content": "You suggest the next goal that should be worked on in writing the text. Give only the suggestion without any preamble or comment. Be as brief as possible. Respond in German."},
        {"role": "user", "content": "What should I work on next to improve my review of this business case: " + case},
        {"role": "assistant", "content": "Start to brainstorm for strengths and weaknesses of the review."},
        {"role": "user", "content": "Do the same but with a new writing subgoal."},
        {"role": "assistant", "content": "Use simple language to get your point across."},
        {"role": "user", "content": "Do the same but with a new writing subgoal. This is the review so far:" + str(review)},
        {"role": "system", "content": "All responses must be in German now."},
        ]
    )
    return msg['choices'][0]['message']['content']

def getOrganizingFromGPT(review):
    msg = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    max_tokens=40,
    temperature=0,
    # top_p=0,
    messages=[
            {"role": "system", "content": "You suggest how to reorder the text. Give only the suggestion without any preamble or comment. Be as brief as possible. Respond in German."},
            {"role": "user", "content": "This is the business case I am reviewing. How should I arrange my ideas: " + case},
            {"role": "assistant", "content": "Start off with a short summary."},
            {"role": "user", "content": "Do the same but with a new suggestion on how to order the ideas in the text."},
            {"role": "assistant", "content": "Go from general to more specific ideas over the course of the paragraph."},
            {"role": "user", "content": "Do the same but with a new suggestion on how to order the ideas in the text. This is the review so far:" + str(review)},
            {"role": "system", "content": "All responses must be in German now."},
        ]
    )
    return msg['choices'][0]['message']['content']

@app.route('/')
def home():
    return redirect(url_for('static', filename='index.html'))

@app.route('/getNewIdeation', methods=['POST'])
def getNewIdeation():
    username = request.json['username']
    text = request.json['text']
    lock.acquire()
    try:
        new_gpt = getIdeationFromGPT(text)
        each_gpt_data = load_data_from_file("each_gpt")
        each_gpt_data.append({"username": username, "text": text, "type": "ideation", "gpt": new_gpt, "time": int(time.time())})
        save_data_to_file("each_gpt", each_gpt_data)
        lock.release()
        return jsonify({"success": True, "gpt": new_gpt})
    except Exception as e:
        print(e)
        save_error_log("getNewIdeation")
        lock.release()
        return jsonify({"success": False, "gpt": ""})

@app.route('/getNewEvaluation', methods=['POST'])
def getNewEvaluation():
    username = request.json['username']
    text = request.json['text']
    lock.acquire()
    try:
        new_gpt = getEvaluationFromGPT(text)
        each_gpt_data = load_data_from_file("each_gpt")
        each_gpt_data.append({"username": username, "text": text, "type": "evaluation", "gpt": new_gpt, "time": int(time.time())})
        save_data_to_file("each_gpt", each_gpt_data)
        lock.release()
        return jsonify({"success": True, "gpt": new_gpt})
    except Exception as e:
        print(e)
        save_error_log("getNewEvaluation")
        lock.release()
        return jsonify({"success": False, "gpt": ""})

@app.route('/getNewGoalSetting', methods=['POST'])
def getNewGoalSetting():
    username = request.json['username']
    text = request.json['text']
    lock.acquire()
    try:
        new_gpt = getGoalSettingFromGPT(text)
        each_gpt_data = load_data_from_file("each_gpt")
        each_gpt_data.append({"username": username, "text": text, "type": "goal_setting", "gpt": new_gpt, "time": int(time.time())})
        save_data_to_file("each_gpt", each_gpt_data)
        lock.release()
        return jsonify({"success": True, "gpt": new_gpt})
    except Exception as e:
        print(e)
        save_error_log("getNewGoalSetting")
        lock.release()
        return jsonify({"success": False, "gpt": ""})

@app.route('/getNewOrganizing', methods=['POST'])
def getNewOrganizing():
    username = request.json['username']
    text = request.json['text']
    lock.acquire()
    try:
        new_gpt = getOrganizingFromGPT(text)
        each_gpt_data = load_data_from_file("each_gpt")
        each_gpt_data.append({"username": username, "text": text, "type": "organizing", "gpt": new_gpt, "time": int(time.time())})
        save_data_to_file("each_gpt", each_gpt_data)
        lock.release()
        return jsonify({"success": True, "gpt": new_gpt})
    except Exception as e:
        print(e)
        save_error_log("getNewOrganizing")
        lock.release()
        return jsonify({"success": False, "gpt": ""})

@app.route('/submit', methods=['POST'])
def submit():
    text = request.json['text']
    username = request.json['username']
    studyGroup = request.json['studyGroup']
    keystrokes = request.json['keystrokes']
    buttonTaps = request.json['buttonTaps']
    lock.acquire()
    try:
        submissions_data = load_data_from_file("submissions")
        submissions_data.append({"username": username, "text": text, "studyGroup": studyGroup, "time": int(time.time())})
        save_data_to_file("submissions", submissions_data)
    except Exception as e:
        print(e)
        save_error_log("submit-submissions")
        lock.release()
        return jsonify({"success": False})

    try:
        keystrokes_data = load_data_from_file("keystrokes")
        keystrokes_data.append({"username": username, "keystrokes": keystrokes, "time": int(time.time())})
        save_data_to_file("keystrokes", keystrokes_data)
    except Exception as e:
        print(e)
        save_error_log("submit-keystrokes")

    if len(buttonTaps) > 0:
        try:
            buttonTaps_data = load_data_from_file("buttonTaps")
            buttonTaps_data.append({"username": username, "buttonTaps": buttonTaps, "time": int(time.time())})
            save_data_to_file("buttonTaps", buttonTaps_data)
        except Exception as e:
            print(e)
            save_error_log("submit-buttonTaps")

    lock.release()
    return jsonify({"success": True})

if __name__ == '__main__':
    app.run(host = '0.0.0.0', port = 5001, debug = True)

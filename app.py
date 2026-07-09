import os
from flask import Flask, jsonify, render_template, request
from dotenv import load_dotenv

from db.supabase_client import insert_application, insert_guarantor, insert_hod, insert_hr, insert_risk

load_dotenv()

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('Stafform.html')


@app.route('/staff-form')
def staff_form():
    return render_template('Stafform.html')


@app.route('/g1-form')
def guarantor1_form():
    return render_template('G1form.html')


@app.route('/g2-form')
def guarantor2_form():
    return render_template('G2form.html')


@app.route('/hod-form')
def hod_form():
    return render_template('HODform.html')


@app.route('/hr-form')
def hr_form():
    return render_template('HRform.html')


@app.route('/risk-form')
def risk_form():
    return render_template('Riskform.html')


@app.route('/api/submit-loan', methods=['POST'])
def submit_loan():
    data = request.get_json(silent=True) or {}
    try:
        result = insert_application(data)
        return jsonify({"message": "Application saved successfully.", "applicationId": result.get("application_id"), "data": result}), 201
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400


@app.route('/api/submit-guarantor/<int:seq_id>', methods=['POST'])
def submit_guarantor(seq_id: int):
    data = request.get_json(silent=True) or {}
    try:
        result = insert_guarantor(data, seq_id)
        return jsonify({"message": f"Guarantor {seq_id} saved successfully.", "data": result}), 201
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400


@app.route('/api/submit-hod', methods=['POST'])
def submit_hod():
    data = request.get_json(silent=True) or {}
    try:
        result = insert_hod(data)
        return jsonify({"message": "HOD review saved successfully.", "data": result}), 201
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400


@app.route('/api/submit-hr', methods=['POST'])
def submit_hr():
    data = request.get_json(silent=True) or {}
    try:
        result = insert_hr(data)
        return jsonify({"message": "HR review saved successfully.", "data": result}), 201
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400


@app.route('/api/submit-risk', methods=['POST'])
def submit_risk():
    data = request.get_json(silent=True) or {}
    try:
        result = insert_risk(data)
        return jsonify({"message": "Risk review saved successfully.", "data": result}), 201
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400


if __name__ == '__main__':
    app.run(debug=True, port=5000)
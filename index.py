from numbers import Number
import os
from datetime import datetime
from typing import Any, Dict
from uuid import uuid4

from flask import Flask, jsonify, render_template, request
from dotenv import load_dotenv
from supabase import Client, create_client

# Load a local .env during development only; Vercel provides envs in production
load_dotenv(override=False)

# --- Supabase client setup ---
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client | None = None
if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def _ensure_client() -> Client:
    if supabase is None:
        raise RuntimeError("SUPABASE_URL and SUPABASE_KEY must be set in the environment")
    return supabase


def _generate_application_no() -> str:
    return f"SLA-{datetime.now().strftime('%Y%m%d')}-{uuid4().hex[:4].upper()}"


def insert_application(payload: Dict[str, Any]) -> Dict[str, Any]:
    record = {
        "application_no": payload.get("applicationNo") or payload.get("application_no") or _generate_application_no(),
        "staff_id": payload.get("staffId"),
        "staff_name": payload.get("staffName"),
        "position_title": payload.get("position"),
        "department_name": payload.get("department"),
        "nrc_no": payload.get("nrc"),
        "father_name": payload.get("fatherName"),
        "father_nrc_no": payload.get("fatherNRC"),
        "permanent_address": payload.get("address"),
        "phone_no": payload.get("phone"),
        "gross_salary": Number(payload.get("salary")),
        "loan_type": payload.get("loanType"),
        "loan_amount": Number(payload.get("loanAmount")),
        "salary_multiple": payload.get("salaryMultiple") or 1,
        "cb_account_no": payload.get("accountNo"),
        "guarantor1_name": payload.get("guarantor1Name"),
        "guarantor1_email": payload.get("guarantor1Email"),
        "guarantor2_name": payload.get("guarantor2Name"),
        "guarantor2_email": payload.get("guarantor2Email"),
        "hod_name": payload.get("hodName"),
        "hod_email": payload.get("hodEmail"),
        "applicant_agreement": bool(payload.get("applicantAgreement") or payload.get("agreement") == "agree"),
        "declaration_1": bool(payload.get("declaration1") or payload.get("declaration_1")),
        "declaration_2": bool(payload.get("declaration2") or payload.get("declaration_2")),
        "declaration_3": bool(payload.get("declaration3") or payload.get("declaration_3")),
        "declaration_4": bool(payload.get("declaration4") or payload.get("declaration_4")),
        "overall_status": payload.get("overallStatus") or "PENDING",
        "created_by": payload.get("createdBy") or payload.get("staffId"),
    }
    response = _ensure_client().table("staff_loan_application").insert(record).execute()
    return response.data[0] if response.data else {}


def insert_guarantor(payload: Dict[str, Any], seq_id: int) -> Dict[str, Any]:
    record = {
        "application_id": int(payload.get("applicationId")),
        "guarantor_seq": seq_id,
        "guarantor_staff_id": payload.get("guarantorStaffId") or payload.get("guarantorId") or payload.get("guarantor2Id"),
        "guarantor_name": payload.get("guarantorName") or payload.get("guarantor2Name"),
        "guarantor_email": payload.get("guarantorEmail") or "",
        "position_title": payload.get("positionTitle") or payload.get("guarantorPosition") or payload.get("guarantor2Position"),
        "nrc_no": payload.get("nrcNo") or payload.get("guarantorNrc") or payload.get("guarantor2Nrc"),
        "father_name": payload.get("fatherName") or payload.get("guarantorFather") or payload.get("guarantor2Father"),
        "department_name": payload.get("departmentName") or payload.get("guarantorDepartment") or payload.get("guarantor2Department"),
        "permanent_address": payload.get("permanentAddress") or payload.get("guarantorAddress") or payload.get("guarantor2Address"),
        "declaration_agreed": bool(payload.get("declarationAgreed") or payload.get("declarationCheck")),
        "approval_status": payload.get("approvalStatus") or "PENDING",
        "remarks": payload.get("remarks") or payload.get("actionStatus"),
    }
    response = _ensure_client().table("staff_loan_guarantor").insert(record).execute()
    return response.data[0] if response.data else {}


def insert_hod(payload: Dict[str, Any]) -> Dict[str, Any]:
    record = {
        "application_id": int(payload.get("applicationId")),
        "hod_name": payload.get("hodName"),
        "hod_position": payload.get("hodPosition"),
        "hod_department": payload.get("hodDepartment"),
        "hod_email": payload.get("hodEmail") or "",
        "remarks": payload.get("remarks"),
        "declaration_agreed": bool(payload.get("declarationAgreed") or payload.get("declarationCheck")),
        "approval_status": payload.get("approvalStatus") or ("APPROVED" if payload.get("actionStatus") == "Approve" else "REJECTED"),
    }
    response = _ensure_client().table("staff_loan_hod_approval").insert(record).execute()
    return response.data[0] if response.data else {}


def insert_hr(payload: Dict[str, Any]) -> Dict[str, Any]:
    record = {
        "application_id": int(payload.get("applicationId")),
        "hr_name": payload.get("hrName"),
        "hr_department": payload.get("hrDepartment"),
        "hr_remarks": payload.get("hrRemarks") or payload.get("remarks"),
        "declaration_agreed": bool(payload.get("declarationAgreed") or payload.get("checkConfirm")),
        "approval_status": payload.get("approvalStatus") or ("APPROVED" if payload.get("actionDecision") == "Approved" else "REJECTED"),
    }
    response = _ensure_client().table("staff_loan_hr_approval").insert(record).execute()
    return response.data[0] if response.data else {}


def insert_risk(payload: Dict[str, Any]) -> Dict[str, Any]:
    record = {
        "application_id": int(payload.get("applicationId")),
        "staff_loan_record": payload.get("staffLoanRecord"),
        "gm_name": payload.get("gmName"),
        "loan_record_no": payload.get("loanRecordNo"),
        "loan_id": payload.get("loanId"),
        "loan_ld_no": payload.get("loanLdNo"),
        "approved_amount": float(payload.get("approvedAmount") or 0),
        "risk_remark": payload.get("riskRemark"),
        "approval_status": payload.get("approvalStatus") or ("APPROVED" if payload.get("actionDecision") == "Approved" else "REJECTED"),
    }
    response = _ensure_client().table("staff_loan_risk_approval").insert(record).execute()
    return response.data[0] if response.data else {}


# --- Flask app and routes ---
app = Flask(__name__)


@app.route('/')
def index_view():
    # Try to fetch something from Supabase; if envs missing, show helpful message
    try:
        client = _ensure_client()
    except Exception as exc:
        return (
            f"<h1>Configuration error</h1><p>{exc}</p>"
            "<p>Set SUPABASE_URL and SUPABASE_KEY in environment variables.</p>",
            500,
        )

    try:
        response = client.table('staff_loan_application').select('*').limit(10).execute()
        records = response.data or []
    except Exception as db_exc:
        return (
            f"<h1>Database error</h1><p>{db_exc}</p>",
            500,
        )

    # Simple rendered output for quick verification
    html = '<h1>Recent Applications</h1><ul>'
    for r in records:
        html += f"<li>{r.get('application_no') or r.get('staff_name') or r.get('id')}</li>"
    html += '</ul>'
    return html


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


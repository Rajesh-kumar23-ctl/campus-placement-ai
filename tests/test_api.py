import os
import time
import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

# Global test state
auth_token = None
user_id = None
aptitude_attempt_id = None
gd_session_id = None
interview_session_id = None
resume_id = None
simulation_id = None

def get_auth_headers():
    return {"Authorization": f"Bearer {auth_token}"}


class TestHealth:
    def test_health_check(self):
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "AI Placement Coach" in data["app"]


class TestAuth:
    def test_register(self):
        global auth_token, user_id
        email = f"student_{int(time.time() * 1000)}@campus.edu"
        payload = {
            "name": "Rajesh Kumar",
            "email": email,
            "password": "Password123!",
            "college": "National Institute of Technology",
            "degree": "B.Tech",
            "branch": "Computer Science and Engineering",
            "graduation_year": 2026
        }
        response = client.post("/api/auth/register", json=payload)
        assert response.status_code == 201, response.text
        data = response.json()
        assert "access_token" in data
        assert data["user"]["email"] == email
        assert data["user"]["name"] == "Rajesh Kumar"
        auth_token = data["access_token"]
        user_id = data["user"]["id"]

    def test_login_invalid(self):
        response = client.post("/api/auth/login", json={
            "email": "nonexistent@campus.edu",
            "password": "WrongPassword!"
        })
        assert response.status_code == 401

    def test_get_me(self):
        response = client.get("/api/auth/me", headers=get_auth_headers())
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == user_id
        assert data["name"] == "Rajesh Kumar"


class TestDashboard:
    def test_dashboard_metrics(self):
        response = client.get("/api/dashboard", headers=get_auth_headers())
        assert response.status_code == 200
        data = response.json()
        assert data["user_name"] == "Rajesh Kumar"
        assert "readiness_percentage" in data
        assert "category_scores" in data
        assert "aptitude" in data["category_scores"]
        assert "gd" in data["category_scores"]
        assert "technical" in data["category_scores"]
        assert "hr" in data["category_scores"]
        assert "communication" in data["category_scores"]
        assert "recent_activities" in data
        assert "recommendations" in data


class TestAptitude:
    def test_get_categories(self):
        response = client.get("/api/aptitude/categories", headers=get_auth_headers())
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 4
        ids = [c["id"] for c in data]
        assert "quantitative" in ids
        assert "logical" in ids
        assert "verbal" in ids
        assert "data_interpretation" in ids

    def test_start_and_submit_aptitude(self):
        global aptitude_attempt_id
        # Start test
        payload = {
            "category": "quantitative",
            "difficulty": "medium",
            "num_questions": 5,
            "timer_minutes": 10
        }
        res_start = client.post("/api/aptitude/start", json=payload, headers=get_auth_headers())
        assert res_start.status_code == 200, res_start.text
        questions = res_start.json()
        assert isinstance(questions, list)
        assert len(questions) == 5

        # Submit test answers
        answers = []
        for q in questions:
            answers.append({
                "question_id": q["id"],
                "selected_answer": "B",
                "time_taken": 20
            })

        submit_payload = {
            "category": "quantitative",
            "difficulty": "medium",
            "time_taken": 100,
            "answers": answers
        }
        res_submit = client.post("/api/aptitude/submit", json=submit_payload, headers=get_auth_headers())
        assert res_submit.status_code == 200, res_submit.text
        res_data = res_submit.json()
        assert "id" in res_data
        aptitude_attempt_id = res_data["id"]
        assert "score" in res_data
        assert res_data["total_questions"] == 5
        assert "correct_answers" in res_data
        assert len(res_data["review"]) == 5

        # Fetch results by id
        res_get = client.get(f"/api/aptitude/results/{aptitude_attempt_id}", headers=get_auth_headers())
        assert res_get.status_code == 200
        assert res_get.json()["id"] == aptitude_attempt_id


class TestGroupDiscussion:
    def test_get_topics(self):
        response = client.get("/api/gd/topics", headers=get_auth_headers())
        assert response.status_code == 200
        topics = response.json()
        assert len(topics) >= 10
        assert "topic" in topics[0]
        assert "category" in topics[0]

    def test_generate_custom_gd(self):
        payload = {
            "topic": "Ethics of Autonomous AI Agents in Workplace",
            "category": "Technology"
        }
        response = client.post("/api/gd/generate", json=payload, headers=get_auth_headers())
        assert response.status_code == 200
        data = response.json()
        assert "topic" in data
        assert "opening_statement" in data
        assert "key_arguments_for" in data
        assert "key_arguments_against" in data
        assert "conclusion" in data

    def test_gd_simulator_flow(self):
        global gd_session_id
        # 1. Start simulation
        start_payload = {
            "topic": "Remote Work vs Office Work: The Future of IT",
            "num_participants": 3,
            "duration_minutes": 10,
            "difficulty": "Medium"
        }
        res_start = client.post("/api/gd/start", json=start_payload, headers=get_auth_headers())
        assert res_start.status_code == 200, res_start.text
        start_data = res_start.json()
        gd_session_id = start_data["session_id"]
        assert len(start_data["initial_messages"]) >= 2

        # 2. User responds
        user_msg_payload = {
            "session_id": gd_session_id,
            "user_response": "I agree with the point on productivity. However, mentorship for junior engineers is significantly more effective when collaborating in person."
        }
        res_msg = client.post("/api/gd/respond", json=user_msg_payload, headers=get_auth_headers())
        assert res_msg.status_code == 200, res_msg.text
        msg_data = res_msg.json()
        assert len(msg_data["ai_responses"]) >= 1

        # 3. Evaluate session
        eval_payload = {
            "session_id": gd_session_id
        }
        res_eval = client.post("/api/gd/evaluate", json=eval_payload, headers=get_auth_headers())
        assert res_eval.status_code == 200, res_eval.text
        eval_data = res_eval.json()
        assert "overall" in eval_data
        assert "content" in eval_data
        assert "relevance" in eval_data
        assert "clarity" in eval_data
        assert "structure" in eval_data
        assert "fluency" in eval_data
        assert len(eval_data["strengths"]) > 0
        assert len(eval_data["improvements"]) > 0


class TestInterview:
    def test_interview_flow(self):
        global interview_session_id
        # 1. Start interview
        start_payload = {
            "interview_type": "cloud_engineer",
            "target_role": "Cloud Engineer",
            "difficulty": "medium",
            "experience_level": "entry",
            "use_resume": False
        }
        res_start = client.post("/api/interview/start", json=start_payload, headers=get_auth_headers())
        assert res_start.status_code == 200, res_start.text
        start_data = res_start.json()
        interview_session_id = start_data["session_id"]
        assert "first_question" in start_data
        question_id = start_data["first_question"]["question_id"]

        # 2. Answer question
        ans_payload = {
            "session_id": interview_session_id,
            "question_id": question_id,
            "answer": "In AWS, Amazon EC2 provides scalable virtual computing instances with full OS-level control, whereas AWS Lambda is a serverless compute service that runs code in response to events without provisioning servers."
        }
        res_ans = client.post("/api/interview/answer", json=ans_payload, headers=get_auth_headers())
        assert res_ans.status_code == 200, res_ans.text
        ans_data = res_ans.json()
        assert "feedback" in ans_data
        assert "technical_accuracy" in ans_data
        assert "next_question" in ans_data

        # 3. End interview and get evaluation
        end_payload = {
            "session_id": interview_session_id
        }
        res_end = client.post("/api/interview/end", json=end_payload, headers=get_auth_headers())
        assert res_end.status_code == 200, res_end.text
        end_data = res_end.json()
        assert "score" in end_data
        assert "technical_accuracy" in end_data
        assert "communication" in end_data
        assert "strengths" in end_data
        assert "improvements" in end_data

        # 4. Fetch session details
        res_get = client.get(f"/api/interview/{interview_session_id}", headers=get_auth_headers())
        assert res_get.status_code == 200
        assert res_get.json()["id"] == interview_session_id


class TestResume:
    def test_resume_upload_and_questions(self):
        global resume_id
        # Upload sample resume file
        content = b"Rajesh Kumar - Computer Science Graduate\nSkills: Python, FastAPI, Docker, AWS, PostgreSQL\nProjects: Built cloud microservices on AWS EC2 and RDS with CI/CD GitHub Actions\nEducation: B.Tech CSE (2026)"
        files = {
            "file": ("resume.txt", content, "text/plain")
        }
        response = client.post("/api/resume/upload", files=files, headers=get_auth_headers())
        assert response.status_code == 200, response.text
        data = response.json()
        resume_id = data["id"]
        assert len(data["skills"]) > 0

        # Get resume
        res_get = client.get(f"/api/resume/{resume_id}", headers=get_auth_headers())
        assert res_get.status_code == 200
        assert res_get.json()["id"] == resume_id

        # Generate interview questions based on resume
        res_q = client.post("/api/resume/questions", json={"resume_id": resume_id}, headers=get_auth_headers())
        assert res_q.status_code == 200
        q_data = res_q.json()
        assert "questions" in q_data
        assert len(q_data["questions"]) >= 3


class TestCompanies:
    def test_get_companies(self):
        response = client.get("/api/companies", headers=get_auth_headers())
        assert response.status_code == 200
        companies = response.json()
        assert len(companies) >= 10
        names = [c["name"] for c in companies]
        assert any("Amazon" in n for n in names)
        assert any("TCS" in n or "Tata" in n for n in names)
        assert any("Google" in n for n in names)

    def test_get_company_detail(self):
        companies = client.get("/api/companies", headers=get_auth_headers()).json()
        company_id = companies[0]["id"]
        response = client.get(f"/api/companies/{company_id}", headers=get_auth_headers())
        assert response.status_code == 200
        detail = response.json()
        assert detail["id"] == company_id
        assert "preparation_areas" in detail
        assert "sample_questions" in detail


class TestProgress:
    def test_get_progress_summary(self):
        response = client.get("/api/progress", headers=get_auth_headers())
        assert response.status_code == 200
        data = response.json()
        assert "readiness_score" in data
        assert "skill_radar" in data
        assert "performance_over_time" in data
        assert "recommendations" in data

    def test_get_sub_progress(self):
        res_apt = client.get("/api/progress/aptitude", headers=get_auth_headers())
        assert res_apt.status_code == 200
        res_gd = client.get("/api/progress/gd", headers=get_auth_headers())
        assert res_gd.status_code == 200
        res_int = client.get("/api/progress/interview", headers=get_auth_headers())
        assert res_int.status_code == 200


class TestPlacementSimulation:
    def test_full_simulation_drive(self):
        global simulation_id
        # 1. Start simulation
        start_payload = {
            "target_role": "Associate Software Engineer",
            "company_focus": "Amazon"
        }
        res_start = client.post("/api/simulation/start", json=start_payload, headers=get_auth_headers())
        assert res_start.status_code == 200, res_start.text
        sim_data = res_start.json()
        simulation_id = sim_data["simulation_id"]
        assert sim_data["current_round"] == "aptitude"

        # 2. Complete Aptitude Round
        round_1 = client.post("/api/simulation/complete-round", json={
            "simulation_id": simulation_id,
            "round_type": "aptitude",
            "round_score": 85.0,
            "round_data": {"correct": 17, "total": 20}
        }, headers=get_auth_headers())
        assert round_1.status_code == 200, round_1.text
        assert round_1.json()["current_round"] == "gd"

        # 3. Complete GD Round
        round_2 = client.post("/api/simulation/complete-round", json={
            "simulation_id": simulation_id,
            "round_type": "gd",
            "round_score": 78.0,
            "round_data": {"content": 8, "relevance": 8, "clarity": 7}
        }, headers=get_auth_headers())
        assert round_2.status_code == 200, round_2.text
        assert round_2.json()["current_round"] == "technical"

        # 4. Complete Technical Round
        round_3 = client.post("/api/simulation/complete-round", json={
            "simulation_id": simulation_id,
            "round_type": "technical",
            "round_score": 82.0,
            "round_data": {"technical_accuracy": 8, "system_design": 8}
        }, headers=get_auth_headers())
        assert round_3.status_code == 200, round_3.text
        assert round_3.json()["current_round"] == "hr"

        # 5. Complete HR Round
        round_4 = client.post("/api/simulation/complete-round", json={
            "simulation_id": simulation_id,
            "round_type": "hr",
            "round_score": 88.0,
            "round_data": {"behavioral": 9, "culture_fit": 9}
        }, headers=get_auth_headers())
        assert round_4.status_code == 200, round_4.text
        assert round_4.json()["status"] == "completed"

        # 6. Final report
        res_report = client.post("/api/simulation/final-report", json={
            "simulation_id": simulation_id
        }, headers=get_auth_headers())
        assert res_report.status_code == 200, res_report.text
        rep_data = res_report.json()
        assert "overall_score" in rep_data
        assert rep_data["aptitude_score"] == 85.0
        assert rep_data["gd_score"] == 78.0
        assert rep_data["technical_score"] == 82.0
        assert rep_data["hr_score"] == 88.0
        assert len(rep_data["strengths"]) > 0
        assert len(rep_data["weak_areas"]) > 0
        assert len(rep_data["recommendations"]) > 0

        # 7. Get simulation by id
        res_get = client.get(f"/api/simulation/{simulation_id}", headers=get_auth_headers())
        assert res_get.status_code == 200
        assert res_get.json()["id"] == simulation_id


class TestMaterials:
    def test_list_materials_default(self):
        response = client.get("/api/materials")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 500
        assert len(data["materials"]) == 24
        assert data["page"] == 1
        assert "drive_root_url" in data
        assert "1NC5wLHUMUye5_5zHzSgTgXDUdVmh43ZU" in data["drive_root_url"]
        first = data["materials"][0]
        assert "id" in first
        assert "title" in first
        assert "company" in first
        assert "view_url" in first
        assert "download_url" in first
        assert "format" in first

    def test_materials_company_filter(self):
        response = client.get("/api/materials?company=INFOSYS&limit=10")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 100
        for item in data["materials"]:
            assert item["company"] == "INFOSYS"

    def test_materials_search(self):
        response = client.get("/api/materials?search=paper")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] > 0
        for item in data["materials"]:
            matches = "paper" in item["title"].lower() or "paper" in item["description"].lower() or any("paper" in t.lower() for t in item["tags"]) or "paper" in item["filename"].lower()
            assert matches

    def test_material_companies_summary(self):
        response = client.get("/api/materials/companies")
        assert response.status_code == 200
        companies = response.json()
        assert len(companies) >= 15
        company_names = [c["company"] for c in companies]
        assert "INFOSYS" in company_names
        assert "CAPGEMINI" in company_names
        assert "ACCENTURE" in company_names
        assert "General / Core CS" in company_names

    def test_material_categories(self):
        response = client.get("/api/materials/categories")
        assert response.status_code == 200
        data = response.json()
        assert "categories" in data
        assert len(data["categories"]) > 0

    def test_drive_info(self):
        response = client.get("/api/materials/drive-info")
        assert response.status_code == 200
        info = response.json()
        assert info["total_materials"] >= 500
        assert info["companies_count"] >= 15
        assert "1NC5wLHUMUye5_5zHzSgTgXDUdVmh43ZU" in info["drive_root_url"]

    def test_company_materials_endpoint(self):
        response = client.get("/api/materials/company/INFOSYS")
        assert response.status_code == 200
        res = response.json()
        assert isinstance(res, list)
        assert len(res) > 0
        assert res[0]["company"] == "INFOSYS"

    def test_get_single_material(self):
        list_res = client.get("/api/materials?limit=1")
        assert list_res.status_code == 200
        item_id = list_res.json()["materials"][0]["id"]
        single_res = client.get(f"/api/materials/{item_id}")
        assert single_res.status_code == 200
        assert single_res.json()["id"] == item_id



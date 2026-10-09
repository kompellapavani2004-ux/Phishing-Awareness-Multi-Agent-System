import datetime as dt


def demo_student():
    d = lambda n: (dt.date.today() + dt.timedelta(days=n)).isoformat()
    return {
        "name": "Rahul", "course": "B.Tech CSE", "goal": "Java Full Stack Developer",
        "daily_hours": 3.0, "today_hours": None,
        "weak_areas": ["DSA", "SQL", "Spring Boot"],
        "progress": {"scores": [{"subject": "DSA", "percent": 45, "date": dt.date.today().isoformat()}]},
        "tasks": [
            {"name": "Placement test - DSA prep", "subject": "DSA", "deadline": d(5), "importance": 9,
             "difficulty": 8, "est_hours": 6, "hours_done": 0, "score": 45, "done": False},
            {"name": "Placement test - SQL prep", "subject": "SQL", "deadline": d(5), "importance": 8,
             "difficulty": 5, "est_hours": 3, "hours_done": 0, "score": None, "done": False},
            {"name": "Spring Boot project", "subject": "Spring Boot", "deadline": d(7), "importance": 8,
             "difficulty": 7, "est_hours": 10, "hours_done": 0, "score": None, "done": False},
            {"name": "University exam preparation", "subject": "Exam", "deadline": d(10), "importance": 7,
             "difficulty": 6, "est_hours": 12, "hours_done": 0, "score": None, "done": False},
        ],
    }

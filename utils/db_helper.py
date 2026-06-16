import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database", "mentor.db")

__all__ = [
    'init_db',
    'save_document',
    'update_document_summary',
    'get_document_count',
    'get_all_documents',
    'get_document',
    'delete_document',
    'save_quiz',
    'get_quiz_history',
    'get_average_score',
    'get_weak_topics_list',
    'save_study_plan',
    'get_study_plan'
]

def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Create documents table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            extracted_text TEXT NOT NULL,
            summary TEXT,
            uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create quizzes table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS quizzes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id INTEGER,
            score INTEGER NOT NULL,
            total_questions INTEGER NOT NULL,
            weak_topics TEXT,
            completed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(document_id) REFERENCES documents(id)
        )
    """)
    
    # Create study_plans table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS study_plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id INTEGER,
            days INTEGER NOT NULL,
            plan_text TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(document_id) REFERENCES documents(id)
        )
    """)
    
    conn.commit()
    conn.close()

def save_document(filename, text, summary=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO documents (filename, extracted_text, summary) VALUES (?, ?, ?)",
        (filename, text, summary)
    )
    doc_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return doc_id

def update_document_summary(doc_id, summary):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE documents SET summary = ? WHERE id = ?",
        (summary, doc_id)
    )
    conn.commit()
    conn.close()

def get_document_count():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM documents")
    count = cursor.fetchone()[0]
    conn.close()
    return count

def get_all_documents():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, filename, uploaded_at FROM documents ORDER BY uploaded_at DESC")
    docs = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return docs

def get_document(doc_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM documents WHERE id = ?", (doc_id,))
    row = cursor.fetchone()
    doc = dict(row) if row else None
    conn.close()
    return doc

def delete_document(doc_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM quizzes WHERE document_id = ?", (doc_id,))
    cursor.execute("DELETE FROM study_plans WHERE document_id = ?", (doc_id,))
    cursor.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
    conn.commit()
    conn.close()

def save_quiz(document_id, score, total_questions, weak_topics):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO quizzes (document_id, score, total_questions, weak_topics) VALUES (?, ?, ?, ?)",
        (document_id, score, total_questions, weak_topics)
    )
    quiz_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return quiz_id

def get_quiz_history():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT q.id, q.score, q.total_questions, q.weak_topics, q.completed_at, d.filename 
        FROM quizzes q 
        LEFT JOIN documents d ON q.document_id = d.id 
        ORDER BY q.completed_at DESC
    """)
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows

def get_average_score():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT score, total_questions FROM quizzes")
    rows = cursor.fetchall()
    conn.close()
    if not rows:
        return 0.0
    
    total_pct = sum((row[0] / row[1]) * 100.0 for row in rows)
    return total_pct / len(rows)

def get_weak_topics_list():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT weak_topics FROM quizzes WHERE weak_topics IS NOT NULL AND weak_topics != ''")
    rows = cursor.fetchall()
    conn.close()
    
    topics = []
    for row in rows:
        # Split topics by comma or newlines
        parts = [p.strip() for p in row[0].replace("\n", ",").split(",") if p.strip()]
        topics.extend(parts)
    return topics

def save_study_plan(document_id, days, plan_text):
    conn = get_connection()
    cursor = conn.cursor()
    # Check if a plan already exists for this document and duration
    cursor.execute(
        "SELECT id FROM study_plans WHERE document_id = ? AND days = ?",
        (document_id, days)
    )
    row = cursor.fetchone()
    if row:
        cursor.execute(
            "UPDATE study_plans SET plan_text = ?, created_at = CURRENT_TIMESTAMP WHERE id = ?",
            (plan_text, row['id'])
        )
    else:
        cursor.execute(
            "INSERT INTO study_plans (document_id, days, plan_text) VALUES (?, ?, ?)",
            (document_id, days, plan_text)
        )
    conn.commit()
    conn.close()

def get_study_plan(document_id, days):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT plan_text FROM study_plans WHERE document_id = ? AND days = ?",
        (document_id, days)
    )
    row = cursor.fetchone()
    plan = row['plan_text'] if row else None
    conn.close()
    return plan

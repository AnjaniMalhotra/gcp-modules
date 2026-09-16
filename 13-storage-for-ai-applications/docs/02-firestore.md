# 2. Firestore

## What Is It? (Plain English)

Firestore stores flexible, document-shaped records — each one can have a different set of fields, nested objects, and arrays, without needing to define a schema up front.

## Why It Matters for AI Engineers

Not all app data is neatly tabular. A student profile might have a variable-length list of extracurriculars, an optional nested address, fields that simply don't apply to every student. Forcing that into rigid relational columns is awkward; Firestore is built for exactly this shape.

## Key Concepts

| Term | Meaning |
|------|---------|
| **Document** | One record, stored as JSON-like data — this module's "student profile" |
| **Collection** | A group of documents, like `students` |
| **Nested Fields** | An object inside a document field (e.g., `contact: {email, phone}`) |
| **Array Field** | A list inside a document field (e.g., `extracurriculars: [...]`) |
| **`ArrayUnion`** | Adds an item to an array field without overwriting the rest of the document |

## How It Fits Together

```mermaid
flowchart LR
    A["Collection: students"] --> B["Document: student_alex"]
    B --> C["{ name, grade,<br/>contact: {email, phone},<br/>extracurriculars: [...] }"]
```

## Hands-On

See `code/13-storage-for-ai-applications/02_firestore.ipynb` — **Student Profiles**: nested contact info, an extracurriculars array, and a grade-level query.

```python
from google.cloud import firestore
from google.cloud.firestore_v1 import ArrayUnion

db = firestore.Client(project=PROJECT_ID)
students = db.collection("students")

# Create — nested + array fields in one document
students.document("alex").set({
    "name": "Alex Chen",
    "grade": 10,
    "contact": {"email": "alex@example.com", "phone": "555-0100"},
    "extracurriculars": ["chess club", "robotics"],
})

# Query — find all grade-10 students
for doc in students.where("grade", "==", 10).stream():
    print(doc.id, doc.to_dict())

# Update — append without overwriting the rest
students.document("alex").update({"extracurriculars": ArrayUnion(["debate team"])})
```

## Common Pitfalls

- Designing a rigid, uniform schema across every document out of relational habit — the flexibility is the point; not every student profile needs identical fields.
- Using `.set()` without `merge=True` when you meant to update part of a document — it silently overwrites the whole thing.
- Modeling something genuinely relational (like attendance across many dates, joined against many students) in Firestore instead of Cloud SQL — that's next topic's job.

## Quick Recap

1. What kind of data shape is Firestore built for that a spreadsheet-like table isn't?
2. What does `ArrayUnion` do, and why is it different from `.set()`?
3. When would student attendance data be a bad fit for Firestore?

try:
    from sklearn.ensemble import RandomForestClassifier
    HAS_SKLEARN = True
except ImportError as e:
    import warnings
    warnings.warn(f"sklearn could not be imported (falling back to heuristic classifier): {e}")
    HAS_SKLEARN = False
import numpy as np
import pandas as pd
from django.db import transaction
from .models import Course, Student, ActivityLog, Prediction


def run_ml_pipeline():
    """
    ML Pipeline for LMS logs:
    1. Extract features from ActivityLog database records.
    2. Compute Engagement Scores (0 - 100).
    3. Generate target labels based on engagement scores.
    4. Train a RandomForestClassifier.
    5. Predict risk levels (Low, Medium, High Risk).
    6. Generate tailored recommendations.
    7. Save/update predictions in the SQLite database.
    """
    # 1. Fetch activity logs
    logs = ActivityLog.objects.all().select_related('student', 'course')
    if not logs.exists():
        return 0

    # Convert queryset to Pandas DataFrame
    data = []
    for log in logs:
        data.append({
            'student_id': log.student.id,
            'course_id': log.course.id,
            'action': log.action,
            'duration': log.duration
        })
    df = pd.DataFrame(data)

    # 2. Extract features per student-course pair
    # Features: total activities, total duration, quiz submissions, forum posts, content/resource views
    grouped = df.groupby(['student_id', 'course_id'])

    features_list = []
    for (student_id, course_id), group in grouped:
        total_activities = len(group)
        total_duration = group['duration'].sum()
        quiz_submissions = len(group[group['action'] == 'submit_quiz'])
        forum_posts = len(group[group['action'] == 'post_forum'])
        resource_views = len(group[group['action'] == 'access_resource'])

        features_list.append({
            'student_id': student_id,
            'course_id': course_id,
            'total_activities': total_activities,
            'total_duration': total_duration,
            'quiz_submissions': quiz_submissions,
            'forum_posts': forum_posts,
            'resource_views': resource_views
        })

    features_df = pd.DataFrame(features_list)

    # 3. Calculate Engagement Score
    # We define benchmark maximums to normalize scores between 0 and 100.
    # If actual values exceed benchmarks, they are capped.
    max_activities = max(features_df['total_activities'].max(), 10)
    max_duration = max(features_df['total_duration'].max(), 3600)  # at least 1 hour
    max_quizzes = max(features_df['quiz_submissions'].max(), 2)
    max_forums = max(features_df['forum_posts'].max(), 2)

    def calculate_score(row):
        score = (
            0.30 * (min(row['total_activities'], max_activities) / max_activities) +
            0.35 * (min(row['total_duration'], max_duration) / max_duration) +
            0.20 * (min(row['quiz_submissions'], max_quizzes) / max_quizzes) +
            0.15 * (min(row['forum_posts'], max_forums) / max_forums)
        ) * 100
        return float(np.round(score, 1))

    features_df['engagement_score'] = features_df.apply(calculate_score, axis=1)

    # 4. Generate Target Labels for training
    # Score < 35 => High Risk, 35 <= Score < 70 => Medium Risk, Score >= 70 => Low Risk
    def assign_label(score):
        if score < 35:
            return 'High Risk'
        elif score < 70:
            return 'Medium Risk'
        else:
            return 'Low Risk'

    features_df['risk_label'] = features_df['engagement_score'].apply(assign_label)

    # 5. Train RandomForestClassifier
    # Features to use:
    X = features_df[['total_activities', 'total_duration', 'quiz_submissions', 'forum_posts', 'resource_views']]
    y = features_df['risk_label']

    # Handle tiny datasets, single-class datasets, or missing sklearn gracefully
    unique_classes = y.unique()
    if HAS_SKLEARN and len(unique_classes) > 1:
        clf = RandomForestClassifier(n_estimators=50, max_depth=5, random_state=42)
        clf.fit(X, y)
        # Predict using trained RF
        features_df['predicted_risk'] = clf.predict(X)
    else:
        # Default to base rules if we can't train RF (e.g. only 1 data point, 1 class, or no sklearn)
        features_df['predicted_risk'] = features_df['risk_label']

    # 6. Generate tailored recommendations based on predicted risk & features
    def generate_recommendation(row):
        risk = row['predicted_risk']
        quizzes = row['quiz_submissions']
        forums = row['forum_posts']
        duration_hours = row['total_duration'] / 3600.0

        if risk == 'High Risk':
            recs = [
                "Critical Alert: Set up an urgent 1-on-1 counseling session.",
                "Mandatory attendance review and academic intervention required.",
            ]
            if quizzes == 0:
                recs.append("Assign catch-up quiz sessions immediately.")
            return " ".join(recs)

        elif risk == 'Medium Risk':
            recs = ["Student shows moderate engagement but is falling behind."]
            if quizzes < 2:
                recs.append("Recommend completion of outstanding online quizzes.")
            if forums < 2:
                recs.append("Encourage participation in the course discussion boards to boost engagement.")
            if duration_hours < 5.0:
                recs.append("Suggest dedicated study hours accessing reading materials on the LMS.")
            return " ".join(recs)

        else: # Low Risk
            return "Excellent engagement. Student is on track. Recommend encouraging peer study groups or leadership roles."

    features_df['recommendation'] = features_df.apply(generate_recommendation, axis=1)

    # 7. Save predictions in SQLite database using a transaction
    predictions_count = 0
    with transaction.atomic():
        for _, row in features_df.iterrows():
            student = Student.objects.get(id=int(row['student_id']))
            course = Course.objects.get(id=int(row['course_id']))

            Prediction.objects.update_or_create(
                student=student,
                course=course,
                defaults={
                    'engagement_score': row['engagement_score'],
                    'predicted_risk': row['predicted_risk'],
                    'recommendation': row['recommendation']
                }
            )
            predictions_count += 1

    return predictions_count

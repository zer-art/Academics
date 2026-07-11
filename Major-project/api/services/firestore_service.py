"""AIVOX — Firestore Service (Firebase Admin SDK)
Handles server-side DB writes for saving interview reports.
Client-side Firebase SDK handles reads directly (more efficient).
"""

import os
import json
import uuid
from datetime import datetime, timezone

import firebase_admin
from firebase_admin import credentials, firestore_async


# Initialize Firebase Admin SDK (singleton)
_firebase_app = None


def _get_firebase_app():
    global _firebase_app
    if _firebase_app is None:
        service_account_json = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")
        if not service_account_json:
            raise RuntimeError("FIREBASE_SERVICE_ACCOUNT_JSON env var not set")
        cred_dict = json.loads(service_account_json)
        cred = credentials.Certificate(cred_dict)
        _firebase_app = firebase_admin.initialize_app(cred)
    return _firebase_app


class FirestoreService:
    def __init__(self):
        _get_firebase_app()
        self.db = firestore_async.client()

    async def save_report(self, user_id: str, report: dict) -> str:
        """
        Save interview report to Firestore.
        Returns the generated report_id.

        Schema:
          /users/{user_id}/interviews/{report_id}
        """
        report_id = str(uuid.uuid4())
        report_data = {
            **report,
            "report_id": report_id,
            "user_id": user_id,
            "created_at": datetime.now(timezone.utc),
        }

        doc_ref = self.db.collection("users").document(user_id).collection("interviews").document(report_id)
        await doc_ref.set(report_data)

        # Update user's aggregate stats
        await self._update_user_stats(user_id, report)

        # Update global stats
        await self._update_global_stats()

        return report_id

    async def _update_user_stats(self, user_id: str, report: dict):
        """Increment user's total interview count and update avg score."""
        user_ref = self.db.collection("users").document(user_id)
        final_score = report.get("scoring", {}).get("final_score", 0)

        await user_ref.set(
            {
                "total_interviews": firestore_async.firestore.Increment(1),
                "last_interview_at": datetime.now(timezone.utc),
                "last_score": final_score,
            },
            merge=True,
        )

    async def _update_global_stats(self):
        """Increment global interview counter (shown on landing page)."""
        stats_ref = self.db.collection("stats").document("global")
        await stats_ref.set(
            {"total_interviews": firestore_async.firestore.Increment(1)},
            merge=True,
        )

"""
ExamPilot Native Message Handler Module
Routes incoming Chrome requests to the core application engines.
GT InnoX LLP
"""

from typing import Dict, Any
from desktop.security.validation import validate_native_message
from desktop.core.answer_engine import answer_engine
from desktop.core.model_manager import model_manager
from desktop.database.repository import repository
from desktop.database.models import QuestionModel
from desktop.utils.logger import logger

class MessageHandler:
    """Processes messages received from Chrome Extension."""

    def handle(self, message: Dict[str, Any]) -> Dict[str, Any]:
        req_id = message.get("request_id")
        action = message.get("action", "")

        is_valid, err_msg = validate_native_message(message)
        if not is_valid:
            return {
                "request_id": req_id,
                "success": False,
                "action": action,
                "error": err_msg
            }

        try:
            if action == "ping":
                return {
                    "request_id": req_id,
                    "success": True,
                    "action": "pong",
                    "status": "connected",
                    "app_version": "1.0.0"
                }

            elif action == "get_status":
                status = model_manager.get_status()
                return {
                    "request_id": req_id,
                    "success": True,
                    "action": "status_response",
                    "service_running": status["service_running"],
                    "active_model": status["active_model"],
                    "installed_models": [m["name"] for m in status["installed_models"]]
                }

            elif action == "analyze_question":
                payload = message.get("payload", {})
                question_text = payload.get("question", "")
                options = payload.get("options", {})
                subject = payload.get("subject_name", "General")

                success, result, error = answer_engine.analyze(question_text, options, subject)
                if not success or not result:
                    return {
                        "request_id": req_id,
                        "success": False,
                        "action": "answer_response",
                        "error": error
                    }

                # Save question to database
                try:
                    q_model = QuestionModel(
                        question_text=question_text,
                        options=options,
                        suggested_answer=result.get("suggested_answer"),
                        answer_text=result.get("answer_text"),
                        explanation=result.get("explanation"),
                        option_analysis=result.get("option_analysis", {}),
                        confidence=result.get("confidence", 0.0),
                        subject_name=subject
                    )
                    qid = repository.save_question(q_model)
                    result["id"] = qid
                except Exception as db_err:
                    logger.warning(f"Failed to auto-save question to history: {db_err}")

                return {
                    "request_id": req_id,
                    "success": True,
                    "action": "answer_response",
                    "data": result
                }

            elif action == "open_desktop":
                return {
                    "request_id": req_id,
                    "success": True,
                    "action": "desktop_opened"
                }

            else:
                return {
                    "request_id": req_id,
                    "success": False,
                    "error": f"Unhandled action: {action}"
                }

        except Exception as e:
            logger.error(f"Error handling message {action}: {e}", exc_info=True)
            return {
                "request_id": req_id,
                "success": False,
                "error": str(e)
            }

message_handler = MessageHandler()


from app.domain.utterances.service import UtteranceService


class LessonService:
    def __init__(self):
        self.utterance_service = UtteranceService()

    async def get_lessons(self):
        return self.utterance_service.get_lessons()

    async def get_lesson(self, lesson_id: str):
        return self.utterance_service.get_lesson(lesson_id)

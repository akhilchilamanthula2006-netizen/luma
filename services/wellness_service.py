class WellnessService:
    """
    Service for wellness content and tasks (breathing exercises, meditations).
    """
    @staticmethod
    def get_activities() -> list:
        """
        Retrieves a list of available wellness activities (breathing, meditation).
        """
        return [
            {"id": "breath_1", "type": "breathing", "title": "Box Breathing", "duration": "5 min"},
            {"id": "med_1", "type": "meditation", "title": "Mindful Calm", "duration": "10 min"}
        ]

class EssayFeedbackService:
    def analyze(self, text):
        if len(text) < 100:
            return "Try expanding your ideas with more detail and examples."
        elif "I" not in text:
            return "Consider adding more personal voice to your essay."
        return "Your essay shows strong structure and clarity. Keep refining!"

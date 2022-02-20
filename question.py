class question:
    subject: str
    question_number: str
    question_text: str
    option_1: str
    option_2: str
    option_3: str
    option_4: str
    correct_answer: str

    def populate(self, question_number, question_text, option_1, option_2, option_3, option_4, correct_answer, subject):
        self.question_number = question_number
        self.question_text = question_text
        self.option_1 = option_1
        self.option_2 = option_2
        self.option_3 = option_3
        self.option_4 = option_4
        self.correct_answer = correct_answer
        self.subject = subject

    def __str__(self):
        return self.question_number + ' : ' + self.question_text + "\n" \
               + '1)' + self.option_1 \
               + '2)' + self.option_2 \
               + '3)' + self.option_3 \
               + '4)' + self.option_4 \
               + '\n    Correct Answer: ' + self.correct_answer

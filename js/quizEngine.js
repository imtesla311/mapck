/**
 * Quiz Engine Module
 * Handles question generation, answer validation, and quiz flow
 */

class QuizEngine {
    constructor(regionManager, scoreTracker) {
        this.regionManager = regionManager;
        this.scoreTracker = scoreTracker;
        this.questions = [];
        this.currentQuestionIndex = 0;
        this.quizMode = 'multiple_choice';
        this.isAnswered = false;
        this.questionCount = null;
    }

    /**
     * Initialize quiz for a region
     */
    initQuiz(regionId, mode, questionCount = null) {
        this.quizMode = mode;
        this.questionCount = questionCount;
        this.currentQuestionIndex = 0;
        this.isAnswered = false;
        let allQuestions = this.generateQuestions(regionId);
        
        // Limit questions if questionCount is specified
        if (questionCount && questionCount > 0 && questionCount < allQuestions.length) {
            this.questions = this.shuffleArray(allQuestions).slice(0, questionCount);
        } else {
            this.questions = allQuestions;
        }
        
        this.scoreTracker.startQuiz();
        return this.questions;
    }

    /**
     * Generate questions for a region
     */
    generateQuestions(regionId) {
        const region = this.regionManager.getRegion(regionId);
        const countries = region?.countries || [];
        const questions = [];
        const questionTypes = this.getQuestionTypes(region);

        countries.forEach(country => {
            questionTypes.forEach(questionType => {
                const question = this.createQuestion(questionType, country, region);
                if (question) {
                    questions.push(question);
                }
            });
        });

        return this.shuffleArray(questions);
    }

    /**
     * Get enabled question types for a region
     */
    getQuestionTypes(region) {
        if (Array.isArray(region?.questionTypes) && region.questionTypes.length > 0) {
            return region.questionTypes;
        }

        return ['pointed_country', 'capital', 'reverse_capital'];
    }

    /**
     * Create a question object for a given type
     */
    createQuestion(questionType, country, region) {
        const entityLabel = this.getEntityLabel(region);

        switch (questionType) {
            case 'pointed_country':
                return {
                    type: 'pointed_country',
                    country,
                    question: `What ${entityLabel} is pointed to in this image?`,
                    correctAnswer: country.name,
                    alternateAnswers: country.alternateNames,
                    image: this.getQuestionImage(country, 'pointed_country', region)
                };
            case 'capital':
                return {
                    type: 'capital',
                    country,
                    question: `What is the capital city of ${country.name}?`,
                    correctAnswer: country.capital,
                    alternateAnswers: country.alternateCapitals,
                    image: this.getQuestionImage(country, 'capital', region)
                };
            case 'reverse_capital':
                return {
                    type: 'reverse_capital',
                    country,
                    question: `${country.capital} is the capital of which ${entityLabel}?`,
                    correctAnswer: country.name,
                    alternateAnswers: country.alternateNames,
                    image: this.getQuestionImage(country, 'capital', region)
                };
            case 'numbered_region':
                if (!region?.numberedMapImage || country.mapNumber === undefined || country.mapNumber === null) {
                    return null;
                }

                return {
                    type: 'numbered_region',
                    country,
                    question: `What ${entityLabel} is number ${country.mapNumber} on this map?`,
                    correctAnswer: country.name,
                    alternateAnswers: country.alternateNames,
                    image: this.getQuestionImage(country, 'numbered_region', region)
                };
            default:
                return null;
        }
    }

    /**
     * Get the entity label for prompts
     */
    getEntityLabel(region) {
        return region?.entityLabel || 'country';
    }

    /**
     * Get the image path for a question
     * Falls back to default map image if no specific image is defined
     */
    getQuestionImage(country, questionType, region) {
        const defaultImage = region ? region.mapImage : null;

        if (country.questionImages && country.questionImages[questionType]) {
            return country.questionImages[questionType];
        }

        if (questionType === 'numbered_region' && region?.numberedMapImage) {
            return region.numberedMapImage;
        }

        if (questionType === 'pointed_country' && country.pointed_country) {
            return country.pointed_country;
        }

        return defaultImage;
    }

    /**
     * Get current question
     */
    getCurrentQuestion() {
        return this.questions[this.currentQuestionIndex];
    }

    /**
     * Get total number of questions
     */
    getTotalQuestions() {
        return this.questions.length;
    }

    /**
     * Get current question index (1-based)
     */
    getCurrentQuestionNumber() {
        return this.currentQuestionIndex + 1;
    }

    /**
     * Check if quiz is complete
     */
    isComplete() {
        return this.currentQuestionIndex >= this.questions.length;
    }

    /**
     * Get multiple choice options for current question
     */
    getMultipleChoiceOptions(question) {
        const countries = this.regionManager.getCountries();
        let wrongOptions = [];

        if (
            question.type === 'pointed_country' ||
            question.type === 'reverse_capital' ||
            question.type === 'numbered_region'
        ) {
            wrongOptions = countries
                .filter(c => c.id !== question.country.id)
                .map(c => c.name)
                .filter(name => name !== question.correctAnswer);
        } else if (question.type === 'capital') {
            wrongOptions = countries
                .filter(c => c.id !== question.country.id)
                .map(c => c.capital)
                .filter(capital => capital !== question.correctAnswer);
        }

        const selectedWrongOptions = this.shuffleArray(wrongOptions).slice(0, 3);
        const options = [...selectedWrongOptions, question.correctAnswer];
        return this.shuffleArray(options);
    }

    /**
     * Validate answer
     */
    validateAnswer(userAnswer) {
        const question = this.getCurrentQuestion();
        const isCorrect = this.isAnswerCorrect(userAnswer, question);

        this.scoreTracker.recordAnswer(
            question.question,
            userAnswer,
            question.correctAnswer,
            isCorrect
        );

        this.isAnswered = true;
        return isCorrect;
    }

    /**
     * Check if answer is correct (with fuzzy matching)
     */
    isAnswerCorrect(userAnswer, question) {
        const normalizedUserAnswer = this.normalizeString(userAnswer);
        
        // Check against correct answer
        if (this.stringsMatch(normalizedUserAnswer, this.normalizeString(question.correctAnswer))) {
            return true;
        }

        // Check against alternate answers
        if (question.alternateAnswers) {
            for (const altAnswer of question.alternateAnswers) {
                if (this.stringsMatch(normalizedUserAnswer, this.normalizeString(altAnswer))) {
                    return true;
                }
            }
        }

        return false;
    }

    /**
     * Normalize string for comparison
     */
    normalizeString(str) {
        return str
            .toLowerCase()
            .trim()
            .replace(/[^\w\s]/g, '')
            .replace(/\s+/g, ' ');
    }

    /**
     * Check if two strings match (with fuzzy matching)
     */
    stringsMatch(str1, str2) {
        // Exact match
        if (str1 === str2) return true;

        // Levenshtein distance for fuzzy matching
        const distance = this.levenshteinDistance(str1, str2);
        const maxLength = Math.max(str1.length, str2.length);
        
        // Allow up to 30% difference
        return distance / maxLength <= 0.05;
    }

    /**
     * Calculate Levenshtein distance between two strings
     */
    levenshteinDistance(str1, str2) {
        const m = str1.length;
        const n = str2.length;
        const dp = Array(m + 1).fill(null).map(() => Array(n + 1).fill(0));

        for (let i = 0; i <= m; i++) dp[i][0] = i;
        for (let j = 0; j <= n; j++) dp[0][j] = j;

        for (let i = 1; i <= m; i++) {
            for (let j = 1; j <= n; j++) {
                if (str1[i - 1] === str2[j - 1]) {
                    dp[i][j] = dp[i - 1][j - 1];
                } else {
                    dp[i][j] = 1 + Math.min(
                        dp[i - 1][j],
                        dp[i][j - 1],
                        dp[i - 1][j - 1]
                    );
                }
            }
        }

        return dp[m][n];
    }

    /**
     * Move to next question
     */
    nextQuestion() {
        this.currentQuestionIndex++;
        this.isAnswered = false;
    }

    /**
     * Get quiz results
     */
    getResults() {
        const progress = this.scoreTracker.getCurrentProgress();
        return {
            score: progress.score,
            total: progress.total,
            duration: this.scoreTracker.getElapsedTime(),
            answers: this.scoreTracker.currentAnswers
        };
    }

    /**
     * Shuffle array using Fisher-Yates algorithm
     */
    shuffleArray(array) {
        const shuffled = [...array];
        for (let i = shuffled.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
        }
        return shuffled;
    }

    /**
     * Reset quiz
     */
    reset() {
        this.questions = [];
        this.currentQuestionIndex = 0;
        this.isAnswered = false;
    }
}

export default QuizEngine;

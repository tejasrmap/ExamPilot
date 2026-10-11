"""
ExamPilot 100+ Benchmark MCQ Dataset
Subjects:
1. Computer Science (13)
2. Mathematics (13)
3. Data Science (13)
4. General Knowledge (13)
5. Physics (13)
6. Chemistry (13)
7. Business & Finance (13)
8. Networking (13)
Total: 104 Questions
GT InnoX LLP
"""

BENCHMARK_MCQS = [
    # --- 1. Computer Science (13) ---
    {
        "id": 1,
        "subject": "Computer Science",
        "question": "Which data structure follows the First In First Out (FIFO) principle?",
        "options": {"A": "Stack", "B": "Queue", "C": "Binary Search Tree", "D": "Heap"},
        "correct_answer": "B",
        "explanation": "A queue is an abstract data type where elements are added at the rear and removed from the front (FIFO)."
    },
    {
        "id": 2,
        "subject": "Computer Science",
        "question": "What is the worst-case time complexity of QuickSort?",
        "options": {"A": "O(n)", "B": "O(n log n)", "C": "O(n^2)", "D": "O(log n)"},
        "correct_answer": "C",
        "explanation": "QuickSort degrades to O(n^2) when an unbalanced pivot is chosen, such as picking the smallest or largest element on an already sorted array."
    },
    {
        "id": 3,
        "subject": "Computer Science",
        "question": "Which scheduling algorithm is non-preemptive?",
        "options": {"A": "Round Robin", "B": "Shortest Remaining Time First", "C": "First-Come First-Served (FCFS)", "D": "Priority Preemptive"},
        "correct_answer": "C",
        "explanation": "FCFS allocates CPU to processes in the exact order they arrive and does not preempt until completion or I/O."
    },
    {
        "id": 4,
        "subject": "Computer Science",
        "question": "Which database normal form eliminates transitive dependencies?",
        "options": {"A": "First Normal Form (1NF)", "B": "Second Normal Form (2NF)", "C": "Third Normal Form (3NF)", "D": "Boyce-Codd Normal Form (BCNF)"},
        "correct_answer": "C",
        "explanation": "3NF requires the relation to be in 2NF and that no non-prime attribute is transitively dependent on the primary key."
    },
    {
        "id": 5,
        "subject": "Computer Science",
        "question": "What is the primary purpose of a virtual memory page table?",
        "options": {"A": "Translate virtual addresses to physical addresses", "B": "Manage CPU registers", "C": "Control hard disk sectors", "D": "Encrypt memory contents"},
        "correct_answer": "A",
        "explanation": "Page tables map virtual page numbers into physical page frames in RAM."
    },
    {
        "id": 6,
        "subject": "Computer Science",
        "question": "In Python, which built-in data type is immutable?",
        "options": {"A": "List", "B": "Dictionary", "C": "Set", "D": "Tuple"},
        "correct_answer": "D",
        "explanation": "Tuples cannot be altered in-place after instantiation in Python."
    },
    {
        "id": 7,
        "subject": "Computer Science",
        "question": "Which design pattern ensures a class has only one instance and provides global access to it?",
        "options": {"A": "Factory Method", "B": "Singleton", "C": "Observer", "D": "Adapter"},
        "correct_answer": "B",
        "explanation": "The Singleton pattern restricts class instantiation to a single object."
    },
    {
        "id": 8,
        "subject": "Computer Science",
        "question": "Which graph algorithm is used to find the shortest path in a weighted graph with non-negative weights?",
        "options": {"A": "Dijkstra's Algorithm", "B": "Kruskal's Algorithm", "C": "Tarjan's Algorithm", "D": "Depth First Search"},
        "correct_answer": "A",
        "explanation": "Dijkstra's algorithm greedily explores the nearest unvisited node to calculate single-source shortest paths."
    },
    {
        "id": 9,
        "subject": "Computer Science",
        "question": "What is the time complexity to access an element by index in a dynamically allocated array?",
        "options": {"A": "O(1)", "B": "O(log n)", "C": "O(n)", "D": "O(n log n)"},
        "correct_answer": "A",
        "explanation": "Array indexing uses direct pointer arithmetic base + index * size in constant O(1) time."
    },
    {
        "id": 10,
        "subject": "Computer Science",
        "question": "Which of the following is NOT an ACID property in relational database transactions?",
        "options": {"A": "Atomicity", "B": "Consistency", "C": "Concurrency", "D": "Durability"},
        "correct_answer": "C",
        "explanation": "ACID stands for Atomicity, Consistency, Isolation, and Durability ('I' is Isolation, not Concurrency)."
    },
    {
        "id": 11,
        "subject": "Computer Science",
        "question": "What is the primary condition for a deadlock to occur involving non-shareable resources?",
        "options": {"A": "Mutual Exclusion", "B": "Preemption", "C": "Process Starvation", "D": "Context Switching"},
        "correct_answer": "A",
        "explanation": "Mutual exclusion is the condition that at least one resource must be held in a non-shareable mode."
    },
    {
        "id": 12,
        "subject": "Computer Science",
        "question": "In object-oriented programming, defining multiple methods with the same name but different parameter lists is called:",
        "options": {"A": "Method Overriding", "B": "Method Overloading", "C": "Encapsulation", "D": "Polymorphic Casting"},
        "correct_answer": "B",
        "explanation": "Method overloading occurs when methods share a name but differ in parameter count or types within the same scope."
    },
    {
        "id": 13,
        "subject": "Computer Science",
        "question": "Which traversal of a Binary Search Tree produces values in strictly ascending sorted order?",
        "options": {"A": "Pre-order", "B": "In-order", "C": "Post-order", "D": "Level-order"},
        "correct_answer": "B",
        "explanation": "In-order traversal visits Left -> Root -> Right, yielding sorted order in a valid BST."
    },

    # --- 2. Mathematics (13) ---
    {
        "id": 14,
        "subject": "Mathematics",
        "question": "What is the derivative of f(x) = sin(x) with respect to x?",
        "options": {"A": "-cos(x)", "B": "cos(x)", "C": "-sin(x)", "D": "tan(x)"},
        "correct_answer": "B",
        "explanation": "d/dx [sin(x)] = cos(x) by standard calculus differential rules."
    },
    {
        "id": 15,
        "subject": "Mathematics",
        "question": "What is the determinant of a 2x2 matrix [[a, b], [c, d]]?",
        "options": {"A": "ad + bc", "B": "ab - cd", "C": "ad - bc", "D": "ac - bd"},
        "correct_answer": "C",
        "explanation": "The determinant of a 2x2 matrix is computed by ad - bc."
    },
    {
        "id": 16,
        "subject": "Mathematics",
        "question": "What is the value of limit as x approaches 0 of sin(x)/x?",
        "options": {"A": "0", "B": "1", "C": "Infinity", "D": "Undefined"},
        "correct_answer": "B",
        "explanation": "By L'Hopital's rule or trigonometric squeeze theorem, lim(x->0) sin(x)/x = 1."
    },
    {
        "id": 17,
        "subject": "Mathematics",
        "question": "If two events A and B are independent, what is P(A and B)?",
        "options": {"A": "P(A) + P(B)", "B": "P(A) * P(B)", "C": "P(A) / P(B)", "D": "P(A|B)"},
        "correct_answer": "B",
        "explanation": "For statistically independent events, joint probability P(A ∩ B) = P(A) * P(B)."
    },
    {
        "id": 18,
        "subject": "Mathematics",
        "question": "What is the solution to the differential equation dy/dx = y?",
        "options": {"A": "y = C * x", "B": "y = C * e^x", "C": "y = x^2 / 2", "D": "y = ln(x) + C"},
        "correct_answer": "B",
        "explanation": "Separating variables: dy/y = dx leads to ln|y| = x + k, so y = C * e^x."
    },
    {
        "id": 19,
        "subject": "Mathematics",
        "question": "What is the rank of an identity matrix of size n x n?",
        "options": {"A": "0", "B": "1", "C": "n - 1", "D": "n"},
        "correct_answer": "D",
        "explanation": "An n x n identity matrix has n linearly independent rows, hence rank n."
    },
    {
        "id": 20,
        "subject": "Mathematics",
        "question": "What is the integral of 1/x dx for x > 0?",
        "options": {"A": "ln(x) + C", "B": "e^x + C", "C": "-1/x^2 + C", "D": "x + C"},
        "correct_answer": "A",
        "explanation": "The antiderivative of 1/x for positive x is the natural logarithm ln(x) + C."
    },
    {
        "id": 21,
        "subject": "Mathematics",
        "question": "How many degrees are in 3*pi/2 radians?",
        "options": {"A": "90", "B": "180", "C": "270", "D": "360"},
        "correct_answer": "C",
        "explanation": "(3 * 180) / 2 = 270 degrees."
    },
    {
        "id": 22,
        "subject": "Mathematics",
        "question": "Which of the following numbers is irrational?",
        "options": {"A": "3/4", "B": "0.333...", "C": "sqrt(2)", "D": "sqrt(4)"},
        "correct_answer": "C",
        "explanation": "sqrt(2) cannot be represented as a ratio of two integers and has a non-repeating infinite decimal expansion."
    },
    {
        "id": 23,
        "subject": "Mathematics",
        "question": "What is the sum of angles in a plane hexagon (6-sided polygon)?",
        "options": {"A": "360 degrees", "B": "540 degrees", "C": "720 degrees", "D": "900 degrees"},
        "correct_answer": "C",
        "explanation": "Sum of interior angles = (n - 2) * 180 = (6 - 2) * 180 = 720 degrees."
    },
    {
        "id": 24,
        "subject": "Mathematics",
        "question": "If vector u = (1, 2) and vector v = (3, -1), what is their dot product u . v?",
        "options": {"A": "1", "B": "5", "C": "7", "D": "-1"},
        "correct_answer": "A",
        "explanation": "u . v = (1 * 3) + (2 * -1) = 3 - 2 = 1."
    },
    {
        "id": 25,
        "subject": "Mathematics",
        "question": "What is the value of 5! (5 factorial)?",
        "options": {"A": "60", "B": "100", "C": "120", "D": "720"},
        "correct_answer": "C",
        "explanation": "5! = 5 * 4 * 3 * 2 * 1 = 120."
    },
    {
        "id": 26,
        "subject": "Mathematics",
        "question": "Which statistical measure represents the middle value in a sorted dataset?",
        "options": {"A": "Mean", "B": "Median", "C": "Mode", "D": "Variance"},
        "correct_answer": "B",
        "explanation": "The median divides the upper half of ordered observations from the lower half."
    },

    # --- 3. Data Science & Machine Learning (13) ---
    {
        "id": 27,
        "subject": "Data Science",
        "question": "Which metric evaluates classification models when class distribution is highly imbalanced?",
        "options": {"A": "Accuracy", "B": "F1-Score", "C": "Mean Squared Error", "D": "R-squared"},
        "correct_answer": "B",
        "explanation": "F1-Score computes the harmonic mean of precision and recall, balancing false positives and false negatives under severe class imbalance."
    },
    {
        "id": 28,
        "subject": "Data Science",
        "question": "In supervised learning, what does high variance typically indicate?",
        "options": {"A": "Underfitting", "B": "Overfitting", "C": "High bias", "D": "Data leakage"},
        "correct_answer": "B",
        "explanation": "High variance means the model fits noise in training data too closely, failing to generalize to unseen data."
    },
    {
        "id": 29,
        "subject": "Data Science",
        "question": "Which dimensionality reduction technique finds orthogonal axes maximizing variance?",
        "options": {"A": "Linear Discriminant Analysis", "B": "Principal Component Analysis (PCA)", "C": "t-SNE", "D": "K-Means"},
        "correct_answer": "B",
        "explanation": "PCA projects data onto principal eigenvectors that maximize variance without supervision labels."
    },
    {
        "id": 30,
        "subject": "Data Science",
        "question": "What activation function outputs values strictly in the range [0, 1]?",
        "options": {"A": "ReLU", "B": "Sigmoid", "C": "Tanh", "D": "Leaky ReLU"},
        "correct_answer": "B",
        "explanation": "The sigmoid function sigma(z) = 1 / (1 + e^-z) maps real inputs into (0, 1)."
    },
    {
        "id": 31,
        "subject": "Data Science",
        "question": "Which loss function is standard for training multi-class neural network classifiers?",
        "options": {"A": "Mean Absolute Error", "B": "Categorical Cross-Entropy", "C": "Hinge Loss", "D": "Huber Loss"},
        "correct_answer": "B",
        "explanation": "Categorical cross-entropy measures divergence between predicted probability distributions and true one-hot labels."
    },
    {
        "id": 32,
        "subject": "Data Science",
        "question": "What is the primary mechanism of L2 regularization (Ridge)?",
        "options": {"A": "Sets irrelevant weights exactly to zero", "B": "Penalizes the sum of squared weights", "C": "Removes redundant training records", "D": "Normalizes gradient descent learning rate"},
        "correct_answer": "B",
        "explanation": "L2 regularization adds a penalty proportional to the square of model weight magnitudes."
    },
    {
        "id": 33,
        "subject": "Data Science",
        "question": "In K-Means clustering, what is the role of the silhouette coefficient?",
        "options": {"A": "Determine convergence step size", "B": "Measure cluster separation and cohesion", "C": "Select optimal features", "D": "Estimate neural network layers"},
        "correct_answer": "B",
        "explanation": "The silhouette score measures how similar an object is to its own cluster compared to neighboring clusters."
    },
    {
        "id": 34,
        "subject": "Data Science",
        "question": "What is the vanishing gradient problem primarily caused by in deep networks using sigmoid activations?",
        "options": {"A": "Derivatives of sigmoid are strictly less than 0.25", "B": "Learning rate is exponentially large", "C": "Weights explode beyond numeric bounds", "D": "Dropout probability is 0"},
        "correct_answer": "A",
        "explanation": "Repeated multiplication of small derivatives (max 0.25) through many layers causes gradients to decay toward zero."
    },
    {
        "id": 35,
        "subject": "Data Science",
        "question": "Which ensemble technique builds trees sequentially to correct errors of predecessor trees?",
        "options": {"A": "Bagging", "B": "Gradient Boosting", "C": "Random Forest", "D": "Stacking"},
        "correct_answer": "B",
        "explanation": "Boosting methods train models iteratively, focusing subsequent trees on residual errors of previous iterations."
    },
    {
        "id": 36,
        "subject": "Data Science",
        "question": "What does ROC curve plot?",
        "options": {"A": "Precision vs Recall", "B": "True Positive Rate vs False Positive Rate", "C": "Accuracy vs Loss", "D": "Variance vs Bias"},
        "correct_answer": "B",
        "explanation": "Receiver Operating Characteristic plots TPR against FPR across all classification probability thresholds."
    },
    {
        "id": 37,
        "subject": "Data Science",
        "question": "Which pandas operation reshapes data from long format to wide format?",
        "options": {"A": "melt()", "B": "pivot()", "C": "concat()", "D": "drop_duplicates()"},
        "correct_answer": "B",
        "explanation": "pivot() spreads values into columns based on specified index keys, converting long to wide."
    },
    {
        "id": 38,
        "subject": "Data Science",
        "question": "What is 'data leakage' in machine learning pipeline development?",
        "options": {"A": "Database corruption due to power failure", "B": "Test dataset information inadvertently entering the training process", "C": "Under-representation of minority classes", "D": "Unencrypted model files stored on disk"},
        "correct_answer": "B",
        "explanation": "Data leakage occurs when features contain information from the target or test split that would not be available in real inference."
    },
    {
        "id": 39,
        "subject": "Data Science",
        "question": "Which self-attention architecture revolutionized NLP and vision models?",
        "options": {"A": "Transformer", "B": "Recurrent Neural Network (RNN)", "C": "Long Short-Term Memory (LSTM)", "D": "Radial Basis Network"},
        "correct_answer": "A",
        "explanation": "The Transformer architecture replaces recurrence with multi-head self-attention mechanisms."
    },

    # --- 4. General Knowledge (13) ---
    {
        "id": 40,
        "subject": "General Knowledge",
        "question": "Who is credited with discovering penicillin in 1928?",
        "options": {"A": "Louis Pasteur", "B": "Alexander Fleming", "C": "Robert Koch", "D": "Edward Jenner"},
        "correct_answer": "B",
        "explanation": "Sir Alexander Fleming discovered the antibacterial properties of Penicillium notatum in 1928."
    },
    {
        "id": 41,
        "subject": "General Knowledge",
        "question": "Which planet in our solar system has the highest number of recognized moons?",
        "options": {"A": "Mars", "B": "Jupiter", "C": "Saturn", "D": "Neptune"},
        "correct_answer": "C",
        "explanation": "Saturn leads the solar system with over 140 officially confirmed moons."
    },
    {
        "id": 42,
        "subject": "General Knowledge",
        "question": "What is the capital city of Australia?",
        "options": {"A": "Sydney", "B": "Melbourne", "C": "Canberra", "D": "Brisbane"},
        "correct_answer": "C",
        "explanation": "Canberra is the federal capital of Australia, purpose-built between Sydney and Melbourne."
    },
    {
        "id": 43,
        "subject": "General Knowledge",
        "question": "In what year did the Apollo 11 mission successfully land humans on the Moon?",
        "options": {"A": "1965", "B": "1969", "C": "1972", "D": "1975"},
        "correct_answer": "B",
        "explanation": "Apollo 11 landed on the lunar surface on July 20, 1969."
    },
    {
        "id": 44,
        "subject": "General Knowledge",
        "question": "What is the longest river in the world by general consensus?",
        "options": {"A": "Amazon River", "B": "Nile River", "C": "Yangtze River", "D": "Mississippi River"},
        "correct_answer": "B",
        "explanation": "The Nile River in northeastern Africa is traditionally recognized as the longest river (~6,650 km)."
    },
    {
        "id": 45,
        "subject": "General Knowledge",
        "question": "Who wrote the play 'Hamlet'?",
        "options": {"A": "Christopher Marlowe", "B": "William Shakespeare", "C": "John Milton", "D": "Charles Dickens"},
        "correct_answer": "B",
        "explanation": "William Shakespeare authored Hamlet around 1599-1601."
    },
    {
        "id": 46,
        "subject": "General Knowledge",
        "question": "What is the currency of Japan?",
        "options": {"A": "Yuan", "B": "Won", "C": "Yen", "D": "Ringgit"},
        "correct_answer": "C",
        "explanation": "The official currency of Japan is the Japanese Yen (JPY)."
    },
    {
        "id": 47,
        "subject": "General Knowledge",
        "question": "Which treaty marked the formal end of World War I in 1919?",
        "options": {"A": "Treaty of Versailles", "B": "Treaty of Paris", "C": "Treaty of Utrecht", "D": "Treaty of Ghent"},
        "correct_answer": "A",
        "explanation": "The Treaty of Versailles was signed on June 28, 1919, officially ending the state of war between Germany and the Allied Powers."
    },
    {
        "id": 48,
        "subject": "General Knowledge",
        "question": "Which organ in the human body produces insulin?",
        "options": {"A": "Liver", "B": "Kidney", "C": "Pancreas", "D": "Gallbladder"},
        "correct_answer": "C",
        "explanation": "Beta cells in the islets of Langerhans of the pancreas secrete insulin."
    },
    {
        "id": 49,
        "subject": "General Knowledge",
        "question": "What is the hardest naturally occurring mineral on Earth?",
        "options": {"A": "Corundum", "B": "Topaz", "C": "Diamond", "D": "Quartz"},
        "correct_answer": "C",
        "explanation": "Diamond rates 10 on the Mohs hardness scale, making it the hardest natural mineral."
    },
    {
        "id": 50,
        "subject": "General Knowledge",
        "question": "What is the chemical symbol for gold?",
        "options": {"A": "Ag", "B": "Au", "C": "Fe", "D": "Pb"},
        "correct_answer": "B",
        "explanation": "Au derives from the Latin word 'aurum', meaning shining dawn or gold."
    },
    {
        "id": 51,
        "subject": "General Knowledge",
        "question": "In which country are the ancient pyramids of Giza located?",
        "options": {"A": "Sudan", "B": "Egypt", "C": "Greece", "D": "Jordan"},
        "correct_answer": "B",
        "explanation": "The Giza pyramid complex sits on the Giza plateau near Cairo, Egypt."
    },
    {
        "id": 52,
        "subject": "General Knowledge",
        "question": "Who proposed the General Theory of Relativity?",
        "options": {"A": "Isaac Newton", "B": "Albert Einstein", "C": "Niels Bohr", "D": "Max Planck"},
        "correct_answer": "B",
        "explanation": "Albert Einstein published the General Theory of Relativity in 1915."
    },

    # --- 5. Physics (13) ---
    {
        "id": 53,
        "subject": "Physics",
        "question": "What is the SI unit of electrical resistance?",
        "options": {"A": "Volt", "B": "Ohm", "C": "Ampere", "D": "Farad"},
        "correct_answer": "B",
        "explanation": "The Ohm (symbol Omega) is the derived SI unit of electrical impedance and resistance."
    },
    {
        "id": 54,
        "subject": "Physics",
        "question": "According to Newton's Second Law of Motion, force equals:",
        "options": {"A": "Mass divided by acceleration", "B": "Mass multiplied by acceleration", "C": "Velocity multiplied by mass", "D": "Work divided by time"},
        "correct_answer": "B",
        "explanation": "F = m * a states that resultant force equals mass multiplied by acceleration."
    },
    {
        "id": 55,
        "subject": "Physics",
        "question": "What is the approximate speed of light in a vacuum?",
        "options": {"A": "3 x 10^6 m/s", "B": "3 x 10^8 m/s", "C": "3 x 10^10 m/s", "D": "3 x 10^5 km/s"},
        "correct_answer": "B",
        "explanation": "The speed of light c in vacuum is exactly 299,792,458 m/s, approximately 3 x 10^8 m/s."
    },
    {
        "id": 56,
        "subject": "Physics",
        "question": "Which principle states that an increase in fluid speed occurs simultaneously with a decrease in pressure?",
        "options": {"A": "Pascal's Principle", "B": "Bernoulli's Principle", "C": "Archimedes' Principle", "D": "Hooke's Law"},
        "correct_answer": "B",
        "explanation": "Bernoulli's principle establishes conservation of energy along a fluid streamline."
    },
    {
        "id": 57,
        "subject": "Physics",
        "question": "What type of wave is sound in air?",
        "options": {"A": "Transverse wave", "B": "Longitudinal wave", "C": "Electromagnetic wave", "D": "Surface wave"},
        "correct_answer": "B",
        "explanation": "Sound propagates through air as longitudinal compressions and rarefactions parallel to the wave motion."
    },
    {
        "id": 58,
        "subject": "Physics",
        "question": "What physical quantity is measured in Joules per second (J/s)?",
        "options": {"A": "Work", "B": "Power", "C": "Momentum", "D": "Torque"},
        "correct_answer": "B",
        "explanation": "Power is the rate of energy transfer, measured in Watts (1 Watt = 1 Joule per second)."
    },
    {
        "id": 59,
        "subject": "Physics",
        "question": "Which thermodynamic law defines the concept of temperature and thermal equilibrium?",
        "options": {"A": "Zeroth Law", "B": "First Law", "C": "Second Law", "D": "Third Law"},
        "correct_answer": "A",
        "explanation": "The Zeroth Law of Thermodynamics establishes that if systems A and B are each in equilibrium with C, they are in equilibrium with each other."
    },
    {
        "id": 60,
        "subject": "Physics",
        "question": "What happens to the resistance of a pure semiconductor as temperature increases?",
        "options": {"A": "Increases linearly", "B": "Decreases", "C": "Remains constant", "D": "Drops to absolute zero"},
        "correct_answer": "B",
        "explanation": "Semiconductors have a negative temperature coefficient; higher thermal energy excites more valence electrons into the conduction band."
    },
    {
        "id": 61,
        "subject": "Physics",
        "question": "What is the phenomenon where light bends when passing from one medium to another?",
        "options": {"A": "Reflection", "B": "Refraction", "C": "Diffraction", "D": "Polarization"},
        "correct_answer": "B",
        "explanation": "Refraction is the change in wave direction caused by a change in speed across differing optical densities."
    },
    {
        "id": 62,
        "subject": "Physics",
        "question": "What conservation law directly yields Kirchhoff's Current Law (junction rule)?",
        "options": {"A": "Conservation of Energy", "B": "Conservation of Charge", "C": "Conservation of Momentum", "D": "Conservation of Mass"},
        "correct_answer": "B",
        "explanation": "KCL reflects charge conservation: total charge entering an electrical junction must equal total charge leaving."
    },
    {
        "id": 63,
        "subject": "Physics",
        "question": "What is the acceleration due to gravity on the surface of the Earth approximately?",
        "options": {"A": "8.9 m/s^2", "B": "9.8 m/s^2", "C": "10.8 m/s^2", "D": "12.0 m/s^2"},
        "correct_answer": "B",
        "explanation": "Standard surface gravitational acceleration on Earth is 9.80665 m/s^2."
    },
    {
        "id": 64,
        "subject": "Physics",
        "question": "Which particle mediates the electromagnetic force in the Standard Model?",
        "options": {"A": "Gluon", "B": "Photon", "C": "W boson", "D": "Graviton"},
        "correct_answer": "B",
        "explanation": "Photons are the gauge bosons mediating quantum electrodynamic interactions."
    },
    {
        "id": 65,
        "subject": "Physics",
        "question": "What is the capacitance unit named after Michael Faraday?",
        "options": {"A": "Henry", "B": "Tesla", "C": "Farad", "D": "Weber"},
        "correct_answer": "C",
        "explanation": "The Farad (F) is the SI unit of capacitance."
    },

    # --- 6. Chemistry (13) ---
    {
        "id": 66,
        "subject": "Chemistry",
        "question": "What is the pH value of pure water at 25 degrees Celsius?",
        "options": {"A": "5.0", "B": "7.0", "C": "8.5", "D": "14.0"},
        "correct_answer": "B",
        "explanation": "At 25°C, pure neutral water has equal [H+] and [OH-] concentrations of 10^-7 M, giving a pH of 7.0."
    },
    {
        "id": 67,
        "subject": "Chemistry",
        "question": "Which noble gas is the lightest and most unreactive?",
        "options": {"A": "Neon", "B": "Helium", "C": "Argon", "D": "Krypton"},
        "correct_answer": "B",
        "explanation": "Helium has an atomic number of 2 with a filled 1s^2 outer shell, making it the lightest noble gas."
    },
    {
        "id": 68,
        "subject": "Chemistry",
        "question": "What type of bond is formed by the sharing of electron pairs between atoms?",
        "options": {"A": "Ionic bond", "B": "Covalent bond", "C": "Metallic bond", "D": "Hydrogen bond"},
        "correct_answer": "B",
        "explanation": "Covalent bonds form when non-metal atoms share valence electron pairs."
    },
    {
        "id": 69,
        "subject": "Chemistry",
        "question": "What is Avogadro's number approximately?",
        "options": {"A": "6.022 x 10^21", "B": "6.022 x 10^23", "C": "3.141 x 10^23", "D": "1.602 x 10^-19"},
        "correct_answer": "B",
        "explanation": "Avogadro's constant is approximately 6.02214076 x 10^23 particles per mole."
    },
    {
        "id": 70,
        "subject": "Chemistry",
        "question": "What happens during an oxidation reaction?",
        "options": {"A": "Gain of electrons", "B": "Loss of electrons", "C": "Gain of neutrons", "D": "Decrease in oxidation state"},
        "correct_answer": "B",
        "explanation": "Oxidation is defined as the loss of electrons ('OIL RIG': Oxidation Is Loss, Reduction Is Gain)."
    },
    {
        "id": 71,
        "subject": "Chemistry",
        "question": "Which element has the highest electronegativity on the Pauling scale?",
        "options": {"A": "Oxygen", "B": "Chlorine", "C": "Fluorine", "D": "Nitrogen"},
        "correct_answer": "C",
        "explanation": "Fluorine has the highest electronegativity value of ~3.98."
    },
    {
        "id": 72,
        "subject": "Chemistry",
        "question": "What is the chemical formula for table salt?",
        "options": {"A": "KCl", "B": "NaCl", "C": "CaCl2", "D": "Na2SO4"},
        "correct_answer": "B",
        "explanation": "Table salt is sodium chloride, NaCl."
    },
    {
        "id": 73,
        "subject": "Chemistry",
        "question": "What law states that at constant temperature, pressure is inversely proportional to volume for an ideal gas?",
        "options": {"A": "Charles's Law", "B": "Boyle's Law", "C": "Gay-Lussac's Law", "D": "Dalton's Law"},
        "correct_answer": "B",
        "explanation": "Boyle's Law states P1 * V1 = P2 * V2 when temperature is kept constant."
    },
    {
        "id": 74,
        "subject": "Chemistry",
        "question": "What is the main component of natural gas?",
        "options": {"A": "Propane", "B": "Butane", "C": "Methane", "D": "Ethane"},
        "correct_answer": "C",
        "explanation": "Methane (CH4) typically comprises 70% to 90% of natural gas."
    },
    {
        "id": 75,
        "subject": "Chemistry",
        "question": "Which catalyst is traditionally used in the industrial Haber-Bosch process for ammonia synthesis?",
        "options": {"A": "Platinum", "B": "Iron", "C": "Nickel", "D": "Copper"},
        "correct_answer": "B",
        "explanation": "Iron enriched with potassium and aluminum oxides acts as the heterogeneous catalyst in the Haber process."
    },
    {
        "id": 76,
        "subject": "Chemistry",
        "question": "What is an isotope?",
        "options": {"A": "Atoms with same neutrons, different protons", "B": "Atoms with same protons, different neutrons", "C": "Molecules with same formula, different structures", "D": "Ions with identical charge"},
        "correct_answer": "B",
        "explanation": "Isotopes are variants of a chemical element with equal proton counts but differing numbers of neutrons."
    },
    {
        "id": 77,
        "subject": "Chemistry",
        "question": "What is the atomic number of Carbon?",
        "options": {"A": "4", "B": "6", "C": "12", "D": "14"},
        "correct_answer": "B",
        "explanation": "Carbon contains 6 protons, giving it atomic number 6."
    },
    {
        "id": 78,
        "subject": "Chemistry",
        "question": "Which of the following compounds is an aromatic hydrocarbon?",
        "options": {"A": "Cyclohexane", "B": "Benzene", "C": "Hexene", "D": "Acetylene"},
        "correct_answer": "B",
        "explanation": "Benzene (C6H6) satisfies Huckel's rule (4n + 2 pi electrons = 6) and has delocalized aromatic ring stability."
    },

    # --- 7. Business & Finance (13) ---
    {
        "id": 79,
        "subject": "Business & Finance",
        "question": "What financial statement shows a firm's assets, liabilities, and shareholders' equity at a specific point in time?",
        "options": {"A": "Income Statement", "B": "Balance Sheet", "C": "Cash Flow Statement", "D": "Statement of Retained Earnings"},
        "correct_answer": "B",
        "explanation": "The Balance Sheet reports the financial position equation: Assets = Liabilities + Equity at a snapshot date."
    },
    {
        "id": 80,
        "subject": "Business & Finance",
        "question": "What metric represents market capitalization of a public company?",
        "options": {"A": "Total Debt + Equity", "B": "Share Price * Total Outstanding Shares", "C": "Annual Net Profit / Shares", "D": "Gross Revenue * Operating Margin"},
        "correct_answer": "B",
        "explanation": "Market capitalization is calculated by multiplying current market price per share by total outstanding shares."
    },
    {
        "id": 81,
        "subject": "Business & Finance",
        "question": "What is the primary objective of monetary policy conducted by central banks?",
        "options": {"A": "Maximize corporate tax collections", "B": "Maintain price stability and employment", "C": "Fix currency exchange rates permanently", "D": "Fund infrastructure projects directly"},
        "correct_answer": "B",
        "explanation": "Central banks use interest rates and open market operations to manage inflation and promote sustainable employment."
    },
    {
        "id": 82,
        "subject": "Business & Finance",
        "question": "Which financial ratio measures a company's ability to cover short-term obligations with liquid assets?",
        "options": {"A": "Debt-to-Equity Ratio", "B": "Current Ratio", "C": "Return on Assets", "D": "Price-to-Earnings Ratio"},
        "correct_answer": "B",
        "explanation": "Current Ratio = Current Assets / Current Liabilities, assessing liquidity over a one-year horizon."
    },
    {
        "id": 83,
        "subject": "Business & Finance",
        "question": "In economics, what is 'opportunity cost'?",
        "options": {"A": "Out-of-pocket cash spent on raw materials", "B": "The value of the next best alternative foregone", "C": "Depreciation of physical machinery", "D": "Sunk cost that cannot be recovered"},
        "correct_answer": "B",
        "explanation": "Opportunity cost is the potential benefit lost when choosing one alternative over another."
    },
    {
        "id": 84,
        "subject": "Business & Finance",
        "question": "What does EBITDA stand for?",
        "options": {"A": "Earnings Before Interest, Taxes, Depreciation, and Amortization", "B": "Equity Before Investment, Turnover, Debt, and Assets", "C": "Estimated Balance of Interest, Taxes, and Dividends Available", "D": "Enterprise Budget for Internal Training and Development Administration"},
        "correct_answer": "A",
        "explanation": "EBITDA evaluates core operational profitability by stripping financing decisions and accounting depreciation."
    },
    {
        "id": 85,
        "subject": "Business & Finance",
        "question": "What market condition exists when a single seller controls the entire supply of a good or service?",
        "options": {"A": "Oligopoly", "B": "Monopsony", "C": "Monopoly", "D": "Perfect Competition"},
        "correct_answer": "C",
        "explanation": "A monopoly is an industry structure characterized by a single supplier with substantial market entry barriers."
    },
    {
        "id": 86,
        "subject": "Business & Finance",
        "question": "What is the break-even point in business operations?",
        "options": {"A": "When revenue equals operating cash flow", "B": "When total revenues equal total costs (fixed + variable)", "C": "When gross margin reaches 50%", "D": "When debt is completely retired"},
        "correct_answer": "B",
        "explanation": "Break-even occurs at the production/sales volume where total revenue matches total incurred costs, yielding zero profit."
    },
    {
        "id": 87,
        "subject": "Business & Finance",
        "question": "What does the 'P/E ratio' compare?",
        "options": {"A": "Profit to Equity", "B": "Price per share to Earnings per share", "C": "Preferred stock to Enterprise value", "D": "Payables to Expenses"},
        "correct_answer": "B",
        "explanation": "The Price-to-Earnings ratio measures how much investors pay per dollar of annual net earnings."
    },
    {
        "id": 88,
        "subject": "Business & Finance",
        "question": "Which marketing framework evaluates Strengths, Weaknesses, Opportunities, and Threats?",
        "options": {"A": "PESTLE Analysis", "B": "Porter's Five Forces", "C": "SWOT Analysis", "D": "BCG Matrix"},
        "correct_answer": "C",
        "explanation": "SWOT analysis is a strategic planning tool auditing internal capabilities and external market dynamics."
    },
    {
        "id": 89,
        "subject": "Business & Finance",
        "question": "In project management, what does the critical path determine?",
        "options": {"A": "The lowest cost budget allocation", "B": "The longest sequence of dependent activities determining minimum project duration", "C": "The safety compliance requirements", "D": "The team staffing matrix"},
        "correct_answer": "B",
        "explanation": "The critical path is the longest path of planned activities to the end of the project without float."
    },
    {
        "id": 90,
        "subject": "Business & Finance",
        "question": "What is a 'bear market' commonly defined as?",
        "options": {"A": "A market with rising prices and investor optimism", "B": "A market decline of 20% or more from recent peak levels", "C": "A trading session halted by exchange circuit breakers", "D": "An equity market dominated by retail investors"},
        "correct_answer": "B",
        "explanation": "Financial markets describe a 20%+ drop from recent highs accompanied by widespread pessimism as a bear market."
    },
    {
        "id": 91,
        "subject": "Business & Finance",
        "question": "What is working capital?",
        "options": {"A": "Total long-term assets minus long-term debt", "B": "Current assets minus current liabilities", "C": "Retained earnings plus capital stock", "D": "Net operating profit after tax"},
        "correct_answer": "B",
        "explanation": "Working capital = Current Assets - Current Liabilities, representing short-term operating liquidity."
    },

    # --- 8. Networking & Cloud (13) ---
    {
        "id": 92,
        "subject": "Networking",
        "question": "Which layer of the OSI model is responsible for end-to-end reliable transmission and flow control?",
        "options": {"A": "Network Layer", "B": "Transport Layer", "C": "Data Link Layer", "D": "Session Layer"},
        "correct_answer": "B",
        "explanation": "Layer 4 (Transport Layer, e.g. TCP) provides end-to-end communication, segmentation, error recovery, and flow control."
    },
    {
        "id": 93,
        "subject": "Networking",
        "question": "What is the standard port number for secure HTTPS communication?",
        "options": {"A": "80", "B": "22", "C": "443", "D": "8080"},
        "correct_answer": "C",
        "explanation": "Port 443 is designated for HTTP over TLS/SSL (HTTPS)."
    },
    {
        "id": 94,
        "subject": "Networking",
        "question": "How many bits are in an IPv4 address compared to an IPv6 address?",
        "options": {"A": "32 bits vs 64 bits", "B": "32 bits vs 128 bits", "C": "64 bits vs 128 bits", "D": "16 bits vs 32 bits"},
        "correct_answer": "B",
        "explanation": "IPv4 addresses are 32 bits (4 octets) long; IPv6 addresses are 128 bits (16 octets) long."
    },
    {
        "id": 95,
        "subject": "Networking",
        "question": "Which protocol automatically assigns dynamic IP addresses to devices on a local area network?",
        "options": {"A": "DNS", "B": "DHCP", "C": "ARP", "D": "BGP"},
        "correct_answer": "B",
        "explanation": "Dynamic Host Configuration Protocol (DHCP) leases IP configuration automatically to network clients."
    },
    {
        "id": 96,
        "subject": "Networking",
        "question": "What is the primary role of the Address Resolution Protocol (ARP)?",
        "options": {"A": "Map IP addresses to physical MAC addresses", "B": "Translate domain names to IP addresses", "C": "Encrypt IP packets across routers", "D": "Filter traffic at the firewall boundary"},
        "correct_answer": "A",
        "explanation": "ARP resolves an IPv4 network address into its corresponding physical Ethernet MAC hardware address."
    },
    {
        "id": 97,
        "subject": "Networking",
        "question": "Which protocol is connectionless and does not guarantee packet delivery or sequencing?",
        "options": {"A": "TCP", "B": "UDP", "C": "SCTP", "D": "TLS"},
        "correct_answer": "B",
        "explanation": "User Datagram Protocol (UDP) is an unacknowledged, connectionless protocol prioritizing low latency over reliability."
    },
    {
        "id": 98,
        "subject": "Networking",
        "question": "What type of DNS record maps a domain hostname directly to an IPv4 address?",
        "options": {"A": "AAAA Record", "B": "A Record", "C": "CNAME Record", "D": "MX Record"},
        "correct_answer": "B",
        "explanation": "An 'A' record points a domain name to an IPv4 address; 'AAAA' is used for IPv6."
    },
    {
        "id": 99,
        "subject": "Networking",
        "question": "What is the maximum transmission unit (MTU) standard for Ethernet frames?",
        "options": {"A": "576 bytes", "B": "1500 bytes", "C": "4096 bytes", "D": "9000 bytes"},
        "correct_answer": "B",
        "explanation": "The standard Ethernet MTU is 1500 bytes of payload per packet."
    },
    {
        "id": 100,
        "subject": "Networking",
        "question": "Which routing protocol is an exterior gateway protocol used to route traffic between autonomous systems on the Internet?",
        "options": {"A": "OSPF", "B": "RIP", "C": "BGP", "D": "EIGRP"},
        "correct_answer": "C",
        "explanation": "Border Gateway Protocol (BGP) is the core routing protocol coordinating traffic between Internet Service Providers."
    },
    {
        "id": 101,
        "subject": "Networking",
        "question": "What CIDR prefix corresponds to the standard subnet mask 255.255.255.0?",
        "options": {"A": "/16", "B": "/24", "C": "/28", "D": "/32"},
        "correct_answer": "B",
        "explanation": "255.255.255.0 contains 24 contiguous binary ones (8 + 8 + 8 = 24)."
    },
    {
        "id": 102,
        "subject": "Networking",
        "question": "Which security protocol provides authenticated and encrypted communication for remote terminal sessions over port 22?",
        "options": {"A": "Telnet", "B": "SSH", "C": "FTP", "D": "SNMP"},
        "correct_answer": "B",
        "explanation": "Secure Shell (SSH) replaces unencrypted Telnet with strong cryptographic authentication on port 22."
    },
    {
        "id": 103,
        "subject": "Networking",
        "question": "What is the function of Network Address Translation (NAT)?",
        "options": {"A": "Convert analog signals into digital bits", "B": "Map private IP addresses within a local network to a public IP address", "C": "Compress video stream packets", "D": "Authenticate Wi-Fi users via 802.1X"},
        "correct_answer": "B",
        "explanation": "NAT conserves public IPv4 addresses by translating private RFC 1918 addresses into a single public address."
    },
    {
        "id": 104,
        "subject": "Networking",
        "question": "What is the default TCP port for DNS queries?",
        "options": {"A": "25", "B": "53", "C": "110", "D": "143"},
        "correct_answer": "B",
        "explanation": "DNS uses UDP/TCP port 53 for hostname resolution and zone transfers."
    }
]


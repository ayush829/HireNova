import re

# Comprehensive dictionary/list of standard industry keywords across software engineering, data science, DevOps, and soft skills
SKILLS = [
    # Programming Languages
    "python", "javascript", "typescript", "java", "c++", "c#", "ruby", "go", "golang", "rust", "php", "swift", "kotlin", "scala", "r", "c", "matlab",
    
    # Web Frameworks & Libraries
    "react", "react native", "next.js", "nextjs", "vue", "vuejs", "angular", "angularjs", "svelte", "jquery", "bootstrap", "tailwind", "tailwindcss",
    "nodejs", "node.js", "express", "expressjs", "django", "flask", "fastapi", "spring", "spring boot", "ruby on rails", "laravel", "asp.net", ".net",
    
    # Databases & Caching
    "sql", "mysql", "postgresql", "postgres", "sqlite", "mongodb", "redis", "cassandra", "dynamodb", "oracle", "mariadb", "firebase", "firestore", "elasticsearch",
    
    # Cloud & DevOps
    "aws", "amazon web services", "azure", "gcp", "google cloud", "google cloud platform", "docker", "kubernetes", "k8s", "terraform", "ansible", 
    "jenkins", "github actions", "gitlab ci", "ci/cd", "cicd", "linux", "unix", "nginx", "apache", "prometheus", "grafana",
    
    # AI, Data Science & Machine Learning
    "machine learning", "deep learning", "ai", "artificial intelligence", "data science", "nlp", "natural language processing", "computer vision", 
    "tensorflow", "pytorch", "keras", "scikit-learn", "sklearn", "pandas", "numpy", "matplotlib", "seaborn", "tableau", "power bi", "spark", "hadoop",
    
    # Version Control & Tools
    "git", "github", "gitlab", "bitbucket", "jira", "confluence", "trello", "slack", "postman", "figma",
    
    # Concepts & Methodologies
    "agile", "scrum", "kanban", "oop", "object-oriented programming", "rest api", "restful api", "graphql", "grpc", "microservices", "system design", 
    "tdd", "test-driven development", "unit testing", "clean code", "dry", "mvc", "data structures", "algorithms",
    
    # Soft Skills & Roles
    "leadership", "communication", "teamwork", "collaboration", "problem solving", "critical thinking", "project management", "product management",
    "time management", "mentoring", "agile leadership", "adaptability", "creativity"
]

def extract_skills(text: str) -> list:
    """
    Extracts defined skills from a text string.
    Uses regex to ensure boundary-safe matches (e.g. 'go' is not matched in 'good').
    """
    if not text:
        return []
        
    found = []
    text_lower = f" {text.lower()} "  # Pad with spaces to make boundary checks simpler
    
    for skill in SKILLS:
        # Handle special skills with dots or symbols like c++, c#, .net
        escaped_skill = re.escape(skill)
        
        # Define matching pattern depending on whether skill contains special symbols
        if any(char in skill for char in ['+', '#', '.']):
            # For skills like c++, c#, .net, check if it's bounded by whitespace or punctuation
            pattern = r'(?:^|[\s,;().])' + escaped_skill + r'(?:$|[\s,;().])'
        else:
            # Standard word boundary check
            pattern = r'\b' + escaped_skill + r'\b'
            
        if re.search(pattern, text_lower):
            found.append(skill)
            
    return sorted(list(set(found)))

def compare_skills(resume_skills: list, jd_skills: list) -> tuple:
    """
    Compares resume skills against job description skills.
    Returns (matched_skills, missing_skills).
    """
    matched = []
    missing = []
    
    # Convert resume_skills to set for O(1) lookup
    resume_skills_set = set(resume_skills)
    
    for skill in jd_skills:
        if skill in resume_skills_set:
            matched.append(skill)
        else:
            missing.append(skill)
            
    return sorted(matched), sorted(missing)

def ats_score(matched: list, total_jd_skills: int) -> int:
    """
    Calculates the ATS percentage score.
    Returns an integer percentage between 0 and 100.
    """
    if total_jd_skills == 0:
        # If JD lists no skills, default to a high standard or 0 based on user logic.
        # Let's say if no skills are found in JD, score is 100 (or 0 if no comparison is possible).
        # We will return 100 if the resume has skills, or 0 if it has none.
        return 100 if len(matched) > 0 else 0
        
    return int((len(matched) / total_jd_skills) * 100)

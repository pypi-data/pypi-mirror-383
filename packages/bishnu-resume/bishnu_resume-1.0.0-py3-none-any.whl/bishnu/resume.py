"""Resume data, formatting, and animations for the bishnu package."""

import sys
import time
from typing import List

DEFAULT_BIO = {
    "full_name": "Bishnu Sahu",
    "title": "Student | Aspiring Data Scientist & ML Engineer",
    "email": "mebishnusahu0595@gmail.com",
    "phone": "+91-9301105706",
    "github": "https://github.com/mebishnusahu0595",
    "linkedin": "https://linkedin.com/in/mebishnusahu05",
    "portfolio": "https://mebishnusahu.netlify.app/",
    "education": {
        "degree": "Bachelor of Computer Applications (BCA)",
        "university": "Hemchand Yadav University, Bhilai",
        "graduation": "Class of 2026",
    },
    "objective": (
        "Enthusiastic and dedicated BCA student with strong skills in web development, Python, SQL, data "
        "analysis, machine learning, and AI. Seeking to apply and expand knowledge through diverse projects "
        "and internships, with the long-term goal of becoming a Data Scientist and ML Engineer backed by "
        "hands-on experience and continuous learning."
    ),
    "skills": {
        "Programming": ["Python", "SQL"],
        "Web Development": ["HTML", "CSS", "JavaScript (full-stack exposure)"],
        "Tools & Platforms": ["Excel", "Git", "Open-source AI Models"],
        "Domains": ["Data Analysis", "Machine Learning", "Artificial Intelligence"],
    },
    "experience": [
        {
            "role": "Internship — Cognizant",
            "duration": "3 Months",
            "description": [
                "Gained practical experience in software development and project management.",
                "Worked on client-based tasks involving coding, testing, and debugging."
            ]
        },
        {
            "role": "Freelance Developer",
            "duration": "Ongoing",
            "description": [
                "Developed websites including alhpost38.com, urdesindia.in, bbntours.com, and oncorg.com.",
                "Created a trailing-based real-time stock dashboard to track market data dynamically.",
                "Built a 3D AI avatar model demonstrating integration of AI with animation.",
                "Developed a healthcare chatbot using open-source Gemma 3n AI models.",
                "Created a smart screenshot manager tool for efficient screenshot tagging and searching.",
                "Designed 'Hello Roomie' — a hostel student management platform.",
                "Built an AI diagnosis detection model for healthcare applications.",
                "Projects are hosted locally due to hosting cost constraints; full code available on GitHub."
            ]
        },
        {
            "role": "Open Source Contributor — AOOSIE-org",
            "duration": "Ongoing",
            "description": [
                "Active contributor to the Association of Open Source in Education.",
                "Contributing to open-source projects and educational AI initiatives."
            ]
        }
    ],
    "projects": [
        {
            "name": "Real-Time Stock Dashboard",
            "description": "Developed a dynamic dashboard using trailing algorithms to monitor live stock data."
        },
        {
            "name": "3D AI Avatar Model",
            "description": "Integrated AI capabilities with 3D modeling for an interactive avatar."
        },
        {
            "name": "Healthcare Chatbot",
            "description": "Created a medical chatbot using open-source Gemma 3n models to assist patient queries."
        },
        {
            "name": "Screenshot Manager",
            "description": "Developed a tool to organize and tag screenshots automatically with search functionality."
        },
        {
            "name": "Hostel Management Website",
            "description": "Designed a full-featured portal for student accommodation management."
        },
        {
            "name": "AI Diagnosis Detection Model",
            "description": "Built a diagnostic AI system to aid healthcare professionals."
        }
    ],
    "certifications": [
        {
            "name": "Data Science 101",
            "issuer": "IBM - Cognitive Class (Course ID: DS0101EN)",
            "date": "October 30, 2024",
            "skills": [
                "Statistical Analysis", "Data Visualization", "Machine Learning Fundamentals",
                "Python for Data Science", "Data Mining and Analytics"
            ],
            "description": "Successfully completed comprehensive Data Science fundamentals course covering statistical analysis, data visualization, and machine learning concepts through IBM's developer skills network."
        },
        {
            "name": "Learn To Build A Real Time Gen AI Customer Service Bot",
            "issuer": "NullClass",
            "date": "August 18, 2024",
            "skills": [
                "Generative AI Model Implementation", "Natural Language Processing (NLP)",
                "Real-time Chatbot Development", "Customer Service Automation", "AI Integration and Deployment"
            ],
            "description": "Completed advanced training on building real-time generative AI customer service bots, including natural language processing and automated response systems."
        }
    ],
    "websites": [
        "https://mebishnusahu.netlify.app/",
        "https://alhpost38.com",
        "https://urdesindia.in",
        "https://bbntours.com",
        "https://oncorg.com",
        "http://tuneinprayer.com/"
    ]
}

# ASCII Animation Frames
RUNNER_FRAMES = [
    "     __o",
    "   _ \\<,",
    "  (_)/(_)",
    "",
    "      o",
    "     /|",
    "    / \\",
    "",
    "     _o",
    "   __\\-",
    "  (_)/(_)",
]

LOADING_FRAMES = [
    "⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"
]

STAR_FRAMES = [
    "✦",
    "✧",
    "★",
    "☆",
    "✦",
    "✧"
]


def animate_loading(message: str = "Loading Resume", duration: float = 2.0) -> None:
    """Display a loading animation with spinner."""
    if duration <= 0:
        return
    
    start_time = time.time()
    frame_index = 0
    
    while time.time() - start_time < duration:
        frame = LOADING_FRAMES[frame_index % len(LOADING_FRAMES)]
        sys.stdout.write(f"\r{frame} {message}...")
        sys.stdout.flush()
        time.sleep(0.1)
        frame_index += 1
    
    sys.stdout.write(f"\r✓ {message} Complete!\n")
    sys.stdout.flush()


def animate_runner(duration: float = 3.0) -> None:
    """Display a running person animation."""
    if duration <= 0:
        return
    
    start_time = time.time()
    frame_index = 0
    
    while time.time() - start_time < duration:
        # Clear previous frame
        sys.stdout.write("\r" + " " * 20 + "\r")
        
        # Display current frame
        frame = RUNNER_FRAMES[frame_index % len(RUNNER_FRAMES)]
        if frame:  # Skip empty frames
            sys.stdout.write(f"\r🏃 {frame}")
        sys.stdout.flush()
        
        time.sleep(0.3)
        frame_index += 1
    
    sys.stdout.write("\r" + " " * 20 + "\r")
    sys.stdout.flush()


def create_border_box(content: List[str], width: int = 80) -> List[str]:
    """Create a beautiful border box around content."""
    result = []
    
    # Top border
    result.append("╔" + "═" * (width - 2) + "╗")
    
    # Content with side borders
    for line in content:
        # Ensure line fits within box width
        if len(line) > width - 4:
            line = line[:width - 7] + "..."
        padding = width - len(line) - 4
        result.append(f"║ {line}{' ' * padding} ║")
    
    # Bottom border
    result.append("╚" + "═" * (width - 2) + "╝")
    
    return result


def get_resume(mode: str = "short", animated: bool = False) -> str:
    """Return a formatted resume string with beautiful alignment and optional animations."""
    bio = DEFAULT_BIO
    
    if animated:
        animate_loading("Preparing Resume", 1.5)
        print()

    if mode == "short":
        header_content = [
            f"{bio['full_name']} — {bio['title']}",
            f"Email: {bio['email']} | Phone: {bio['phone']}",
            f"Skills: {', '.join(bio['skills']['Programming'] + bio['skills']['Domains'])}"
        ]
        
        if animated:
            print("✨ Here's a quick summary:")
            time.sleep(0.5)
        
        return "\n".join(create_border_box(header_content, 80))

    # Full detailed resume with beautiful formatting
    lines = []
    
    # Header Section with Box
    header_content = [
        "",
        f"🧑‍💻 {bio['full_name'].upper()}",
        f"📋 {bio['title']}",
        "",
        f"📧 Email: {bio['email']}",
        f"📱 Phone: {bio['phone']}",
        f"🔗 GitHub: {bio['github']}",
        f"💼 LinkedIn: {bio['linkedin']}",
        f"🌐 Portfolio: {bio['portfolio']}",
        ""
    ]
    
    lines.extend(create_border_box(header_content, 80))
    lines.append("")
    
    if animated:
        animate_runner(2.0)
        print("\n🎯 Building your complete profile...\n")
        time.sleep(1)
    
    # Objective Section
    lines.append("🎯 OBJECTIVE")
    lines.append("═" * 50)
    # Word wrap objective for better readability
    objective_words = bio["objective"].split()
    current_line = ""
    for word in objective_words:
        if len(current_line + word + " ") <= 75:
            current_line += word + " "
        else:
            lines.append(f"   {current_line.strip()}")
            current_line = word + " "
    if current_line:
        lines.append(f"   {current_line.strip()}")
    lines.append("")
    
    # Education Section
    lines.append("🎓 EDUCATION")
    lines.append("═" * 50)
    edu = bio["education"]
    lines.append(f"   🏫 {edu['degree']}")
    lines.append(f"   🏛️  {edu['university']}")
    lines.append(f"   📅 {edu['graduation']}")
    lines.append("")
    
    # Skills Section with better formatting
    lines.append("🧠 TECHNICAL SKILLS")
    lines.append("═" * 50)
    for category, items in bio["skills"].items():
        lines.append(f"   💡 {category}:")
        for i, skill in enumerate(items):
            prefix = "   ├─" if i < len(items) - 1 else "   └─"
            lines.append(f"{prefix} {skill}")
        lines.append("")
    
    # Experience Section
    lines.append("💼 PROFESSIONAL EXPERIENCE")
    lines.append("═" * 50)
    for i, exp in enumerate(bio["experience"]):
        lines.append(f"   {i+1}. {exp['role']} ({exp['duration']})")
        for desc in exp["description"]:
            lines.append(f"      ▸ {desc}")
        lines.append("")
    
    # Projects Section
    lines.append("🚀 KEY PROJECTS")
    lines.append("═" * 50)
    for i, proj in enumerate(bio["projects"]):
        lines.append(f"   {i+1}. {proj['name']}")
        lines.append(f"      ▸ {proj['description']}")
        lines.append("")
    
    # Certifications Section
    lines.append("📜 CERTIFICATIONS")
    lines.append("═" * 50)
    for i, cert in enumerate(bio["certifications"]):
        lines.append(f"   {i+1}. {cert['name']}")
        lines.append(f"      🏢 {cert['issuer']} ({cert['date']})")
        lines.append(f"      📝 {cert['description']}")
        lines.append(f"      🎯 Skills: {', '.join(cert['skills'])}")
        lines.append("")
    
    # Websites Section
    lines.append("🌐 PORTFOLIO WEBSITES")
    lines.append("═" * 50)
    for i, site in enumerate(bio["websites"]):
        lines.append(f"   {i+1}. {site}")
    lines.append("")
    
    # Footer
    footer_content = [
        "",
        "⭐ Thank you for viewing my resume! ⭐",
        "© 2025 Bishnu Sahu — All Rights Reserved",
        "🚀 Future Data Scientist & ML Engineer 🚀",
        ""
    ]
    lines.extend(create_border_box(footer_content, 80))
    
    if animated:
        print("\n✨ Resume generation complete! ✨")
        time.sleep(0.5)
    
    return "\n".join(lines)


def display_animated_resume(mode: str = "long") -> None:
    """Display resume with full animations and effects."""
    print("\n" + "🌟" * 25 + " WELCOME " + "🌟" * 25)
    time.sleep(0.5)
    
    # Show loading animation
    animate_loading("Initializing Resume System", 2.0)
    time.sleep(0.5)
    
    # Show runner animation
    print("\n🏃 Fetching latest information...")
    animate_runner(3.0)
    
    # Display the resume
    print("\n" + "=" * 70)
    print(get_resume(mode, animated=True))
    print("=" * 70)
    
    # Final animation
    print("\n🎉 Resume display complete! 🎉")
    for i in range(5):
        for star in STAR_FRAMES:
            sys.stdout.write(f"\r{star} Thanks for viewing! {star}")
            sys.stdout.flush()
            time.sleep(0.2)
    print("\n")


# Maintain backward compatibility
def show_resume(mode: str = "short") -> str:
    """Simple wrapper for get_resume function for backward compatibility."""
    return get_resume(mode)

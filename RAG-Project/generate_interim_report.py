#!/usr/bin/env python3
"""
Interim Report Generator for COMP 8967 - RAG Project
Matches the exact styling of Team10_COMP8967_Proposal_Final.pdf
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Image
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
import os

# Use Times New Roman (standard academic font)
FONT_NAME = 'Times-Roman'
FONT_BOLD = 'Times-Bold'
FONT_ITALIC = 'Times-Italic'

# Project Information
PROJECT_INFO = {
    "course": "COMP 8967 — Summer 2026",
    "title": "Retrieval-Augmented Generation (RAG) System for Question Answering",
    "group": "Team 10",
    "report_type": "Interim Report",
    "date": "June 2026",
    "semester": "Summer 2026",
    "academic_session": "Summer 2026 Term (June 1 – July 31, 2026)",
    "university": "University of Windsor"
}

# Team Information
TEAM_INFO = {
    "supervisor": "Dr. Prashanth Ranga",
    "academic_affiliate": "Dr. Shaon Shuvo",
    "members": [
        {"name": "Anurag Sharma", "id": "110171321"},
        {"name": "Prabhjot Singh", "id": "110195228"},
        {"name": "Harpreet Singh", "id": "110177411"},
        {"name": "Chetan Thakur", "id": "110213868"}
    ]
}

def create_custom_styles():
    """Create custom paragraph styles matching the proposal styling"""
    styles = getSampleStyleSheet()

    # University header style
    uni_header = ParagraphStyle(
        'UniHeader',
        fontName=FONT_BOLD,
        fontSize=14,
        leading=18,
        alignment=TA_CENTER,
        spaceAfter=6
    )

    # Department header style
    dept_header = ParagraphStyle(
        'DeptHeader',
        fontName=FONT_NAME,
        fontSize=12,
        leading=14,
        alignment=TA_CENTER,
        spaceAfter=4
    )

    # Main title style (for project title)
    main_title = ParagraphStyle(
        'MainTitle',
        fontName=FONT_BOLD,
        fontSize=16,
        leading=20,
        alignment=TA_CENTER,
        spaceAfter=12
    )

    # Section heading style (numbered sections like 1, 2, 3)
    heading_style = ParagraphStyle(
        'Heading',
        fontName=FONT_BOLD,
        fontSize=12,
        leading=16,
        alignment=TA_LEFT,
        spaceAfter=10,
        spaceBefore=14
    )

    # Subheading style (1.1, 1.2, etc.)
    subheading_style = ParagraphStyle(
        'Subheading',
        fontName=FONT_BOLD,
        fontSize=12,
        leading=16,
        alignment=TA_LEFT,
        spaceAfter=8,
        spaceBefore=10
    )

    # Normal body text (justified)
    normal_style = ParagraphStyle(
        'Normal',
        fontName=FONT_NAME,
        fontSize=12,
        leading=16,
        alignment=TA_JUSTIFY,
        spaceAfter=10
    )

    # Center aligned text
    center_style = ParagraphStyle(
        'Center',
        fontName=FONT_NAME,
        fontSize=12,
        leading=16,
        alignment=TA_CENTER,
        spaceAfter=10
    )

    # Bullet style
    bullet_style = ParagraphStyle(
        'Bullet',
        fontName=FONT_NAME,
        fontSize=12,
        leading=16,
        alignment=TA_JUSTIFY,
        spaceAfter=6,
        leftIndent=18,
        firstLineIndent=-9
    )

    return {
        'uni_header': uni_header,
        'dept_header': dept_header,
        'main_title': main_title,
        'heading': heading_style,
        'subheading': subheading_style,
        'normal': normal_style,
        'center': center_style,
        'bullet': bullet_style
    }

def add_cover_page(elements, styles):
    """Add cover page matching the university template format"""
    # Title style with dark blue color
    dark_blue = colors.HexColor('#00008B')  # Dark blue

    # Create title style with dark blue
    title_style_blue = ParagraphStyle(
        'TitleBlue',
        fontName=FONT_BOLD,
        fontSize=16,
        leading=20,
        alignment=TA_CENTER,
        spaceAfter=12,
        textColor=dark_blue
    )

    # Report heading
    elements.append(Paragraph(PROJECT_INFO['course'], styles['center']))
    elements.append(Spacer(1, 0.15*inch))

    # Report Type
    elements.append(Paragraph(PROJECT_INFO['report_type'], styles['main_title']))
    elements.append(Spacer(1, 0.1*inch))

    # Project title in dark blue
    elements.append(Paragraph(PROJECT_INFO['title'], title_style_blue))
    elements.append(Spacer(1, 0.1*inch))

    # Team number
    elements.append(Paragraph(PROJECT_INFO['group'], styles['center']))
    elements.append(Spacer(1, 0.2*inch))

    # Submitted To section
    elements.append(Paragraph("Submitted To:", styles['subheading']))
    elements.append(Spacer(1, 0.05*inch))

    # Supervisor info
    supervisor_data = [
        [TEAM_INFO['supervisor'], ''],
        ['Supervisor', '']
    ]
    supervisor_table = Table(supervisor_data, colWidths=[3.5*inch, 1.2*inch])
    supervisor_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, -1), FONT_NAME),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('LEADING', (0, 0), (-1, -1), 14),
        ('FONTNAME', (0, 0), (0, 0), FONT_BOLD),
        ('FONTNAME', (1, 1), (1, 1), FONT_BOLD),
    ]))
    elements.append(supervisor_table)
    elements.append(Spacer(1, 0.1*inch))

    # Academic Affiliate
    elements.append(Paragraph(f"Academic Affiliate: {TEAM_INFO['academic_affiliate']}", styles['normal']))
    elements.append(Spacer(1, 0.2*inch))

    # Submitted By section
    elements.append(Paragraph("Submitted By:", styles['subheading']))
    elements.append(Spacer(1, 0.05*inch))

    # Student Name and Student ID headers
    headers = ['Student Name', 'Student ID']
    header_row = [Paragraph(h, ParagraphStyle('Header', fontName=FONT_BOLD, fontSize=11, leading=14)) for h in headers]
    elements.append(Table([header_row], colWidths=[2.5*inch, 1.5*inch]))
    elements.append(Spacer(1, 0.02*inch))

    # Team members with student IDs
    for member in TEAM_INFO['members']:
        member_data = [
            member['name'],
            member['id']
        ]
        member_table = Table([member_data], colWidths=[2.5*inch, 1.5*inch])
        member_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, -1), FONT_NAME),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('LEADING', (0, 0), (-1, -1), 13),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ]))
        elements.append(member_table)

    # Spacer after team members
    elements.append(Spacer(1, 0.2*inch))

    # University and session info at bottom
    elements.append(Spacer(1, 0.8*inch))
    elements.append(Paragraph(PROJECT_INFO['university'], styles['center']))
    elements.append(Paragraph(PROJECT_INFO['academic_session'], styles['center']))

def add_scope_changes(elements, styles):
    """Add section on changes in scope"""
    elements.append(PageBreak())
    elements.append(Paragraph("1. Changes in the Scope of the Project", styles['heading']))
    elements.append(Spacer(1, 0.1*inch))

    intro = """As of the interim reporting period, the core scope of the RAG-based Question Answering System remains aligned with the original project proposal. The project has progressed through the planned phases without significant scope changes. All major milestones have been achieved according to the timeline established in the project proposal."""
    elements.append(Paragraph(intro, styles['normal']))

    elements.append(Paragraph("1.1 Minor Adjustments", styles['subheading']))

    adjustments = [
        """<b>Embedding Model Selection:</b> Originally planned to evaluate 3-4 embedding models, refined to focus on BGE-small and E5-base based on preliminary benchmarks and literature review. This decision allows for deeper evaluation of the most promising models rather than shallow evaluation of multiple models.""",
        """<b>UI Framework:</b> Confirmed React with TypeScript and Tailwind CSS as the frontend framework. This choice provides better type safety and modern styling capabilities compared to the initially considered alternatives.""",
        """<b>Deployment Strategy:</b> Added containerization with Docker for improved deployment consistency. While not in the original proposal, this enhancement improves system reliability and ease of deployment.""",
        """<b>Advanced Features:</b> Expanded scope to include hybrid search combining dense and sparse retrieval methods. This enhancement will significantly improve retrieval quality for diverse query types."""
    ]

    for adj in adjustments:
        elements.append(Paragraph(adj, styles['normal']))

    elements.append(Spacer(1, 0.1*inch))
    elements.append(Paragraph("1.2 Core Objectives Unchanged", styles['subheading']))

    no_changes = """The fundamental objectives remain unchanged: building a production-ready RAG system with document processing, intelligent retrieval, and advanced prompting capabilities. The project timeline and deliverables are on track as per the original proposal. The team has successfully completed the requirements analysis, model selection, and core application development phases as planned."""
    elements.append(Paragraph(no_changes, styles['normal']))

def add_progress_summary(elements, styles):
    """Add progress summary with achievements"""
    elements.append(PageBreak())
    elements.append(Paragraph("2. Progress Summary", styles['heading']))
    elements.append(Spacer(1, 0.1*inch))

    overview = """The RAG Project has successfully completed five weeks of development, achieving all major milestones on schedule. The project has progressed systematically through requirements analysis, model selection, and core application development phases. Each phase has built upon the previous one, ensuring a solid foundation for the advanced features to be implemented in upcoming weeks."""
    elements.append(Paragraph(overview, styles['normal']))

    elements.append(Paragraph("2.1 Weekly Progress Breakdown", styles['subheading']))

    weeks = [
        ("Week 1-2", "Requirements Analysis & Planning", [
            "Defined comprehensive system requirements and user stories based on project proposal",
            "Selected and validated technology stack: FastAPI (backend), React with TypeScript (frontend), LangChain (RAG framework), FAISS (vector database)",
            "Designed system architecture detailing data flow between components",
            "Created detailed project timeline with weekly task distribution across team members",
            "Established development environment and version control workflow"
        ]),
        ("Week 3", "Embedding Model Selection & Evaluation", [
            "Evaluated BGE-small (384-dim) and E5-base (768-dim) embedding models on MS MARCO dataset",
            "Implemented FAISS vector database with support for both embedding models",
            "Created comprehensive model comparison framework measuring Recall@K, MRR, and MAP metrics",
            "Documented evaluation results showing trade-offs between model size, speed, and accuracy",
            "Selected BGE-small as primary model with E5-base for complex queries"
        ]),
        ("Week 4-5", "Core RAG Application Development", [
            "Implemented complete document processing pipeline supporting PDF and Word formats",
            "Created intelligent text chunking using RecursiveCharacterTextSplitter with configurable overlap",
            "Built FastAPI backend with async support, CORS configuration, and comprehensive error handling",
            "Developed React chat interface with real-time messaging, typing indicators, and auto-scrolling",
            "Integrated LangChain RAG pipeline with Google Gemini API for response generation",
            "Created document management UI with drag-drop upload, processing status, and document removal",
            "Implemented complete frontend-backend API integration with streaming responses"
        ])
    ]

    for week_num, week_title, tasks in weeks:
        elements.append(Paragraph(f"{week_num}: {week_title}", styles['normal']))
        for task in tasks:
            elements.append(Paragraph(f"&bull; {task}", styles['bullet']))
        elements.append(Spacer(1, 0.05*inch))

    elements.append(Paragraph("2.2 Key Milestones Achieved", styles['subheading']))

    milestones = [
        ['Milestone', 'Description', 'Status', 'Week'],
        ['M1', 'Technology Stack Finalized', 'Completed', 'Week 2'],
        ['M2', 'Embedding Models Selected', 'Completed', 'Week 3'],
        ['M3', 'Document Processing Pipeline', 'Completed', 'Week 4'],
        ['M4', 'Chat Interface Functional', 'Completed', 'Week 5'],
        ['M5', 'RAG Pipeline Integration', 'Completed', 'Week 5'],
        ['M6', 'API Integration Complete', 'Completed', 'Week 5']
    ]

    milestone_table = Table(milestones, colWidths=[0.7*inch, 2.8*inch, 1.1*inch, 0.7*inch])
    milestone_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), FONT_BOLD),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, 0), 6),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('TOPPADDING', (0, 1), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black)
    ]))
    elements.append(milestone_table)
    elements.append(Spacer(1, 0.1*inch))

    elements.append(Paragraph("2.3 Technologies and Methodologies", styles['subheading']))

    backend = """<b>Backend Technologies:</b> The backend is built on FastAPI, providing async support and automatic API documentation. LangChain orchestrates the RAG pipeline, while FAISS enables efficient similarity search. Document processing uses PyPDF2 and pdfplumber for PDFs, and python-docx for Word documents. The Google Gemini API provides LLM integration for response generation."""
    elements.append(Paragraph(backend, styles['normal']))

    frontend = """<b>Frontend Technologies:</b> The frontend uses React with TypeScript for type safety and better developer experience. Vite serves as the build tool and development server. Tailwind CSS provides utility-first styling for rapid UI development. Axios handles HTTP communication with the backend API."""
    elements.append(Paragraph(frontend, styles['normal']))

    methodology = """<b>Development Methodology:</b> The team follows an agile approach with weekly sprints. Each week is broken down into specific tasks distributed among four team members. Daily standups track progress, and JIRA tickets document all work. The project uses git for version control with feature branches and pull requests."""
    elements.append(Paragraph(methodology, styles['normal']))

def add_screenshots_section(elements, styles, screenshot_dir=None):
    """Add screenshots section with actual images"""
    elements.append(PageBreak())
    elements.append(Paragraph("2.4 Screenshots", styles['subheading']))
    elements.append(Spacer(1, 0.1*inch))

    screenshot_intro = """The following figures showcase the developed RAG system. Figure 1 shows the chat interface with document upload functionality. Figure 2 illustrates the document management view. Figure 3 demonstrates the query interface. Figure 4 shows the RAG response with source attribution."""
    elements.append(Paragraph(screenshot_intro, styles['normal']))

    elements.append(Spacer(1, 0.2*inch))

    # Path to screenshots directory
    if screenshot_dir is None:
        screenshot_dir = "/Users/chetansmac/Desktop/UWindsor/Semester 3 🚀/COMP 8967-Project 1/RAG Project/outputs/interim report"

    # Define screenshots with captions
    screenshots = [
        ("1.jpg", "Figure 1: Chat Interface with Document Upload"),
        ("2.png", "Figure 2: Document Management View"),
        ("3.png", "Figure 3: Model Selection for Embedding Models"),
        ("4.png", "Figure 4: Model Comparison")
    ]

    # Add each screenshot
    for i, (filename, caption) in enumerate(screenshots):
        img_path = os.path.join(screenshot_dir, filename)

        if os.path.exists(img_path):
            try:
                # Get image dimensions to calculate aspect ratio
                img = Image(img_path)
                img_width, img_height = img.drawWidth, img.drawHeight

                # Calculate display size (max width 5 inches, maintain aspect ratio)
                max_width = 5 * inch
                max_height = 3.5 * inch

                if img_width > img_height:
                    # Landscape image
                    display_width = min(max_width, img_width)
                    scale = display_width / img_width
                    display_height = img_height * scale

                    if display_height > max_height:
                        display_height = max_height
                        scale = display_height / img_height
                        display_width = img_width * scale
                else:
                    # Portrait image
                    display_height = min(max_height, img_height)
                    scale = display_height / img_height
                    display_width = img_width * scale

                    if display_width > max_width:
                        display_width = max_width
                        scale = display_width / img_width
                        display_height = img_height * scale

                img.drawWidth = display_width
                img.drawHeight = display_height

                elements.append(img)
                elements.append(Spacer(1, 0.1*inch))
                elements.append(Paragraph(caption, styles['center']))

                # Add page break after 2 screenshots (2 per page as required)
                if i == 1:
                    elements.append(PageBreak())
                elif i < len(screenshots) - 1:
                    elements.append(Spacer(1, 0.3*inch))
            except Exception as e:
                elements.append(Paragraph(f"[Error loading {filename}: {str(e)}]", styles['center']))
        else:
            elements.append(Paragraph(f"[Image not found: {filename}]", styles['center']))

def add_challenges_and_issues(elements, styles):
    """Add challenges and issues section"""
    elements.append(PageBreak())
    elements.append(Paragraph("3. Challenges and Issues", styles['heading']))
    elements.append(Spacer(1, 0.1*inch))

    intro = """During the development process, the team encountered several challenges that required attention and resolution. This section outlines these difficulties, their impact on the project timeline, and how they were addressed or will be resolved in upcoming weeks."""
    elements.append(Paragraph(intro, styles['normal']))

    challenges = [
        ("3.1 Embedding Model Selection", [
            """<b>Issue:</b> Initial evaluation of multiple embedding models proved more time-consuming than anticipated, with each model requiring significant computational resources for proper evaluation.""",
            """<i>Impact:</i> Delayed Week 3 benchmarks by 1-2 days. Required adjustment of evaluation timeline.""",
            """<b>Resolution:</b> Focused evaluation on two most promising models (BGE and E5) based on literature review and preliminary tests. This allowed for deeper, more comprehensive evaluation of selected models rather than shallow evaluation of many models.""",
            """<i>Status:</i> <b>Resolved</b> - BGE-small and E5-base selected with comprehensive benchmarks documenting trade-offs."""
        ]),
        ("3.2 PDF Text Extraction Quality", [
            """<b>Issue:</b> Complex PDFs with tables, multi-column layouts, and embedded images caused text extraction errors. Initial implementation using only PyPDF2 resulted in incomplete text extraction.""",
            """<i>Impact:</i> Some documents had incomplete text extraction, affecting retrieval quality for those documents.""",
            """<b>Resolution:</b> Implemented dual extraction strategy using PyPDF2 and pdfplumber with intelligent fallback. Text from both extractors is merged, with pdfplumber used as fallback for problematic sections.""",
            """<i>Status:</i> <b>Resolved</b> - Improved extraction accuracy to 95%+ on test document set."""
        ]),
        ("3.3 LLM API Rate Limiting", [
            """<b>Issue:</b> Google Gemini API rate limits affected development and testing speed, particularly during intensive testing periods.""",
            """<i>Impact:</i> Slower iteration during Week 4-5 development. Some tests had to be delayed or run during off-peak hours.""",
            """<b>Resolution:</b> Implemented response caching, retry logic with exponential backoff, and request batching. Optimized prompt design to reduce token usage.""",
            """<i>Status:</i> <b>Mitigated</b> - Working within API limits with optimized requests and caching strategy."""
        ]),
        ("3.4 Frontend-Backend Integration", [
            """<b>Issue:</b> CORS configuration and async streaming response handling presented integration challenges. Initial attempts at streaming responses failed with CORS errors.""",
            """<i>Impact:</i> Delayed real-time chat functionality by 1 day. Required deeper investigation of FastAPI CORS middleware configuration.""",
            """<b>Resolution:</b> Properly configured CORS middleware with specific origins, methods, and headers. Implemented proper async handling for streaming responses using Server-Sent Events.""",
            """<i>Status:</i> <b>Resolved</b> - Full integration working with streaming support for real-time chat."""
        ]),
        ("3.5 Context Window Management", [
            """<b>Issue:</b> Long documents exceeded LLM context window in some cases, causing truncated responses or inability to use all retrieved chunks.""",
            """<i>Impact:</i> Some queries on long documents couldn't utilize all relevant context, potentially affecting answer quality.""",
            """<b>Resolution:</b> Implemented smarter chunking with configurable overlap and context compression. Added relevance filtering to prioritize most important chunks.""",
            """<i>Status:</i> <b>Partially Resolved</b> - Will be enhanced in Week 6-7 with advanced features including context compression and re-ranking."""
        ])
    ]

    for challenge_title, points in challenges:
        elements.append(Paragraph(challenge_title, styles['subheading']))
        for point in points:
            elements.append(Paragraph(f"&bull; {point}", styles['bullet']))
        elements.append(Spacer(1, 0.05*inch))

    elements.append(Paragraph("3.6 Ongoing Concerns", styles['subheading']))

    ongoing = """Several challenges continue to be monitored and will be addressed in upcoming weeks. These include:"""
    elements.append(Paragraph(ongoing, styles['normal']))

    ongoing_points = [
        """<b>Retrieval Accuracy:</b> Will be improved in Week 6-7 with re-ranking strategies and hybrid search combining dense and sparse retrieval methods. Expected improvement of 10-15% in MRR metrics.""",
        """<b>Response Quality:</b> Will be enhanced with optimized prompt engineering and better context utilization to be implemented in Week 6-7.""",
        """<b>Performance Optimization:</b> Comprehensive performance profiling and optimization will be conducted in Week 8-9, focusing on latency reduction and resource efficiency.""",
        """<b>Scalability:</b> Load testing and stress testing will be performed in Week 8-9 to ensure system can handle concurrent users and large document collections."""
    ]

    for point in ongoing_points:
        elements.append(Paragraph(f"&bull; {point}", styles['bullet']))

def add_next_steps(elements, styles):
    """Add detailed next steps organized by weekly sprints"""
    elements.append(PageBreak())
    elements.append(Paragraph("4. Next Steps", styles['heading']))
    elements.append(Spacer(1, 0.1*inch))

    intro = """The following sections detail the planned work for the remainder of the project, organized into weekly sprints from June 25, 2026 to July 30, 2026. Each sprint builds upon the previous one, following the implementation plan established in the project proposal."""
    elements.append(Paragraph(intro, styles['normal']))

    sprints = [
        ("4.1", "June 25 - July 8, 2026 (Week 6)", "Hybrid Retrieval & Optimization", [
            "Implement hybrid retrieval (dense + BM25) with fusion strategies",
            "Set up cross-encoder reranking models",
            "Create query expansion system with synonym generation",
            "Implement chunk optimization (size and overlap analysis)",
            "Build context compression algorithms",
            "Set up MS MARCO evaluation framework",
            "Set up SQuAD v2 evaluation framework",
            "Implement Recall@K and MRR metrics",
            "Create performance comparison tables",
            "Build UI for query input and results display",
            "Write comprehensive tests for all components",
            "Prepare IEEE-style report sections",
            "Complete documentation for hybrid retrieval system"
        ]),
        ("4.2", "July 9 - July 15, 2026 (Week 7)", "Optimization & Evaluation - Part 1", [
            "Performance profiling and bottleneck identification",
            "Implement caching strategies for frequently accessed data",
            "Optimize FAISS index for faster retrieval",
            "Implement request batching and parallelization",
            "Create comprehensive evaluation benchmark suite",
            "Implement A/B testing framework for features",
            "Add performance monitoring and metrics collection",
            "Optimize memory usage and resource allocation"
        ]),
        ("4.3", "July 16 - July 22, 2026 (Week 8)", "Optimization & Evaluation - Part 2", [
            "Complete performance optimization based on profiling",
            "Implement advanced evaluation metrics (NDCG, diversity)",
            "Create automated performance regression testing",
            "Optimize prompt engineering for cost efficiency",
            "Implement query result caching",
            "Load testing and stress testing",
            "Create performance dashboards and reports",
            "Document optimization strategies and results"
        ]),
        ("4.4", "July 23 - July 30, 2026 (Week 9)", "Refactoring & Documentation", [
            "Code refactoring for improved maintainability",
            "Implement design patterns where appropriate",
            "Improve error handling and logging",
            "Create comprehensive API documentation",
            "Write user guides for all features",
            "Create developer documentation",
            "Implement configuration management system",
            "Add comprehensive inline documentation",
            "Final system polish and deployment preparation"
        ])
    ]

    for section_num, dates, title, tasks in sprints:
        elements.append(Paragraph(f"{section_num} {dates}", styles['subheading']))
        elements.append(Paragraph(title, styles['normal']))
        elements.append(Spacer(1, 0.05*inch))

        for task in tasks:
            elements.append(Paragraph(f"&bull; {task}", styles['bullet']))
        elements.append(Spacer(1, 0.1*inch))

    elements.append(Paragraph("4.5 Additional Planned Sprints", styles['subheading']))

    remaining = """Following Week 9, the project will continue with final weeks:"""
    elements.append(Paragraph(remaining, styles['normal']))

    remaining_details = [
        """<b>Week 10 (July 31 - August 6, 2026):</b> Final refactoring, documentation completion, and code quality assurance. Focus on polish and preparation for final delivery.""",
        """<b>Week 11 (August 7 - August 13, 2026):</b> Final demo preparation, system polish, deployment configuration, and final presentation preparation. All deliverables finalized and packaged."""
    ]

    for detail in remaining_details:
        elements.append(Paragraph(f"&bull; {detail}", styles['bullet']))

    elements.append(Spacer(1, 0.15*inch))
    elements.append(Paragraph("4.6 Timeline Summary", styles['subheading']))

    timeline_data = [['Week', 'Dates', 'Focus Area', 'Key Deliverables']]
    timeline_data.extend([
        ['Week 6', 'Jun 25 - Jul 8', 'Hybrid Retrieval', 'Dense+BM25, Reranking, Chunk Optimization'],
        ['Week 7', 'Jul 9 - Jul 15', 'Optimization', 'Profiling, Caching, Fine-tuning'],
        ['Week 8', 'Jul 16 - Jul 22', 'Evaluation', 'MS MARCO, SQuAD v2, Metrics'],
        ['Week 9', 'Jul 23 - Jul 30', 'Analysis', 'Failed Cases, Results Analysis'],
        ['Week 10', 'Jul 31 - Aug 6', 'Final Docs', 'IEEE Report, Presentation'],
        ['Week 11', 'Aug 7 - Aug 13', 'Final Demo', 'Presentation, Deployment']
    ])

    timeline_table = Table(timeline_data, colWidths=[0.65*inch, 1.1*inch, 1.4*inch, 2.5*inch])
    timeline_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), FONT_BOLD),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('TOPPADDING', (0, 0), (-1, 0), 6),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('TOPPADDING', (0, 1), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black)
    ]))
    elements.append(timeline_table)
    elements.append(Spacer(1, 0.1*inch))

    elements.append(Paragraph("4.7 Expected Outcomes", styles['subheading']))

    outcomes = """By the end of Week 11, the project will deliver a fully functional RAG-based question answering system with advanced features including re-ranking, hybrid search, multi-document QA, context window management, and query rewriting/expansion. The system will be optimized for performance, thoroughly tested, well-documented, and ready for deployment. All objectives outlined in the project proposal will be achieved."""
    elements.append(Paragraph(outcomes, styles['normal']))

def generate_report(output_filename="group10_interim_report.pdf"):
    """Generate the complete interim report"""

    # Create PDF document
    doc = SimpleDocTemplate(
        output_filename,
        pagesize=letter,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch
    )

    # Get custom styles
    styles = create_custom_styles()

    # Build document elements
    elements = []

    # Add sections
    add_cover_page(elements, styles)
    add_scope_changes(elements, styles)
    add_progress_summary(elements, styles)
    add_screenshots_section(elements, styles, screenshot_dir="/Users/chetansmac/Desktop/UWindsor/Semester 3 🚀/COMP 8967-Project 1/RAG Project/outputs/interim report")
    add_challenges_and_issues(elements, styles)
    add_next_steps(elements, styles)

    # Build PDF
    try:
        doc.build(elements)
        print(f"✅ Interim report generated successfully: {output_filename}")
        print(f"📄 Location: {os.path.abspath(output_filename)}")
        return True
    except Exception as e:
        print(f"❌ Error generating report: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("COMP 8967 - RAG Project Interim Report Generator")
    print("Matching Team10_COMP8967_Proposal_Final.pdf styling")
    print("=" * 60)

    # Generate report
    success = generate_report("group10_interim_report.pdf")

    if success:
        print("\n📋 Report sections included:")
        print("   1. Cover Page (with team members)")
        print("   2. Changes in Scope (if any)")
        print("   3. Progress Summary")
        print("   4. Challenges and Issues")
        print("   5. Next Steps (Weekly Sprints)")

    print("=" * 60)

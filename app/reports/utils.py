from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib import colors
from datetime import datetime
from app.interns.models import Intern
from app.ai.utils import analyze_intern_feedback, predict_conversion, generate_cohort_summary

def generate_intern_report(intern_id, filepath):
    """
    Generate a professional PDF report for a single intern.
    """
    intern = Intern.query.get_or_404(intern_id)
    
    doc = SimpleDocTemplate(filepath, pagesize=letter, 
                            leftMargin=0.75*inch, rightMargin=0.75*inch,
                            topMargin=0.75*inch, bottomMargin=0.75*inch)
    story = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=28,
        textColor=colors.HexColor('#1D9E75'),
        spaceAfter=6,
        alignment=0,
    )
    heading_style = ParagraphStyle(
        'Heading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#1D9E75'),
        spaceAfter=12,
        spaceBefore=12,
    )
    body_style = ParagraphStyle(
        'Body',
        parent=styles['BodyText'],
        fontSize=11,
        leading=16,
    )
    
    # Header
    story.append(Paragraph("InternAI IMS", title_style))
    story.append(Paragraph("Intern Evaluation Report", styles['Heading2']))
    story.append(Spacer(1, 0.3*inch))
    
    # Basic Info Table
    info_data = [
        ["Name", intern.name, "Intern ID", intern.intern_id],
        ["College", intern.college_name or "—", "Status", intern.status],
        ["Type", intern.intern_type or "—", "Paid/Unpaid", intern.paid_unpaid or "—"],
        ["Duration", intern.duration or "—", "FTE Recommendation", intern.fte_recommendation],
    ]
    
    info_table = Table(info_data, colWidths=[1.5*inch, 2*inch, 1.5*inch, 2*inch])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#E1F5EE')),
        ('BACKGROUND', (2, 0), (2, -1), colors.HexColor('#E1F5EE')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Performance Analysis
    story.append(Paragraph("Performance Analysis", heading_style))
    analysis = analyze_intern_feedback(intern)
    # Strip HTML tags for readability
    analysis_clean = analysis.replace('<b>', '').replace('</b>', '').replace('<br/>', '\n')
    story.append(Paragraph(analysis_clean, body_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Conversion Prediction
    story.append(Paragraph("Conversion Assessment", heading_style))
    prediction = predict_conversion(intern)
    pred_text = f"<b>Probability: {prediction['probability']}%</b><br/>Assessment: {prediction['reasoning']}"
    story.append(Paragraph(pred_text, body_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Evaluation Feedback
    story.append(Paragraph("Recorded Feedback", heading_style))
    feedback = intern.evaluation_feedback or "(No feedback recorded)"
    story.append(Paragraph(feedback, body_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Footer
    footer_data = [
        ["Generated", datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
        ["System", "InternAI IMS v1.0"],
    ]
    footer_table = Table(footer_data, colWidths=[1.5*inch, 3.5*inch])
    footer_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F5F5F5')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.grey),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
    ]))
    story.append(footer_table)
    
    doc.build(story)
    return filepath

def generate_cohort_report(filepath):
    """
    Generate a professional cohort PDF report.
    """
    interns = Intern.query.all()
    
    doc = SimpleDocTemplate(filepath, pagesize=letter,
                            leftMargin=0.75*inch, rightMargin=0.75*inch,
                            topMargin=0.75*inch, bottomMargin=0.75*inch)
    story = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=28,
        textColor=colors.HexColor('#1D9E75'),
        spaceAfter=6,
    )
    heading_style = ParagraphStyle(
        'Heading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#1D9E75'),
        spaceAfter=12,
        spaceBefore=12,
    )
    body_style = ParagraphStyle(
        'Body',
        parent=styles['BodyText'],
        fontSize=11,
        leading=16,
    )
    
    # Header
    story.append(Paragraph("InternAI IMS", title_style))
    story.append(Paragraph("Intern Cohort Report", styles['Heading2']))
    story.append(Spacer(1, 0.3*inch))
    
    # Summary
    story.append(Paragraph("Executive Summary", heading_style))
    summary = generate_cohort_summary(interns)
    summary_clean = summary.replace('<b>', '').replace('</b>', '').replace('<br/>', ' ')
    story.append(Paragraph(summary_clean, body_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Statistics
    story.append(Paragraph("Cohort Statistics", heading_style))
    total = len(interns)
    pursuing = len([i for i in interns if i.status == "Pursuing"])
    relieved = len([i for i in interns if i.status == "Relieved"])
    fte_yes = len([i for i in interns if i.fte_recommendation == "YES"])
    fte_no = len([i for i in interns if i.fte_recommendation == "NO"])
    
    stats_data = [
        ["Metric", "Count", "Percentage"],
        ["Total Interns", str(total), "100%"],
        ["Pursuing", str(pursuing), f"{round(pursuing/total*100) if total else 0}%"],
        ["Relieved", str(relieved), f"{round(relieved/total*100) if total else 0}%"],
        ["FTE: YES (Recommended)", str(fte_yes), f"{round(fte_yes/total*100) if total else 0}%"],
        ["FTE: NO (Not Recommended)", str(fte_no), f"{round(fte_no/total*100) if total else 0}%"],
    ]
    
    stats_table = Table(stats_data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch])
    stats_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1D9E75')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('PADDING', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F9F9F9')]),
    ]))
    story.append(stats_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Intern Breakdown
    story.append(Paragraph("All Interns", heading_style))
    intern_data = [["ID", "Name", "College", "Status", "FTE"]]
    for i in interns[:25]:  # Limit to 25 per page
        intern_data.append([
            i.intern_id,
            i.name[:20],  # Truncate long names
            (i.college_name or "—")[:15],
            i.status,
            i.fte_recommendation,
        ])
    
    intern_table = Table(intern_data, colWidths=[0.8*inch, 1.6*inch, 1.4*inch, 1*inch, 0.7*inch])
    intern_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E1F5EE')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F9F9F9')]),
    ]))
    story.append(intern_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Footer
    footer_data = [
        ["Generated", datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
        ["System", "InternAI IMS v1.0"],
        ["Total Cohort Size", f"{total} interns"],
    ]
    footer_table = Table(footer_data, colWidths=[1.5*inch, 3.5*inch])
    footer_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F5F5F5')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.grey),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
    ]))
    story.append(footer_table)
    
    doc.build(story)
    return filepath
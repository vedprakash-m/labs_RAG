#!/usr/bin/env python3
"""
Healthcare PDF Generator
========================
Generates realistic healthcare documents for RAG testing and training.

This script creates:
1. Blood Pressure Guide (comprehensive guide with classifications and lifestyle tips)
2. Diabetes Basics (overview with blood sugar levels and management strategies)
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, black, blue, red
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.pdfgen import canvas

def print_success(message):
    """Print success message in green"""
    print(f"✓ {message}")

def print_info(message):
    """Print info message in blue"""
    print(f"ℹ {message}")

def print_step(step, total, message):
    """Print step progress"""
    print(f"\n[{step}/{total}] {message}")
    print("=" * 50)

def create_blood_pressure_guide(output_path):
    """Create comprehensive blood pressure guide PDF"""
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=18
    )
    
    # Get styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=HexColor('#2E86AB'),
        alignment=TA_CENTER,
        spaceAfter=30
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=HexColor('#A23B72'),
        spaceAfter=15
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=11,
        alignment=TA_JUSTIFY,
        spaceAfter=12,
        leading=14
    )
    
    # Build story
    story = []
    
    # Title
    story.append(Paragraph("Blood Pressure Management Guide", title_style))
    story.append(Paragraph("A Comprehensive Healthcare Reference", styles['Heading3']))
    story.append(Spacer(1, 20))
    
    # Introduction
    story.append(Paragraph("Introduction", subtitle_style))
    intro_text = """
    Blood pressure is the force exerted by circulating blood against the walls of blood vessels. 
    It's one of the most important vital signs and a key indicator of cardiovascular health. 
    Understanding blood pressure classifications and management strategies is essential for 
    maintaining optimal health and preventing serious cardiovascular complications.
    
    This guide provides healthcare professionals and patients with evidence-based information 
    on blood pressure categories, risk factors, and management approaches. Regular monitoring 
    and appropriate interventions can significantly reduce the risk of heart disease, stroke, 
    and other cardiovascular events.
    """
    story.append(Paragraph(intro_text, body_style))
    story.append(Spacer(1, 15))
    
    # Blood Pressure Classifications
    story.append(Paragraph("Blood Pressure Classifications", subtitle_style))
    
    # Create classification table
    classification_data = [
        ['Category', 'Systolic (mmHg)', 'Diastolic (mmHg)', 'Clinical Significance'],
        ['Normal', 'Less than 120', 'AND less than 80', 'Optimal cardiovascular health'],
        ['Elevated', '120-129', 'AND less than 80', 'Increased risk, lifestyle modifications needed'],
        ['Stage 1 Hypertension', '130-139', 'OR 80-89', 'Medical evaluation and treatment indicated'],
        ['Stage 2 Hypertension', '140/90 or higher', 'OR 90 or higher', 'Immediate medical attention required'],
        ['Hypertensive Crisis', 'Higher than 180', 'AND/OR higher than 120', 'Emergency medical care needed']
    ]
    
    classification_table = Table(classification_data, colWidths=[1.5*inch, 1.2*inch, 1.2*inch, 2*inch])
    classification_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#2E86AB')),
        ('TEXTCOLOR', (0, 0), (-1, 0), HexColor('#FFFFFF')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), HexColor('#F8F9FA')),
        ('GRID', (0, 0), (-1, -1), 1, black),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [HexColor('#FFFFFF'), HexColor('#F8F9FA')])
    ]))
    
    story.append(classification_table)
    story.append(Spacer(1, 20))
    
    # Risk Factors
    story.append(Paragraph("Risk Factors for High Blood Pressure", subtitle_style))
    risk_factors_text = """
    <b>Modifiable Risk Factors:</b><br/>
    • <b>Dietary factors:</b> High sodium intake, excessive alcohol consumption, inadequate potassium intake<br/>
    • <b>Physical inactivity:</b> Sedentary lifestyle contributes to cardiovascular risk<br/>
    • <b>Obesity:</b> Body mass index above 30 kg/m² significantly increases risk<br/>
    • <b>Smoking:</b> Tobacco use damages blood vessels and increases blood pressure<br/>
    • <b>Stress:</b> Chronic psychological stress can contribute to sustained hypertension<br/>
    • <b>Sleep disorders:</b> Sleep apnea and insufficient sleep affect blood pressure regulation<br/><br/>
    
    <b>Non-modifiable Risk Factors:</b><br/>
    • <b>Age:</b> Risk increases with age, particularly after 45 in men and 55 in women<br/>
    • <b>Gender:</b> Men have higher risk until age 64; women's risk increases after menopause<br/>
    • <b>Ethnicity:</b> African Americans have higher prevalence and earlier onset<br/>
    • <b>Family history:</b> Genetic predisposition plays a significant role<br/>
    • <b>Chronic kidney disease:</b> Impaired kidney function affects blood pressure regulation
    """
    story.append(Paragraph(risk_factors_text, body_style))
    story.append(Spacer(1, 15))
    
    # Lifestyle Recommendations
    story.append(Paragraph("Lifestyle Modifications for Blood Pressure Management", subtitle_style))
    lifestyle_text = """
    <b>1. Dietary Approaches (DASH Diet):</b><br/>
    The Dietary Approaches to Stop Hypertension (DASH) diet emphasizes fruits, vegetables, 
    whole grains, lean proteins, and low-fat dairy products. Limit sodium intake to less than 
    2,300 mg daily (ideally 1,500 mg for optimal benefit). Increase potassium-rich foods such 
    as bananas, oranges, spinach, and beans. Reduce saturated fats and avoid trans fats.<br/><br/>
    
    <b>2. Physical Activity:</b><br/>
    Engage in at least 150 minutes of moderate-intensity aerobic exercise weekly, or 75 minutes 
    of vigorous exercise. Include muscle-strengthening activities at least twice weekly. Regular 
    physical activity can reduce systolic blood pressure by 4-9 mmHg. Activities can include 
    brisk walking, swimming, cycling, or dancing.<br/><br/>
    
    <b>3. Weight Management:</b><br/>
    Maintain a healthy body weight (BMI 18.5-24.9 kg/m²). Even modest weight loss of 5-10 pounds 
    can significantly impact blood pressure. Focus on sustainable lifestyle changes rather than 
    restrictive dieting. Consider working with healthcare professionals for personalized approaches.<br/><br/>
    
    <b>4. Stress Management:</b><br/>
    Practice stress-reduction techniques such as meditation, deep breathing exercises, yoga, or 
    tai chi. Maintain work-life balance and ensure adequate sleep (7-9 hours nightly). Consider 
    counseling or therapy for chronic stress management. Social support and relaxation techniques 
    are valuable components of comprehensive blood pressure management.<br/><br/>
    
    <b>5. Limit Alcohol and Avoid Tobacco:</b><br/>
    If consuming alcohol, limit to moderate amounts (1 drink daily for women, 2 for men). 
    Complete tobacco cessation is essential, as smoking damages blood vessels and reduces 
    oxygen delivery. Seek professional support for smoking cessation programs if needed.
    """
    story.append(Paragraph(lifestyle_text, body_style))
    story.append(Spacer(1, 15))
    
    # Monitoring and Follow-up
    story.append(Paragraph("Monitoring and Follow-up Care", subtitle_style))
    monitoring_text = """
    Regular blood pressure monitoring is essential for effective management. Home monitoring 
    can provide valuable information between clinic visits. Use validated, properly calibrated 
    devices and follow proper measurement techniques. Record readings at consistent times and 
    share data with healthcare providers.
    
    Follow-up schedules vary based on blood pressure category and individual risk factors. 
    Patients with normal blood pressure should have annual screenings, while those with 
    elevated readings may require more frequent monitoring. Medication adherence, when prescribed, 
    is crucial for optimal outcomes.
    
    Regular healthcare consultations allow for assessment of treatment effectiveness, medication 
    adjustments, and screening for complications. Laboratory tests may include lipid profiles, 
    kidney function tests, and diabetes screening as part of comprehensive cardiovascular 
    risk management.
    """
    story.append(Paragraph(monitoring_text, body_style))
    
    # Footer
    story.append(Spacer(1, 30))
    footer_text = f"<i>Document generated: {datetime.now().strftime('%B %d, %Y')}<br/>For educational purposes - Consult healthcare professionals for personalized medical advice</i>"
    story.append(Paragraph(footer_text, styles['Normal']))
    
    # Build PDF
    doc.build(story)
    return True

def create_diabetes_guide(output_path):
    """Create comprehensive diabetes basics PDF"""
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=18
    )
    
    # Get styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=HexColor('#D2691E'),
        alignment=TA_CENTER,
        spaceAfter=30
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=HexColor('#8B4513'),
        spaceAfter=15
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=11,
        alignment=TA_JUSTIFY,
        spaceAfter=12,
        leading=14
    )
    
    # Build story
    story = []
    
    # Title
    story.append(Paragraph("Diabetes Management Fundamentals", title_style))
    story.append(Paragraph("Essential Guide for Understanding and Managing Diabetes", styles['Heading3']))
    story.append(Spacer(1, 20))
    
    # Introduction
    story.append(Paragraph("Understanding Diabetes", subtitle_style))
    intro_text = """
    Diabetes mellitus is a group of metabolic disorders characterized by chronic hyperglycemia 
    resulting from defects in insulin secretion, insulin action, or both. It affects how the 
    body processes blood glucose (blood sugar), which is the primary source of energy for 
    cellular functions.
    
    This comprehensive guide provides essential information about diabetes types, blood glucose 
    classifications, management strategies, and lifestyle modifications. Early detection, proper 
    management, and patient education are crucial for preventing complications and maintaining 
    quality of life. Understanding these fundamentals empowers patients and caregivers to make 
    informed decisions about diabetes care.
    """
    story.append(Paragraph(intro_text, body_style))
    story.append(Spacer(1, 15))
    
    # Types of Diabetes
    story.append(Paragraph("Types of Diabetes", subtitle_style))
    types_text = """
    <b>Type 1 Diabetes:</b><br/>
    An autoimmune condition where the pancreas produces little or no insulin. Typically 
    diagnosed in children and young adults, though it can occur at any age. Requires 
    lifelong insulin therapy and careful blood glucose monitoring. Accounts for approximately 
    5-10% of all diabetes cases.<br/><br/>
    
    <b>Type 2 Diabetes:</b><br/>
    The most common form, accounting for 90-95% of cases. Characterized by insulin resistance 
    and relative insulin deficiency. Often associated with obesity, physical inactivity, and 
    genetic predisposition. Can often be managed with lifestyle modifications, oral medications, 
    and sometimes insulin.<br/><br/>
    
    <b>Gestational Diabetes:</b><br/>
    Develops during pregnancy and usually resolves after delivery. However, it increases the 
    risk of developing Type 2 diabetes later in life for both mother and child. Requires 
    careful monitoring and management during pregnancy to prevent complications.
    """
    story.append(Paragraph(types_text, body_style))
    story.append(Spacer(1, 15))
    
    # Blood Sugar Classifications
    story.append(Paragraph("Blood Glucose Classifications", subtitle_style))
    
    # Create glucose levels table
    glucose_data = [
        ['Test Type', 'Normal', 'Prediabetes', 'Diabetes', 'Units'],
        ['Fasting Plasma Glucose', 'Less than 100', '100-125', '126 or higher', 'mg/dL'],
        ['2-Hour OGTT', 'Less than 140', '140-199', '200 or higher', 'mg/dL'],
        ['Random Plasma Glucose', 'Varies', 'Not applicable', '200 or higher*', 'mg/dL'],
        ['Hemoglobin A1C', 'Less than 5.7%', '5.7-6.4%', '6.5% or higher', 'Percentage'],
    ]
    
    glucose_table = Table(glucose_data, colWidths=[1.8*inch, 1*inch, 1*inch, 1.2*inch, 0.8*inch])
    glucose_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#D2691E')),
        ('TEXTCOLOR', (0, 0), (-1, 0), HexColor('#FFFFFF')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), HexColor('#FFF8DC')),
        ('GRID', (0, 0), (-1, -1), 1, black),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [HexColor('#FFFFFF'), HexColor('#FFF8DC')])
    ]))
    
    story.append(glucose_table)
    story.append(Spacer(1, 10))
    story.append(Paragraph("<i>*With classic symptoms of hyperglycemia</i>", styles['Normal']))
    story.append(Paragraph("<i>OGTT = Oral Glucose Tolerance Test</i>", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Management Strategies
    story.append(Paragraph("Comprehensive Diabetes Management", subtitle_style))
    management_text = """
    <b>1. Blood Glucose Monitoring:</b><br/>
    Regular monitoring is essential for effective diabetes management. Self-monitoring of blood 
    glucose (SMBG) helps patients understand how food, exercise, medication, and stress affect 
    blood sugar levels. Continuous glucose monitors (CGMs) provide real-time data and trends. 
    Target ranges vary by individual but generally aim for 80-130 mg/dL before meals and 
    less than 180 mg/dL after meals.<br/><br/>
    
    <b>2. Medication Management:</b><br/>
    <b>Type 1 Diabetes:</b> Requires insulin therapy with multiple daily injections or insulin 
    pump therapy. Various insulin types include rapid-acting, short-acting, intermediate-acting, 
    and long-acting formulations.<br/>
    <b>Type 2 Diabetes:</b> Treatment often begins with metformin, progressing to combination 
    therapies including sulfonylureas, DPP-4 inhibitors, GLP-1 receptor agonists, SGLT-2 
    inhibitors, or insulin as needed. Medication selection depends on individual factors, 
    contraindications, and treatment goals.<br/><br/>
    
    <b>3. Nutritional Management:</b><br/>
    Medical nutrition therapy is fundamental to diabetes care. Focus on portion control, 
    carbohydrate counting, and meal timing. Emphasize non-starchy vegetables, lean proteins, 
    whole grains, and healthy fats. Limit refined sugars, processed foods, and saturated fats. 
    Consider working with registered dietitians for personalized meal planning. The plate 
    method (½ plate non-starchy vegetables, ¼ plate lean protein, ¼ plate starchy foods) 
    provides a practical approach to meal planning.
    """
    story.append(Paragraph(management_text, body_style))
    story.append(Spacer(1, 15))
    
    # Lifestyle Recommendations
    story.append(Paragraph("Essential Lifestyle Modifications", subtitle_style))
    lifestyle_text = """
    <b>Physical Activity:</b><br/>
    Regular exercise improves insulin sensitivity and glucose control. Aim for at least 150 
    minutes of moderate-intensity aerobic exercise weekly, plus resistance training twice 
    weekly. Monitor blood glucose before, during, and after exercise to prevent hypoglycemia. 
    Stay hydrated and carry rapid-acting carbohydrates during exercise.<br/><br/>
    
    <b>Weight Management:</b><br/>
    For individuals with Type 2 diabetes who are overweight, modest weight loss (5-10% of 
    body weight) can significantly improve glycemic control. Focus on sustainable lifestyle 
    changes rather than restrictive dieting. Consider bariatric surgery for severely obese 
    individuals when other interventions are insufficient.<br/><br/>
    
    <b>Stress Management and Sleep:</b><br/>
    Chronic stress and poor sleep quality can adversely affect blood glucose control. Practice 
    stress-reduction techniques such as meditation, relaxation exercises, or counseling. 
    Maintain consistent sleep schedules and aim for 7-9 hours of quality sleep nightly.<br/><br/>
    
    <b>Preventive Care:</b><br/>
    Annual comprehensive foot examinations, dilated eye exams, and kidney function assessments 
    are essential for early detection of complications. Maintain up-to-date vaccinations, 
    including annual influenza vaccines. Regular dental care is important as diabetes increases 
    the risk of periodontal disease.
    """
    story.append(Paragraph(lifestyle_text, body_style))
    story.append(Spacer(1, 15))
    
    # Complications Prevention
    story.append(Paragraph("Preventing Diabetes Complications", subtitle_style))
    complications_text = """
    Long-term diabetes complications can be prevented or delayed through optimal glucose control 
    and regular healthcare monitoring. Microvascular complications include diabetic retinopathy, 
    nephropathy, and neuropathy. Macrovascular complications involve cardiovascular disease, 
    stroke, and peripheral arterial disease.
    
    The importance of achieving and maintaining target HbA1c levels (generally less than 7% 
    for most adults) cannot be overstated. However, individualized targets may vary based on 
    age, life expectancy, comorbidities, and hypoglycemia risk. Regular monitoring of blood 
    pressure and lipid levels is equally important for comprehensive cardiovascular risk reduction.
    
    Patient education and self-management support are crucial components of diabetes care. 
    Diabetes self-management education and support (DSMES) programs provide evidence-based 
    interventions to help individuals develop the knowledge, skills, and confidence needed 
    for optimal diabetes management.
    """
    story.append(Paragraph(complications_text, body_style))
    
    # Footer
    story.append(Spacer(1, 30))
    footer_text = f"<i>Document generated: {datetime.now().strftime('%B %d, %Y')}<br/>This guide provides general information - Always consult healthcare professionals for personalized diabetes management plans</i>"
    story.append(Paragraph(footer_text, styles['Normal']))
    
    # Build PDF
    doc.build(story)
    return True

def verify_pdf_created(pdf_path):
    """Verify PDF was created successfully"""
    if pdf_path.exists() and pdf_path.stat().st_size > 0:
        size_kb = pdf_path.stat().st_size / 1024
        print_success(f"PDF created: {pdf_path.name} ({size_kb:.1f} KB)")
        return True
    else:
        print(f"✗ Failed to create: {pdf_path.name}")
        return False

def main():
    """Main function to generate healthcare PDFs"""
    print("Healthcare PDF Generator")
    print("=" * 50)
    print("Generating realistic healthcare documents for RAG testing...\n")
    
    # Ensure docs directory exists
    docs_dir = Path("docs")
    docs_dir.mkdir(exist_ok=True)
    print_info(f"Using output directory: {docs_dir.absolute()}")
    
    total_steps = 4
    success_count = 0
    
    # Generate Blood Pressure Guide
    print_step(1, total_steps, "Generating Blood Pressure Management Guide")
    bp_guide_path = docs_dir / "Blood_Pressure_Management_Guide.pdf"
    try:
        if create_blood_pressure_guide(bp_guide_path):
            if verify_pdf_created(bp_guide_path):
                success_count += 1
                print_info("✓ Comprehensive guide with classifications, risk factors, and lifestyle recommendations")
    except Exception as e:
        print(f"✗ Error creating blood pressure guide: {e}")
    
    # Generate Diabetes Guide
    print_step(2, total_steps, "Generating Diabetes Management Fundamentals")
    diabetes_guide_path = docs_dir / "Diabetes_Management_Fundamentals.pdf"
    try:
        if create_diabetes_guide(diabetes_guide_path):
            if verify_pdf_created(diabetes_guide_path):
                success_count += 1
                print_info("✓ Complete guide with glucose classifications, types, and management strategies")
    except Exception as e:
        print(f"✗ Error creating diabetes guide: {e}")
    
    # Verify all files
    print_step(3, total_steps, "Verifying Generated Documents")
    pdf_files = list(docs_dir.glob("*.pdf"))
    print_info(f"Total PDF files in docs/: {len(pdf_files)}")
    
    for pdf_file in pdf_files:
        size_kb = pdf_file.stat().st_size / 1024
        print(f"  • {pdf_file.name}: {size_kb:.1f} KB")
    
    # Summary
    print_step(4, total_steps, "Generation Summary")
    if success_count == 2:
        print_success("🎉 All healthcare PDFs generated successfully!")
        print_info("Documents are ready for RAG testing and training")
        print_info("Both guides contain comprehensive, medically accurate information")
        
        # Display file details
        print("\n📄 Generated Documents:")
        print("  1. Blood Pressure Management Guide:")
        print("     • Classifications (Normal, Elevated, Stage 1 & 2 Hypertension)")
        print("     • Risk factors and prevention strategies")
        print("     • DASH diet and lifestyle recommendations")
        
        print("  2. Diabetes Management Fundamentals:")
        print("     • Blood glucose classifications and target ranges")
        print("     • Type 1, Type 2, and gestational diabetes information")
        print("     • Comprehensive management and prevention strategies")
        
        print(f"\n📁 Files location: {docs_dir.absolute()}")
        print("Ready for upload to Azure Storage or local RAG testing!")
        
    else:
        print(f"⚠ Generated {success_count}/2 documents successfully")
        print("Check error messages above for troubleshooting")
    
    return success_count == 2

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠ Generation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        sys.exit(1)
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
from PIL import Image
import os

 # Paths
base = os.path.dirname(__file__)
abgabe = os.path.join(base, '../documentation/250922_Abgabe')
pdf_path = os.path.join(abgabe, 'Befriends_AISA25_presentation.pdf')

# Screenshot order for logical user journey
screens = [
    ('1_IInitial Screen.png', 'Welcome: The EventBot Home Screen'),
    ('2_Thinking.png', 'User asks for event suggestions'),
    ('3_Suggestions.png', 'EventBot suggests events based on user profile'),
    ('4_Continue_Conversation.png', 'User continues the conversation'),
    ('5_Recommend_Event.png', 'EventBot recommends a specific event'),
    ('6_Insta.png', 'Event details with Instagram link'),
]

# Copilot/dev images (full Copilot productivity story)
copilot_imgs = [
    ('../documentation/250921_1_Event_Cards_Before.png', 'Before Copilot: The original event card UI was functional but basic.'),
    ('../documentation/250921_2_Event_Improvement_Prompt.png', 'Using GitHub Copilot: I prompted Copilot to suggest improvements for the event card UI.'),
    ('../documentation/250921_3_Event_Improvement_Response.png', 'Copilot Response: Copilot provided actionable suggestions and code for a more modern, user-friendly card.'),
    ('../documentation/250921_4_Event_Card_After.png', 'After Copilot: The event card UI is now visually appealing and much more usable, thanks to Copilot-driven changes.'),
]

def add_title(c, title, y=None):
    # Reduce font size and add left/right margin to avoid cutoff
    c.setFont('Helvetica-Bold', 22)
    c.setFillColor(colors.HexColor('#2E4053'))
    y = y if y is not None else A4[1]-60
    # Use a smaller width for centering to avoid edge cutoff
    margin = 40
    c.drawCentredString(A4[0]/2, y, title[:80])
    c.setFillColor(colors.black)
    c.setFont('Helvetica', 14)

from reportlab.platypus import Paragraph, Frame
from reportlab.lib.styles import getSampleStyleSheet

def add_text(c, text, y, max_width=A4[0]-120, font_size=13, height=120):
    # Use a Paragraph for automatic line wrapping
    style = getSampleStyleSheet()['BodyText']
    style.fontName = 'Helvetica'
    style.fontSize = font_size
    style.leading = font_size + 2
    para = Paragraph(text, style)
    # Frame for text (x, y, width, height)
    frame = Frame(60, y, max_width, height, showBoundary=0)
    frame.addFromList([para], c)

def add_image(c, img_path, y, max_height=None):
    try:
        img = Image.open(img_path)
        width, height = img.size
        aspect = width / height
        # Margins
        top_margin = 80  # space for title
        bottom_margin = 60  # space for caption
        available_height = A4[1] - top_margin - bottom_margin
        available_width = A4[0] - 80  # 40pt margin each side
        # Fit image to available area
        scale = min(available_width / width, available_height / height)
        new_width = width * scale
        new_height = height * scale
        x = (A4[0] - new_width) / 2
        y = bottom_margin + ((available_height - new_height) / 2)  # center between title and caption
        c.drawImage(ImageReader(img), x, y, new_width, new_height, preserveAspectRatio=True, anchor='c')
    except Exception as e:
        c.setFont('Helvetica', 10)
        c.setFillColor(colors.red)
        c.drawString(60, y, f'Error loading image: {img_path}')
        c.setFillColor(colors.black)

def main():
    c = canvas.Canvas(pdf_path, pagesize=A4)
    # Cover/title page (title and subtitle together)
    add_title(c, 'BeFriends: Event Recommendation Platform', y=A4[1]-80)
    add_text(c, 'Discover local events with a friendly chatbot. This presentation follows a typical user journey and highlights the software\'s architecture and development process.', A4[1]-120, height=60)
    c.showPage()

    # User journey
    for fname, caption in screens:
        add_title(c, caption, y=A4[1]-60)
        add_image(c, os.path.join(abgabe, fname), y=120)
        c.setFont('Helvetica', 12)
        c.drawCentredString(A4[0]/2, 60, caption)
        c.showPage()

    # Copilot/dev productivity story (heading and text together)
    add_title(c, 'How GitHub Copilot Boosted Productivity', y=A4[1]-80)
    add_text(c, 'GitHub Copilot was a game-changer in this project. It accelerated UI and logic improvements, helped me iterate faster, and provided high-quality code suggestions. Here is the story of how Copilot transformed the event card UI:', A4[1]-120, height=60)
    c.showPage()
    for img, caption in copilot_imgs:
        add_title(c, 'Copilot Productivity in Action', y=A4[1]-60)
        add_image(c, os.path.join(base, img), y=120)
        c.setFont('Helvetica', 12)
        c.drawCentredString(A4[0]/2, 60, caption)
        c.showPage()

    # Architecture summary (heading and text together)
    add_title(c, 'Software Architecture Overview', y=A4[1]-80)
    add_text(c, 'The platform uses a modular Python backend (FastAPI), a modern Streamlit frontend, and a robust event ingestion pipeline.\n\nKey components: Streamlit UI, UI Components, Recommendation/Search Service, Catalog Repository, ResponseFormatter, Chatbot Client, Domain Models, Config.\n\nSee README and architecture docs for details.', A4[1]-120, height=80)
    c.showPage()

    c.save()

if __name__ == '__main__':
    main()

from fpdf import FPDF
import re

def clean_text(text):
    """Replace Unicode characters with ASCII equivalents"""
    replacements = {
        '\u2013': '-',  # en dash
        '\u2014': '--', # em dash
        '\u2018': "'",  # left single quote
        '\u2019': "'",  # right single quote
        '\u201c': '"',  # left double quote
        '\u201d': '"'   # right double quote
    }
    for unicode_char, replacement in replacements.items():
        text = text.replace(unicode_char, replacement)
    return text

def remove_emojis(text):
    """Remove emoji characters from text"""
    emoji_pattern = re.compile("[\U00010000-\U0010FFFF]", flags=re.UNICODE)
    return emoji_pattern.sub(r'', text)

class PDF(FPDF):
    def header(self):
        """PDF header with title"""
        self.set_font("Arial", "B", 16)
        self.set_text_color(0, 51, 102)  # Dark blue
        self.cell(0, 15, "Customer Service Knowledge Base", ln=True, align="C")
        self.line(10, 25, 200, 25)  # Add separator line
        self.ln(10)

    def footer(self):
        """PDF footer with page numbers"""
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.set_text_color(128)
        self.cell(0, 10, f"Page {self.page_no()}", 0, 0, "C")

    def chapter_title(self, title):
        """Format section titles"""
        self.set_font("Arial", "B", 14)
        self.set_text_color(0, 102, 204)  # Blue
        self.set_fill_color(240, 248, 255)  # Light blue background
        self.cell(0, 10, title, ln=True, fill=True)
        self.ln(5)

    def chapter_body(self, body):
        """Format section content with proper line handling"""
        self.set_font("Arial", "", 11)
        self.set_text_color(0)  # Black text
        
        # Handle both string and list inputs
        body_text = "\n".join(body) if isinstance(body, list) else body
        clean_body = clean_text(remove_emojis(body_text))
        
        # Process each line with appropriate formatting
        lines = clean_body.split('\n')
        for line in lines:
            if not line.strip():  # Empty line
                self.ln(5)
            elif line.startswith('  - '):  # Sub-bullet
                self.set_x(20)
                self.multi_cell(0, 7, line[4:])
            elif line.startswith('- '):  # Main bullet
                self.set_x(15)
                self.multi_cell(0, 7, line[2:])
            elif line.startswith('Q:') or line.startswith('A:'):  # FAQ items
                self.set_font("Arial", "B" if line.startswith('Q:') else "", 11)
                self.multi_cell(0, 7, line)
                self.set_font("Arial", "", 11)
            else:  # Regular text
                self.multi_cell(0, 7, line)
            self.ln(3)

# Content data structure
content = {
    "1. Refund & Return Policy": [
        "Eligibility for Refunds:",
        "- Customers can request a refund within 30 calendar days of purchase.",
        "- Refunds are eligible if:",
        "  - The product received is defective, damaged, or not as described.",
        "  - The product was not delivered due to a fault on our side.",
        "- Products marked \"Final Sale\" or \"Clearance\" are non-refundable.",
        "",
        "Digital Products:",
        "- Once accessed, streamed, or downloaded, digital items are considered consumed and are non-refundable.",
        "- If access fails or the digital product is corrupted or incomplete, a refund or replacement will be provided.",
        "- Example: If a purchased eBook cannot be downloaded due to a broken link, a new link or refund will be provided upon validation.",
        "",
        "Refund Processing:",
        "- Refunds are initiated within 7 business days after complaint validation.",
        "- The refunded amount will be credited to the original payment method.",
        "- A confirmation email/SMS will be shared after refund initiation.",
        "",
        "Required Documentation:",
        "- A valid proof of purchase (Order ID, invoice copy, or payment reference) is required.",
        "- Photos of defective products may be required for validation."
    ],
    "2. Complaint Handling Process": [
        "Submission Channels:",
        "- Complaints can be submitted via:",
        "  - Chatbot",
        "  - Web Form on the Help page",
        "  - Email: support@example.com",
        "",
        "After Submission:",
        "- Every complaint is registered with a unique Complaint ID.",
        "- An acknowledgment is sent instantly with tracking instructions.",
        "",
        "Resolution Timeline:",
        "- A support executive is assigned within 24 hours.",
        "- Complaints are resolved within 5-7 business days.",
        "- High-priority cases are resolved within 48 hours.",
        "- Users are notified via email/SMS when the complaint is updated or resolved.",
        "",
        "Tips for Faster Resolution:",
        "- Include supporting documentation.",
        "- Mention the preferred contact time if unavailable during business hours."
    ],
    "3. Contact Policy": [
        "Availability:",
        "- Support Hours: 9:00 AM - 9:00 PM, all days.",
        "- Modes: Phone (+91-9876543210), Email (support@example.com), Live Chat.",
        "",
        "Response Times:",
        "- Live Chat: Instant",
        "- Email: Within 24 hours",
        "- Phone Calls: Within 2 minutes during working hours"
    ],
    "4. Data Privacy & Security": [
        "Data Protection:",
        "- All customer data is encrypted and stored securely.",
        "- Compliance with GDPR, IT Act 2000, ISO/IEC 27001 standards.",
        "",
        "Complaint Access:",
        "- Only accessible using a valid Complaint ID.",
        "- Role-based access for staff.",
        "",
        "Third-Party Sharing:",
        "- No sharing without explicit consent.",
        "- Data retained only as required."
    ],
    "5. Frequently Asked Questions (FAQs)": [
        "General Complaints",
        "Q: How do I raise a complaint?",
        "A: Use the chatbot, email, or web form. Provide name, phone, email, order ID, and description.",
        "",
        "Q: Can I edit my complaint?",
        "A: No. Submit a new complaint referencing the previous Complaint ID.",
        "",
        "Q: How do I track my complaint?",
        "A: Share your Complaint ID with chatbot or email.",
        "",
        "Q: What if I don't get a response?",
        "A: Email support@example.com after 5 business days.",
        "",
        "Refunds",
        "Q: Can I get a refund for digital content?",
        "A: Only if it's defective or inaccessible.",
        "",
        "Q: How do I get a refund?",
        "A: Submit request with proof of purchase. Processed in 7 business days.",
        "",
        "Q: Can I exchange instead?",
        "A: Yes. Mention it in your complaint.",
        "",
        "Returns",
        "Q: Do I need to return the product?",
        "A: In some cases. Our team will guide you.",
        "",
        "Q: Who pays for return shipping?",
        "A: We do, if it's our fault.",
        "",
        "Account & Data",
        "Q: How is my data used?",
        "A: Only for orders/support. Never sold.",
        "",
        "Q: Can I delete my data?",
        "A: Yes. Request via registered email.",
        "",
        "Order & Delivery",
        "Q: My order hasn't arrived. What now?",
        "A: Wait till delivery estimate, then complain.",
        "",
        "Q: Can I cancel my order?",
        "A: Yes, within 2 hours unless shipped."
    ]
}

# Create and configure PDF
pdf = PDF()
pdf.set_auto_page_break(auto=True, margin=15)
pdf.add_page()

# Add all content to PDF
for title, body in content.items():
    pdf.chapter_title(title)
    pdf.chapter_body(body)

# Save PDF
pdf_path = "Customer_Service_Knowledge_Base.pdf"
pdf.output(pdf_path)

print(f"PDF successfully generated: {pdf_path}")


# from fpdf import FPDF
# import re

# # Emoji removal utility
# def remove_emojis(text):
#     emoji_pattern = re.compile("[\U00010000-\U0010FFFF]", flags=re.UNICODE)
#     return emoji_pattern.sub(r'', text)

# # Create PDF class with header and content methods
# class PDF(FPDF):
#     def header(self):
#         self.set_font("Arial", "B", 12)
#         self.cell(0, 10, "Customer Service Knowledge Base", ln=True, align="C")
#         self.ln(5)

#     def chapter_title(self, title):
#         self.set_font("Arial", "B", 12)
#         self.set_fill_color(230, 230, 230)
#         self.cell(0, 10, title, ln=True, fill=True)
#         self.ln(2)

#     def chapter_body(self, body):
#         self.set_font("Arial", "", 11)
#         clean_body = remove_emojis(body)
#         self.multi_cell(0, 8, clean_body)
#         self.ln()

# # PDF instance
# pdf = PDF()
# pdf.set_auto_page_break(auto=True, margin=15)
# pdf.add_page()

# # Content sections without emojis
# content = {
#     "1. Refund & Return Policy": [
#         "Eligibility for Refunds:",
#         "- Customers can request a refund within 30 calendar days of purchase.",
#         "- Refunds are eligible if:",
#         "  - The product received is defective, damaged, or not as described.",
#         "  - The product was not delivered due to a fault on our side.",
#         "- Products marked \"Final Sale\" or \"Clearance\" are non-refundable.",
#         "",
#         "Digital Products:",
#         "- Once accessed, streamed, or downloaded, digital items are considered consumed and are non-refundable.",
#         "- If access fails or the digital product is corrupted or incomplete, a refund or replacement will be provided.",
#         "- Example: If a purchased eBook cannot be downloaded due to a broken link, a new link or refund will be provided upon validation.",
#         "",
#         "Refund Processing:",
#         "- Refunds are initiated within 7 business days after complaint validation.",
#         "- The refunded amount will be credited to the original payment method.",
#         "- A confirmation email/SMS will be shared after refund initiation.",
#         "",
#         "Required Documentation:",
#         "- A valid proof of purchase (Order ID, invoice copy, or payment reference) is required.",
#         "- Photos of defective products may be required for validation."
#     ],
#     "2. Complaint Handling Process": [
#         "Submission Channels:",
#         "- Complaints can be submitted via:",
#         "  - Chatbot",
#         "  - Web Form on the Help page",
#         "  - Email: support@example.com",
#         "",
#         "After Submission:",
#         "- Every complaint is registered with a unique Complaint ID.",
#         "- An acknowledgment is sent instantly with tracking instructions.",
#         "",
#         "Resolution Timeline:",
#         "- A support executive is assigned within 24 hours.",
#         "- Complaints are resolved within 5-7 business days.",
#         "- High-priority cases are resolved within 48 hours.",
#         "- Users are notified via email/SMS when the complaint is updated or resolved.",
#         "",
#         "Tips for Faster Resolution:",
#         "- Include supporting documentation.",
#         "- Mention the preferred contact time if unavailable during business hours."
#     ],
#     "3. Contact Policy": [
#         "Availability:",
#         "- Support Hours: 9:00 AM - 9:00 PM, all days.",
#         "- Modes: Phone (+91-9876543210), Email (support@example.com), Live Chat.",
#         "",
#         "Response Times:",
#         "- Live Chat: Instant",
#         "- Email: Within 24 hours",
#         "- Phone Calls: Within 2 minutes during working hours"
#     ],
#     "4. Data Privacy & Security": [
#         "Data Protection:",
#         "- All customer data is encrypted and stored securely.",
#         "- Compliance with GDPR, IT Act 2000, ISO/IEC 27001 standards.",
#         "",
#         "Complaint Access:",
#         "- Only accessible using a valid Complaint ID.",
#         "- Role-based access for staff.",
#         "",
#         "Third-Party Sharing:",
#         "- No sharing without explicit consent.",
#         "- Data retained only as required."
#     ],
#     "5. Frequently Asked Questions (FAQs)": [
#         "General Complaints",
#         "Q: How do I raise a complaint?",
#         "A: Use the chatbot, email, or web form. Provide name, phone, email, order ID, and description.",
#         "",
#         "Q: Can I edit my complaint?",
#         "A: No. Submit a new complaint referencing the previous Complaint ID.",
#         "",
#         "Q: How do I track my complaint?",
#         "A: Share your Complaint ID with chatbot or email.",
#         "",
#         "Q: What if I don't get a response?",
#         "A: Email support@example.com after 5 business days.",
#         "",
#         "Refunds",
#         "Q: Can I get a refund for digital content?",
#         "A: Only if it's defective or inaccessible.",
#         "",
#         "Q: How do I get a refund?",
#         "A: Submit request with proof of purchase. Processed in 7 business days.",
#         "",
#         "Q: Can I exchange instead?",
#         "A: Yes. Mention it in your complaint.",
#         "",
#         "Returns",
#         "Q: Do I need to return the product?",
#         "A: In some cases. Our team will guide you.",
#         "",
#         "Q: Who pays for return shipping?",
#         "A: We do, if it's our fault.",
#         "",
#         "Account & Data",
#         "Q: How is my data used?",
#         "A: Only for orders/support. Never sold.",
#         "",
#         "Q: Can I delete my data?",
#         "A: Yes. Request via registered email.",
#         "",
#         "Order & Delivery",
#         "Q: My order hasn't arrived. What now?",
#         "A: Wait till delivery estimate, then complain.",
#         "",
#         "Q: Can I cancel my order?",
#         "A: Yes, within 2 hours unless shipped."
#     ]
# }

# # # content = {
# #     "1. Refund & Return Policy": """
# # Eligibility for Refunds:
# # - Customers can request a refund within 30 calendar days of purchase.
# # - Refunds are eligible if:
# #   - The product received is defective, damaged, or not as described.
# #   - The product was not delivered due to a fault on our side.
# # - Products marked "Final Sale" or "Clearance" are non-refundable.

# # Digital Products:
# # - Once accessed, streamed, or downloaded, digital items are considered consumed and are non-refundable.
# # - If access fails or the digital product is corrupted or incomplete, a refund or replacement will be provided.
# # - Example: If a purchased eBook cannot be downloaded due to a broken link, a new link or refund will be provided upon validation.

# # Refund Processing:
# # - Refunds are initiated within 7 business days after complaint validation.
# # - The refunded amount will be credited to the original payment method.
# # - A confirmation email/SMS will be shared after refund initiation.

# # Required Documentation:
# # - A valid proof of purchase (Order ID, invoice copy, or payment reference) is required.
# # - Photos of defective products may be required for validation.
# # """,
# #     "2. Complaint Handling Process": """
# # Submission Channels:
# # - Complaints can be submitted via:
# #   - Chatbot
# #   - Web Form on the Help page
# #   - Email: support@example.com

# # After Submission:
# # - Every complaint is registered with a unique Complaint ID.
# # - An acknowledgment is sent instantly with tracking instructions.

# # Resolution Timeline:
# # - A support executive is assigned within 24 hours.
# # - Complaints are resolved within 5–7 business days.
# # - High-priority cases are resolved within 48 hours.
# # - Users are notified via email/SMS when the complaint is updated or resolved.

# # Tips for Faster Resolution:
# # - Include supporting documentation.
# # - Mention the preferred contact time if unavailable during business hours.
# # """,
# #     "3. Contact Policy": """
# # Availability:
# # - Support Hours: 9:00 AM – 9:00 PM, all days.
# # - Modes: Phone (+91-9876543210), Email (support@example.com), Live Chat.

# # Response Times:
# # - Live Chat: Instant
# # - Email: Within 24 hours
# # - Phone Calls: Within 2 minutes during working hours
# # """,
# #     "4. Data Privacy & Security": """
# # Data Protection:
# # - All customer data is encrypted and stored securely.
# # - Compliance with GDPR, IT Act 2000, ISO/IEC 27001 standards.

# # Complaint Access:
# # - Only accessible using a valid Complaint ID.
# # - Role-based access for staff.

# # Third-Party Sharing:
# # - No sharing without explicit consent.
# # - Data retained only as required.
# # """,
# #     "5. Frequently Asked Questions (FAQs)": """
# # General Complaints
# # Q: How do I raise a complaint?
# # A: Use the chatbot, email, or web form. Provide name, phone, email, order ID, and description.

# # Q: Can I edit my complaint?
# # A: No. Submit a new complaint referencing the previous Complaint ID.

# # Q: How do I track my complaint?
# # A: Share your Complaint ID with chatbot or email.

# # Q: What if I don’t get a response?
# # A: Email support@example.com after 5 business days.

# # Refunds
# # Q: Can I get a refund for digital content?
# # A: Only if it’s defective or inaccessible.

# # Q: How do I get a refund?
# # A: Submit request with proof of purchase. Processed in 7 business days.

# # Q: Can I exchange instead?
# # A: Yes. Mention it in your complaint.

# # Returns
# # Q: Do I need to return the product?
# # A: In some cases. Our team will guide you.

# # Q: Who pays for return shipping?
# # A: We do, if it’s our fault.

# # Account & Data
# # Q: How is my data used?
# # A: Only for orders/support. Never sold.

# # Q: Can I delete my data?
# # A: Yes. Request via registered email.

# # Order & Delivery
# # Q: My order hasn’t arrived. What now?
# # A: Wait till delivery estimate, then complain.

# # Q: Can I cancel my order?
# # A: Yes, within 2 hours unless shipped.
# # """
# # }

# # Add content to PDF
# for title, body in content.items():
#     pdf.chapter_title(title)
#     pdf.chapter_body(body)

# # Save PDF
# pdf_path = "Customer_Service_Knowledge_Base.pdf"
# pdf.output(pdf_path)

# pdf_path

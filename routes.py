# routes.py
from flask import Blueprint, render_template, request, session, jsonify, redirect, url_for, flash, current_app
from flask_babelplus import Babel, gettext as _
from dotenv import load_dotenv
from langdetect import detect
import os
import google.generativeai as genai
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
import json
import replicate
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
import random
from flask_mail import Mail, Message
import requests, uuid
import markdown2  # <-- Import the new library

# Initialize extensions (these will be imported from app.py)
db = SQLAlchemy()
jwt = JWTManager()
babel = Babel()
mail = Mail()

# Create a Blueprint
bp = Blueprint('routes', __name__)

# Constants
PARTNERS = []  # Define your partners list here

# ===== MARKETING QUIZ QUESTIONS =====
MARKETING_QUESTIONS = [
    {
        "id": 1,
        "question": _("Do you currently have an online platform for your business?"),
        "options": [
            _("No, I don't have any platform yet"),
            _("Only on social media"),
            _("Only a website"),
            _("Both website and social media")
        ],
        "key": "platform"
    },
    {
        "id": 2,
        "question": _("What is your primary goal at the moment?"),
        "options": [
            _("Create more content"),
            _("Grow brand awareness"),
            _("Generate more leads/sales")
        ],
        "key": "goal"
    },
    {
        "id": 3,
        "question": _("Who is your main target audience?"),
        "options": [
            _("Businesses (B2B)"),
            _("Individual customers (B2C)"),
            _("Both")
        ],
        "key": "audience"
    },
    {
        "id": 4,
        "question": _("How often do you post or update your content?"),
        "options": [
            _("Rarely or never"),
            _("Once or twice a month"),
            _("Every week"),
            _("Every day")
        ],
        "key": "frequency"
    },
    {
        "id": 5,
        "question": _("How would you describe your current content strategy?"),
        "options": [
            _("I don't have any strategy"),
            _("I post randomly when I can"),
            _("I try to post with a plan, but it's not working well"),
            _("I have a clear strategy and I follow it")
        ],
        "key": "strategy"
    },
    {
        "id": 6,
        "question": _("What type of content do you use most often?"),
        "options": [
            _("Images/Graphics"),
            _("Videos"),
            _("Texts/Articles"),
            _("A mix of everything")
        ],
        "key": "content_type"
    },
    {
        "id": 7,
        "question": _("What do you need help with the most?"),
        "options": [
            _("Content ideas and creation"),
            _("Reaching more people (marketing/distribution)"),
            _("Tracking and improving results (analytics)"),
            _("Building a full content strategy")
        ],
        "key": "help_needed"
    },
    {
        "id": 8,
        "question": _("What is your preferred method of marketing?"),
        "options": [
            _("Paid advertising"),
            _("Organic content and SEO"),
            _("Influencer marketing"),
            _("Word-of-mouth and referrals")
        ],
        "key": "marketing_method"
    },
    {
        "id": 9,
        "question": _("How do you measure success in your marketing efforts?"),
        "options": [
            _("Engagement metrics (likes, shares, comments)"),
            _("Traffic to website/social media"),
            _("Leads and sales conversion"),
            _("Brand awareness and reach")
        ],
        "key": "success_measurement"
    },
    {
        "id": 10,
        "question": _("Do you have a marketing budget?"),
        "options": [
            _("Yes, I have a set budget"),
            _("I spend on marketing, but it's not fixed"),
            _("No, I don't have a marketing budget")
        ],
        "key": "budget"
    },
    {
        "id": 11,
        "question": _("What channels do you use to market your business?"),
        "options": [
            _("Social media (Facebook, Instagram, etc.)"),
            _("Google Ads/Search Engine Marketing"),
            _("Email marketing"),
            _("All of the above")
        ],
        "key": "channels"
    },
    {
        "id": 12,
        "question": _("How do you engage with your audience?"),
        "options": [
            _("Responding to comments and messages"),
            _("Sending emails/newsletters"),
            _("Hosting webinars, workshops, or live sessions"),
            _("I don't engage much with my audience")
        ],
        "key": "engagement"
    },
    {
        "id": 13,
        "question": _("Do you have any content creation resources in-house?"),
        "options": [
            _("Yes, I have a team or person dedicated to creating content"),
            _("I create content myself"),
            _("I outsource content creation"),
            _("I don't create content at all")
        ],
        "key": "resources"
    },
    {
        "id": 14,
        "question": _("What are your main challenges in marketing?"),
        "options": [
            _("Lack of time to create content"),
            _("Limited resources (team, budget, etc.)"),
            _("Not sure how to reach my target audience"),
            _("I don't have a clear marketing strategy")
        ],
        "key": "challenges"
    }
]

# ===== ANALYSIS MESSAGES =====
ANALYSIS_MESSAGES = {
    (_("No, I don't have any platform yet"), _("Create more content")):
        _("Starting without a platform is challenging but not impossible. The key to success in this case lies in building an online presence from scratch, primarily through social media or content-sharing platforms."),
    
    (_("No, I don't have any platform yet"), _("Grow brand awareness")):
        _("No platform means you're starting from zero. You need to build your brand's visibility quickly and consistently."),
    
    (_("No, I don't have any platform yet"), _("Generate more leads/sales")):
        _("Without an established platform, generating leads can be a challenge. However, personal outreach and referrals could still bring opportunities."),
    
    (_("Only on social media"), _("Create more content")):
        _("You're already active on social media, but the key is to ensure that the content you're creating aligns with your goals and resonates with your audience."),
    
    (_("Only on social media"), _("Grow brand awareness")):
        _("Social media can be a powerful tool for brand awareness. However, success here depends on consistent, high-quality posts."),
    
    (_("Only on social media"), _("Generate more leads/sales")):
        _("You've established a presence on social media, now it's time to convert your followers into customers."),
    
    (_("Only a website"), _("Create more content")):
        _("A website is a great foundation, but it requires valuable content to attract traffic and engage visitors."),
    
    (_("Only a website"), _("Grow brand awareness")):
        _("You have a website, but you need strategies to drive traffic to it."),
    
    (_("Only a website"), _("Generate more leads/sales")):
        _("You have an established website, but you need to optimize it for conversions."),
    
    (_("Both website and social media"), _("Create more content")):
        _("You have multiple channels for marketing, but you need a consistent strategy to ensure content is integrated across platforms."),
    
    (_("Both website and social media"), _("Grow brand awareness")):
        _("You are already present on multiple platforms. The goal now is to amplify your brand message and engage your audience consistently."),
    
    (_("Both website and social media"), _("Generate more leads/sales")):
        _("You've got everything in place—website and social media. The challenge now is to convert traffic into leads and sales."),
    
    (_("Paid advertising"), _("Generate more leads/sales")):
        _("You're already investing in paid advertising. Now it's crucial to ensure that your ads convert well."),
    
    (_("I don't have any strategy"), _("Building a full content strategy")):
        _("Without a content strategy, you may be missing out on opportunities. A solid strategy will help you achieve your marketing goals."),
    
    (_("Lack of time to create content"), _("Create more content")):
        _("Time constraints are common, but working smarter can help you manage the workload."),
    
    (_("Not sure how to reach my target audience"), _("Grow brand awareness")):
        _("It's crucial to define your target audience before creating content that speaks directly to their needs and wants."),
    
    (_("Limited resources (team, budget, etc.)"), _("Generate more leads/sales")):
        _("Limited resources mean you need to focus on the most efficient and effective strategies to generate sales.")
}

# ===== RECOMMENDATION MESSAGES =====
RECOMMENDATION_MESSAGES = {
    (_("No, I don't have any platform yet"), _("Create more content")):
        _("Focus on developing easily consumable content like social media posts, blogs, or simple videos. Prioritize platforms like Instagram, Facebook, and LinkedIn to attract your target audience without incurring high costs."),
    
    (_("No, I don't have any platform yet"), _("Grow brand awareness")):
        _("Start building a brand identity. Utilize social media for organic growth. Invest time in creating visually appealing posts, engaging content, and collaborate with influencers to increase brand recognition."),
    
    (_("No, I don't have any platform yet"), _("Generate more leads/sales")):
        _("Focus on networking and direct outreach. Build a simple landing page to capture leads and generate interest through compelling offers like free trials or lead magnets."),
    
    (_("Only on social media"), _("Create more content")):
        _("Create a content calendar and begin posting consistently. Repurpose content (e.g., turn blog posts into infographics or videos) and use user-generated content to improve engagement."),
    
    (_("Only on social media"), _("Grow brand awareness")):
        _("Focus on organic growth strategies, such as branded hashtags, influencer partnerships, and user-generated content. Run awareness campaigns and engage actively with your followers."),
    
    (_("Only on social media"), _("Generate more leads/sales")):
        _("Use clear calls to action, optimize your social media profiles for conversions, and create lead magnets like free downloads or promotions. Additionally, consider adding a simple website with lead capture forms."),
    
    (_("Only a website"), _("Create more content")):
        _("Start a blog and create resource pages. Invest in SEO practices to improve organic traffic. Use call-to-action buttons and email capture forms to convert visitors into leads."),
    
    (_("Only a website"), _("Grow brand awareness")):
        _("Leverage content marketing, SEO, and social media promotions to drive traffic to your website. Consider guest posting and collaborations to increase visibility. Ensure that your website is optimized for both desktop and mobile visitors."),
    
    (_("Only a website"), _("Generate more leads/sales")):
        _("Improve the user experience of your website by focusing on easy navigation, fast load times, and clear calls-to-action. Create lead capture forms, special offers, and consider using live chat or pop-ups for engagement."),
    
    (_("Both website and social media"), _("Create more content")):
        _("Develop a content ecosystem where social media and your website work together. Repurpose your content across both platforms and focus on creating pillar content for your website. Ensure everything aligns with your brand identity."),
    
    (_("Both website and social media"), _("Grow brand awareness")):
        _("Use cross-channel campaigns, create consistent branding across all platforms, and leverage both paid and organic strategies. Run targeted campaigns on social media while maintaining a solid content strategy on your website."),
    
    (_("Both website and social media"), _("Generate more leads/sales")):
        _("Build an integrated sales funnel that connects your social media profiles with your website. Implement lead capture strategies like free resources, email sign-ups, and retargeting ads."),
    
    (_("Paid advertising"), _("Generate more leads/sales")):
        _("Optimize your paid campaigns by focusing on audience targeting, creative testing, and conversion tracking. Ensure that your landing pages are optimized for high conversions."),
    
    (_("I don't have any strategy"), _("Building a full content strategy")):
        _("Start by defining your brand voice, target audience, and key messages. Establish clear objectives, create a content calendar, and track progress to measure success."),
    
    (_("Lack of time to create content"), _("Create more content")):
        _("Use tools to schedule posts and batch-create content. Repurpose content across different platforms and outsource tasks where necessary. Prioritize quality over quantity."),
    
    (_("Not sure how to reach my target audience"), _("Grow brand awareness")):
        _("Identify your ideal customer profile and research where they spend time online. Start testing different channels and messages, track what works, and optimize from there."),
    
    (_("Limited resources (team, budget, etc.)"), _("Generate more leads/sales")):
        _("Utilize organic strategies such as social media marketing, email campaigns, and partnerships. Focus on creating lead magnets and value-driven content to build trust and generate leads.")
}

DEMO_DATASETS = {}  # Define your demo datasets here
ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}  # Define allowed file extensions
ANALYSIS_MESSAGES = {}  # Define analysis messages
RECOMMENDATION_MESSAGES = {}  # Define recommendation messages

# Helper functions
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def parse_uploaded_file(file):
    try:
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file)
        elif file.filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file)
        else:
            return None
        
        return df.to_dict(orient='records')
    except Exception as e:
        print(f"Error parsing file: {str(e)}")
        return None

def reconstruct_dataframe(uploaded_data):
    try:
        return pd.DataFrame.from_records(uploaded_data)
    except Exception as e:
        print(f"Error reconstructing dataframe: {str(e)}")
        return None

def generate_content_from_form(template_id, form_data):
    # Implement your content generation logic here
    return "Generated content based on form data"

# Localization
@babel.localeselector
def get_locale():
    return session.get('language', 'en')

@bp.context_processor
def inject_template_vars():
    return {
        'current_locale': get_locale(),
        'is_rtl': get_locale() == 'ar',
        'partners': PARTNERS[:5]  # Added partners to context processor
    }

# ===== ROUTES =====

@bp.route('/translate-text', methods=['POST'])
def translate_text():
    data = request.get_json()
    original_text = data.get('text')
    target_language = data.get('target_language')

    subscription_key = current_app.config.get("TRANSLATOR_API_KEY")
    region = current_app.config.get("TRANSLATOR_API_REGION")

    if not subscription_key or not region:
        return jsonify({'error': 'Translator API key or region not configured.'}), 500

    endpoint = "https://api.cognitive.microsofttranslator.com"
    path = '/translate'
    constructed_url = endpoint + path

    params = {
        'api-version': '3.0',
        'to': [target_language]
    }

    headers = {
        'Ocp-Apim-Subscription-Key': subscription_key,
        'Ocp-Apim-Subscription-Region': region,
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
    }

    body = [{'text': original_text}]

    try:
        translator_request = requests.post(constructed_url, params=params, headers=headers, json=body)
        translator_request.raise_for_status()
        translator_response = translator_request.json()
        translated_text = translator_response[0]['translations'][0]['text']
        return jsonify({'translated_text': translated_text})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/set_language/<language>')
def set_language(language):
    session['language'] = language
    return jsonify(status="success", message=_("Language changed"), locale=language)

@bp.route('/')
def home():
    return render_template('index.html')

@bp.route('/about')
def about():
    return render_template('about.html')

@bp.route('/ai-consultation')
def ai_consultation():
    return render_template('ai_consultation.html')

@bp.route('/ai-marketing-analytics')
def ai_marketing_analytics():
    return render_template('ai_marketing_analytics.html')

@bp.route('/ai-marketing-analytics/free-plan', methods=['GET', 'POST'])
def free_marketing_optimization():
    metric_explanations = {
        "CTR": _("Click-Through Rate: The percentage of people who clicked on your ad or link out of those who saw it."),
        "CPC": _("Cost Per Click: The average amount you pay for each click on your ad."),
        "Conversion Rate": _("The percentage of visitors who complete a desired action (like making a purchase or signing up)."),
        "ROAS": _("Return on Ad Spend: The revenue generated for every dollar spent on advertising."),
        "Impressions": _("The number of times your ad was shown to potential customers."),
        "Engagement Rate": _("The percentage of people who interacted with your content (likes, shares, comments)."),
        "Bounce Rate": _("The percentage of visitors who leave your site after viewing only one page.")
    }

    uploaded_data = None
    file_error = None

    if request.method == 'POST':
        # Check if file was uploaded
        if 'metrics_file' in request.files:
            file = request.files['metrics_file']
            if file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                
                # Parse the uploaded file
                uploaded_data = parse_uploaded_file(file)
                if not uploaded_data:
                    file_error = _("Could not process the uploaded file. Please check the format.")
                
                # Store in session for later use
                session['uploaded_metrics'] = uploaded_data
            elif file.filename != '':
                file_error = _("Invalid file type. Please upload CSV or Excel files.")
        
        # Process form data if no file was uploaded or if manual entry is used
        if not uploaded_data:
            campaign_type = request.form.get('campaign_type')
            campaign_goal = request.form.get('campaign_goal')
            target_audience = request.form.get('target_audience')
            current_metrics = request.form.get('current_metrics')
            
            prompt = f"""
            Analyze this marketing campaign and provide optimization recommendations:
            Campaign Type: {campaign_type}
            Goal: {campaign_goal}
            Target Audience: {target_audience}
            Current Metrics: {current_metrics}
            
            Please provide specific recommendations to improve:
            1. Content strategy
            2. Targeting approach
            3. Budget allocation (if applicable)
            4. Key metrics to focus on
            
            Respond in {get_locale()} language.
            """
            
            try:
                model = genai.GenerativeModel("gemini-2.0-flash")
                response = model.generate_content(prompt)
                recommendations = response.text
                
                return render_template('free_marketing_optimization.html', 
                                    recommendations=recommendations,
                                    form_data=request.form,
                                    metric_explanations=metric_explanations,
                                    uploaded_data=uploaded_data,
                                    file_error=file_error)
            
            except Exception as e:
                return render_template('free_marketing_optimization.html',
                                    error=str(e),
                                    form_data=request.form,
                                    metric_explanations=metric_explanations,
                                    uploaded_data=uploaded_data,
                                    file_error=file_error)
    
    return render_template('free_marketing_optimization.html',
                         metric_explanations=metric_explanations,
                         uploaded_data=session.get('uploaded_metrics'))

@bp.route('/ai-marketing-analytics/trial-plan', methods=['GET', 'POST'])
def trial_marketing_analytics():
    metric_explanations = {
        "CTR": _("Click-Through Rate: The percentage of people who clicked on your ad or link out of those who saw it."),
        "CPC": _("Cost Per Click: The average amount you pay for each click on your ad."),
        "Conversion Rate": _("The percentage of visitors who complete a desired action (like making a purchase or signing up)."),
        "ROAS": _("Return on Ad Spend: The revenue generated for every dollar spent on advertising."),
        "Impressions": _("The number of times your ad was shown to potential customers."),
        "Engagement Rate": _("The percentage of people who interacted with your content (likes, shares, comments)."),
        "Bounce Rate": _("The percentage of visitors who leave your site after viewing only one page.")
    }

    uploaded_data = None
    file_error = None

    if request.method == 'POST':
        # Check if demo data exists in session
        demo_data = session.get('current_demo', {})
        
        # Use demo data if available, otherwise use form data
        campaign_type = request.form.get('campaign_type', demo_data.get('business_type', ''))
        campaign_goal = request.form.get('campaign_goal', demo_data.get('goal', ''))
        target_audience = request.form.get('target_audience', demo_data.get('audience', ''))
        is_demo = bool(demo_data)
        
        # Check if file was uploaded
        if 'metrics_file' in request.files:
            file = request.files['metrics_file']
            if file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                
                # Parse the uploaded file
                uploaded_data = parse_uploaded_file(file)
                if not uploaded_data:
                    file_error = _("Could not process the uploaded file. Please check the format.")
                
                # Store in session for later use
                session['uploaded_metrics'] = uploaded_data
            elif file.filename != '':
                file_error = _("Invalid file type. Please upload CSV or Excel files.")
        
        # Generate different prompts for demo vs real data
        if is_demo:
            prompt = f"""
            Analyze this DEMO marketing scenario and provide recommendations:
            Campaign Type: {campaign_type}
            Goal: {campaign_goal}
            Target Audience: {target_audience}
            
            Provide sample recommendations showing what the full version would offer.
            Include simulated metrics and a realistic strategy.
            Respond in {get_locale()} language.
            """
        else:
            prompt = f"""
            Analyze this marketing campaign and provide optimization recommendations for a trial user:
            Campaign Type: {campaign_type}
            Goal: {campaign_goal}
            Target Audience: {target_audience}
            Current Metrics: {request.form.get('current_metrics', '')}
            
            Please provide specific recommendations to improve:
            1. Content strategy
            2. Targeting approach
            3. Budget allocation (if applicable)
            4. Key metrics to focus on
            
            Note: This is a trial user, so focus on quick wins and basic optimizations.
            Respond in {get_locale()} language.
            """
        
        try:
            model = genai.GenerativeModel("gemini-2.0-flash")
            response = model.generate_content(prompt)
            recommendations = response.text
            
            return render_template('trial_marketing_analytics.html', 
                                recommendations=recommendations,
                                form_data=request.form,
                                metric_explanations=metric_explanations,
                                uploaded_data=uploaded_data,
                                file_error=file_error,
                                is_demo=is_demo)
        
        except Exception as e:
            return render_template('trial_marketing_analytics.html',
                                error=str(e),
                                form_data=request.form,
                                metric_explanations=metric_explanations,
                                uploaded_data=uploaded_data,
                                file_error=file_error,
                                is_demo=is_demo)
    
    return render_template('trial_marketing_analytics.html',
                         metric_explanations=metric_explanations,
                         uploaded_data=session.get('uploaded_metrics'))

@bp.route('/get-demo-data/<demo_type>')
def get_demo_data(demo_type):
    if demo_type not in DEMO_DATASETS:
        return jsonify({"error": "Invalid demo type"}), 404
    
    # Store in session for form processing
    session['current_demo'] = DEMO_DATASETS[demo_type]
    return jsonify(DEMO_DATASETS[demo_type])

@bp.route('/clear-demo-data')
def clear_demo_data():
    session.pop('current_demo', None)
    return jsonify({"status": "success"})

@bp.route('/content-brand-strategy')
def content_brand_strategy():
    return render_template('content_brand_strategy.html')

@bp.route('/content-brand-strategy/free-plan', methods=['GET', 'POST'])
def free_content_creation():
    # Define available templates with complete business-focused templates
    templates = {
        # Blog Post Templates
        'blog-industry-insights': {
            'name': _('Industry Insights Blog'),
            'description': _('Analyze industry trends and their business impact'),
            'content': '''<h1>[Title of Industry Insight Post]</h1>
                        <h2>Introduction</h2>
                        <p>In this post, we'll explore the latest trends in [industry] and how they might impact your business.</p>
                        <h2>Main Body</h2>
                        <h3>[Trend 1]</h3>
                        <p>Description of the first major trend in the industry.</p>
                        <h3>[Trend 2]</h3>
                        <p>Explanation of the second important development.</p>
                        <h3>[Impact on Your Business]</h3>
                        <p>Here's how these trends can affect your business and how you can prepare.</p>
                        <h2>Conclusion</h2>
                        <p>To stay ahead of the curve, businesses need to [recommendation]. Stay informed about these changes!</p>'''
        },
        'blog-how-to-guide': {
            'name': _('Business How-To Guide'),
            'description': _('Step-by-step guide for business solutions'),
            'content': '''<h1>[How to Implement [Solution] for Your Business]</h1>
                        <h2>Introduction</h2>
                        <p>If you're looking to improve [aspect of business], this guide will help you implement [solution].</p>
                        <h2>Step-by-Step Process</h2>
                        <h3>Step 1: [Step Description]</h3>
                        <p>Start by [action to take in this step].</p>
                        <h3>Step 2: [Step Description]</h3>
                        <p>Next, [action to take in this step].</p>
                        <h3>Step 3: [Step Description]</h3>
                        <p>Complete the process by [action to take in this step].</p>
                        <h2>Conclusion</h2>
                        <p>Following these steps will help you [business benefit]. Stay ahead of your competitors with this simple guide.</p>'''
        },
        'blog-case-study': {
            'name': _('Business Case Study'),
            'description': _('Showcase a business success story'),
            'content': '''<h1>[Business Name] Case Study: How They Achieved [Result]</h1>
                        <h2>Introduction</h2>
                        <p>In this case study, we'll look at how [business name] successfully implemented [solution/product] and achieved [result].</p>
                        <h2>Challenge</h2>
                        <p>[Business Name] faced a challenge in [area where improvement was needed].</p>
                        <h2>Solution</h2>
                        <p>With the help of [product/service], they were able to [describe the solution].</p>
                        <h2>Result</h2>
                        <p>By implementing this solution, [business name] achieved [quantifiable result] such as [example: increased sales, customer satisfaction].</p>
                        <h2>Conclusion</h2>
                        <p>This case study shows how [business owners] can benefit from [solution]. Try it out today and see the results for yourself.</p>'''
        },
        
        # Social Media Templates
        'social-product-feature': {
            'name': _('Product Feature Post'),
            'description': _('Highlight a key product feature for social media'),
            'content': '''<p>🚀 <strong>Feature Spotlight: [Feature Name]</strong></p>
                        <p>We're excited to announce [Feature Name] in our [Product/Service]. This new feature will help you [specific benefit].</p>
                        <p>🔑 Key Benefits:</p>
                        <ul>
                            <li>[Benefit 1]</li>
                            <li>[Benefit 2]</li>
                        </ul>
                        <p>#BusinessGrowth #Innovation</p>'''
        },
        'social-business-tip': {
            'name': _('Business Tip Post'),
            'description': _('Share quick business tips on social media'),
            'content': '''<p>💡 <strong>Business Tip of the Day:</strong></p>
                        <p>To improve your business's [area of focus], try [simple actionable tip]. Small changes can make a huge difference!</p>
                        <p>#BusinessTips #Success</p>'''
        },
        'social-promotional': {
            'name': _('Promotional Post'),
            'description': _('Announce special offers or discounts'),
            'content': '''<p>🎉 <strong>Limited Time Offer!</strong></p>
                        <p>For a limited time, get [discount/details] on our [product/service]. Don't miss out!</p>
                        <p>Use code: <strong>[CODE]</strong> at checkout</p>
                        <p>#SpecialOffer #Discount</p>'''
        },
        
        # Email Templates
        'email-welcome': {
            'name': _('Welcome Email'),
            'description': _('Welcome new subscribers or customers'),
            'content': '''<h2>Welcome to [Company Name]!</h2>
                        <p>Hi [Recipient's Name],</p>
                        <p>Thank you for joining [Company Name]. We're thrilled to have you on board!</p>
                        <p>Here's what you can expect from us:</p>
                        <ul>
                            <li>[Benefit 1]</li>
                            <li>[Benefit 2]</li>
                        </ul>
                        <p>Feel free to reach out if you have any questions. We're here to help!</p>
                        <p>Best,<br>[Your Company Name]</p>'''
        },
        'email-promotional': {
            'name': _('Promotional Email'),
            'description': _('Send special offers to customers'),
            'content': '''<h2>Special Offer Just for You!</h2>
                        <p>Hi [Recipient's Name],</p>
                        <p>We're offering [discount]% off on all [products/services] for a limited time! Don't miss out on this exclusive deal!</p>
                        <p>Use code <strong>[CODE]</strong> at checkout to get your discount.</p>
                        <p>Best regards,<br>[Your Company Name]</p>'''
        },
        'email-abandoned-cart': {
            'name': _('Abandoned Cart Email'),
            'description': _('Recover lost sales from abandoned carts'),
            'content': '''<h2>You Left Something Behind!</h2>
                        <p>Hi [Recipient's Name],</p>
                        <p>We noticed you left items in your cart:</p>
                        <ul>
                            <li>[Product 1]</li>
                            <li>[Product 2]</li>
                        </ul>
                        <p>Complete your purchase now and get [incentive, e.g., free shipping]!</p>
                        <p><a href="[Cart Link]">Return to Cart</a></p>
                        <p>Best,<br>[Your Company Name]</p>'''
        },
        
        # Press Release Templates
        'press-product-launch': {
            'name': _('Product Launch Press Release'),
            'description': _('Announce a new product launch'),
            'content': '''<h1>FOR IMMEDIATE RELEASE</h1>
                        <h2>[Product Name] Launches to Help Businesses [Solve Problem]</h2>
                        <p>[City, Date] – Today, [Company Name] is excited to announce the launch of [Product Name], which offers businesses [solution/benefit].</p>
                        <p>For more information, contact:<br>
                        [Company Name]<br>
                        [Contact Info]</p>'''
        },
        'press-partnership': {
            'name': _('Partnership Announcement'),
            'description': _('Announce a new business partnership'),
            'content': '''<h1>FOR IMMEDIATE RELEASE</h1>
                        <h2>[Company Name] Partners with [Partner Name] to Expand [Service/Product]</h2>
                        <p>[City, Date] – [Company Name] has entered a partnership with [Partner Name] to provide [new offering or service]. This collaboration will help businesses [benefit].</p>
                        <p>For further details, contact:<br>
                        [Company Name]<br>
                        [Contact Info]</p>'''
        },
        
        # Product/Service Description Templates
        'product-description': {
            'name': _('Product Description'),
            'description': _('Detailed description for eCommerce products'),
            'content': '''<h1>[Product Name]</h1>
                        <p>[Brief product introduction]</p>
                        <h2>Key Features:</h2>
                        <ul>
                            <li>[Feature 1]</li>
                            <li>[Feature 2]</li>
                            <li>[Feature 3]</li>
                        </ul>
                        <h2>Specifications:</h2>
                        <ul>
                            <li>[Spec 1]</li>
                            <li>[Spec 2]</li>
                        </ul>'''
        },
        'service-description': {
            'name': _('Service Description'),
            'description': _('Detailed description for service offerings'),
            'content': '''<h1>[Service Name]</h1>
                        <p>[Brief service introduction]</p>
                        <h2>What's Included:</h2>
                        <ul>
                            <li>[Component 1]</li>
                            <li>[Component 2]</li>
                        </ul>
                        <h2>Benefits:</h2>
                        <ul>
                            <li>[Benefit 1]</li>
                            <li>[Benefit 2]</li>
                        </ul>'''
        },
        
        # Event Templates
        'webinar-invitation': {
            'name': _('Webinar Invitation'),
            'description': _('Invite attendees to a webinar'),
            'content': '''<h1>You're Invited: [Webinar Title]</h1>
                        <p>Join us on [Date] at [Time] for an exclusive webinar about [topic].</p>
                        <h2>What You'll Learn:</h2>
                        <ul>
                            <li>[Key Point 1]</li>
                            <li>[Key Point 2]</li>
                        </ul>
                        <p><strong>Featured Speaker:</strong> [Speaker Name], [Title]</p>
                        <p><a href="[Registration Link]">Register Now</a></p>'''
        },
        'event-announcement': {
            'name': _('Event Announcement'),
            'description': _('Promote an upcoming event'),
            'content': '''<h1>Save the Date: [Event Name]</h1>
                        <p>We're excited to announce our upcoming event on [Date] at [Location/Virtual].</p>
                        <h2>Event Highlights:</h2>
                        <ul>
                            <li>[Highlight 1]</li>
                            <li>[Highlight 2]</li>
                        </ul>
                        <p><a href="[Ticket Link]">Get Your Tickets Now</a></p>'''
        }
    }

    if request.method == 'POST':
        template_id = request.form.get('template')
        edited_content = request.form.get('content')
        
        # Check if we're generating from form data
        if request.form.get('generate_from_form'):
            form_data = {
                k: v for k, v in request.form.items() 
                if k not in ['template', 'generate_from_form']
            }
            
            # Generate content based on form data
            edited_content = generate_content_from_form(template_id, form_data)
        
        session['last_content'] = edited_content
        session['last_template'] = template_id
        
        return render_template('free_content_creation.html', 
                            templates=templates,
                            selected_template=template_id,
                            content=edited_content,
                            preview=True)
    
    content = session.get('last_content', '')
    selected_template = request.args.get('template', session.get('last_template', 'blog-industry-insights'))
    
    return render_template('free_content_creation.html',
                         templates=templates,
                         selected_template=selected_template,
                         content=content or templates[selected_template]['content'])

@bp.route('/content-brand-strategy/trial-plan', methods=['GET', 'POST'])
def trial_content_strategy():
    if request.method == 'POST':
        business_type = request.form.get('business_type')
        target_audience = request.form.get('target_audience')
        content_type = request.form.get('content_type')
        content_topic = request.form.get('content_topic')
        
        try:
            prompt = f"""
            Create a comprehensive content strategy for an Algerian business based on:
            - Business Type: {business_type}
            - Target Audience: {target_audience}
            - Content Type: {content_type}
            - Content Topic: {content_topic}
            
            Provide:
            1. The actual content in appropriate format for the type
            2. Posting strategy optimized for Algerian audience
            3. Hashtag and keyword recommendations for Algeria
            4. Performance forecast for Algerian market
            5. Content calendar suggestions
            
            Format the response with clear sections in markdown.
            Include specific Algerian cultural references when relevant.
            Respond in {get_locale()} language.
            """
            
            model = genai.GenerativeModel("gemini-2.0-flash")
            response = model.generate_content(prompt)
            
            # Process the response into structured data
            recommendations = {
                'content': '',
                'posting_strategy': '',
                'hashtag_strategy': '',
                'performance_forecast': '',
                'content_calendar': ''
            }
            
            # Simple parsing (you might want to enhance this)
            sections = response.text.split('## ')
            for section in sections:
                if section.startswith('Content'):
                    recommendations['content'] = section.replace('Content\n', '')
                elif section.startswith('Posting Strategy'):
                    recommendations['posting_strategy'] = section.replace('Posting Strategy\n', '')
                elif section.startswith('Hashtag'):
                    recommendations['hashtag_strategy'] = section.replace('Hashtag and Keyword Recommendations\n', '')
                elif section.startswith('Performance'):
                    recommendations['performance_forecast'] = section.replace('Performance Forecast\n', '')
                elif section.startswith('Content Calendar'):
                    recommendations['content_calendar'] = section.replace('Content Calendar Suggestions\n', '')
            
            return render_template('trial_content_strategy.html', 
                                recommendations=recommendations,
                                form_data=request.form)
        
        except Exception as e:
            return render_template('trial_content_strategy.html', 
                                error=str(e),
                                form_data=request.form)
    
    return render_template('trial_content_strategy.html')

@bp.route('/careers')
def careers():
    return render_template('work_with_us.html')

@bp.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')
        
        try:
            # Create and send email
            msg = Message(
                subject=f"New Contact Form Submission: {subject}",
                recipients=['pelestiastartup@gmail.com'],
                body=f"""
                You have received a new message from the Pelestia contact form:
                
                Name: {name}
                Email: {email}
                Subject: {subject}
                Message: 
                {message}
                
                Please respond to this inquiry promptly.
                """
            )
            mail.send(msg)
            
            flash(_('Your message has been sent successfully! We will get back to you soon.'), 'success')
            return redirect(url_for('routes.contact'))
            
        except Exception as e:
            current_app.logger.error(f"Failed to send contact email: {str(e)}")
            flash(_('There was an error sending your message. Please try again later.'), 'error')
            return redirect(url_for('routes.contact'))
    
    return render_template('contact.html')

@bp.route('/customer-experience')
def customer_experience():
    return render_template('customer_experience.html')

@bp.route('/customer-experience/free-plan', methods=['GET', 'POST'])
def free_customer_experience():
    # Explanations for each field
    field_explanations = {
        'website_experience': _(
            "Describe how customers interact with your website. "
            "For example: 'Customers struggle to find the checkout button' or "
            "'Many users abandon their carts at the payment step'. "
            "Mention any specific problems you've noticed."
        ),
        'customer_feedback': _(
            "Paste recent customer comments, reviews, or survey responses. "
            "For example: 'Customers say the checkout process is too complicated' or "
            "'Many reviews mention slow delivery times'. "
            "Include both positive and negative feedback."
        ),
        'support_metrics': _(
            "If available, share metrics like: "
            "Average response time (e.g., '2 hours to reply to emails'), "
            "Resolution rate (e.g., '80% of issues solved on first contact'), "
            "Customer satisfaction scores (e.g., '4.2/5 rating for support'). "
            "If you don't have exact numbers, describe your support experience."
        )
    }

    if request.method == 'POST':
        website_experience = request.form.get('website_experience', '')
        customer_feedback = request.form.get('customer_feedback', '')
        support_metrics = request.form.get('support_metrics', '')
        
        try:
            prompt = f"""
            Analyze this customer experience data and provide optimization recommendations:
            
            Website Experience:
            {website_experience}
            
            Customer Feedback:
            {customer_feedback}
            
            Support Metrics:
            {support_metrics}
            
            Please provide specific recommendations to improve:
            1. Website user experience (navigation, content, conversion paths)
            2. Customer support interactions (response times, resolution quality)
            3. Overall customer satisfaction and loyalty
            
            Format the response as a list of clear, actionable recommendations with titles and descriptions.
            Use simple language suitable for business owners.
            Respond in {get_locale()} language.
            """
            
            model = genai.GenerativeModel("gemini-2.0-flash")
            response = model.generate_content(prompt)
            
            recommendations = []
            current_title = None
            current_desc = []
            
            for line in response.text.split('\n'):
                if line.strip().startswith(('1.', '2.', '3.', '4.', '5.')):
                    if current_title:
                        recommendations.append({
                            'title': current_title,
                            'description': ' '.join(current_desc)
                        })
                    current_title = line.strip()
                    current_desc = []
                elif line.strip() and current_title:
                    current_desc.append(line.strip())
            
            if current_title:
                recommendations.append({
                    'title': current_title,
                    'description': ' '.join(current_desc)
                })
            
            return render_template('free_customer_experience.html', 
                                recommendations=recommendations,
                                field_explanations=field_explanations,
                                form_data=request.form)
        
        except Exception as e:
            return render_template('free_customer_experience.html', 
                                error=str(e),
                                field_explanations=field_explanations,
                                form_data=request.form)
    
    return render_template('free_customer_experience.html',
                         field_explanations=field_explanations)

@bp.route('/customer-experience/ai-analysis', methods=['GET', 'POST'])
def ai_customer_experience():
    # Explanations for each field
    field_explanations = {
        'website_data': _(
            "Describe your website user experience. Include details about navigation, checkout process, "
            "mobile responsiveness, and any pain points customers have reported."
        ),
        'support_data': _(
            "Share details about your customer support. Include response times, common issues, "
            "support channels (email, chat, phone), and any customer feedback about support quality."
        ),
        'feedback_data': _(
            "Paste customer feedback, reviews, or survey responses. Include both positive and negative comments "
            "to help us identify strengths and areas for improvement."
        ),
        'purchase_data': _(
            "Describe the post-purchase experience. Include details about follow-up communications, "
            "return policies, loyalty programs, and any customer feedback about their post-purchase experience."
        )
    }

    if request.method == 'POST':
        website_data = request.form.get('website_data', '')
        support_data = request.form.get('support_data', '')
        feedback_data = request.form.get('feedback_data', '')
        purchase_data = request.form.get('purchase_data', '')
        
        try:
            prompt = f"""
            Analyze this comprehensive customer experience data and provide detailed recommendations:
            
            Website Experience:
            {website_data}
            
            Customer Support:
            {support_data}
            
            Customer Feedback:
            {feedback_data}
            
            Post-Purchase Experience:
            {purchase_data}
            
            Please provide specific, actionable recommendations in these areas:
            1. Website User Experience Improvements
            2. Customer Support Optimization
            3. Feedback Analysis and Response Strategy
            4. Post-Purchase Engagement Enhancements
            5. Overall Customer Journey Mapping
            
            For each recommendation, include:
            - Priority level (High/Medium/Low)
            - Estimated impact
            - Implementation difficulty
            - Suggested timeline
            
            Format the response with clear headings and bullet points.
            Use professional but accessible language suitable for business owners.
            Respond in {get_locale()} language.
            """
            
            model = genai.GenerativeModel("gemini-2.0-flash")
            response = model.generate_content(prompt)
            
            # Process the response into structured data
            recommendations = []
            current_section = None
            
            for line in response.text.split('\n'):
                if line.strip().startswith(('1.', '2.', '3.', '4.', '5.')):
                    if current_section:
                        recommendations.append(current_section)
                    current_section = {
                        'title': line.strip(),
                        'content': []
                    }
                elif current_section and line.strip():
                    current_section['content'].append(line.strip())
            
            if current_section:
                recommendations.append(current_section)
            
            return render_template('ai_customer_experience.html', 
                                recommendations=recommendations,
                                field_explanations=field_explanations,
                                form_data=request.form)
        
        except Exception as e:
            return render_template('ai_customer_experience.html', 
                                error=str(e),
                                field_explanations=field_explanations,
                                form_data=request.form)
    
    return render_template('ai_customer_experience.html',
                         field_explanations=field_explanations)

@bp.route('/customer-sentiment/trial-plan', methods=['GET', 'POST'])
def trial_sentiment_analysis():
    if request.method == 'POST':
        feedback_text = request.form.get('feedback_text', '')
        
        try:
            prompt = f"""
            Analyze this customer feedback from an Algerian business context and provide:
            1. Sentiment analysis (positive, negative, neutral)
            2. Key emotional tones detected
            3. Specific recommendations for responding to this feedback
            4. Suggestions for improving customer satisfaction
            
            Feedback:
            {feedback_text}
            
            Provide the response in markdown format with clear sections.
            Include cultural considerations for the Algerian market where relevant.
            Respond in {get_locale()} language.
            """
            
            model = genai.GenerativeModel("gemini-2.0-flash")
            response = model.generate_content(prompt)
            
            # Process the response into structured data
            analysis = {
                'sentiment': '',
                'emotions': '',
                'recommendations': '',
                'improvements': ''
            }
            
            # Simple parsing (enhance this for production)
            sections = response.text.split('## ')
            for section in sections:
                if section.startswith('Sentiment'):
                    analysis['sentiment'] = section.replace('Sentiment Analysis\n', '')
                elif section.startswith('Emotional'):
                    analysis['emotions'] = section.replace('Emotional Tones\n', '')
                elif section.startswith('Recommendations'):
                    analysis['recommendations'] = section.replace('Recommendations\n', '')
                elif section.startswith('Suggestions'):
                    analysis['improvements'] = section.replace('Suggestions for Improvement\n', '')
            
            return render_template('trial_sentiment_analysis.html', 
                                analysis=analysis,
                                feedback_text=feedback_text)
        
        except Exception as e:
            return render_template('trial_sentiment_analysis.html', 
                                error=str(e),
                                feedback_text=feedback_text)
    
    return render_template('trial_sentiment_analysis.html')

@bp.route('/ecommerce-solutions')
def ecommerce_solutions():
    return render_template('ecommerce_solutions.html')

@bp.route('/ecommerce-solutions/trial-plan', methods=['GET', 'POST'])
def trial_ecommerce_optimization():
    metric_explanations = {
        "conversion_rate": _("The percentage of visitors who make a purchase. Industry average is typically 2-3%."),
        "average_order_value": _("The average amount spent each time a customer places an order."),
        "cart_abandonment_rate": _("The percentage of shopping carts that are created but never completed."),
        "bounce_rate": _("The percentage of visitors who leave your site after viewing only one page."),
        "customer_acquisition_cost": _("The cost associated with acquiring a new customer through marketing."),
        "customer_lifetime_value": _("The total revenue a business can expect from a single customer account.")
    }

    uploaded_data = None
    file_error = None
    df = None

    if request.method == 'POST':
        # Handle file upload
        if 'metrics_file' in request.files:
            file = request.files['metrics_file']
            if file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                
                uploaded_data = parse_uploaded_file(file)
                if uploaded_data:
                    session['uploaded_metrics'] = uploaded_data
                    df = reconstruct_dataframe(uploaded_data)
                else:
                    file_error = _("Could not process the uploaded file.")
            elif file.filename != '':
                file_error = _("Invalid file type. Please upload CSV or Excel files.")
        
        # If no file uploaded, check session for existing data
        if not uploaded_data and 'uploaded_metrics' in session:
            uploaded_data = session['uploaded_metrics']
            df = reconstruct_dataframe(uploaded_data)

        # Process form data
        store_type = request.form.get('store_type')
        primary_goal = request.form.get('primary_goal')
        current_metrics = request.form.get('current_metrics')
        challenges = request.form.get('challenges')
        
        try:
            prompt = f"""
            Analyze this e-commerce store:
            - Store Type: {store_type}
            - Primary Goal: {primary_goal}
            - Current Metrics: {current_metrics}
            - Main Challenges: {challenges}
            """
            
            if df is not None:
                prompt += f"\n\nData Summary:\n{df.describe().to_markdown()}"
            
            model = genai.GenerativeModel("gemini-2.0-flash")
            response = model.generate_content(prompt)
            recommendations = response.text
            
            return render_template('trial_ecommerce_optimization.html',
                                recommendations=recommendations,
                                form_data=request.form,
                                metric_explanations=metric_explanations,
                                file_error=file_error)
        
        except Exception as e:
            return render_template('trial_ecommerce_optimization.html',
                                error=str(e),
                                form_data=request.form,
                                metric_explanations=metric_explanations,
                                file_error=file_error)

    return render_template('trial_ecommerce_optimization.html',
                         metric_explanations=metric_explanations)

@bp.route('/free-plan')
def free_plan():
    return render_template('free_plan.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        return redirect(url_for('routes.home'))
    return render_template('login.html')

@bp.route('/marketing-quiz', methods=['GET', 'POST'])
def marketing_quiz():
    if request.method == 'POST':
        answers = {}
        missing_questions = []

        for q in MARKETING_QUESTIONS:
            answer = request.form.get(f'q{q["id"]}')
            if not answer:
                missing_questions.append(q["id"])
            answers[q["key"]] = answer

        if missing_questions:
            return render_template('marketing_quiz.html', 
                                questions=MARKETING_QUESTIONS, 
                                error=_("Please answer all questions"))

        platform = answers.get("platform", "")
        goal = answers.get("goal", "")
        strategy = answers.get("strategy", "")
        challenges = answers.get("challenges", "")
        marketing_method = answers.get("marketing_method", "")
        
        analysis_text = ANALYSIS_MESSAGES.get((platform, goal), "")
        
        if strategy == _("I don't have any strategy") and goal == _("Building a full content strategy"):
            analysis_text = ANALYSIS_MESSAGES.get((strategy, goal), analysis_text)
        elif challenges == _("Limited resources (team, budget, etc.)") and goal == _("Generate more leads/sales"):
            analysis_text = ANALYSIS_MESSAGES.get((challenges, goal), analysis_text)
        elif marketing_method == _("Paid advertising") and goal == _("Generate more leads/sales"):
            analysis_text = ANALYSIS_MESSAGES.get((marketing_method, goal), analysis_text)
        
        recommendation_text = RECOMMENDATION_MESSAGES.get((platform, goal), "")
        
        if strategy == _("I don't have any strategy") and goal == _("Building a full content strategy"):
            recommendation_text = RECOMMENDATION_MESSAGES.get((strategy, goal), recommendation_text)
        elif challenges == _("Limited resources (team, budget, etc.)") and goal == _("Generate more leads/sales"):
            recommendation_text = RECOMMENDATION_MESSAGES.get((challenges, goal), recommendation_text)
        elif marketing_method == _("Paid advertising") and goal == _("Generate more leads/sales"):
            recommendation_text = RECOMMENDATION_MESSAGES.get((marketing_method, goal), recommendation_text)

        if not analysis_text:
            analysis_text = _("Based on your responses, we've identified key opportunities for improvement in your marketing strategy.")
        if not recommendation_text:
            recommendation_text = _("We recommend reviewing your marketing approach to better align with your business goals.")

        return render_template('quiz_results.html', 
                            answers=answers,
                            analysis_text=analysis_text,
                            recommendation_text=recommendation_text)

    return render_template('marketing_quiz.html', questions=MARKETING_QUESTIONS)

@bp.route('/faq')
def faq():
    faq_questions = [
        {
            "question": _("What is Pelestia?"),
            "answer": _("Pelestia is a digital platform that uses artificial intelligence to help businesses optimize customer experience, improve marketing strategies, and create tailored content. It provides tools to analyze customer behavior, track market trends, and enhance marketing performance.")
        },
        {
            "question": _("How can I get started with Pelestia?"),
            "answer": _("To get started with Pelestia, simply create an account on our platform. Once logged in, you can explore various tools for content creation, market analysis, and performance tracking. Choose a subscription plan that best suits your needs, and you're all set to begin.")
        },
        {
            "question": _("What services does Pelestia provide?"),
            "answer": _("Pelestia offers: Content Creation Tools to help you create high-quality, customized content; Marketing Strategy Optimization to assist in developing marketing strategies based on data insights; and Customer Experience Management tools to track and improve customer interactions.")
        },
        {
            "question": _("How do I use the content creation tools?"),
            "answer": _("Our content creation tools are easy to use, even if you're not a technical expert. You can start by choosing from various content formats such as articles, graphics, or audio. The platform also provides templates and guidelines tailored to your target audience and marketing goals.")
        },
        {
            "question": _("Can I track my marketing performance on Pelestia?"),
            "answer": _("Yes, Pelestia offers comprehensive performance tracking tools. You can monitor key metrics such as user engagement, conversions, and customer satisfaction. The platform provides real-time analytics and reports to help you measure your campaign's success.")
        },
        {
            "question": _("Is Pelestia easy to use?"),
            "answer": _("Absolutely! Pelestia is designed to be user-friendly, even for those with no technical background. The interface is intuitive, and our tools come with step-by-step guides to help you get the most out of the platform.")
        },
        {
            "question": _("What types of businesses can use Pelestia?"),
            "answer": _("Pelestia is suitable for all types of businesses, including: Small and Medium Enterprises (SMEs) looking to optimize their marketing strategies; Marketing Agencies that need advanced tools for content creation and performance analysis; and Public and Government Institutions wanting to improve engagement with the public.")
        },
        {
            "question": _("How does Pelestia improve customer experience?"),
            "answer": _("Pelestia helps you understand customer behavior by analyzing data from different channels. You can use this information to optimize customer interactions, personalize content, and develop strategies that enhance overall customer satisfaction.")
        },
        {
            "question": _("Can Pelestia help me with social media marketing?"),
            "answer": _("Yes, Pelestia provides social media analytics tools that allow you to monitor trends, track engagement, and optimize your social media strategies. The platform also helps you understand your audience's preferences across different social media channels.")
        },
        {
            "question": _("What are the pricing plans for Pelestia?"),
            "answer": _("Pelestia offers various pricing plans to suit different business sizes and needs. You can find more information and details on the options available on our Plans Page.")
        },
        {
            "question": _("Does Pelestia offer customer support?"),
            "answer": _("Pelestia does not have traditional customer support, but we do provide an AI-powered consultation service. This AI tool is available to assist you with free consultations and answers to your questions, ensuring you can get the help you need quickly and efficiently.")
        },
        {
            "question": _("How secure is my data on Pelestia?"),
            "answer": _("Pelestia takes your data security seriously. We use advanced encryption and secure servers to protect your information. Additionally, we comply with all relevant data protection regulations to ensure your data is safe.")
        },
        {
            "question": _("Can Pelestia integrate with other platforms?"),
            "answer": _("Yes, Pelestia integrates with various tools and platforms. You can connect it to your CRM systems, social media platforms, and email marketing tools to streamline your marketing processes.")
        },
        {
            "question": _("Can I customize the platform to my business needs?"),
            "answer": _("Pelestia allows customization to fit your business goals. Whether you need personalized reports, unique content formats, or specific marketing strategies, you can adjust the platform's features to meet your needs.")
        },
        {
            "question": _("How can I track customer behavior using Pelestia?"),
            "answer": _("Pelestia provides social listening and data analysis tools that help you track customer behavior in real-time. By monitoring interactions across various digital channels, you can gain insights into what your customers are saying and adjust your marketing efforts accordingly.")
        },
        {
            "question": _("What are the key features of Pelestia?"),
            "answer": _("Key features include: Customer Experience Management tools; Market Trend Analytics and reporting; Content Creation and Optimization tools; and Real-Time Performance Tracking and reporting.")
        },
        {
            "question": _("How do I upgrade my subscription?"),
            "answer": _("To upgrade your subscription, simply go to your Account Settings and select Subscription. Choose the plan that fits your needs and follow the instructions to complete the upgrade.")
        },
        {
            "question": _("Is there a mobile version of Pelestia?"),
            "answer": _("Yes, Pelestia is optimized for mobile devices. You can access your account, track performance, and manage content creation directly from your mobile phone or tablet.")
        },
        {
            "question": _("How do I get help if I need assistance?"),
            "answer": _("If you need help, you can visit our Help Center, where you'll find FAQs, tutorials, and guides. You can also use our AI consultation tool for immediate assistance with any questions or issues.")
        },
        {
            "question": _("What is social listening, and how does it benefit me?"),
            "answer": _("Social listening is the process of tracking online conversations to understand customer sentiments, preferences, and behaviors. Pelestia's social listening tools help you monitor market trends and adjust your marketing strategies to better meet customer expectations.")
        }
    ]
    return render_template('faq.html', questions=faq_questions)

@bp.route('/plans')
def plans():
    return render_template('plans.html')

@bp.route('/trial-plan')
def trial_plan():
    return render_template('trial_plan.html')

@bp.route('/monthly-paid-plan')
def monthly_paid_plan():
    return render_template('monthly_paid_plan.html')

@bp.route('/monthly-paid-plan/content-creation', strict_slashes=False)
def monthly_content_creation():
    return render_template('monthly_content_creation.html')

@bp.route('/monthly-paid-plan/customer-experience')
def monthly_customer_experience():
    return render_template('monthly_customer_experience.html')

@bp.route('/monthly-paid-plan/integrations')
def monthly_integrations():
    integration_tools = [
        {
            'icon': 'globe',
            'name': 'Live Website Analyzer',
            'description': 'Enter a site → get structure, UX, CTA, SEO feedback',
            'has_ai': True
        },
        {
            'icon': 'tag',
            'name': 'Tech Stack Detector',
            'description': 'Detect backend tools (CMS, JS libs, analytics tools)',
            'has_ai': True
        },
        {
            'icon': 'search',
            'name': 'Competitor Campaign Decoder',
            'description': 'Scan public campaign → extract offer, tone, hooks',
            'has_ai': True
        },
        {
            'icon': 'chart-line',
            'name': 'GA4/Meta Report Reader',
            'description': 'Paste data or upload report → auto-detect KPIs',
            'has_ai': True
        },
        {
            'icon': 'file-csv',
            'name': 'CSV/KPI Uploader',
            'description': 'Upload performance data → plot + analyze',
            'has_ai': True
        },
        {
            'icon': 'comment-dots',
            'name': 'Social Scraper + Sentiment',
            'description': 'Get mentions + mood on Twitter/LinkedIn',
            'has_ai': True
        },
        {
            'icon': 'brain',
            'name': 'Prompt Evaluator',
            'description': 'Paste text/code → get breakdown + rewrite',
            'has_ai': True
        },
        {
            'icon': 'envelope',
            'name': 'Email API Linker',
            'description': 'Paste email or webhook → receive auto-updates',
            'has_ai': False
        },
        {
            'icon': 'user-cog',
            'name': 'CRM Field Mapper',
            'description': 'Map CRM export fields to Pelestia templates',
            'has_ai': False
        },
        {
            'icon': 'receipt',
            'name': 'Traffic Source Auditor',
            'description': 'Breaks down your sources by ROI/quality',
            'has_ai': True
        },
        {
            'icon': 'sync',
            'name': 'Sync Schedule Manager',
            'description': 'Automate when your platform pulls from each source',
            'has_ai': False
        },
        {
            'icon': 'language',
            'name': 'Multilingual Review Interpreter',
            'description': 'Paste user feedback → auto sentiment + translation',
            'has_ai': True
        }
    ]
    return render_template('monthly_integrations.html', integration_tools=integration_tools)

@bp.route('/monthly-paid-plan/marketing-strategy')
def monthly_marketing_strategy():
    metric_explanations = {
        "CTR": _("Click-Through Rate: The percentage of people who clicked on your ad or link out of those who saw it."),
        "CPC": _("Cost Per Click: The average amount you pay for each click on your ad."),
        "Conversion Rate": _("The percentage of visitors who complete a desired action (like making a purchase or signing up)."),
        "ROAS": _("Return on Ad Spend: The revenue generated for every dollar spent on advertising."),
        "Impressions": _("The number of times your ad was shown to potential customers."),
        "Engagement Rate": _("The percentage of people who interacted with your content (likes, shares, comments)."),
        "Bounce Rate": _("The percentage of visitors who leave your site after viewing only one page.")
    }
    
    return render_template('monthly_marketing_strategy.html', 
                         metric_explanations=metric_explanations)

@bp.route('/monthly-paid-plan/reports-dashboards')
def monthly_reports_dashboards():
    return render_template('monthly_reports_dashboards.html')

@bp.route('/yearly-paid-plan')
def yearly_paid_plan():
    return render_template('yearly_paid_plan.html')

@bp.route('/request-demo')
def request_demo():
    return render_template('request_demo.html')

@bp.route('/submit-demo-request', methods=['POST'])
def submit_demo_request():
    # Get form data
    first_name = request.form.get('firstName')
    last_name = request.form.get('lastName')
    email = request.form.get('email')
    phone = request.form.get('phone')
    company = request.form.get('company')
    job_title = request.form.get('jobTitle')
    employees = request.form.get('employees')
    solutions = request.form.getlist('solutions')
    message = request.form.get('message')
    
    # Here you would typically:
    # 1. Validate the data
    # 2. Store it in a database
    # 3. Send email notifications
    # 4. Redirect to a thank you page
    
    # For now, we'll just print the data and redirect
    print(f"Demo request received from {first_name} {last_name} ({email})")
    print(f"Company: {company} ({employees} employees)")
    print(f"Solutions needed: {', '.join(solutions)}")
    if message:
        print(f"Additional message: {message}")
    
    return redirect(url_for('routes.demo_request_thank_you'))

@bp.route('/demo-request-thank-you')
def demo_request_thank_you():
    return render_template('demo_request_thank_you.html')

@bp.route('/create-account', methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        # Process form data
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        company = request.form.get('company')
        job_title = request.form.get('job_title')
        employees = request.form.get('employees')
        
        # Here you would typically:
        # 1. Validate the data
        # 2. Create the user account
        # 3. Redirect to appropriate page
        
        return redirect(url_for('routes.account_created'))
    
    return render_template('create_account.html')

@bp.route('/account-created')
def account_created():
    return render_template('account_created.html')

@bp.route('/ask-ai', methods=['POST'])
def ask_ai():
    try:
        question = request.get_json().get("question", "")

        # Detect current question language
        try:
            detected_lang = detect(question)
        except:
            detected_lang = 'en'

        # Set system instruction based on detected language
        if detected_lang == 'ar':
            system_instruction = (
                "أنت بيليستيا، مستشار ذكاء اصطناعي محترف متخصص في إدارة الأعمال. "
                "أجب دائمًا بطريقة واضحة ومهنية باللغة العربية. "
                "ركز على الاستراتيجية التجارية، التسويق، القيادة، السلوك التنظيمي، إدارة العمليات، وريادة الأعمال."
                "قم بتنسيق إجاباتك باستخدام الماركداون. استخدم العناوين والنقاط والنص الغامق لتنظيم إجابتك بوضوح."

            )
        elif detected_lang == 'fr':
            system_instruction = (
                "Vous êtes Pelestia, un consultant IA professionnel spécialisé en gestion d'entreprise. "
                "Répondez toujours de manière claire et professionnelle en français. "
                "Concentrez-vous sur la stratégie commerciale, le marketing, le leadership, le comportement organisationnel, la gestion des opérations et l'entrepreneuriat."
                "Formatez vos réponses en utilisant Markdown. Utilisez des titres, des puces et du texte en gras pour structurer clairement votre réponse."
            )
        else:
            system_instruction = (
                "You are Pelestia, a professional AI business consultant. "
                "Always answer clearly and professionally in English. "
                "Focus on business strategy, marketing, leadership, organizational behavior, operations management, and entrepreneurship."
                "Format your responses using Markdown. Use headings, bullet points, and bold text to structure your answer clearly."
            )

        # Initialize chat history
        if "chat_history" not in session:
            session["chat_history"] = []

        # Filter history based on detected language
        filtered_history = []
        for entry in session["chat_history"]:
            try:
                entry_lang = detect(entry["user"])
            except:
                entry_lang = 'en'

            if entry_lang == detected_lang:
                filtered_history.append(entry)

        # Build conversation
        conversation = ""
        for entry in filtered_history:
            conversation += f"You: {entry['user']}\nPelestia AI: {entry['ai']}\n"

        conversation += f"You: {question}\nPelestia AI:"

        # Send to Gemini
        model = genai.GenerativeModel("gemini-2.0-flash", system_instruction=system_instruction)
        response = model.generate_content(conversation)

        # Convert the Markdown response to HTML
        html_response = markdown2.markdown(response.text)

        # Update history
        session["chat_history"].append({
            "user": question,
            "ai": response.text # Store the raw markdown response in history
        })
        session["chat_history"] = session["chat_history"][-10:]  # Keep last 10 messages
        session.modified = True

        return jsonify(reply=html_response)
    except Exception as e:
        return jsonify(reply=f"<p>Error occurred: {str(e)}</p>"), 500

@bp.route('/clear-chat', methods=['POST'])
def clear_chat():
    session.pop('chat_history', None)
    return jsonify(status="success", message="Chat cleared")

@bp.route('/partnerships')
def partnerships():
    return render_template('partnerships.html')

@bp.route('/social-listening')
def social_listening():
    return render_template('social_listening.html')

@bp.route('/website-development')
def website_development():
    return render_template('website_development.html')

@bp.route('/generate-content', methods=['POST'])
def generate_content():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        content_type = data.get('content_type', 'Social Media Post')
        topic = data.get('topic', '')
        tone = data.get('tone', 'Professional')
        
        if not topic.strip():
            return jsonify({'error': 'Topic/description is required'}), 400
        
        prompt = f"""
        Create a {content_type} about {topic} with a {tone} tone for Algerian audience.
        Provide the response in this EXACT JSON format:
        {{
            "post_text": "Main content text (3-5 paragraphs)",
            "hashtags": "#example1 #example2 #example3",
            "cta": "Call to action sentence"
        }}
        
        Rules:
        - post_text should be plain text (no markdown)
        - hashtags should be space-separated (no commas)
        - cta should be 1-2 sentences
        - All text in English
        """
        
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(prompt)
        
        # Parse and validate response
        try:
            # Remove markdown code blocks
            clean_response = response.text.replace('```json', '').replace('```', '').strip()
            content = json.loads(clean_response)
            
            # Validate structure
            required_keys = ['post_text', 'hashtags', 'cta']
            if not all(key in content for key in required_keys):
                raise ValueError("Missing required fields in response")
                
            # Clean up hashtags
            content['hashtags'] = ' '.join(
                tag.strip() for tag in content['hashtags'].replace(',', ' ').split()
                if tag.startswith('#')
            )
            
        except (json.JSONDecodeError, ValueError) as e:
            current_app.logger.error(f"Failed to parse AI response: {str(e)}")
            raise ValueError("Failed to generate properly formatted content")
            
        return jsonify(content)
        
    except Exception as e:
        return jsonify({
            'error': 'Content generation failed',
            'message': str(e)
        }), 500

@bp.route('/generate-image', methods=['POST'])
def generate_image():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        description = data.get('description', '')
        style = data.get('style', 'realistic')
        
        # Validate required fields
        if not description.strip():
            return jsonify({'error': 'Image description is required'}), 400
        
        prompt = f"{description}, {style} style, high quality, professional"
        
        output = replicate.run(
            "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
            input={
                "prompt": prompt,
                "negative_prompt": "blurry, low quality, text, watermark",
                "width": 1024,
                "height": 1024,
                "num_outputs": 1,
                "guidance_scale": 7.5,
                "num_inference_steps": 50
            }
        )
        
        if not output or len(output) == 0:
            raise ValueError("No image generated")
            
        return jsonify({
            'images': [output[0]],  # Return the first image URL
            'prompt': prompt  # For debugging
        })
        
    except Exception as e:
        current_app.logger.error(f"Error generating image: {str(e)}")
        return jsonify({
            'error': 'Could not generate image',
            'message': str(e)
        }), 500

# ===== CUSTOMER EXPERIENCE TOOLS =====

@bp.route('/analyze-sentiment', methods=['POST'])
def analyze_sentiment():
    try:
        data = request.get_json()
        feedback_text = data.get('feedback_text', '')
        include_dialect = data.get('include_dialect', True)
        
        if not feedback_text.strip():
            return jsonify({'error': 'Please enter feedback to analyze'}), 400
        
        prompt = f"""
        Analyze this customer feedback from an Algerian business context:
        {feedback_text}
        
        Provide a detailed sentiment analysis with:
        1. Sentiment score (positive/neutral/negative percentages)
        2. Key emotions detected
        3. Cultural context insights (if Algerian dialect is present)
        4. Recommended response approach
        5. Suggested improvements
        
        Format the response as JSON with these keys:
        - sentiment (object with positive, neutral, negative percentages)
        - emotions (array of detected emotions)
        - cultural_insights (string)
        - recommendation (string)
        - improvements (string)
        
        Respond in English.
        """
        
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(prompt)
        
        # Parse the response
        try:
            # Remove markdown code blocks if present
            clean_response = response.text.replace('```json', '').replace('```', '').strip()
            analysis = json.loads(clean_response)
            
            # Validate structure
            required_keys = ['sentiment', 'emotions', 'recommendation']
            if not all(key in analysis for key in required_keys):
                raise ValueError("Missing required fields in analysis")
                
            return jsonify(analysis)
            
        except (json.JSONDecodeError, ValueError) as e:
            current_app.logger.error(f"Failed to parse sentiment analysis: {str(e)}")
            # Fallback to manual parsing if JSON fails
            return jsonify({
                'sentiment': {'positive': 70, 'neutral': 20, 'negative': 10},
                'emotions': ['Satisfaction', 'Trust'],
                'cultural_insights': 'Feedback shows typical Algerian customer expectations',
                'recommendation': 'Thank the customer and ask if they would like any additional assistance',
                'improvements': 'Consider shortening response times for better customer satisfaction'
            })
            
    except Exception as e:
        current_app.logger.error(f"Error in sentiment analysis: {str(e)}")
        return jsonify({'error': 'Analysis failed', 'message': str(e)}), 500

@bp.route('/generate-customer-response', methods=['POST'])
def generate_customer_response():
    try:
        data = request.get_json()
        feedback_text = data.get('feedback_text', '')
        include_context = data.get('include_context', True)
        
        if not feedback_text.strip():
            return jsonify({'error': 'Please enter customer feedback'}), 400
        
        prompt = f"""
        Generate a professional customer response for this feedback:
        {feedback_text}
        
        Requirements:
        - Use a polite and professional tone
        - Address all concerns raised
        - { "Include Algerian cultural context where appropriate" if include_context else "" }
        - Offer solutions or next steps
        - Keep it concise (3-5 sentences)
        
        Provide only the response text without any additional formatting.
        Respond in the same language as the feedback.
        """
        
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(prompt)
        
        return jsonify({'response': response.text})
        
    except Exception as e:
        return jsonify({'error': 'Response generation failed', 'message': str(e)}), 500

@bp.route('/calculate-cx-score', methods=['POST'])
def calculate_cx_score():
    try:
        data = request.get_json()
        answers = data.get('answers', {})
        
        # Validate required fields
        required_fields = ['satisfaction', 'ease_of_use', 'support_quality', 'likelihood_to_recommend']
        if not all(field in answers for field in required_fields):
            return jsonify({'error': 'Missing required assessment fields'}), 400
        
        prompt = f"""
        Calculate a Customer Experience (CX) score based on these metrics:
        - Customer Satisfaction: {answers.get('satisfaction')}/10
        - Ease of Use: {answers.get('ease_of_use')}/10
        - Support Quality: {answers.get('support_quality')}/10
        - Likelihood to Recommend: {answers.get('likelihood_to_recommend')}/10
        
        Provide:
        1. Overall CX score (0-100)
        2. Strengths identified
        3. Key areas for improvement
        4. Priority recommendations
        
        Format the response as JSON with these keys:
        - score (number)
        - strengths (array)
        - improvements (array)
        - recommendations (array)
        """
        
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(prompt)
        
        # Parse the response
        try:
            clean_response = response.text.replace('```json', '').replace('```', '').strip()
            analysis = json.loads(clean_response)
            
            # Add calculated score if not provided
            if 'score' not in analysis:
                satisfaction = int(answers.get('satisfaction', 0))
                ease = int(answers.get('ease_of_use', 0))
                support = int(answers.get('support_quality', 0))
                recommend = int(answers.get('likelihood_to_recommend', 0))
                calculated_score = (satisfaction + ease + support + recommend) * 2.5
                analysis['score'] = min(100, calculated_score)
                
            return jsonify(analysis)
            
        except (json.JSONDecodeError, ValueError) as e:
            current_app.logger.error(f"Failed to parse CX score analysis: {str(e)}")
            # Fallback response
            return jsonify({
                'score': 75,
                'strengths': ['Good customer satisfaction', 'Responsive support'],
                'improvements': ['Streamline onboarding process', 'Improve self-service options'],
                'recommendations': ['Implement customer feedback system', 'Train support staff on advanced issues']
            })
            
    except Exception as e:
        return jsonify({'error': 'CX score calculation failed', 'message': str(e)}), 500

@bp.route('/analyze-customer-journey', methods=['POST'])
def analyze_customer_journey():
    try:
        data = request.get_json()
        journey_stages = data.get('stages', [])
        
        if not journey_stages:
            return jsonify({'error': 'Please provide at least one journey stage'}), 400
        
        prompt = f"""
        Analyze this customer journey with {len(journey_stages)} stages:
        {json.dumps(journey_stages, indent=2)}
        
        Provide:
        1. Potential friction points
        2. Opportunities for improvement
        3. Recommended optimizations
        4. Key metrics to track for each stage
        
        Format the response as JSON with these keys:
        - friction_points (array)
        - opportunities (array)
        - optimizations (array)
        - metrics (object with stage names as keys)
        """
        
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(prompt)
        
        # Parse the response
        try:
            clean_response = response.text.replace('```json', '').replace('```', '').strip()
            analysis = json.loads(clean_response)
            return jsonify(analysis)
            
        except (json.JSONDecodeError, ValueError) as e:
            current_app.logger.error(f"Failed to parse journey analysis: {str(e)}")
            # Fallback response
            return jsonify({
                'friction_points': ['Onboarding process too lengthy', 'Lack of clear call-to-action'],
                'opportunities': ['Add self-service options', 'Implement live chat support'],
                'optimizations': ['Simplify signup form', 'Add progress indicators'],
                'metrics': {
                    'awareness': ['Impressions', 'Click-through rate'],
                    'consideration': ['Time on page', 'Content engagement']
                }
            })
            
    except Exception as e:
        return jsonify({'error': 'Journey analysis failed', 'message': str(e)}), 500

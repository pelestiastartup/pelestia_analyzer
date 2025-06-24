# ai.py
import google.generativeai as genai
import replicate
from langdetect import detect
import json
from flask import jsonify
import random
import os
from dotenv import load_dotenv

load_dotenv()
# Ensure your GEMINI_API_KEY is set in your .env file
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

class AIServices:
    # ... (all your other AIServices methods like ask_ai, generate_content_from_form, etc., remain here) ...
    @staticmethod
    def generate_content_from_form(template_id, form_data):
        """Generate content based on template and form data"""
        if template_id == 'blog-industry-insights':
            trends = form_data.get('trends', '').split(',')
            return f"""<h1>{form_data.get('industry', 'Industry')} Insights</h1>
                    <h2>Introduction</h2>
                    <p>In this post, we'll explore the latest trends in {form_data.get('industry', 'this industry')}.</p>
                    <h2>Key Trends</h2>
                    <ul>{''.join(f'<li>{t.strip()}</li>' for t in trends if t.strip())}</ul>
                    <h2>Conclusion</h2>
                    <p>Businesses should consider these emerging trends.</p>"""
        
        elif template_id == 'social-product-feature':
            benefits = form_data.get('benefits', '').split('\n')
            emoji = '🚀 ' if form_data.get('emoji') == 'on' else ''
            return f"""<p>{emoji}<strong>Feature Spotlight: {form_data.get('product', 'Our Product')}</strong></p>
                    <p>We're excited to highlight {form_data.get('product', 'our product')} for {form_data.get('audience', 'our customers')}.</p>
                    <p>Key Benefits:</p>
                    <ul>{''.join(f'<li>{b.strip()}</li>' for b in benefits if b.strip())}</ul>
                    <p>#{form_data.get('product', '').replace(' ', '')} #{form_data.get('audience', '')}</p>"""
        
        elif template_id == 'blog-how-to-guide':
            steps = form_data.get('steps', '').split('\n')
            return f"""<h1>How to {form_data.get('task', 'Complete This Task')}</h1>
                    <h2>Introduction</h2>
                    <p>This guide will help you {form_data.get('task', 'complete this task')} efficiently.</p>
                    <h2>Step-by-Step Process</h2>
                    {''.join(f'<h3>Step {i+1}: {step.strip()}</h3><p>Detailed instructions here.</p>' 
                            for i, step in enumerate(steps) if step.strip())}
                    <h2>Conclusion</h2>
                    <p>Following these steps will help you achieve your goal.</p>"""
        
        elif template_id == 'email-welcome':
            benefits = form_data.get('benefits', '').split('\n')
            return f"""<h2>Welcome to {form_data.get('company', 'Our Company')}!</h2>
                    <p>Hi [Recipient's Name],</p>
                    <p>Thank you for joining {form_data.get('company', 'us')}. We're thrilled to have you on board!</p>
                    <p>Here's what you can expect from us:</p>
                    <ul>{''.join(f'<li>{b.strip()}</li>' for b in benefits if b.strip())}</ul>
                    <p>Feel free to reach out if you have any questions.</p>
                    <p>Best,<br>{form_data.get('company', 'Our Team')}</p>"""
        
        elif template_id == 'press-product-launch':
            features = form_data.get('features', '').split(',')
            return f"""<h1>FOR IMMEDIATE RELEASE</h1>
                    <h2>{form_data.get('company', 'Company')} Launches {form_data.get('product', 'New Product')}</h2>
                    <p>[City, Date] - Today, {form_data.get('company', 'Company')} announced the launch of {form_data.get('product', 'new product')}, 
                    which offers {form_data.get('benefit', 'significant benefits')}.</p>
                    <p>Key Features:</p>
                    <ul>{''.join(f'<li>{f.strip()}</li>' for f in features if f.strip())}</ul>
                    <p>For more information, contact:<br>
                    {form_data.get('company', 'Company')}<br>
                    {form_data.get('contact', 'Contact Info')}</p>"""
        
        return ""

    @staticmethod
    def ask_ai(question, chat_history=None):
        try:
            # Detect current question language to tailor the response
            try:
                detected_lang = detect(question)
            except:
                detected_lang = 'en'

            # Set system instruction based on detected language
            if detected_lang == 'ar':
                system_instruction = (
                    "أنت بيليستيا، مستشار أعمال خبير بالذكاء الاصطناعي. قدم إجابات واضحة ومهنية ومنظمة باستخدام Markdown (عناوين، قوائم، نص غامق) باللغة العربية. "
                    "ركز على استراتيجية العمل، التسويق، القيادة، السلوك التنظيمي، إدارة العمليات، وريادة الأعمال."
                )
            elif detected_lang == 'fr':
                system_instruction = (
                    "Vous êtes Pelestia, un consultant d'affaires IA expert. Fournissez des réponses claires, professionnelles et structurées en utilisant Markdown (titres, listes, gras) en français. "
                    "Concentrez-vous sur la stratégie d'entreprise, le marketing, le leadership, le comportement organisationnel, la gestion des opérations et l'entrepreneuriat."
                )
            else:
                system_instruction = (
                    "You are Pelestia, an expert AI business consultant. Provide clear, professional, and structured answers using Markdown (headings, lists, bold text) in English. "
                    "Focus on business strategy, marketing, leadership, organizational behavior, operations management, and entrepreneurship."
                )

            # Build conversation history
            conversation = []
            if chat_history:
                for entry in chat_history:
                    conversation.append({'role': 'user', 'parts': [entry['user']]})
                    conversation.append({'role': 'model', 'parts': [entry['ai']]})
            
            conversation.append({'role': 'user', 'parts': [question]})

            # Send to Gemini
            model = genai.GenerativeModel("gemini-1.5-flash", system_instruction=system_instruction)
            chat = model.start_chat(history=conversation[:-1])
            response = chat.send_message(question)

            return response.text
            
        except Exception as e:
            raise Exception(f"AI consultation failed: {str(e)}")

    @staticmethod
    def analyze_marketing_campaign(form_data, locale='en'):
        """Analyzes marketing data and returns structured recommendations."""
        try:
            prompt = f"""
            Analyze this marketing campaign:
            - Campaign Type: {form_data.get('campaign_type')}
            - Goal: {form_data.get('campaign_goal')}
            - Target Audience: {form_data.get('target_audience')}
            - Current Metrics: {form_data.get('current_metrics')}

            Provide specific optimization recommendations.
            Respond in {locale} language.

            Format the response as a JSON object with a single key "recommendations", which is an array of objects.
            Each object should have a "title" and a "description".
            Example:
            {{
                "recommendations": [
                    {{
                        "title": "Recommendation 1 Title",
                        "description": "Detailed description of the first recommendation."
                    }},
                    {{
                        "title": "Recommendation 2 Title",
                        "description": "Detailed description of the second recommendation."
                    }}
                ]
            }}
            """
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
            
            return json.loads(response.text)
        except (json.JSONDecodeError, Exception) as e:
            raise Exception(f"Marketing analysis failed: {str(e)}")

    @staticmethod
    def analyze_customer_experience(form_data, locale='en'):
        """Analyzes customer experience data and returns structured recommendations."""
        try:
            prompt = f"""
            Analyze this customer experience data:
            - Website Experience: {form_data.get('website_experience')}
            - Customer Feedback: {form_data.get('customer_feedback')}
            - Support Metrics: {form_data.get('support_metrics')}

            Provide specific recommendations to improve Website UX, Customer Support, and Overall Satisfaction.
            Respond in {locale} language.
            
            Format the response as a JSON object with a single key "recommendations", which is an array of objects.
            Each object should have a "title" and a "description".
            Example:
            {{
                "recommendations": [
                    {{
                        "title": "Improve Website Navigation",
                        "description": "The main menu is confusing. Simplify it by grouping items into logical categories..."
                    }},
                    {{
                        "title": "Optimize Checkout Process",
                        "description": "Reduce the number of steps in the checkout process to lower cart abandonment rates."
                    }}
                ]
            }}
            """
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
            return json.loads(response.text)

        except (json.JSONDecodeError, Exception) as e:
            # Provide a fallback in case of API or parsing failure
            return {
                "recommendations": [
                    {"title": "Analysis Error", "description": f"Could not generate recommendations due to an error: {str(e)} Please try again."}
                ]
            }
    @staticmethod
    def generate_content(data):
        try:
            if not data:
                raise ValueError('No data provided')
                
            content_type = data.get('content_type', 'Social Media Post')
            topic = data.get('topic', '')
            tone = data.get('tone', 'Professional')
            
            if not topic.strip():
                raise ValueError('Topic/description is required')
            
            prompt = f"""
            Create a {content_type} about {topic} with a {tone} tone for Algerian audience.
            Provide the response in this EXACT JSON format:
            {{
                "post_text": "Main content text (3-5 paragraphs, separated by \\n for new lines)",
                "hashtags": "#example1 #example2 #example3",
                "cta": "Call to action sentence"
            }}
            
            Rules:
            - post_text should be plain text (no markdown)
            - hashtags should be space-separated (no commas)
            - cta should be 1-2 sentences
            - All text in English
            """
            
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
            
            clean_response = response.text.replace('```json', '').replace('```', '').strip()
            content = json.loads(clean_response)
            
            required_keys = ['post_text', 'hashtags', 'cta']
            if not all(key in content for key in required_keys):
                raise ValueError("Missing required fields in response")
                
            content['hashtags'] = ' '.join(
                tag.strip() for tag in content['hashtags'].replace(',', ' ').split()
                if tag.startswith('#')
            )
            
            return content
                
        except (json.JSONDecodeError, ValueError) as e:
            raise ValueError(f"Failed to generate properly formatted content: {e}")
                
        except Exception as e:
            raise Exception(f"Content generation failed: {str(e)}")

    @staticmethod
    def generate_image(description, style='realistic'):
        try:
            if not description.strip():
                raise ValueError('Image description is required')
            
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
                
            return output[0]  # Return the first image URL
                
        except Exception as e:
            raise Exception(f"Image generation failed: {str(e)}")

    @staticmethod
    def analyze_sentiment(feedback_text, include_dialect=True):
        """
        Analyzes customer feedback using a detailed prompt for a structured JSON response.
        """
        try:
            if not feedback_text.strip():
                raise ValueError('Please enter feedback to analyze')
            
            prompt = f"""
            Analyze this customer feedback from an Algerian business context:
            "{feedback_text}"
            
            Provide a detailed sentiment analysis. Format the response as a valid JSON object with these exact keys:
            - "sentiment": an object with "positive", "neutral", and "negative" keys, with percentage values (e.g., "positive": 85).
            - "emotions": an array of detected emotion strings (e.g., ["Satisfaction", "Trust"]).
            - "cultural_insights": a string explaining cultural context, especially if Algerian dialect is present. Keep it concise.
            - "recommendation": a string with the recommended response approach.
            - "improvements": a string with suggested product/service improvements based on the feedback.
            
            Respond in English. Ensure the JSON is valid.
            """
            
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
            
            analysis = json.loads(response.text)
            
            # Basic validation for the presence of key fields
            required_keys = ['sentiment', 'emotions', 'recommendation', 'improvements', 'cultural_insights']
            if not all(key in analysis for key in required_keys):
                # If the AI fails to provide the full structure, create a graceful fallback
                raise ValueError("AI response was missing required fields.")
                    
            return analysis
                
        except (json.JSONDecodeError, ValueError) as e:
            # Fallback for when the AI gives a malformed response or is missing keys
            return {
                'sentiment': {'positive': 0, 'neutral': 50, 'negative': 50},
                'emotions': ['Error'],
                'cultural_insights': 'Could not perform a detailed cultural analysis.',
                'recommendation': f'Could not generate a recommendation due to an internal error. The original feedback was: "{feedback_text}"',
                'improvements': 'Analysis failed. Please check the server logs.'
            }
                
        except Exception as e:
            # Catch all other exceptions (e.g., API failures)
            raise Exception(f"Sentiment analysis failed: {str(e)}")

    @staticmethod
    def generate_customer_response(feedback_text, include_context=True):
        try:
            if not feedback_text.strip():
                raise ValueError('Please enter customer feedback')
            
            prompt = f"""
            Generate a professional customer response for this feedback:
            "{feedback_text}"
            
            Follow these requirements:
            - Use a polite and professional tone.
            - Address all concerns raised in the feedback.
            - {"Include Algerian cultural context where appropriate." if include_context else ""}
            - Offer clear solutions or next steps.
            - Keep the response concise (around 3-5 sentences).
            
            Provide only the response text, without any additional formatting or explanations.
            Respond in the same language as the feedback.
            """
            
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt)
            
            return response.text
            
        except Exception as e:
            raise Exception(f"Response generation failed: {str(e)}")

    @staticmethod
    def calculate_cx_score(answers):
        try:
            required_fields = ['satisfaction', 'ease_of_use', 'support_quality', 'likelihood_to_recommend']
            if not all(field in answers for field in required_fields):
                raise ValueError('Missing required assessment fields')
            
            prompt = f"""
            Calculate a Customer Experience (CX) score based on these metrics:
            - Customer Satisfaction: {answers.get('satisfaction')}/10
            - Ease of Use: {answers.get('ease_of_use')}/10
            - Support Quality: {answers.get('support_quality')}/10
            - Likelihood to Recommend: {answers.get('likelihood_to_recommend')}/10
            
            Provide a JSON response with these keys:
            - "score": a number for the overall CX score (0-100).
            - "strengths": an array of strings identifying strengths.
            - "improvements": an array of strings for key areas of improvement.
            - "recommendations": an array of strings for priority recommendations.
            """
            
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
            
            analysis = json.loads(response.text)
            
            # Add calculated score if not provided by the model
            if 'score' not in analysis or not isinstance(analysis['score'], (int, float)):
                satisfaction = int(answers.get('satisfaction', 0))
                ease = int(answers.get('ease_of_use', 0))
                support = int(answers.get('support_quality', 0))
                recommend = int(answers.get('likelihood_to_recommend', 0))
                analysis['score'] = min(100, (satisfaction + ease + support + recommend) * 2.5)
                    
            return analysis
                
        except (json.JSONDecodeError, ValueError) as e:
            # Fallback response
            return {
                'score': 75,
                'strengths': ['Good customer satisfaction', 'Responsive support'],
                'improvements': ['Streamline onboarding process', 'Improve self-service options'],
                'recommendations': ['Implement customer feedback system', 'Train support staff on advanced issues']
            }
                
        except Exception as e:
            raise Exception(f"CX score calculation failed: {str(e)}")

    @staticmethod
    def analyze_customer_journey(journey_stages):
        try:
            if not journey_stages:
                raise ValueError('Please provide at least one journey stage')
            
            prompt = f"""
            Analyze this customer journey:
            {json.dumps(journey_stages, indent=2)}
            
            Provide a JSON response with these keys:
            - "friction_points": an array of strings identifying potential friction points.
            - "opportunities": an array of strings identifying opportunities for improvement.
            - "optimizations": an array of strings with recommended optimizations.
            - "metrics": an object where each key is a stage name and the value is an array of key metrics to track.
            """
            
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
            
            analysis = json.loads(response.text)
            return analysis
                
        except (json.JSONDecodeError, ValueError) as e:
            # Fallback response
            return {
                'friction_points': ['Onboarding process too lengthy', 'Lack of clear call-to-action'],
                'opportunities': ['Add self-service options', 'Implement live chat support'],
                'optimizations': ['Simplify signup form', 'Add progress indicators'],
                'metrics': {
                    'awareness': ['Impressions', 'Click-through rate'],
                    'consideration': ['Time on page', 'Content engagement']
                }
            }
                
        except Exception as e:
            raise Exception(f"Journey analysis failed: {str(e)}")
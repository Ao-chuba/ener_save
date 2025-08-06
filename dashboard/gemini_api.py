# Updated gemini_api.py - Replace your existing file with this

import json
import os
import requests
from django.conf import settings

class GeminiAPI:
    """Utility class to handle interactions with the Google Gemini API"""
    
    API_URL = "https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent"
    
    @classmethod
    def get_api_key(cls):
        """Get the API key from settings or environment variables"""
        # Try to get from settings
        api_key = getattr(settings, 'GEMINI_API_KEY', None)
        
        # Fallback to environment variable
        if not api_key:
            api_key = os.environ.get('GEMINI_API_KEY')
            
        if not api_key:
            print("WARNING: Gemini API key not found!")
            return "dummy_key_for_testing"  # For testing purposes
            
        return api_key
    
    @classmethod
    def generate_response(cls, user_message, household_data=None):
        """Generate a response from Gemini API based on user message and household data"""
        
        print(f"Generating response for message: {user_message}")
        print(f"Household data received: {household_data}")
        
        # Inside generate_response method
        print("Checking available models...")
        available_models = cls.list_available_models()
        
        # For testing without API key, return a mock response
        api_key = cls.get_api_key()
        if api_key == "dummy_key_for_testing":
            return cls._generate_mock_response(user_message, household_data)
        
        # Prepare system prompt with context
        system_prompt = """You are EnergyAssist AI, an expert in energy conservation and efficiency.
Your task is to provide helpful, practical advice on saving energy in household settings.

Response Guidelines:
1. Always structure your response with clear numbered points (1., 2., 3.)
2. Each main point should have sub-points (•) for specific actions
3. Use **bold** for key terms and measurements
4. Keep responses concise but informative
5. Tailor advice to the user's household size and appliances
6. If appliance data is missing, mention that more specific advice could be given with that information

Example Response Format:
1. **Heating Efficiency**
   • Lower thermostat to **24-26°C** for optimal savings
   • Seal windows with weather stripping
   • Use thick curtains at night

2. **Lighting Solutions**
   • Replace all bulbs with **LED** alternatives
   • Utilize natural light during daytime
"""

        # Add household context if available
        household_context = ""
        if household_data and isinstance(household_data, dict):
            rooms = household_data.get('rooms', 0)
            members = household_data.get('members', 0)
            
            if rooms > 0 or members > 0:
                household_context = f"The user has a {rooms}-room household with {members} members.\n"
                
                # Add appliance information if available
                appliances = household_data.get('appliances', [])
                if appliances and isinstance(appliances, list):
                    household_context += "They have the following appliances:\n"
                    for appliance in appliances:
                        if isinstance(appliance, dict):
                            name = appliance.get('name', 'Unknown')
                            power = appliance.get('power', 0)
                            household_context += f"- {name} (power rating: {power} watts)\n"
        
        # Construct the final prompt
        final_prompt = system_prompt
        if household_context:
            final_prompt += "\nUser Context:\n" + household_context
        
        final_prompt += f"\nUser Question: {user_message}"
        
        print(f"Final prompt: {final_prompt}")
        
        # Prepare the request payload
        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": final_prompt}]
                }
            ],
            "generationConfig": {
                "temperature": 0.7,
                "topK": 40,
                "topP": 0.95,
                "maxOutputTokens": 500
            }
        }
        
        # Make the API request
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": api_key
        }
        
        try:
            print("Making API request to Gemini...")
            response = requests.post(
                cls.API_URL,
                headers=headers,
                data=json.dumps(payload),
                timeout=30
            )
            
            print(f"API Response status: {response.status_code}")
            print(f"API Response headers: {response.headers}")
            
            # Parse the response
            if response.status_code == 200:
                response_data = response.json()
                print(f"API Response data: {response_data}")
                
                # Extract the generated text from the response
                candidates = response_data.get('candidates', [])
                if candidates:
                    content = candidates[0].get('content', {})
                    parts = content.get('parts', [])
                    if parts:
                        generated_text = parts[0].get('text', '')
                        if generated_text:
                            print(f"Generated text: {generated_text}")
                            return generated_text
                
                print("No generated text found in response")
                return "I'm sorry, I couldn't generate a response. Please try again."
            else:
                error_text = response.text
                print(f"API Error: {response.status_code} - {error_text}")
                
                # Try to parse error details
                try:
                    error_data = response.json()
                    error_message = error_data.get('error', {}).get('message', 'Unknown error')
                    return f"API Error: {error_message}"
                except:
                    return f"I'm having trouble connecting to my knowledge base. Status: {response.status_code}"
                
        except requests.exceptions.Timeout:
            print("API request timed out")
            return "Request timed out. Please try again."
        except requests.exceptions.ConnectionError:
            print("Connection error to API")
            return "Connection error. Please check your internet connection and try again."
        except Exception as e:
            print(f"Error calling Gemini API: {str(e)}")
            import traceback
            traceback.print_exc()
            return f"Error processing request: {str(e)}"
    
    @classmethod  # Added missing @classmethod decorator
    def list_available_models(cls):
        """Check available models"""
        url = "https://generativelanguage.googleapis.com/v1/models"
        headers = {"x-goog-api-key": cls.get_api_key()}
    
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                models = [model['name'] for model in response.json().get('models', [])]
                print("AVAILABLE MODELS:", models)
                return models
            print(f"Error listing models: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Error listing models: {str(e)}")
        return []

    # @classmethod
    # def _generate_mock_response(cls, user_message, household_data=None):
    #     """Generate a mock response for testing purposes"""
    #     print("Generating mock response...")
        
    #     mock_responses = {
    #         "ac": "To save energy with your AC: Set it to 24-26°C, clean filters regularly, and use fans for better air circulation.",
    #         "refrigerator": "For your refrigerator: Keep it at 3-5°C, ensure door seals are tight, and let hot foods cool before storing.",
    #         "washing": "Washing machine tips: Run full loads, use cold water when possible, and air-dry clothes instead of using a dryer.",
    #         "general": "Here are some general energy-saving tips: Switch to LED bulbs, unplug devices when not in use, and use natural light when possible."
    #     }
        
    #     user_message_lower = user_message.lower()
        
    #     for key, response in mock_responses.items():
    #         if key in user_message_lower:
    #             return response
        
    #     # Default response with household context
    #     if household_data and isinstance(household_data, dict):
    #         rooms = household_data.get('rooms', 0)
    #         members = household_data.get('members', 0)
    #         appliances = household_data.get('appliances', [])
            
    #         context_response = f"Based on your {rooms}-room household with {members} members"
    #         if appliances:
    #             context_response += f" and {len(appliances)} appliances"
    #         context_response += ", here are some personalized energy-saving tips: Use LED lighting, maintain optimal AC temperature, and unplug devices when not in use."
            
    #         return context_response
        
    #     return "Thank you for your question! Here are some general energy-saving tips: Use energy-efficient appliances, maintain optimal temperatures, and develop energy-conscious habits."
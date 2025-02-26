from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import google.generativeai as genai
from app.requests.models import ClientBeneficiary
import re
from django.db.models import Q

# Debug: Print the API key
print(f"API Key: {settings.GOOGLE_API_KEY}")

genai.configure(api_key=settings.GOOGLE_API_KEY)

model = genai.GenerativeModel('gemini-1.5-pro-latest')
def chatPage(request):
    chat_history = request.session.get('chat_history', [])
    return render(request, "chatsupport.html", {'chat_history': chat_history})

@csrf_exempt
def gemini_chat(request):
    if request.method == "POST":
        user_message = request.POST.get("message", "")

        if not user_message:
            return JsonResponse({"error": "No message provided"}, status=400)

        try:
            user_message_lower = user_message.lower()
            print(user_message_lower)
            if "give me the details of" in user_message_lower:
                parts = user_message_lower.split("give me the details of", 1)  # Split lowercase message
                if len(parts) > 1 and parts[1].strip():  # Check for name after phrase
                    name_to_search = parts[1].strip()
                    print(name_to_search)

                    beneficiaries = find_related_beneficiaries(name_to_search)
                    print(beneficiaries)

                    if beneficiaries:
                        bot_reply = format_beneficiary_details(beneficiaries)
                    else:
                        bot_reply = f"Client with name '{name_to_search}' not found."
                else:
                    bot_reply = "Please use the format: give me the details of [name]"

            elif "client details" in user_message_lower or "bene details" in user_message_lower or "beneficiary details" in user_message_lower:
                name_to_search = extract_name_from_full_message_preserve_initials(user_message_lower)
                print(name_to_search)
                if name_to_search:
                    beneficiaries = find_related_beneficiaries(name_to_search)
                    print(beneficiaries)
                    if beneficiaries:
                        bot_reply = format_beneficiary_details(beneficiaries)
                    else:
                        bot_reply = f"Client with related name '{name_to_search}' not found."
                else:
                    bot_reply = "Please provide a client name after 'client details'."

            elif "unique id" in user_message_lower:
                unique_id = extract_unique_id(user_message)
                if unique_id:
                    try:
                        beneficiary = ClientBeneficiary.objects.get(unique_id_number=unique_id)
                        bot_reply = format_beneficiary_details([beneficiary])
                    except ClientBeneficiary.DoesNotExist:
                        bot_reply = "Client with that ID not found."
                else:
                    bot_reply = "Please provide a Unique ID."

            else:
                response = model.generate_content(user_message)
                bot_reply = response.text

            if 'chat_history' not in request.session:
                request.session['chat_history'] = []

            request.session['chat_history'].append({
                'user': user_message,
                'bot': bot_reply,
            })
            request.session.modified = True

        except Exception as e:
            bot_reply = f"Error: {str(e)}"

        return JsonResponse({"response": bot_reply})

    return JsonResponse({"error": "Invalid request"}, status=400)

def extract_name_from_full_message_preserve_initials(message):
    message = message.replace('client details', '')
    message = message.replace('bene details', '')
    message = message.replace('beneficiary details', '')
    message = message.strip()
    return message.title()

def extract_unique_id(message):
    match = re.search(r'\b\d{1,50}\b', message)
    if match:
        return match.group(0)
    return None

def format_beneficiary_details(beneficiaries):
    if not beneficiaries:
        return "No beneficiaries found."

    details = ""
    for beneficiary in beneficiaries:
        details += f"Full Name: {beneficiary.get_client_fullname}\n"
        details += f"Birthdate: {beneficiary.birthdate}\n"
        details += f"Age: {beneficiary.age}\n"
        details += f"Sex: {beneficiary.sex.name}\n"
        details += f"Contact Number: {beneficiary.contact_number}\n"
        details += f"Civil Status: {beneficiary.civil_status.name}\n"
        details += f"address: {beneficiary.region}, {beneficiary.province}, {beneficiary.city}, {beneficiary.barangay_value}\n"
        details += f"Date Registered: {beneficiary.date_of_registration}\n"
        details += f"Unique ID: {beneficiary.unique_id_number}\n\n"

    return details

def find_related_beneficiaries(name_to_search):
    search_parts = name_to_search.lower().split()
    query = Q()

    for part in search_parts:
        query &= Q(client_bene_fullname__icontains=part) # icontains for case-insensitive search

    related_beneficiaries = ClientBeneficiary.objects.filter(query)
    return related_beneficiaries
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from .models import ChatMessage
import json
import os
import google.generativeai as genai
from django.conf import settings  # Import settings
from app.requests.models import ClientBeneficiaryFamilyComposition, ClientBeneficiary, Transaction, uploadfile, TransactionStatus1, SocialWorker_Status, \
	FileType,Category,SubCategory,ServiceProvider,TypeOfAssistance,SubModeofAssistance,LibAssistanceType,PriorityLine, ErrorLogData, ClientBeneficiaryUpdateHistory
import re # Import the re module

genai.configure(api_key=settings.GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-pro')

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
            if "client details" in user_message_lower or "bene details" in user_message_lower or "beneficiary details" in user_message_lower:
                name_to_search = extract_name_from_full_message_preserve_initials(user_message_lower)

                print(name_to_search) #debugging
                if name_to_search:
                    beneficiaries = find_related_beneficiaries(name_to_search) #use new function
                    print(beneficiaries) #debugging
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

            # Store chat history in session
            if 'chat_history' not in request.session:
                request.session['chat_history'] = []

            request.session['chat_history'].append({
                'user': user_message,
                'bot': bot_reply,
            })
            request.session.modified = True #Important to save the session changes.

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
        details += f"Barangay: {beneficiary.barangay.brgy_name}\n"
        details += f"Date Registered: {beneficiary.date_of_registration}\n"
        details += f"Unique ID: {beneficiary.unique_id_number}\n\n"

    return details

def find_related_beneficiaries(name_to_search):
    search_parts = name_to_search.lower().split()
    all_beneficiaries = ClientBeneficiary.objects.all()
    related_beneficiaries = []

    for beneficiary in all_beneficiaries:
        full_name_lower = beneficiary.client_bene_fullname.lower()
        all_parts_found = True
        for part in search_parts:
            if part not in full_name_lower:
                all_parts_found = False
                break
        if all_parts_found:
            related_beneficiaries.append(beneficiary)

    return related_beneficiaries
# def chatPage(request, *args, **kwargs):
#     if not request.user.is_authenticated:
#         return redirect("login-user")

#     room_name = kwargs.get('room_name', 'default')  # Get room name or set default chat room
#     chat_messages = ChatMessage.objects.filter(room_name=room_name).order_by('timestamp')[:50]  # Fetch latest 50 messages

#     context = {
#         'room_name': room_name,
#         'chat_messages': chat_messages,  # Add chat messages to context
#     }
#     return render(request, "chatpage.html", context)
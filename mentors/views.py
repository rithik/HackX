from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib.auth import authenticate, login
from django.core.mail import send_mail
from django.contrib.auth import logout
from django.conf import settings
from django.contrib.auth.decorators import login_required

import uuid
from pytz import timezone
from datetime import datetime
from applications.models import Application, Confirmation
from users.models import User, EmailView, Ticket
from judging.models import Organization
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json
import dropbox 

dbx = dropbox.Dropbox(settings.DROPBOX_ACCESS_TOKEN)

@login_required
def make_mentor_manual(request):
    u = request.user
    if not u.is_authenticated:
        return redirect("/logout")
    if request.method == "GET":
        return render(request, "make-mentor.html", {
            "highlight": "", 
            "user": u,
            "msg": "Please enter the mentor password to make yourself a mentor!",
            "organizations": Organization.objects.all()
        })

    if request.method == "POST":
        mentor_password = request.POST.get('mentor_password', '')
        full_name = request.POST.get('name', '')
        org_id = request.POST.get('organization-id', 0)
        if mentor_password == settings.MENTOR_PASSWORD:
            u.is_mentor = True
            u.full_name = full_name
            o = Organization.objects.get(id=org_id)
            u.organization = o
            u.save()
            return render(request, "make-mentor.html", {
                "highlight": "", 
                "user": u,
                "msg": "You are now an mentor!",
                "organizations": Organization.objects.all()
            })
        else:
            return render(request, "make-mentor.html", {
                "highlight": "", 
                "user": u,
                "msg": "Incorrect Password! Try again!",
                "organizations": Organization.objects.all()
            })
            
@login_required
def tickets_main(request):
    u = request.user
    if not u.is_authenticated:
        return redirect("/logout")
    # another_one = True if len(u.tickets) < settings.MAX_NUMBER_TICKETS else False
    return render(request, "tickets.html", {
        "highlight": "ticket", 
        "user": u, 
        "tickets": u.tickets
    })#, can_create_more=another_one)

@login_required
def mentor_tickets_main(request):
    u = request.user
    if not u:
        return redirect("/logout")
    if not u.is_mentor:
        return redirect("/")
    # another_one = True if len(u.tickets) < settings.MAX_NUMBER_TICKETS else False
    all_tickets = Ticket.objects.all()
    ticket_data = []
    for ticket in all_tickets:
        if ticket.mentor == u or ticket.mentor == None:
            ticket_data.append({
                "question": ticket.question,
                "location": ticket.location,
                "full_name": ticket.user.full_name, 
                "contact": ticket.contact,
                "status": ticket.status,
                "id": ticket.id,
                "email": ticket.user.email,
                "claimedByMe": False if ticket.status == "Unclaimed" else True
            })
    return render(request,"mentor-tickets.html", {
        "highlight": "mentor-ticket", 
        "user": u, 
        "tickets": ticket_data
    })#, can_create_more=another_one)

@login_required
def create_ticket(request):
    email = request.POST.get('email', '')
    if not request.user.is_authenticated:
        return redirect("/logout")
    t = Ticket.objects.create(
        user=request.user,
        location=request.POST.get('where', ''),
        question=request.POST.get('help', ''),
        contact=request.user.confirmation.phone,
        status="Unclaimed"
    )
    
    ret_response = {
        "code" : "200",
        "message": "success",
        "id": t.id,
        "contact": t.contact,
        "status": t.status,
        "question": t.question,
        "location": t.location,
        'name': t.user.full_name, 
        "type": 'create-ticket-mentors'
    }

    layer = get_channel_layer()
    async_to_sync(layer.group_send)('chat_main', {
        'type': 'chat_message',
        'message': json.dumps(ret_response)
    })

    return JsonResponse(ret_response)

@login_required
def delete_ticket(request):
    email = request.POST.get('email', '')
    u = request.user
    if not u:
        return JsonResponse({
            "message": "Invalid Email Address",
            "code": "403"
        })
    try:
        tid = int(request.POST.get('tid', -1))
        t = Ticket.objects.filter(id=tid).first()
        if not t.user == u and not u.is_admin and not u.is_mentor:
            raise AssertionError
        t.delete()
    except:
        return JsonResponse({
            "message": "Error finding ticket",
            "code": "403"
        })
   
    ret_response = {
        "code": "200",
        "message": "success",
        "id": tid,
        "type": 'ticket-deleted'
    }
    layer = get_channel_layer()
    async_to_sync(layer.group_send)('chat_main', {
        'type': 'chat_message',
        'message': json.dumps(ret_response)
    })

    
    return JsonResponse({
        "code" : "200",
        "message": "success"
    })

@login_required
def claim_ticket(request):
    email = request.POST.get('email', '')
    u = request.user
    if not u.is_authenticated:
        return JsonResponse({
            "message": "Invalid Email Address",
            "code": "403"
        })
    if not u.is_mentor:
        return JsonResponse({
            "message": "Not a mentor",
            "code": "403"
        })
    try:
        tid = int(request.POST.get('tid', -1))
        t = Ticket.objects.filter(id=tid).first()
        t.mentor = request.user
        if request.user.organization == None:
            org_name = "Unknown Organization"
        else:
            org_name = request.user.organization.name
        t.status = "Claimed by Mentor " + u.full_name + " - " + org_name
        t.save()

        ret_response = {
            "code" : "200",
            "message": "success",
            "id": t.id,
            "contact": t.contact,
            "status": t.status,
            "question": t.question,
            "location": t.location,
            "mentor_email": u.email,
            "type": 'ticket-status-change'
        }

        layer = get_channel_layer()
        async_to_sync(layer.group_send)('chat_main', {
            'type': 'chat_message',
            'message': json.dumps(ret_response)
        })
        
        return JsonResponse(ret_response)
    except:
        return JsonResponse({
            "message": "Error finding ticket",
            "code": "403"
        })

@login_required
def unclaim_ticket(request):
    email = request.POST.get('email', '')
    u = request.user
    if not u.is_authenticated:
        return JsonResponse({
            "message": "Invalid Email Address",
            "code": "403"
        })
    if not u.is_mentor:
        return JsonResponse({
            "message": "Not a mentor",
            "code": "403"
        })
    try:
        tid = int(request.POST.get('tid', -1))
        t = Ticket.objects.filter(id=tid).first()
        t.mentor = None
        t.status = "Unclaimed"
        t.save()

        ret_response = {
            "code" : "200",
            "message": "success",
            "id": t.id,
            "contact": t.contact,
            "status": t.status,
            "question": t.question,
            "location": t.location,
            "mentor_email": u.email,
            "type": 'ticket-status-change'
        }

        layer = get_channel_layer()
        async_to_sync(layer.group_send)('chat_main', {
            'type': 'chat_message',
            'message': json.dumps(ret_response)
        })
        
        return JsonResponse(ret_response)
    except:
        return JsonResponse({
            "message": "Error finding ticket",
            "code": "403"
        })

@login_required
def download_resumes(request, gradYear):
    u = request.user
    if not u.is_authenticated:
        return redirect("/logout")
    if not u.is_admin and not u.is_mentor:
        return redirect("/dashboard")
    try:
        if gradYear == "all":
            metadata, zip_file = dbx.files_download_zip("/Resumes/")
        else:
            metadata, zip_file = dbx.files_download_zip("/Resumes/" + gradYear + "/")
        response = HttpResponse(zip_file.content, content_type="application/zip")
        response['Content-Disposition'] = 'inline; filename=' + 'Resumes-{}.zip'.format(gradYear)
        return response
    except:
        return resume_book(request, error=True)

@login_required
def get_resume_by_id(request, uid):
    u = request.user
    if not u:
        return redirect("/logout")
    if not u.is_admin and not u.is_mentor:
        return redirect("/dashboard")
    u = User.objects.filter(id=uid)
    if u.count() > 0:
        u = u.first()
    else:
        return HttpResponse("ERROR")
    c = u.confirmation
    if c.resume_file_name == "":
        return HttpResponse("You have not uploaded a resume!")
    metadata, r_file = dbx.files_download(c.resume_file_name)
    file_name = u.full_name + "-Resume.pdf"
    response = HttpResponse(r_file.content, content_type="application/pdf")
    response['Content-Disposition'] = 'inline; filename=' + file_name
    return response

@login_required
def get_my_resume(request):
    u = request.user
    if not u:
        return redirect("/logout")
    c = u.confirmation
    if c.resume_file_name == "":
        return HttpResponse("You have not uploaded a resume!")
    metadata, r_file = dbx.files_download(c.resume_file_name)
    file_name = u.full_name + "-Resume.pdf"
    response = HttpResponse(r_file.content, content_type="application/pdf")
    response['Content-Disposition'] = 'inline; filename=' + file_name
    return response

@login_required
def resume_book(request, error=False):
    u = request.user
    if not u:
        return redirect("/logout")
    if not u.is_admin and not u.is_mentor:
        return redirect("/dashboard")
    return render(request, "resume-book.html", {
        "highlight": "resume-book", 
        "user": u, 
        "grad_years": settings.GRADUATION_YEARS, 
        "error": error
    })

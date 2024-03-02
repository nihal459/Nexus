from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from . models import *
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.db.models import Q  # Import Q object
from django.utils import timezone
# Create your views here.

def index(request):
    user = request.user.pk
    workspaces = Workspace.objects.filter(user=user)
    members = set()

    if workspaces.exists():
        for workspace in workspaces:
            members |= set(workspace.user.all())
        context = {'workspace': workspaces, 'members': members}
        return render(request, 'index.html', context)
    else:
        return render(request, 'index2.html')
    




def user_register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('passw')

        # Check if email already exists
        if User.objects.filter(email=username).exists():
            messages.error(request, 'Email already exists.')
        else:
            # Create user
            user = User.objects.create_user(username=username, email=username, password=password)
            messages.success(request, 'Registration Successful !!!')
            return redirect('user_register')

    return render(request, 'user_register.html')



def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('passw')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')  # Replace 'index' with the name of your index page URL
        else:
            messages.error(request, 'Invalid Credentials')

    return render(request, 'user_login.html')


def signout(request):
    logout(request)
    return redirect('user_login') 


def create_workspace(request):
    if request.method == 'POST':
        workspace_name = request.POST.get('workspace_name')
        user_ids = request.POST.getlist('users')
        admin = request.user
        
        # Check if workspace name already exists
        if Workspace.objects.filter(name=workspace_name).exists():
            messages.error(request, "Workspace name already exists.")
            return render(request, 'create_workspace.html')
        
        else:

            workspace = Workspace.objects.create(name=workspace_name, admin=admin)
            workspace.user.add(*user_ids)
            
            # Redirect to a page where you want to go after creating the workspace
            return redirect('index')

    # Fetch all users to populate the select field
    users = User.objects.all()
    context = {'users': users}
    return render(request, 'create_workspace.html', context)



def edit_workspace(request, pk):
    workspace = get_object_or_404(Workspace, pk=pk)
    all_users = User.objects.all()

    if request.method == "POST":
        new_workspace_name = request.POST.get('workspace_name')
        
        # Check if the new workspace name is different from the current one
        if new_workspace_name != workspace.name:
            # Check if the new workspace name already exists
            if Workspace.objects.filter(name=new_workspace_name).exists():
                messages.error(request, "Workspace name already exists.")
                return render(request, 'edit_workspace.html', {'workspace': workspace, 'all_users': all_users, 'selected_users': workspace.user.all()})

        # Proceed with editing if the new name is unique or unchanged
        workspace.name = new_workspace_name
        users_ids = request.POST.getlist('users')
        workspace.user.set(users_ids)  
        workspace.save()
        return redirect('index') 

    selected_users = workspace.user.all()

    context = {'workspace': workspace, 'all_users': all_users, 'selected_users': selected_users}
    return render(request, 'edit_workspace.html', context)




def join_workspace(request):
    if request.method == "POST":
        workspace_name = request.POST.get('workspace_name')
        try:
            workspace = Workspace.objects.get(name=workspace_name)
            workspace.user.add(request.user)
            return redirect('index')
        except Workspace.DoesNotExist:
            messages.error(request, "Workspace does not exist.")
            return render(request, "join_workspace.html")
    return render(request, "join_workspace.html")



def chat(request, pk):
    other_user = get_object_or_404(User, pk=pk)
    current_user = request.user
    messages = Message.objects.filter(
        (Q(from_user=current_user) & Q(to_user=other_user)) |
        (Q(from_user=other_user) & Q(to_user=current_user))
    ).order_by('date')

    return render(request, 'chat.html', {'other_user': other_user, 'messages': messages})


# def send_message(request):
#     if request.method == 'POST':
#         to_user_id = request.POST.get('to_user')
#         message_content = request.POST.get('message')

#         # Get the sender and receiver
#         from_user = request.user
#         to_user = User.objects.get(pk=to_user_id)

#         # Create and save the message
#         message = Message(from_user=from_user, to_user=to_user, message=message_content, date=timezone.now())
#         message.save()

#     # Redirect back to the chat page
#     return redirect('chat', pk=to_user_id)



# def send_message(request):
#     if request.method == 'POST':
#         to_user_id = request.POST.get('to_user')
#         message_content = request.POST.get('message')
#         image_file = request.FILES.get('image')

#         # Get the sender and receiver
#         from_user = request.user
#         to_user = User.objects.get(pk=to_user_id)

#         # Create and save the message
#         message = Message(from_user=from_user, to_user=to_user, message=message_content, date=timezone.now())
#         if image_file:
#             # If an image is uploaded, save it
#             message.image = image_file
#         message.save()

#     # Redirect back to the chat page
#     return redirect('chat', pk=to_user_id)


from django.http import HttpResponseBadRequest

def send_message(request):
    if request.method == 'POST':
        to_user_id = request.POST.get('to_user')
        message_content = request.POST.get('message')
        file = request.FILES.get('file')

        # Get the sender and receiver
        from_user = request.user
        to_user = User.objects.get(pk=to_user_id)

        # Create and save the message
        message = Message(from_user=from_user, to_user=to_user, message=message_content, date=timezone.now())

        # Check if file is uploaded
        if file:
            # Determine file type
            if file.content_type.startswith('image'):
                # If it's an image, save it to 'images' folder
                message.image = file
            elif file.content_type.startswith('video'):
                # If it's a video, save it to 'videos' folder
                message.video = file
            else:
                # If it's neither image nor video, return bad request
                return HttpResponseBadRequest("Unsupported file type")

        message.save()

    # Redirect back to the chat page
    return redirect('chat', pk=to_user_id)


def my_profile(request):
    if request.method == 'POST':
        user = request.user
        name = request.POST.get('name')
        mobile_number = request.POST.get('mobile_number')
        profile_picture = request.FILES.get('profile_picture')

        # Update user profile fields
        user.name = name
        user.mobile_number = mobile_number
        if profile_picture:
            user.profile_picture = profile_picture
        user.save()
    
        return redirect('my_profile')
    else:
        return render(request, 'my_profile.html')
    

def view_user(request,pk):
    user = get_object_or_404(User, pk=pk)
    context = {'user':user}
    return render(request, "view_user.html", context)


def exit(request, pk):
    workspace = get_object_or_404(Workspace, pk=pk)

    # Check if the current user is a member of the workspace
    if request.user in workspace.user.all():
        # Remove the current user from the workspace
        workspace.user.remove(request.user)
    else:
        messages.error(request, 'You are not a member of this workspace.')

    return redirect('index') 
                


def delete_workspace(request, pk):
    workspace = get_object_or_404(Workspace, pk=pk)

    # Check if the current user is the admin of the workspace
    if request.user == workspace.admin:
        # Delete the workspace
        workspace.delete()
    else:
        messages.error(request, 'You are not authorized to delete this workspace.')

    return redirect('index') 
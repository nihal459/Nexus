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
        user_channels = Channel.objects.filter(workspace__in=workspaces)  # Filter channels based on user's workspaces

        for workspace in workspaces:
            members |= set(workspace.user.all())
        context = {'workspace': workspaces, 'members': members, 'user_channels': user_channels}
        return render(request, 'index.html', context)
    else:
        return render(request, 'index2.html')
    
from django.db.models import Q

def search_results(request):
    keyword = request.GET.get('keyword')
    user = request.user

    # Search for messages containing the keyword
    user_messages = Message.objects.filter(Q(from_user=user) | Q(to_user=user), message__icontains=keyword)

    # Search for channel messages containing the keyword
    user_channel_messages = Channel_message.objects.filter(channel__users=user, message__icontains=keyword)

    context = {
        'user_messages': user_messages,
        'user_channel_messages': user_channel_messages,
        'keyword': keyword
    }
    return render(request, 'search_results.html', context)


def whiteboard(request):
    return render(request, 'whiteboard.html')



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



# def add_channel(request):
#     if request.user.is_authenticated:
#         user_workspaces = request.user.workspaces.all()
#         context = {'user_workspaces': user_workspaces}
#         return render(request, 'add_channel.html', context)
#     else:
#         # Handle the case when the user is not authenticated
#         return render(request, 'add_channel.html')
    



from django.shortcuts import render, redirect
from .models import User, Workspace, Channel

def add_channel(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            print(request.POST)  # Print out POST data for debugging
            channel_name = request.POST.get('channel_name')
            workspace_id = request.POST.get('users')
            image = request.FILES.get('profile_picture')
            
            # Create the channel with the provided data
            try:
                workspace = Workspace.objects.get(id=workspace_id)
            except Workspace.DoesNotExist:
                print("Workspace does not exist")  # Debugging message
                return redirect('add_channel')  # Redirect or handle the error as needed
            
            channel = Channel.objects.create(
                channel_name=channel_name,
                workspace=workspace,
            )
            if image:
                channel.profile_picture = image
            # Add all users of the selected workspace to the channel
            users = workspace.user.all()
            for user in users:
                channel.users.add(user)
            
            channel.save()
            return redirect('index')  # Redirect to the index page or wherever you want
        else:
            user_workspaces = request.user.workspaces.all()
            context = {'user_workspaces': user_workspaces}
            return render(request, 'add_channel.html', context)
    else:
        # Handle the case when the user is not authenticated
        return render(request, 'add_channel.html')



# def channel_chat(request, pk):
#     # Retrieve the channel object
#     channel =get_object_or_404(Channel, pk=pk)
#     # Retrieve all messages related to the channel
#     messages = Channel.objects.filter(pk=pk)  # Assuming related_name is not defined in the ChannelMessage model

#     context = {
#         'channel': channel,
#         'messages':messages,
#     }
#     return render(request, 'channel_chat.html', context)
    

def channel_chat(request, pk):
    # Retrieve the channel object
    channel = get_object_or_404(Channel, pk=pk)
    # Retrieve all messages related to the channel
    messages = Channel_message.objects.filter(channel=channel)
    colors = ['#FFFF00', '#008000', '#0000FF', '#8A2BE2', '#FF0000']  # List of colors

    context = {
        'channel': channel,
        'messages': messages,
        'colors':colors,
    }
    return render(request, 'channel_chat.html', context)

def send_channel_message(request):
    if request.method == 'POST':
        text = request.POST.get('text')
        file = request.FILES.get('file')
        channel_id = request.POST.get('channel')
        channel = get_object_or_404(Channel, pk=channel_id)

        # Check if file is provided
        if file:
            # Check file type
            if file.content_type.startswith('image'):
                # If it's an image, save it to 'image' field
                Channel_message.objects.create(
                    channel=channel,
                    sender=request.user,
                    message=text,
                    image=file
                )
            elif file.content_type.startswith('video'):
                # If it's a video, save it to 'video' field
                Channel_message.objects.create(
                    channel=channel,
                    sender=request.user,
                    message=text,
                    video=file
                )
            else:
                # If it's neither image nor video, return bad request
                return HttpResponseBadRequest("Unsupported file type")
        else:
            # If no file is provided, create message without image or video
            Channel_message.objects.create(
                channel=channel,
                sender=request.user,
                message=text
            )

    return redirect('channel_chat', pk=channel_id)





def channel_details(request,pk):
    channel = get_object_or_404(Channel, pk=pk)
    context = {'channel':channel}
    return render(request, "channel_details.html", context)



def edit_channel(request, pk):
    channel = get_object_or_404(Channel, pk=pk)

    if request.method == "POST":
        channel_name = request.POST.get('channel_name')
        img = request.FILES.get('img')

        # Update channel details
        if channel_name:
            channel.channel_name = channel_name
        if img:
            channel.profile_picture = img
        channel.save()
        
    context = {'channel': channel}
    return render(request, "edit_channel.html", context)




def delete_channel(request, pk):
    channel = get_object_or_404(Channel, pk=pk)

    channel.delete()

    return redirect('index')
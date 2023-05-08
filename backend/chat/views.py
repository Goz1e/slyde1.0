from django.shortcuts import render, get_object_or_404, redirect
from .models import *
from django.contrib import messages
from .forms import RoomForm, CreateRoomForm

# Create your views here.
def create_room(request):
    if request.POST:
        form = CreateRoomForm(request.POST)
        if form.is_valid():
            room = form.save()
            msg = f'{room.name} created with ID: {room.room_id}'
            return redirect('room',room.room_id)
        msg = 'room creation failed'
        messages.info(request,msg)
        return redirect('index')

def anon_room(request):
    dp_name = request.GET.get('dp_name')
    room_name = request.GET.get('room_name')
    sexxion = request.session
    sexxion['dp_name'] = dp_name
    room = Room.objects.create(name = room_name)
    return redirect('room',room.room_id)

def dashboard(request):
    form = CreateRoomForm(request.POST)
    template_name = 'chat/dashboard.html'
    context = {
        'title' : f" welcome {request.user.username}",
        'chat_page':'chat_page',
        'form':form
    }
    if request.user.is_authenticated:
        rooms = Room.objects.all_rooms(request.user)
        if rooms.exists():
            context['rooms']=rooms
    return render(request, template_name, context)

def get_room(request):
    room_id = request.GET.get('q')
    try:
        room = get_object_or_404(Room,room_id=room_id)
        return redirect('room',room.room_id)
    except:
        messages.info(request,f'room with id: {room_id} does not exist')
        if request.user.is_authenticated:
            return redirect('dashboard')
        return redirect('index')


def room(request,room_id):
    room = get_object_or_404(Room,room_id = room_id)
    access = room.admit_user(request.user)
    if access == None:
        messages.info('login to access private rooms!')
        return redirect('index')
    if access !=True:
        messages.info(request,access)
        if request.user.is_authenticated:
            return redirect('dashboard')
        return redirect('index')
    context = {
        'room':room, 'title':room.name,
        'chat_page':'chat_page',
    }

    if request.user.is_authenticated:
        rooms = Room.objects.all_rooms(request.user)
        context['username'] = request.user.username
        context['rooms'] = rooms
        context['auth_user'] = 'auth_user'
    else:
        context['username'] = request.session['dp_name']

    return render(request,'chat/room.html',context)

    
def room_settings(request,room_id):
    room = get_object_or_404(Room,room_id=room_id)
    form = CreateRoomForm(request.POST or None, instance=room)
    if request.user.is_authenticated:
        form = RoomForm(request.POST or None, instance=room)
    if request.POST:
        if form.is_valid():
            form.save()
            return redirect('room',room.room_id)
    context = {
        'room':room, 'members':room.members.all(), 'admins':room.room_admin.all(),
        'room_requests':room.requests.all(), 'form':form, 'title': f'{room.name} settings'
    }
    if room.has_access(request.user):
        context['admin_access'] = 'admin_access'
    if room.has_prem_access(request.user):
        context['prem_access'] = 'prem_access'
    template_name = 'chat/room_settings.html'     
    return render(request, template_name, context)


def admin_actions(request,room_id,username,action):
    room = get_object_or_404(Room,room_id=room_id)
    user = get_object_or_404(User,username=username)
    command = {
        'accept':room.approve_requests,
        'decline':room.decline_requests,
        'remove':room.remove_member,
        'make_admin':room.make_admin,
        'revoke_admin':room.revoke_admin,
        'accept_all':room.approve_all_requests,
        'decline_all':room.decline_all_requests,
    }

    if command[action](request.user,user):
        messages.success(request, f'{action} successful!')
        return redirect('room_settings',room_id)
    messages.warning(request, f'{action} failed')    
    return redirect('room_settings',room_id)
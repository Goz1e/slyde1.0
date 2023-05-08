from django.db import models
from django.contrib.auth.models import User, Group, Permission
import uuid, string, random
from django.db.models import Q
# Create your models here.
class Message(models.Model):
    author = models.ForeignKey(User,related_name='messages', related_query_name='messages', on_delete=models.CASCADE, null=True)
    content = models.TextField(max_length=500)
    timestamp = models.DateTimeField(auto_now_add=True)
    display_name = models.CharField(max_length=50)

    @property
    def created_on(self):
        h = self.timestamp.hour
        m = self.timestamp.minute
        x = 'AM'
        if h > 12:
            x = 'PM'
            h -=12
        return f'{h}:{m} {x}'

    @property
    def author_name(self):
        if self.author == None:
            return str(self.display_name)
        return str(self.author.username)


    def __str__(self):
        return f'{self.content[:5]} by {self.author}'
    
class RoomQueryset(models.QuerySet):
    def my_rooms(self,user):
        qs = self.filter(owner=user)
        return qs
    
    def all_rooms(self,user):
        q1 = self.my_rooms(user)
        q2 = user.memberships.all()
        qs = (q1|q2).distinct()
        return qs
    
    def pending_requests(self,user):
        qs = user.requests.all()
        return qs
    
    def search(self,user,query):
        lookup= (
            Q(name__icontains=query)| Q(room_id__icontains=query)
        )
        qs = self.all_rooms(user)
        if user.is_staff:
            qs = self.all()
        return qs.filter(lookup) 

class Room(models.Model):
    name = models.CharField(max_length=50)
    room_id = models.CharField(unique=True,max_length=4,blank=True,null=False)
    created_on = models.DateTimeField(auto_now_add=True)
    private = models.BooleanField(default=False)
    allow_anon =models.BooleanField(default=False)
    members = models.ManyToManyField(User, related_name='memberships', blank=True)
    requests = models.ManyToManyField(User, related_name='requests', blank=True)
    room_admin = models.ManyToManyField(User, blank=True, related_name='administrations')
    owner = models.ForeignKey(
        User,on_delete=models.CASCADE, blank=True, null=True,
        related_name='my_rooms',related_query_name='my_rooms'
    )
    messages = models.ManyToManyField(
        Message,related_name='room', related_query_name='room',
        blank=True
    )
    objects = RoomQueryset.as_manager()
    
    class Meta:
        ordering =['name']
        permissions = [
            ("super_admin","has super permisson over room")
        ]
    
    def save(self,*args,**kwargs):
        if self.room_id == '':
            self.room_id = Room.random_uuid()
        return super().save(*args,**kwargs)

    @classmethod
    def random_uuid(cls):
        id = str(uuid.uuid4())[:4].lower()
        try:
            if Room.objects.get(room_id=id).exists():    
                y = random.choice(list(string.ascii_lowercase))
                x = id[random.choice(range(0,4))]
                id = id.replace(x,y)
        except:
            pass
        return id

    def __str__(self):
        return self.name
    
    def is_owner(self,user):
        return user == self.owner
    
    def is_member(self,user):
        return user in self.members.all()
    
    def is_admin(self,user):
        return bool(
            self.is_member(user=user) and                    
            user in self.room_admin.all()
        )
    
    def has_access(self,admin):
        return bool(
            admin.has_perm('change_room',self) or 
            admin in self.room_admin.all() or 
            admin == self.owner
        )

    def has_prem_access(self,admin):
        return bool(
            admin == self.owner
        )

    def admit_user(self,user):
        if self.private:
            if self.is_member(user) or self.has_prem_access(user):
                return True
            else:
                if not user.is_authenticated:
                    return None    
                if user in self.requests.all():
                    msg='request pending'
                else:
                    self.requests.add(user)
                    msg='private room!, request sent'
                return msg
        return True

    def approve_requests(self,admin,user):
        if self.has_access(admin) or self.has_prem_access(admin):
            self.requests.remove(user)
            self.members.add(user)
            return True
        return False    
    
    def approve_all_requests(self,admin,user):
        if self.has_access(admin) or self.has_prem_access(admin):
            if self.requests.all().exists():
                for user in self.requests.all():
                    self.requests.remove(user)
                    self.members.add(user)
                return True
        return False    

    def decline_requests(self,admin,user):
        if self.has_access(admin) or self.has_prem_access(admin):
            self.requests.remove(user)
            return True
        return False    
    
    def decline_all_requests(self,admin,user):
        if self.has_access(admin) or self.has_prem_access(admin):
            if self.requests.all().exists():
                for user in self.requests.all():
                    self.requests.remove(user)
                return True
        return False    
    
    def make_admin(self,owner,user):
        if self.has_prem_access(owner):
            room_admins = Group.objects.get(name = 'room admins')
            if self.is_member(user=user):
                user.groups.add(room_admins)
                self.room_admin.add(user)
                return True
        return False
    
    def revoke_admin(self,owner,user):
        if self.has_prem_access(owner):
           self.room_admin.remove(user)
           return True
        return False
    
    def remove_member(self,admin,user):
        if self.has_access(admin) or self.has_prem_access(admin):
            self.members.remove(user)
            try:
                self.revoke_admin(owner=self.owner,user=user)
            except:
                pass
            return True
        return False
    


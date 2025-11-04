from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Profile, Post, Comment
from .forms import PostForm, CommentForm, ProfileForm
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout


from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login



from .models import Post
from .forms import PostForm
from django.contrib.auth.decorators import login_required

from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages



def profile_view(request, username):
    user = get_object_or_404(User, username=username)
    profile = get_object_or_404(Profile, user=user)
    posts = Post.objects.filter(author=user).order_by('-created_at')
    is_following = False
    if request.user.is_authenticated:
        is_following = profile.followers.filter(id=request.user.id).exists()
    return render(request, 'profile.html', {
        'profile': profile,
        'posts': posts,
        'is_following': is_following
    })


@login_required
def follow_toggle(request, username):
    target_user = get_object_or_404(User, username=username)
    target_profile = get_object_or_404(Profile, user=target_user)

    if request.user in target_profile.followers.all():
        target_profile.followers.remove(request.user)
    else:
        target_profile.followers.add(request.user)

    return redirect('profile', username=username)




def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('index')  # redirect to homepage
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'login.html')


from django.contrib.auth.models import User
from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.contrib import messages

def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 == password2:
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists')
            elif User.objects.filter(email=email).exists():
                messages.error(request, 'Email already exists')
            else:
                user = User.objects.create_user(username=username, email=email, password=password1)
                user.save()  # ✅ Only this is needed — Profile is auto-created by your signal
                messages.success(request, 'Account created successfully')
                return redirect('login')
        else:
            messages.error(request, 'Passwords do not match')
    return render(request, 'register.html')


@login_required
def index(request):
    posts = Post.objects.all().order_by('-created')
    form = PostForm()

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('home')

    return render(request, 'index.html', {'form': form, 'posts': posts})


from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect

def logout_view(request):
    logout(request)
    return redirect('login')





@login_required
def edit_profile(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile', username=request.user.username)
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'edit_profile.html', {'form': form})


@login_required
def feed(request):
    profiles_followed = request.user.profile.followers.all()
    posts = Post.objects.filter(user__in=profiles_followed).order_by('-created')
    return render(request, 'feed.html', {'posts': posts})

@login_required
def profile(request, username):
    user = get_object_or_404(User, username=username)
    posts = Post.objects.filter(user=user).order_by('-created')
    is_following = request.user in user.profile.followers.all()
    return render(request, 'profile.html', {
        'profile_user': user,
        'posts': posts,
        'is_following': is_following
    })

@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            return redirect('feed')
    else:
        form = PostForm()
    return render(request, 'create_post.html', {'form': form})

@login_required
def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.all().order_by('created')

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.post = post
            comment.save()
            return HttpResponseRedirect(reverse('post_detail', args=[post.id]))
    else:
        form = CommentForm()

    return render(request, 'post_detail.html', {
        'post': post,
        'comments': comments,
        'form': form
    })

@login_required
def follow_user(request, username):
    target_user = get_object_or_404(User, username=username)
    profile = target_user.profile
    if request.user in profile.followers.all():
        profile.followers.remove(request.user)
    else:
        profile.followers.add(request.user)
    return redirect('profile', username=username)

@login_required
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user in post.likes.all():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)
    return redirect('post_detail', post_id=post.id)



from django.shortcuts import render, get_object_or_404

from post.forms import NewPostForm
from comment.forms import CommentForm

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect
from django.urls import reverse

from post.models import Post, PostFileContent, Stream, Likes, Bookmark
from tier.models import Tier, Subscription
from comment.models import Comment

# Create your views here.

@login_required
def index(request):
    user = request.user
    stream_items = Stream.objects.filter(user=user).order_by('-date')

    #Pagination
    paginator = Paginator(stream_items, 9)
    page_number = request.GET.get('page')
    stream_data = paginator.get_page(page_number)

    context = {
        'stream_data': stream_data,
    }

    return render(request, 'index.html', context)

@login_required
def PostDetails(request, post_id):
    user = request.user
    post = get_object_or_404(Post, id=post_id)

    #Check if the user liked the post
    if Likes.objects.filter(post=post, user=user).exists():
        liked = True
    else:
        liked = False
    
    #Comment stuff:
    comments = Comment.objects.filter(post=post).order_by('-date')

    #Comment form
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.user = user
            comment.save()
            post.comments_count += 1
            post.save()
            return HttpResponseRedirect(reverse('postdetails', args=[post_id]))
    else:
        form = CommentForm()
    
    #To validate that the user can see the post
    if user != post.user:
        subscriber = Subscription.objects.get(subscriber=request.user, subscribed=post.user)
        if (subscriber.tier.number >= post.tier.number):
            visible = True
        else:
            visible = False
    else:
        visible = True
    
    context = {
        'post': post,
        'visible': visible,
        'liked': liked,
        'comments': comments,
        'form': form,
    }

    return render(request, 'post_detail.html', context)


@login_required
def NewPost(request):
    user = request.user
    files_objs = []

    if request.method == "POST":
        form = NewPostForm(request.POST, request.FILES)

        if form.is_valid():
            files = request.FILES.getlist('content')
            title = form.cleaned_data.get('title')
            caption = form.cleaned_data.get('caption')
            tier = form.cleaned_data.get('tier')
            tiers = get_object_or_404(Tier, id=tier.id)

            for file in files:
                file_instance = PostFileContent(file=file, user=user, tier=tiers)
                file_instance.save()
                files_objs.append(file_instance)
            
            p, created = Post.objects.get_or_create(title=title, caption=caption, user=user, tier=tiers)
            p.content.set(files_objs)
            p.save()
            return redirect('index')
    else:
        form = NewPostForm()
        form.fields['tier'].queryset = Tier.objects.filter(user=user)
    
    context = {
        'form': form,
    }

    return render(request, 'newpost.html', context)

@login_required
def like(request, post_id):
    user = request.user
    post = get_object_or_404(Post, id=post_id)
    current_likes = post.likes_count

    liked = Likes.objects.filter(user=user, post=post).count()

    if not liked:
        like = Likes.objects.create(user=user, post=post)
        current_likes = current_likes + 1
    else:
        Likes.objects.filter(user=user, post=post).delete()
        current_likes = current_likes - 1
    
    post.likes_count = current_likes
    post.save()

    return HttpResponseRedirect(reverse('postdetails', args=[post_id]))

@login_required
def bookmark(request, post_id):
    user = request.user
    post = get_object_or_404(Post, id=post_id)
    current_bookmarks = post.favorites_count

    try:
        b, created = Bookmark.objects.get_or_create(user=user)
        if b.posts.filter(id=post_id).exists():
            b.posts.remove(post)
            current_bookmarks = current_bookmarks - 1
        else:
            b.posts.add(post)
            current_bookmarks = current_bookmarks + 1
        post.favorites_count = current_bookmarks
        post.save()
        return HttpResponseRedirect(reverse('postdetails', args=[post_id]))
    except Exception as e:
        raise e

@login_required
def BookmarkList(request):
    bookmark_list = Bookmark.objects.get(user=request.user)

    #Pagination
    paginator = Paginator(bookmark_list.posts.all(), 9)
    page_number = request.GET.get('page')
    bookmark_data = paginator.get_page(page_number)

    context = {
        'bookmark_data': bookmark_data,
    }

    return render(request, 'bookmark_list.html', context)




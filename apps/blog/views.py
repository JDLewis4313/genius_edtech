# apps/blog/views.py

from itertools import chain
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.contenttypes.models import ContentType
from collections import Counter
from django.urls import reverse

# Import models and forms.
from .models import BlogPost, ExternalArticle
from .forms import BlogPostForm, ShareToCommonsForm
from apps.community.models import Board, Thread, Post  # Community models
from apps.interactions.models import Comment, Reaction  # Comments and Reactions

# Reaction choices for internal posts.
REACTION_CHOICES = [
    ("like", "👍"),
    ("fire", "🔥"),
    ("wow", "🤯"),
    ("rocket", "🚀"),
]

def blog_index(request):
    """
    Display a combined feed of internal blog posts and external articles.
    """
    # Query internal posts.
    internal_posts = list(BlogPost.objects.filter(is_published=True).order_by('-created_at'))
    # Query external articles.
    external_articles = list(ExternalArticle.objects.order_by('-published_date', '-fetched_date'))
    
    # Annotate internal posts with common fields.
    for post in internal_posts:
        post.is_external = False
        post.created_at_common = post.created_at
        post.excerpt_common = post.excerpt
    
    # Annotate external articles.
    for article in external_articles:
        article.is_external = True
        article.created_at_common = article.published_date if article.published_date else article.fetched_date
        article.excerpt_common = article.summary

    # Merge and sort both lists by the common creation date.
    combined_feed = sorted(
        internal_posts + external_articles,
        key=lambda x: x.created_at_common,
        reverse=True
    )
    
    return render(request, 'blog/index.html', {'posts': combined_feed})

def external_article_detail(request, pk):
    """
    Display details for an external article.
    """
    article = get_object_or_404(ExternalArticle, pk=pk)
    context = {'article': article}
    return render(request, 'blog/external_detail.html', context)

@login_required
def take_external_to_commons(request, pk):
    """
    Displays a form to capture a user's comment before sharing an external article 
    to The Commons. On submission, creates a new thread in a designated board
    (e.g. a board with slug "the-feed") and an initial post containing the article info 
    plus the user's comment, then redirects to that thread.
    """
    article = get_object_or_404(ExternalArticle, pk=pk)
    
    if request.method == 'POST':
        form = ShareToCommonsForm(request.POST)
        if form.is_valid():
            user_comment = form.cleaned_data['comment']
            
            # Get the board where shared posts are grouped; make sure this board exists.
            board = get_object_or_404(Board, slug="the-feed")
            thread_title = f"Discussion: {article.title}"
            
            # Create a new thread.
            thread = Thread.objects.create(
                board=board,
                title=thread_title,
                author=request.user,
            )
            
            # Format published date if available.
            published_date_str = (
                article.published_date.strftime("%B %d, %Y")
                if article.published_date else "N/A"
            )
            
            # Build the initial post body.
            if user_comment:
                post_body = (
                    f"Let's discuss this article from our Feed:<br><br>"
                    f"<strong>{article.title}</strong><br>"
                    f"Published on: {published_date_str}<br><br>"
                    f"{article.summary}<br><br>"
                    f"User says: {user_comment}<br><br>"
                    f"<a href='{article.original_url}' target='_blank'>Read full article on original site</a>"
                )
            else:
                post_body = (
                    f"Let's discuss this article from our Feed:<br><br>"
                    f"<strong>{article.title}</strong><br>"
                    f"Published on: {published_date_str}<br><br>"
                    f"{article.summary}<br><br>"
                    f"<a href='{article.original_url}' target='_blank'>Read full article on original site</a>"
                )
            
            # Create the initial post in the thread.
            Post.objects.create(
                thread=thread,
                author=request.user,
                body=post_body
            )
            
            # Redirect to the new thread's detail page.
            return redirect('community:thread_detail', slug=thread.slug)
    else:
        form = ShareToCommonsForm()
    
    return render(request, 'blog/share_to_commons.html', {'article': article, 'form': form})

def blog_detail(request, slug):
    """
    Display details for an internal blog post (The Feed). Allow users to react and comment.
    """
    post = get_object_or_404(BlogPost, slug=slug, is_published=True)

    if request.method == "POST" and request.user.is_authenticated:
        content = request.POST.get("content")
        reaction = request.POST.get("reaction")
        if content:
            Comment.objects.create(
                user=request.user,
                content_type=ContentType.objects.get_for_model(post),
                object_id=post.id,
                content=content
            )
        elif reaction:
            Reaction.objects.create(
                user=request.user,
                content_type=ContentType.objects.get_for_model(post),
                object_id=post.id,
                reaction=reaction
            )
        return redirect(request.path)

    comments = Comment.objects.filter(
        content_type=ContentType.objects.get_for_model(post),
        object_id=post.id
    ).order_by("-created_at")

    reactions = Reaction.objects.filter(
        content_type=ContentType.objects.get_for_model(post),
        object_id=post.id
    )
    reaction_count = Counter(r.reaction for r in reactions)

    context = {
        'post': post,
        'comments': comments,
        'reaction_count': reaction_count,
        'REACTION_CHOICES': REACTION_CHOICES,
    }
    return render(request, 'blog/detail.html', context)

@login_required
@user_passes_test(lambda u: u.is_staff)
def create_post(request):
    """
    Allow staff users to create a new internal blog post.
    """
    form = BlogPostForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.is_published = False  # Admin publishes later.
        post.save()
        return redirect('blog:detail', slug=post.slug)
    return render(request, 'blog/create.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.is_staff)
def edit_post(request, slug):
    """
    Allow staff users to edit an existing blog post.
    """
    post = get_object_or_404(BlogPost, slug=slug, author=request.user)
    form = BlogPostForm(request.POST or None, instance=post)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('blog:detail', slug=post.slug)
    return render(request, 'blog/create.html', {
        'form': form,
        'is_edit': True,
        'post': post
    })

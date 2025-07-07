# apps/blog/views.py - COMPLETE WITH INTERACTIONS
from itertools import chain
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.contenttypes.models import ContentType
from collections import Counter
from django.urls import reverse
from django.contrib import messages

from .models import BlogPost, Post, ExternalArticle
from .forms import BlogPostForm, ShareToCommonsForm
from apps.community.models import Board, Thread, Post as CommunityPost
from apps.interactions.models import Comment, Reaction

REACTION_CHOICES = [
    ("like", "👍"),
    ("fire", "🔥"),
    ("wow", "🤯"),
    ("rocket", "🚀"),
]

def blog_index(request):
    internal_posts = list(BlogPost.objects.filter(is_published=True).order_by('-created_at'))
    quick_posts = list(Post.objects.filter(published=True).order_by('-created_at'))
    external_articles = list(ExternalArticle.objects.order_by('-published_date', '-fetched_date'))

    for post in internal_posts:
        post.is_external = False
        post.is_quick_post = False
        post.created_at_common = post.created_at or post.updated_at
        post.excerpt_common = getattr(post, 'excerpt', '') or ''
        post.feed_type = 'editorial'
        post.comment_count = Comment.objects.filter(content_type=ContentType.objects.get_for_model(post), object_id=post.id).count()
        reactions = Reaction.objects.filter(content_type=ContentType.objects.get_for_model(post), object_id=post.id)
        post.reaction_count = Counter(r.reaction for r in reactions)
        post.total_reactions = sum(post.reaction_count.values())

    for post in quick_posts:
        post.is_external = False
        post.is_quick_post = True
        post.created_at_common = post.created_at
        post.excerpt_common = post.excerpt or post.content[:300]
        post.feed_type = 'quick'
        post.comment_count = Comment.objects.filter(content_type=ContentType.objects.get_for_model(post), object_id=post.id).count()
        reactions = Reaction.objects.filter(content_type=ContentType.objects.get_for_model(post), object_id=post.id)
        post.reaction_count = Counter(r.reaction for r in reactions)
        post.total_reactions = sum(post.reaction_count.values())

    for article in external_articles:
        article.is_external = True
        article.is_quick_post = False
        article.created_at_common = article.published_date or article.fetched_date
        article.excerpt_common = article.summary or ''
        article.feed_type = 'external'
        article.comment_count = Comment.objects.filter(content_type=ContentType.objects.get_for_model(article), object_id=article.id).count()
        reactions = Reaction.objects.filter(content_type=ContentType.objects.get_for_model(article), object_id=article.id)
        article.reaction_count = Counter(r.reaction for r in reactions)
        article.total_reactions = sum(article.reaction_count.values())

    combined_feed = sorted(
        internal_posts + quick_posts + external_articles,
        key=lambda x: x.created_at_common or x.updated_at,
        reverse=True
    )

    announcements = Post.objects.filter(published=True, is_announcement=True)[:3]

    return render(request, 'blog/index.html', {
        'posts': combined_feed,
        'announcements': announcements,
        'REACTION_CHOICES': REACTION_CHOICES,
    })


def blog_detail(request, slug):
    """
    Display details for an internal blog post (BlogPost model) with full interactions.
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
            messages.success(request, "Comment added successfully!")
            
        elif reaction:
            # Check if user already reacted with this reaction
            existing_reaction = Reaction.objects.filter(
                user=request.user,
                content_type=ContentType.objects.get_for_model(post),
                object_id=post.id,
                reaction=reaction
            ).first()
            
            if existing_reaction:
                # Remove the reaction (toggle off)
                existing_reaction.delete()
                messages.info(request, "Reaction removed!")
            else:
                # Remove any other reactions from this user, then add new one
                Reaction.objects.filter(
                    user=request.user,
                    content_type=ContentType.objects.get_for_model(post),
                    object_id=post.id
                ).delete()
                
                Reaction.objects.create(
                    user=request.user,
                    content_type=ContentType.objects.get_for_model(post),
                    object_id=post.id,
                    reaction=reaction
                )
                messages.success(request, "Reaction added!")
                
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
    
    # Get user's current reaction if logged in
    user_reaction = None
    if request.user.is_authenticated:
        user_reaction_obj = Reaction.objects.filter(
            user=request.user,
            content_type=ContentType.objects.get_for_model(post),
            object_id=post.id
        ).first()
        if user_reaction_obj:
            user_reaction = user_reaction_obj.reaction

    context = {
        'post': post,
        'comments': comments,
        'reaction_count': reaction_count,
        'user_reaction': user_reaction,
        'REACTION_CHOICES': REACTION_CHOICES,
        'post_type': 'editorial',
    }
    return render(request, 'blog/detail.html', context)

def external_article_detail(request, pk):
    """
    Display details for an external article with full interactions.
    """
    article = get_object_or_404(ExternalArticle, pk=pk)
    
    if request.method == "POST" and request.user.is_authenticated:
        content = request.POST.get("content")
        reaction = request.POST.get("reaction")
        
        if content:
            Comment.objects.create(
                user=request.user,
                content_type=ContentType.objects.get_for_model(article),
                object_id=article.id,
                content=content
            )
            messages.success(request, "Comment added successfully!")
            
        elif reaction:
            # Check if user already reacted with this reaction
            existing_reaction = Reaction.objects.filter(
                user=request.user,
                content_type=ContentType.objects.get_for_model(article),
                object_id=article.id,
                reaction=reaction
            ).first()
            
            if existing_reaction:
                existing_reaction.delete()
                messages.info(request, "Reaction removed!")
            else:
                # Remove any other reactions from this user, then add new one
                Reaction.objects.filter(
                    user=request.user,
                    content_type=ContentType.objects.get_for_model(article),
                    object_id=article.id
                ).delete()
                
                Reaction.objects.create(
                    user=request.user,
                    content_type=ContentType.objects.get_for_model(article),
                    object_id=article.id,
                    reaction=reaction
                )
                messages.success(request, "Reaction added!")
                
        return redirect(request.path)
    
    # Get related articles from same source
    related_articles = ExternalArticle.objects.filter(
        source=article.source
    ).exclude(pk=pk)[:3]
    
    comments = Comment.objects.filter(
        content_type=ContentType.objects.get_for_model(article),
        object_id=article.id
    ).order_by("-created_at")

    reactions = Reaction.objects.filter(
        content_type=ContentType.objects.get_for_model(article),
        object_id=article.id
    )
    reaction_count = Counter(r.reaction for r in reactions)
    
    # Get user's current reaction if logged in
    user_reaction = None
    if request.user.is_authenticated:
        user_reaction_obj = Reaction.objects.filter(
            user=request.user,
            content_type=ContentType.objects.get_for_model(article),
            object_id=article.id
        ).first()
        if user_reaction_obj:
            user_reaction = user_reaction_obj.reaction
    
    context = {
        'article': article,
        'related_articles': related_articles,
        'comments': comments,
        'reaction_count': reaction_count,
        'user_reaction': user_reaction,
        'REACTION_CHOICES': REACTION_CHOICES,
        'has_full_content': bool(article.full_content),
    }
    return render(request, 'blog/external_detail.html', context)

@login_required
def take_external_to_commons(request, pk):
    """
    Share an external article to The Commons with user's comment.
    """
    article = get_object_or_404(ExternalArticle, pk=pk)

    if request.method == 'POST':
        form = ShareToCommonsForm(request.POST)
        if form.is_valid():
            user_comment = form.cleaned_data['comment']

            # Get or create the board where shared posts are grouped
            board, created = Board.objects.get_or_create(
                slug="the-feed",
                defaults={
                    'name': 'The Feed',
                    'description': 'External articles shared by the community'
                }
            )
            
            thread_title = f"Discussion: {article.title[:100]}..."

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
            post_body_parts = [
                f"🔬 <strong>Shared from The Feed:</strong><br><br>",
                f"<h3>{article.title}</h3>",
                f"<p><strong>Source:</strong> {article.source_name}</p>",
                f"<p><strong>Published:</strong> {published_date_str}</p>",
            ]
            
            if article.complexity_level:
                post_body_parts.append(f"<p><strong>Complexity:</strong> {article.get_complexity_level_display()}</p>")
            
            if article.reading_time_minutes:
                post_body_parts.append(f"<p><strong>Reading Time:</strong> {article.reading_time_minutes} minutes</p>")
                
            post_body_parts.extend([
                f"<br><p><strong>Summary:</strong></p>",
                f"<p>{article.summary}</p><br>",
            ])
            
            if user_comment:
                post_body_parts.extend([
                    f"<p><strong>💭 {request.user.get_full_name() or request.user.username} says:</strong></p>",
                    f"<p><em>{user_comment}</em></p><br>",
                ])
                
            post_body_parts.append(
                f"<p><a href='{article.original_url}' target='_blank' class='btn btn-primary'>📖 Read Full Article</a></p>"
            )

            post_body = "".join(post_body_parts)

            # Create the initial post in the thread.
            CommunityPost.objects.create(
                thread=thread,
                author=request.user,
                body=post_body
            )

            messages.success(request, f"Article shared to The Commons! Discussion started.")
            # Redirect to the new thread's detail page.
            return redirect('community:thread_detail', slug=thread.slug)
    else:
        form = ShareToCommonsForm()

    return render(request, 'blog/share_to_commons.html', {
        'article': article, 
        'form': form
    })

# Add these to the end of apps/blog/views.py

def quick_post_detail(request, slug):
    """
    Display details for a quick post (Post model).
    """
    post = get_object_or_404(Post, slug=slug, published=True)

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
            messages.success(request, "Comment added successfully!")
            
        elif reaction:
            # Check if user already reacted with this reaction
            existing_reaction = Reaction.objects.filter(
                user=request.user,
                content_type=ContentType.objects.get_for_model(post),
                object_id=post.id,
                reaction=reaction
            ).first()
            
            if existing_reaction:
                existing_reaction.delete()
                messages.info(request, "Reaction removed!")
            else:
                # Remove any other reactions from this user, then add new one
                Reaction.objects.filter(
                    user=request.user,
                    content_type=ContentType.objects.get_for_model(post),
                    object_id=post.id
                ).delete()
                
                Reaction.objects.create(
                    user=request.user,
                    content_type=ContentType.objects.get_for_model(post),
                    object_id=post.id,
                    reaction=reaction
                )
                messages.success(request, "Reaction added!")
                
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
    
    # Get user's current reaction if logged in
    user_reaction = None
    if request.user.is_authenticated:
        user_reaction_obj = Reaction.objects.filter(
            user=request.user,
            content_type=ContentType.objects.get_for_model(post),
            object_id=post.id
        ).first()
        if user_reaction_obj:
            user_reaction = user_reaction_obj.reaction

    context = {
        'post': post,
        'comments': comments,
        'reaction_count': reaction_count,
        'user_reaction': user_reaction,
        'REACTION_CHOICES': REACTION_CHOICES,
        'post_type': 'quick',
    }
    return render(request, 'blog/quick_detail.html', context)

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

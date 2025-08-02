from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.contenttypes.models import ContentType
from .models import Board, Thread, Post
from apps.analytics.models import Event

@staff_member_required
def create_board(request):
    if request.method == 'POST':
        name = request.POST.get("name")
        description = request.POST.get("description")

        if name and description:
            Board.objects.create(name=name, description=description)
            return redirect('community:board_index')

    return render(request, "community/create_board.html")

def board_index(request):
    boards = Board.objects.all()
    return render(request, "community/board_index.html", {'boards': boards})

def board_detail(request, slug):
    board = get_object_or_404(Board, slug=slug)
    threads = board.threads.all()

    if request.user.is_authenticated:
        Event.objects.create(
            user=request.user,
            event_type='page_view',
            path=request.path,
            meta={'board': board.name}
        )

    return render(request, "community/board_detail.html", {'board': board, 'threads': threads})

def thread_detail(request, slug):
    thread = get_object_or_404(Thread, slug=slug)
    posts = thread.posts.all()

    if request.user.is_authenticated:
        Event.objects.create(
            user=request.user,
            event_type='page_view',
            path=request.path,
            meta={'thread': thread.title, 'board': thread.board.title}
        )

    return render(request, "community/thread_detail.html", {'thread': thread, 'posts': posts})

@login_required
def post_reply(request, slug):
    thread = get_object_or_404(Thread, slug=slug)
    if request.method == "POST":
        body = request.POST.get("body")
        if body:
            Post.objects.create(thread=thread, author=request.user, body=body)

            Event.objects.create(
                user=request.user,
                event_type='post_reply',
                path=request.path,
                meta={
                    'thread': thread.title,
                    'board': thread.board.title
                }
            )

        return redirect("community:thread_detail", slug=slug)

@login_required
def create_thread(request, board_slug):
    board = get_object_or_404(Board, slug=board_slug)

    if request.method == "POST":
        title = request.POST.get("title")
        body = request.POST.get("body")

        if title and body:
            thread = Thread.objects.create(
                board=board,
                title=title,
                author=request.user
            )
            Post.objects.create(
                thread=thread,
                author=request.user,
                body=body
            )
            return redirect("community:thread_detail", slug=thread.slug)

    return render(request, "community/create_thread.html", {'board': board})

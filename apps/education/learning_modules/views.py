from django.shortcuts import render

def module_detail(request, pk):
    return render(request, "learning_modules/module_detail.html", {"module_id": pk})

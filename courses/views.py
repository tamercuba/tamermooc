from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Course, Enrollment
from .forms import ContactCourse
from django.contrib import messages

def index(request):
    courses = Course.objects.all()
    template_name = 'courses/index.html'
    context = {
        'courses':courses
    }
    return render(request, template_name, context)


def details(request, slug):

    course = get_object_or_404(Course, slug=slug)
    template_name = 'courses/details.html'
    context = {}
    if request.method == 'POST':
        form = ContactCourse(request.POST)
        if form.is_valid():
            context['is_valid']= True
            form.send_mail(course)
            #print(form.cleaned_data['name'])
            #print(form.cleaned_data['email'])
            #print(form.cleaned_data['message'])
            form = ContactCourse()
    else:
        form = ContactCourse()
    context['course']=course
    context['form']=form
    return render(request, template_name, context)


@login_required
def enrollment(request, slug):
    course              = get_object_or_404(Course, slug=slug)
    enrollment, created = Enrollment.objects.get_or_create(
        user=request.user, course=course
    )
    if created:
        enrollment.active()
        messages.success(request, 'Você foi inscrito no curso com sucesso')
    else:
        messages.info(request, 'Você já está inscrito no curso')

    return redirect('accounts:dashboard')

@login_required
def undo_enrollment(request, slug):
    course     = get_object_or_404(Course, slug=slug)
    enrollment = get_object_or_404(
        Enrollment, user=request.user, course=course
    )
    if request.method == 'POST':
        enrollment.delete()
        messages.success(request, "Inscrição cancelada com suceeso!")
        return redirect('accounts:dashboard')
    template = 'courses/undo_enrollment.html'
    context = {
        'enrollment': enrollment,
        'course': course,
    }
    return render(request, template, context)


@login_required
def announcements(request, slug):
    course         = get_object_or_404(Course, slug=slug)
    if not request.user.is_staff:
        enrollment = get_object_or_404(
            Enrollment, user=request.user, course=course
        )
        if not enrollment.is_approved():
            messages.error(request, 'A sua inscrição está pendente')
            return redirect('accounts:dashboard')
    template = 'courses/announcements.html'
    context = {
        'course': course
    }
    return render(request, template, context)

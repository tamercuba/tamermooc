from django.db       import models
from django.urls     import reverse
from django.conf     import settings
from django.utils    import timezone
from core.mail       import send_mail_template
from django.dispatch import receiver

class CourseManager(models.Manager):
    def search(self, query):                                                        #essa função search do custom manager busca query no nome OU na descriçao
        return self.get_queryset().filter(
            models.Q(name__icontains=query) | \
            models.Q(description__icontains = query)
        )

class Course(models.Model):
    name          = models.CharField('Nome', max_length = 100)
    slug          = models.SlugField('Atalho')
    about         = models.CharField('Descrição breve', blank = True, max_length = 250)
    description   = models.TextField('Descrição completa', blank = True)
    start_date    = models.DateField(
        'Data de Início', null = True, blank = True
    )                                                                           #blank = True diz que não é obrigatório preender
                                                                               #null = True diz que a nivel de banco de dados ele pode ser do tipo null
    image         = models.ImageField(
        upload_to = 'courses/images', verbose_name = 'Imagem', null = True, blank = True
    )
    created_at    = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at    = models.DateTimeField('Atualizado em', auto_now=True)
    objects       = CourseManager()

    def __str__(self):
        return(self.name)



    def get_absolute_url(self):
        return reverse('courses:details', kwargs={'slug': self.slug})

    def release_lessons(self):
        today = timezone.now().date()
        return self.lessons.filter(release_date__gte=today)

    class Meta:
        verbose_name        = 'Curso'
        verbose_name_plural = 'Cursos'
        ordering            = ['name']

class Lesson(models.Model):
    name         = models.CharField('Nome', max_length=100)
    description  = models.TextField('Descrição', blank = True)
    number       = models.IntegerField('Número da aula', blank = True, default = 0)
    release_date = models.DateField('Data de liberação', blank=True, null=True)
    course       = models.ForeignKey(Course, verbose_name='Curso', related_name='lessons', on_delete=models.NOT_PROVIDED)

    created_at   = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at   = models.DateTimeField('Atualizado em', auto_now=True)

    def __str__(self):
        return self.name

    def is_available(self):
        if self.release_date:
            today = timezone.now().date()
            return self.release_date >= today
        return False

    class Meta:
        verbose_name        = 'Aula'
        verbose_name_plural = 'Aulas'
        ordering            = ['number']

class Material(models.Model):
    name     = models.CharField('Nome', max_length=100)
    embedded = models.TextField('Conteúdo em mídia', blank=True)
    file     = models.FileField(upload_to='lessons/materials', blank=True, null=True)
    lesson   = models.ForeignKey(Lesson, verbose_name='Aula',related_name='materials', on_delete=models.NOT_PROVIDED)

    def is_embedded(self):
        return bool(self.embedded)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name        = 'Material'
        verbose_name_plural = 'Materiais'


class Enrollment(models.Model):
    STATUS_CHOICE = (
        (0, 'Pendente'), (1, 'Aprovado'), (2, 'Cancelado'),
    )

    user          = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name='Usuário', related_name='enrollments', on_delete=models.NOT_PROVIDED
    )
    course        = models.ForeignKey(
        Course, verbose_name='Curso', related_name='enrollments', on_delete=models.NOT_PROVIDED
    )
    status        = models.IntegerField(
        'Situação', choices=STATUS_CHOICE, default=0, blank=True
    )

    created_at    = models.DateTimeField('Criado em', auto_now_add=True)
    apdated_at    = models.DateTimeField('Atualizado em', auto_now = True)

    def __str__(self):
        return self.user

    def active(self):
        self.status = 1
        self.save()

    def is_approved(self):
        return self.status == 1

    class Meta:
        verbose_name        = 'Inscrição'
        verbose_name_plural = 'Inscrições'
        unique_together     = (('user', 'course'),)

class Announcement(models.Model):
    course  = models.ForeignKey(Course, verbose_name='Curso', related_name='announcements' ,on_delete=models.NOT_PROVIDED)
    title   = models.CharField('Título', max_length=100)
    content = models.TextField('Conteúdo')

    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name        = 'Anúncio'
        verbose_name_plural = 'Anúncios'
        ordering            = ['-created_at']



class Comment(models.Model):
    announcement = models.ForeignKey(
        Announcement, verbose_name='Anúnciio', related_name='comments',on_delete=models.NOT_PROVIDED
    )
    user         = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Usuário',on_delete=models.NOT_PROVIDED)
    comment      = models.TextField('Comentário')


    created_at  = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at  = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name        = 'Comentário'
        verbose_name_plural = 'Comentários'
        ordering            = ['created_at']


    def __str__(self):
        return self.user

    @receiver(models.signals.post_save, sender=Announcement)
    def post_save_announcement(instance, created,**kwargs):
        if created:
            template_name = 'courses/announcement_mail.html'
            subject = instance.title
            context = {'announcement': instance}

            enrollments = Enrollment.objects.filter(course=instance.course, status=1)
            for enrollment in enrollments:
                recipient_list = [enrollment.user.email]
                send_mail_template(subject, template_name, context, recipient_list)

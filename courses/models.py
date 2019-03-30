from django.db import models

class CourseManager(models.Manager):
    def search(self, query):                                                        #essa função search do custom manager busca query no nome OU na descriçao
        return self.get_queryset().filter(
            models.Q(name__icontains=query) | \
            models.Q(description__icontains = query)
        )                               

class Course(models.Model):
    name = models.CharField('Nome', max_length = 100)
    slug = models.SlugField('Atalho')
    description = models.TextField('Descrição', blank = True)
    start_date = models.DateField(
        'Data de Início', null = True, blank = True
    )                                                                           #blank = True diz que não é obrigatório preender
                                                                               #null = True diz que a nivel de banco de dados ele pode ser do tipo null
    image = models.ImageField(
        upload_to = 'courses/images', verbose_name = 'Imagem', null = True, blank = True
    )
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)
    objects = CourseManager()

    def __str__(self):
        return(self.name)

    class Meta:
        verbose_name = 'Curso'
        verbose_name_plural = 'Cursos'
        ordering = ['name']
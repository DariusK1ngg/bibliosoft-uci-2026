from django.shortcuts import render
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from biblioteca.models import Material, Genero, Autor, Carrera, Facultad, Editorial, ConfiguracionGeneral

def index(request):
    config = ConfiguracionGeneral.get_solo()
    return render(request, 'landing/index.html', {'config': config})

def contacto(request):
    config = ConfiguracionGeneral.get_solo()
    return render(request, 'landing/contacto.html', {'config': config})

def catalogo(request):
    query = request.GET.get('q', '')
    genero_id = request.GET.get('genero', '')
    autor_id = request.GET.get('autor', '')
    carrera_id = request.GET.get('carrera', '')
    facultad_id = request.GET.get('facultad', '')
    editorial_id = request.GET.get('editorial', '')
    solo_disponibles = request.GET.get('disponible', '')
    orden = request.GET.get('orden', '')
    tipo_registro = request.GET.get('tipo_registro', '')

    materiales = Material.objects.all().select_related(
        'editoriales_id_editorial',
        'categorias_id_categoria',
        'tipodocumento_id_tipo'
    ).prefetch_related('autores_id_autor', 'generos', 'carreras')

    if query:
        materiales = materiales.filter(
            Q(titulo__icontains=query) |
            Q(autores_id_autor__nombre__icontains=query) |
            Q(autores_id_autor__apellido__icontains=query) |
            Q(isbn__icontains=query) |
            Q(editoriales_id_editorial__nombre__icontains=query)
        )

    if genero_id:
        materiales = materiales.filter(generos=genero_id)

    if autor_id:
        materiales = materiales.filter(autores_id_autor=autor_id)

    if carrera_id:
        materiales = materiales.filter(carreras=carrera_id)

    if facultad_id:
        materiales = materiales.filter(carreras__facultades_id_facultad=facultad_id)

    if editorial_id:
        materiales = materiales.filter(editoriales_id_editorial=editorial_id)

    if tipo_registro:
        materiales = materiales.filter(tipo_registro=tipo_registro)

    if solo_disponibles == '1':
        materiales = materiales.filter(cantidad_disponible__gt=0)

    # Ordenamiento
    if orden == 'reciente':
        materiales = materiales.order_by('-año_publicacion', '-id_material')
    elif orden == 'antiguo':
        materiales = materiales.order_by('año_publicacion', '-id_material')
    elif orden == 'agregado':
        materiales = materiales.order_by('-id_material')
    else:
        materiales = materiales.order_by('-id_material')

    # Pagination
    paginator = Paginator(materiales.distinct(), 12)  # Show 12 materials per page
    page = request.GET.get('page', 1)
    try:
        materiales_paginados = paginator.page(page)
    except PageNotAnInteger:
        materiales_paginados = paginator.page(1)
    except EmptyPage:
        materiales_paginados = paginator.page(paginator.num_pages)

    # Fetch choices for filtering dropdowns
    generos = Genero.objects.all()
    autores = Autor.objects.all()
    facultades = Facultad.objects.all()
    editoriales = Editorial.objects.all()

    if facultad_id:
        carreras = Carrera.objects.filter(facultades_id_facultad=facultad_id)
        if carrera_id and not carreras.filter(id_carrera=carrera_id).exists():
            carrera_id = ''
    else:
        carreras = Carrera.objects.all()

    context = {
        'materiales': materiales_paginados,
        'generos': generos,
        'autores': autores,
        'carreras': carreras,
        'facultades': facultades,
        'editoriales': editoriales,
        'query': query,
        'selected_genero': int(genero_id) if genero_id.isdigit() else None,
        'selected_autor': int(autor_id) if autor_id.isdigit() else None,
        'selected_carrera': int(carrera_id) if carrera_id and carrera_id.isdigit() else None,
        'selected_facultad': int(facultad_id) if facultad_id.isdigit() else None,
        'selected_editorial': int(editorial_id) if editorial_id.isdigit() else None,
        'selected_tipo_registro': tipo_registro,
        'solo_disponibles': solo_disponibles == '1',
        'selected_orden': orden,
    }
    return render(request, 'landing/catalogo.html', context)


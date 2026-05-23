from django.shortcuts import render
from django.db.models import Q
from biblioteca.models import Material, Categoria, Autor, TipoDocumento

def index(request):
    return render(request, 'landing/index.html')

def contacto(request):
    return render(request, 'landing/contacto.html')

def catalogo(request):
    query = request.GET.get('q', '')
    categoria_id = request.GET.get('categoria', '')
    autor_id = request.GET.get('autor', '')
    tipo_id = request.GET.get('tipo', '')
    solo_disponibles = request.GET.get('disponible', '')

    materiales = Material.objects.all().select_related(
        'editoriales_id_editorial',
        'categorias_id_categoria',
        'tipodocumento_id_tipo'
    ).prefetch_related('autores_id_autor')

    if query:
        materiales = materiales.filter(
            Q(titulo__icontains=query) |
            Q(autores_id_autor__nombre__icontains=query) |
            Q(autores_id_autor__apellido__icontains=query) |
            Q(isbn__icontains=query) |
            Q(editoriales_id_editorial__nombre__icontains=query)
        )

    if categoria_id:
        materiales = materiales.filter(categorias_id_categoria=categoria_id)

    if autor_id:
        materiales = materiales.filter(autores_id_autor=autor_id)

    if tipo_id:
        materiales = materiales.filter(tipodocumento_id_tipo=tipo_id)

    if solo_disponibles == '1':
        materiales = materiales.filter(cantidad_disponible__gt=0)

    # Fetch choices for filtering dropdowns
    categorias = Categoria.objects.all()
    autores = Autor.objects.all()
    tipos = TipoDocumento.objects.all()

    context = {
        'materiales': materiales,
        'categorias': categorias,
        'autores': autores,
        'tipos': tipos,
        'query': query,
        'selected_categoria': int(categoria_id) if categoria_id.isdigit() else None,
        'selected_autor': int(autor_id) if autor_id.isdigit() else None,
        'selected_tipo': int(tipo_id) if tipo_id.isdigit() else None,
        'solo_disponibles': solo_disponibles == '1',
    }
    return render(request, 'landing/catalogo.html', context)


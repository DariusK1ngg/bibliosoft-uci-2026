import contextvars
from django.contrib.auth.models import User

_current_user = contextvars.ContextVar('current_user', default=None)
_current_ip = contextvars.ContextVar('current_ip', default=None)

def get_current_user():
    try:
        return _current_user.get()
    except LookupError:
        return None

def get_current_ip():
    try:
        return _current_ip.get()
    except LookupError:
        return None

def set_current_user(user):
    return _current_user.set(user)

def set_current_ip(ip):
    return _current_ip.set(ip)

def registrar_auditoria(accion, tabla, registro_id, detalle, user=None, ip=None):
    from .models import RegistroAuditoria
    
    if user is None:
        user = get_current_user()
    if ip is None:
        ip = get_current_ip()
        
    # Handle lazy user object
    if user and user.is_anonymous:
        user = None
        
    # Double-check that user is an actual User instance or None
    if user and not isinstance(user, User):
        # Could be SimpleLazyObject, try to get actual user ID
        try:
            user = User.objects.get(pk=user.pk)
        except Exception:
            user = None

    RegistroAuditoria.objects.create(
        usuario=user,
        accion=accion,
        tabla=tabla,
        registro_id=str(registro_id) if registro_id else '',
        detalle=detalle,
        ip_address=ip or '127.0.0.1'
    )

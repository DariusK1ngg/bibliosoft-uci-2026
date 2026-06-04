from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in, user_logged_out

from .models import (
    Autor, Editorial, Categoria, Genero, TipoDocumento, Facultad, Carrera,
    Alumno, Material, Prestamo, BajaMaterial
)
from .utils import registrar_auditoria

# List of models we want to track for audit
AUDITED_MODELS = (
    Autor, Editorial, Categoria, Genero, TipoDocumento, Facultad, Carrera,
    Alumno, Material, Prestamo, BajaMaterial, User
)

@receiver(pre_save)
def auditar_pre_save_general(sender, instance, **kwargs):
    if sender in AUDITED_MODELS and instance.pk:
        # 1. Special check for User skip audit (last_login only change)
        if sender == User:
            try:
                old_user = User.objects.get(pk=instance.pk)
                fields_to_check = ['username', 'email', 'password', 'first_name', 'last_name', 'is_active', 'is_staff', 'is_superuser']
                is_modified = False
                for field in fields_to_check:
                    if getattr(old_user, field) != getattr(instance, field):
                        is_modified = True
                        break
                if not is_modified:
                    instance._skip_audit = True
                    return
            except User.DoesNotExist:
                pass

        # 2. Custom checks for Alumno carnet active/inactive flags
        if sender == Alumno:
            try:
                old_obj = Alumno.objects.get(pk=instance.pk)
                if not old_obj.carnet_activo and instance.carnet_activo:
                    instance._audit_action = 'ACTIVACION_CARNET'
                elif old_obj.carnet_activo and not instance.carnet_activo:
                    instance._audit_action = 'DESACTIVACION_CARNET'
            except Alumno.DoesNotExist:
                pass

        # 3. General field diff tracking
        try:
            old_instance = sender.objects.get(pk=instance.pk)
            fields = [f.name for f in sender._meta.get_fields() if not f.many_to_many and not f.one_to_many and f.concrete]
            changes = []
            for field_name in fields:
                old_val = getattr(old_instance, field_name)
                new_val = getattr(instance, field_name)
                
                if old_val != new_val:
                    try:
                        field_obj = sender._meta.get_field(field_name)
                        verbose_name = getattr(field_obj, 'verbose_name', field_name) or field_name
                    except Exception:
                        verbose_name = field_name
                    
                    old_str = str(old_val) if old_val is not None else "Vacío"
                    new_str = str(new_val) if new_val is not None else "Vacío"
                    
                    if 'password' in field_name:
                        old_str = "********"
                        new_str = "********"
                        
                    changes.append(f"{verbose_name}: '{old_str}' -> '{new_str}'")
                    
            if changes:
                instance._changed_fields_summary = "; ".join(changes)
        except Exception:
            pass

@receiver(post_save)
def auditar_guardado(sender, instance, created, **kwargs):
    if getattr(instance, '_skip_audit', False):
        return
        
    if sender in AUDITED_MODELS:
        accion = getattr(instance, '_audit_action', 'CREACION' if created else 'MODIFICACION')
        if getattr(instance, '_audit_prorroga', False):
            accion = 'PRORROGA'

        tabla = sender._meta.verbose_name
        registro_id = instance.pk
        cambios = getattr(instance, '_changed_fields_summary', '')

        # Construct highly detailed descriptions based on model type
        if sender == Prestamo:
            if accion == 'PRORROGA':
                detalle = (
                    f"Se concedió una prórroga para el préstamo #{instance.pk}. "
                    f"El alumno {instance.ALUMNOS_id_alumno.nombre} {instance.ALUMNOS_id_alumno.apellido} "
                    f"(Cédula: {instance.ALUMNOS_id_alumno.matricula}) ahora tiene plazo hasta el "
                    f"{instance.fecha_vencimiento.strftime('%d/%m/%Y')} para devolver el material "
                    f"'{instance.MATERIALES_id_material.titulo}'."
                )
            elif created:
                detalle = (
                    f"Se registró un nuevo préstamo físico (ID: #{instance.pk}). "
                    f"El alumno {instance.ALUMNOS_id_alumno.nombre} {instance.ALUMNOS_id_alumno.apellido} "
                    f"(Cédula: {instance.ALUMNOS_id_alumno.matricula}) retiró 1 ejemplar "
                    f"del material '{instance.MATERIALES_id_material.titulo}' (N° Entrada: {instance.numero_entrada or 'N/A'}). "
                    f"Vencimiento pactado para el {instance.fecha_vencimiento.strftime('%d/%m/%Y')}."
                )
            else:
                if instance.estado == 'DEVUELTO':
                    detalle = (
                        f"Se registró la devolución del material para el préstamo #{instance.pk}. "
                        f"Alumno: {instance.ALUMNOS_id_alumno.nombre} {instance.ALUMNOS_id_alumno.apellido}. "
                        f"Material devuelto: '{instance.MATERIALES_id_material.titulo}'. "
                        f"Estado de entrega: {instance.get_estado_material_display() if hasattr(instance, 'get_estado_material_display') else instance.estado_material}. "
                        f"Multa calculada: {instance.multa} Gs. (Pago multa: {'SÍ' if instance.pago_multa else 'NO/No aplica'}). "
                        f"Observaciones: {instance.observaciones_devolucion or 'Ninguna'}."
                    )
                else:
                    detalle = (
                        f"Se modificaron los datos del préstamo #{instance.pk} de '{instance.ALUMNOS_id_alumno}'. "
                        f"Cambios: {cambios or 'Ninguno'}."
                    )
        elif sender == BajaMaterial:
            if created:
                detalle = (
                    f"Se dio de baja {instance.cantidad} copia(s) del material '{instance.material.titulo}' "
                    f"(N° Entrada: {instance.numero_entrada or 'N/A'}). Motivo de la baja: {instance.get_motivo_display()}. "
                    f"Observaciones: {instance.observaciones or 'Ninguna'}."
                )
            else:
                detalle = (
                    f"Se modificó la baja de material #{instance.pk} de '{instance.material.titulo}'. "
                    f"Cambios: {cambios or 'Ninguno'}."
                )
        elif sender == Alumno:
            if accion == 'ACTIVACION_CARNET':
                detalle = (
                    f"Se procedió a la activación del carnet de biblioteca para el alumno "
                    f"{instance.nombre} {instance.apellido} (Cédula: {instance.matricula}). "
                    f"Fecha de entrega registrada: {instance.carnet_fecha_entrega.strftime('%d/%m/%Y') if instance.carnet_fecha_entrega else 'N/A'}."
                )
            elif accion == 'DESACTIVACION_CARNET':
                detalle = (
                    f"Se desactivó/retiró el carnet de biblioteca del alumno "
                    f"{instance.nombre} {instance.apellido} (Cédula: {instance.matricula})."
                )
            elif created:
                detalle = (
                    f"Se registró un nuevo alumno en el sistema: {instance.nombre} {instance.apellido} "
                    f"(Cédula: {instance.matricula}). Email: {instance.email}. Teléfono: {instance.telefono}. "
                    f"Carrera: {instance.carreras_id_carrera.nombre}."
                )
            else:
                detalle = (
                    f"Se modificaron los campos del alumno '{instance.nombre} {instance.apellido}' (Cédula: {instance.matricula}). "
                    f"Cambios: {cambios or 'Ninguno'}."
                )
        elif sender == Material:
            if created:
                detalle = (
                    f"Se añadió un nuevo material bibliográfico titulado '{instance.titulo}' "
                    f"(Tipo de registro: {instance.get_tipo_registro_display()}). Dewey: {instance.numeracion_dewey or 'N/A'}. "
                    f"N° Entrada: {instance.numero_entrada or 'N/A'}. Año: {instance.año_publicacion or 'N/A'}. "
                    f"Stock inicial total: {instance.cantidad_total}."
                )
            else:
                detalle = (
                    f"Se modificaron los datos del material '{instance.titulo}' ({instance.get_tipo_registro_display()}). "
                    f"Cambios: {cambios or 'Ninguno'}."
                )
        elif sender == User:
            if created:
                detalle = (
                    f"Se creó un nuevo usuario para administración del sistema: '{instance.username}'. "
                    f"Nombre completo: {instance.get_full_name() or 'N/A'}. Email: {instance.email or 'N/A'}. "
                    f"Permisos de staff: {'SÍ' if instance.is_staff else 'NO'}."
                )
            else:
                detalle = (
                    f"Se actualizó la cuenta del usuario '{instance.username}'. "
                    f"Cambios: {cambios or 'Ninguno'}."
                )
        elif sender == Autor:
            if created:
                detalle = f"Se añadió el autor '{instance.nombre} {instance.apellido}' al catálogo del sistema."
            else:
                detalle = f"Se modificaron los datos del autor '{instance.nombre} {instance.apellido}'. Cambios: {cambios or 'Ninguno'}."
        elif sender == Editorial:
            if created:
                detalle = f"Se registró la editorial '{instance.nombre}' (Dirección: {instance.direccion}, Teléfono: {instance.telefono})."
            else:
                detalle = f"Se modificaron los datos de la editorial '{instance.nombre}'. Cambios: {cambios or 'Ninguno'}."
        elif sender == Categoria:
            if created:
                detalle = f"Se creó la categoría temática '{instance.nombre}' (Descripción: {instance.descripcion})."
            else:
                detalle = f"Se modificaron los datos de la categoría '{instance.nombre}'. Cambios: {cambios or 'Ninguno'}."
        elif sender == Carrera:
            if created:
                detalle = f"Se creó la carrera '{instance.nombre}' asociada a la Facultad: '{instance.facultades_id_facultad.nombre}'."
            else:
                detalle = f"Se modificó la carrera '{instance.nombre}' (Facultad: '{instance.facultades_id_facultad.nombre}')."
        else:
            accion_str = "creado/registrado" if created else "modificado"
            detalle = f"Se ha {accion_str} el elemento '{instance}' de la tabla {tabla}."

        registrar_auditoria(accion, tabla, registro_id, detalle)

@receiver(post_delete)
def auditar_eliminacion(sender, instance, **kwargs):
    if sender in AUDITED_MODELS:
        accion = 'ELIMINACION'
        tabla = sender._meta.verbose_name
        registro_id = instance.pk
        
        if sender == Prestamo:
            detalle = (
                f"Se eliminó permanentemente el registro de préstamo #{instance.pk}. "
                f"Alumno asociado: {instance.ALUMNOS_id_alumno.nombre} {instance.ALUMNOS_id_alumno.apellido} "
                f"(Matrícula: {instance.ALUMNOS_id_alumno.matricula}). "
                f"Material prestado: '{instance.MATERIALES_id_material.titulo}'."
            )
        elif sender == Alumno:
            detalle = (
                f"Se eliminó permanentemente el alumno: {instance.nombre} {instance.apellido} "
                f"(Cédula: {instance.matricula}) y su historial académico asociado."
            )
        elif sender == Material:
            detalle = (
                f"Se eliminó permanentemente del catálogo el material bibliográfico: '{instance.titulo}' "
                f"({instance.get_tipo_registro_display()})."
            )
        elif sender == User:
            detalle = f"Se eliminó la cuenta del usuario de administración: '{instance.username}'."
        else:
            detalle = f"Se eliminó de forma definitiva el registro de {tabla.lower()}: '{instance}'."

        registrar_auditoria(accion, tabla, registro_id, detalle)

@receiver(user_logged_in)
def auditar_login(sender, request, user, **kwargs):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    registrar_auditoria('INICIO_SESION', 'Autenticación', user.pk, f"El usuario administrativo '{user.username}' inició sesión en el panel del sistema.", user=user, ip=ip)

@receiver(user_logged_out)
def auditar_logout(sender, request, user, **kwargs):
    if user:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        registrar_auditoria('CERRAR_SESION', 'Autenticación', user.pk, f"El usuario administrativo '{user.username}' cerró sesión y abandonó el panel del sistema.", user=user, ip=ip)

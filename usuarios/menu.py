MENU_POR_ROL = {

    "Administrador": [
        ("Dashboard", "dashboard"),

        ("Usuarios", "usuarios_lista"),

        ("Pagos", "pagos:escanear_pago"),
        ("Tarifas", "pagos:tarifa_lista"),
        ("Productos", "pagos:producto_lista"),

        ("Caja", "reportes:reporte_caja"),
        ("Corte", "reportes:corte_caja"),
        ("Mensual", "reportes:reporte_mensual"),
        ("Por sede", "reportes:reporte_sede"),
        ("Gráfica", "reportes:grafica_ingresos"),
        ("Auditoría", "reportes:historial_lista"),
        ("Online", "reportes:usuarios_en_linea"),

        ("Asignaciones", "asignaciones:dashboard"),
        ("Carriles", "asignaciones:carril_lista"),
        ("Horarios", "asignaciones:horario_lista"),
        ("Inscripciones", "asignaciones:inscripcion_lista"),

        ("Calendario", "calendario:calendario_lista"),

        ("Evaluaciones", "evaluaciones:panel_admin"),

        ("Historial médico", "medico:historial_general"),

        ("Accesos", "accesos:historial"),
    ],

    "Caja": [
        ("Dashboard", "dashboard"),

        ("Cobrar", "pagos:escanear_pago"),
        ("Productos", "pagos:producto_lista"),

        ("Caja", "reportes:reporte_caja"),
        ("Corte", "reportes:corte_caja"),
    ],

    "Recepcion": [
        ("Dashboard", "dashboard"),

        ("Escanear acceso", "accesos:escanear"),
        ("Historial", "accesos:historial"),

        ("Pre-registro", "preregistro:crear"),

        ("Recuperaciones", "calendario:recepcion_recuperacion"),
    ],

    "Medico": [
        ("Dashboard", "dashboard"),

        ("Escanear", "medico:escanear"),
        ("Historial", "medico:historial_general"),
    ],

    "Maestro": [
        ("Dashboard", "dashboard"),

        ("Evaluaciones", "evaluaciones:panel_maestro"),
        ("Historial", "evaluaciones:historial"),
    ],

    "Coordinador": [
        ("Dashboard", "dashboard"),

        ("Asignaciones", "asignaciones:dashboard"),
        ("Horarios", "asignaciones:horario_lista"),
        ("Inscripciones", "asignaciones:inscripcion_lista"),
        ("Reporte carriles", "asignaciones:reporte"),

        ("Caja", "reportes:reporte_caja"),
        ("Mensual", "reportes:reporte_mensual"),
        ("Sede", "reportes:reporte_sede"),

        ("Calendario", "calendario:calendario_lista"),
    ],
}
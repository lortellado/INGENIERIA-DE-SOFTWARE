graph TD
    %% 
    
    Actores Externos
    
    ViajeroWeb[Viajero Web] -->|HTTPS / REST| Trotamundos
    ViajeroMovil[Viajero Móvil + GPS] -->|HTTPS / REST| Trotamundos
    
    ProveedoresCorreo[Proveedores de Correo] -->|IMAP / APIs| Trotamundos
    
    Trotamundos <-->|APIs Estándar| Terceros[Sistemas de Terceros<br/>Aerolíneas, Hoteles, Autos]
    
    Trotamundos -->|Soporte| Agencia[Agencia de Viajes Preferida]
    
    EquipoDatos[Equipo de Datos] -->|Consultas Analíticas| Trotamundos
    
    RedesSociales[Redes Sociales] -.->|Compartir Itinerarios| Trotamundos
    
    Invitados[Usuarios Invitados] -->|Ver Itinerarios| Trotamundos

    subgraph Sistema Trotamundos
        Trotamundos[Panel de Gestión de Viajes]
    end

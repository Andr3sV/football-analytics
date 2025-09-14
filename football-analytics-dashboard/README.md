# Football Analytics Dashboard

Una aplicación moderna de analítica de fútbol construida con Next.js, que proporciona insights comprehensivos sobre el desarrollo de jugadores y datos de academias juveniles.

## 🚀 Características

- **Dashboard Principal**: Métricas clave y visualización de datos
- **Base de Datos de Jugadores**: Tabla completa con búsqueda y filtros
- **Diseño Moderno**: Inspirado en Linear con modo oscuro
- **Sidebar Colapsable**: Navegación eficiente estilo Linear
- **Responsive**: Optimizado para desktop y móvil
- **Paginación**: Manejo eficiente de grandes conjuntos de datos

## 🛠️ Tecnologías Utilizadas

- **Next.js 15** - Framework React
- **TypeScript** - Tipado estático
- **Tailwind CSS** - Estilos utilitarios
- **shadcn/ui** - Componentes UI
- **Lucide React** - Iconos
- **Papa Parse** - Procesamiento de CSV

## 📊 Datos

La aplicación procesa datos de la base de datos `db_football_training_clubs.csv` que incluye:

- Información de jugadores (25,000+ registros)
- Clubes actuales y juveniles
- Valores de mercado
- Nacionalidades y posiciones
- Fechas de transferencia

## 🚀 Desarrollo Local

1. **Instalar dependencias**:

   ```bash
   npm install
   ```

2. **Ejecutar en desarrollo** (puerto 3090):

   ```bash
   npm run dev
   ```

3. **Construir para producción**:
   ```bash
   npm run build
   ```

## 🌐 Despliegue en Vercel

1. **Push a GitHub**:

   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. **Conectar a Vercel**:
   - Ir a [vercel.com](https://vercel.com)
   - Importar el repositorio
   - Configurar automáticamente

## 📁 Estructura del Proyecto

```
src/
├── app/                    # App Router de Next.js
│   ├── page.tsx           # Página principal (Dashboard)
│   ├── players/           # Página de jugadores
│   └── layout.tsx         # Layout principal
├── components/
│   ├── ui/               # Componentes shadcn/ui
│   └── sidebar.tsx       # Sidebar navegación
├── hooks/
│   └── usePlayerData.ts  # Hook para datos de jugadores
└── lib/
    └── utils.ts          # Utilidades
```

## 🎨 Diseño

- **Colores**: Fondo #181822, Texto #E8E8E8
- **Estilo**: Minimalista y futurista
- **Inspiración**: Linear en modo oscuro
- **Componentes**: shadcn/ui customizados

## 📈 Métricas del Dashboard

- **Jugadores Totales**: Conteo total de jugadores
- **Con Clubes Juveniles**: Jugadores con datos de academia
- **Valor de Mercado**: Suma total de valoraciones
- **Países**: Países únicos representados

## 🔍 Funcionalidades de la Tabla

- **Búsqueda**: Por nombre, club actual o club juvenil
- **Filtros**: Por posición
- **Paginación**: 20 jugadores por página
- **Ordenamiento**: Datos organizados eficientemente

## 🤝 Contribuir

1. Fork el proyecto
2. Crear branch para feature (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add AmazingFeature'`)
4. Push al branch (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT.

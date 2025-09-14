"use client"

import { usePlayerData } from '@/hooks/usePlayerData'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Globe, MapPin, ArrowRightLeft, Users, BarChart3, Plane, Building2 } from 'lucide-react'
import { useMemo } from 'react'

// Componente para gráfico de barras verticales futurista
function FuturisticBarChart({ 
  data, 
  title, 
  subtitle,
  color = "primary",
  icon: Icon 
}: {
  data: Array<{ name: string; value: number; percentage: number; ratio?: number }>
  title: string
  subtitle: string
  color?: "primary" | "secondary" | "accent" | "success"
  icon: React.ElementType
}) {
  const maxValue = Math.max(...data.map(d => d.value))
  
  const colorClasses = {
    primary: "from-blue-500 to-purple-600",
    secondary: "from-emerald-500 to-teal-600", 
    accent: "from-orange-500 to-red-600",
    success: "from-green-500 to-emerald-600"
  }

  return (
    <Card className="bg-card border-border hover:bg-card/80 transition-all duration-300 hover:shadow-2xl hover:shadow-primary/10">
      <CardHeader className="pb-4">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-gradient-to-r from-primary/20 to-primary/10">
            <Icon className="h-5 w-5 text-primary" />
          </div>
          <div>
            <CardTitle className="text-xl font-bold bg-gradient-to-r from-foreground to-foreground/80 bg-clip-text text-transparent">
              {title}
            </CardTitle>
            <p className="text-sm text-muted-foreground mt-1">{subtitle}</p>
          </div>
        </div>
      </CardHeader>
      <CardContent className="pt-0">
        <div className="space-y-4">
          {data.map((item, index) => (
            <div key={item.name} className="group">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2 min-w-0 flex-1">
                  <span className="text-xs font-medium text-muted-foreground w-6 text-right">
                    {index + 1}
                  </span>
                  <span className="text-sm font-medium text-foreground truncate">
                    {item.name}
                  </span>
                  {item.ratio && (
                    <span className="text-xs font-bold text-primary bg-primary/10 px-2 py-1 rounded-full">
                      {item.ratio.toFixed(2)}
                    </span>
                  )}
                </div>
                <div className="flex items-center gap-2 ml-3">
                  <span className="text-sm font-bold text-foreground">
                    {item.value.toLocaleString()}
                  </span>
                  <span className="text-xs text-muted-foreground">
                    ({item.percentage.toFixed(1)}%)
                  </span>
                </div>
              </div>
              
              <div className="relative h-8 bg-muted/30 rounded-full overflow-hidden">
                <div 
                  className={`h-full bg-gradient-to-r ${colorClasses[color]} rounded-full transition-all duration-1000 ease-out group-hover:shadow-lg group-hover:shadow-primary/20 relative overflow-hidden`}
                  style={{ 
                    width: `${(item.value / maxValue) * 100}%`,
                    animationDelay: `${index * 100}ms`
                  }}
                >
                  {/* Efecto de brillo animado */}
                  <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent animate-pulse" />
                  
                  {/* Partículas flotantes */}
                  <div className="absolute inset-0">
                    <div className="absolute top-1 left-1/4 w-1 h-1 bg-white/40 rounded-full animate-ping" style={{ animationDelay: `${index * 200}ms` }} />
                    <div className="absolute top-2 right-1/3 w-0.5 h-0.5 bg-white/60 rounded-full animate-ping" style={{ animationDelay: `${index * 300}ms` }} />
                  </div>
                </div>
                
                {/* Efecto de resplandor en hover */}
                <div className="absolute inset-0 bg-gradient-to-r from-primary/0 via-primary/10 to-primary/0 opacity-0 group-hover:opacity-100 transition-opacity duration-300 rounded-full" />
              </div>
            </div>
          ))}
        </div>
        
        {/* Estadísticas adicionales */}
        <div className="mt-6 pt-4 border-t border-border/50">
          <div className="grid grid-cols-3 gap-4 text-center">
            <div className="space-y-1">
              <p className="text-xs text-muted-foreground">Total</p>
              <p className="text-lg font-bold text-foreground">
                {data.reduce((sum, item) => sum + item.value, 0).toLocaleString()}
              </p>
            </div>
            <div className="space-y-1">
              <p className="text-xs text-muted-foreground">Promedio</p>
              <p className="text-lg font-bold text-foreground">
                {Math.round(data.reduce((sum, item) => sum + item.value, 0) / data.length).toLocaleString()}
              </p>
            </div>
            <div className="space-y-1">
              <p className="text-xs text-muted-foreground">Máximo</p>
              <p className="text-lg font-bold text-foreground">
                {maxValue.toLocaleString()}
              </p>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

export default function GeographicPage() {
  const { players, loading, error } = usePlayerData()

  // Talent Migration Patterns
  const talentMigrationPatterns = useMemo(() => {
    if (!players.length) return []
    
    const migrationMap = new Map<string, { from: number; to: number; net: number }>()
    
    players.forEach(player => {
      const nationality = player.nationality
      const youthCountry = player.youth_club_country
      
      if (nationality && youthCountry && nationality !== 'Not found' && youthCountry !== 'Not found') {
        // Jugador que se formó en su país de nacionalidad
        if (nationality === youthCountry) {
          const stats = migrationMap.get(nationality) || { from: 0, to: 0, net: 0 }
          stats.from++
          stats.net++
          migrationMap.set(nationality, stats)
        } else {
          // Jugador que migró
          const fromStats = migrationMap.get(nationality) || { from: 0, to: 0, net: 0 }
          fromStats.from++
          fromStats.net--
          migrationMap.set(nationality, fromStats)
          
          const toStats = migrationMap.get(youthCountry) || { from: 0, to: 0, net: 0 }
          toStats.to++
          toStats.net++
          migrationMap.set(youthCountry, toStats)
        }
      }
    })
    
    const totalPlayers = players.length
    return Array.from(migrationMap.entries())
      .map(([country, stats]) => ({
        name: country.length > 20 ? country.substring(0, 20) + '...' : country,
        value: stats.from + stats.to,
        percentage: ((stats.from + stats.to) / totalPlayers) * 100,
        ratio: stats.to / Math.max(stats.from, 1), // Ratio importación/exportación
        from: stats.from,
        to: stats.to,
        net: stats.net
      }))
      .sort((a, b) => b.value - a.value)
      .slice(0, 10)
  }, [players])

  // Regional Development Centers
  const regionalDevelopmentCenters = useMemo(() => {
    if (!players.length) return []
    
    const regionStats = new Map<string, { players: number; clubs: number; countries: Set<string> }>()
    
    // Mapeo de países a regiones
    const countryToRegion: Record<string, string> = {
      'Brazil': 'South America',
      'Argentina': 'South America',
      'Uruguay': 'South America',
      'Chile': 'South America',
      'Colombia': 'South America',
      'Peru': 'South America',
      'Spain': 'Europe',
      'Germany': 'Europe',
      'France': 'Europe',
      'Italy': 'Europe',
      'England': 'Europe',
      'Netherlands': 'Europe',
      'Portugal': 'Europe',
      'Belgium': 'Europe',
      'Croatia': 'Europe',
      'Serbia': 'Europe',
      'Poland': 'Europe',
      'Czech Republic': 'Europe',
      'Slovakia': 'Europe',
      'Hungary': 'Europe',
      'Romania': 'Europe',
      'Bulgaria': 'Europe',
      'Greece': 'Europe',
      'Turkey': 'Europe',
      'Russia': 'Europe',
      'Ukraine': 'Europe',
      'United States': 'North America',
      'Canada': 'North America',
      'Mexico': 'North America',
      'Japan': 'Asia',
      'South Korea': 'Asia',
      'China': 'Asia',
      'Australia': 'Oceania',
      'Nigeria': 'Africa',
      'Ghana': 'Africa',
      'Senegal': 'Africa',
      'Morocco': 'Africa',
      'Egypt': 'Africa',
      'Algeria': 'Africa',
      'Tunisia': 'Africa',
      'Ivory Coast': 'Africa',
      'Cameroon': 'Africa',
      'South Africa': 'Africa'
    }
    
    players.forEach(player => {
      if (player.youth_club_country && player.youth_club_country !== 'Not found') {
        const region = countryToRegion[player.youth_club_country] || 'Other'
        const stats = regionStats.get(region) || { players: 0, clubs: 0, countries: new Set() }
        
        stats.players++
        if (player.youth_club && player.youth_club !== 'Not found') {
          stats.clubs++
        }
        stats.countries.add(player.youth_club_country)
        
        regionStats.set(region, stats)
      }
    })
    
    const totalPlayers = players.length
    return Array.from(regionStats.entries())
      .map(([region, stats]) => ({
        name: region,
        value: stats.players,
        percentage: (stats.players / totalPlayers) * 100,
        ratio: stats.clubs / stats.countries.size // Clubs por país en la región
      }))
      .sort((a, b) => b.value - a.value)
      .slice(0, 8)
  }, [players])

  // Cross-Border Development
  const crossBorderDevelopment = useMemo(() => {
    if (!players.length) return []
    
    const crossBorderMap = new Map<string, { total: number; crossBorder: number; ratio: number }>()
    
    players.forEach(player => {
      const nationality = player.nationality
      const youthCountry = player.youth_club_country
      
      if (nationality && youthCountry && nationality !== 'Not found' && youthCountry !== 'Not found') {
        const stats = crossBorderMap.get(nationality) || { total: 0, crossBorder: 0, ratio: 0 }
        stats.total++
        
        if (nationality !== youthCountry) {
          stats.crossBorder++
        }
        
        stats.ratio = stats.crossBorder / stats.total
        
        crossBorderMap.set(nationality, stats)
      }
    })
    
    const totalPlayers = players.length
    return Array.from(crossBorderMap.entries())
      .filter(([_, stats]) => stats.total >= 5) // Mínimo 5 jugadores
      .map(([country, stats]) => ({
        name: country.length > 20 ? country.substring(0, 20) + '...' : country,
        value: stats.crossBorder,
        percentage: (stats.crossBorder / totalPlayers) * 100,
        ratio: stats.ratio
      }))
      .sort((a, b) => b.ratio - a.ratio)
      .slice(0, 10)
  }, [players])

  // Talent Export/Import Ratio
  const talentExportImportRatio = useMemo(() => {
    if (!players.length) return []
    
    const countryStats = new Map<string, { exported: number; imported: number; ratio: number }>()
    
    players.forEach(player => {
      const nationality = player.nationality
      const youthCountry = player.youth_club_country
      
      if (nationality && youthCountry && nationality !== 'Not found' && youthCountry !== 'Not found') {
        if (nationality !== youthCountry) {
          // Exportado
          const exportStats = countryStats.get(nationality) || { exported: 0, imported: 0, ratio: 0 }
          exportStats.exported++
          countryStats.set(nationality, exportStats)
          
          // Importado
          const importStats = countryStats.get(youthCountry) || { exported: 0, imported: 0, ratio: 0 }
          importStats.imported++
          countryStats.set(youthCountry, importStats)
        }
      }
    })
    
    // Calcular ratios
    countryStats.forEach((stats, country) => {
      stats.ratio = stats.imported / Math.max(stats.exported, 1)
    })
    
    const totalPlayers = players.length
    return Array.from(countryStats.entries())
      .filter(([_, stats]) => stats.exported + stats.imported >= 3) // Mínimo 3 movimientos
      .map(([country, stats]) => ({
        name: country.length > 20 ? country.substring(0, 20) + '...' : country,
        value: stats.exported + stats.imported,
        percentage: ((stats.exported + stats.imported) / totalPlayers) * 100,
        ratio: stats.ratio
      }))
      .sort((a, b) => b.value - a.value)
      .slice(0, 10)
  }, [players])

  if (error) {
    return (
      <div className="p-8">
        <div className="rounded-lg border border-destructive/50 bg-destructive/10 p-4">
          <p className="text-sm font-medium text-destructive">
            Error loading data: {error}
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="p-8 space-y-8">
      {/* Header */}
      <div className="space-y-2">
        <h1 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-foreground via-primary to-foreground bg-clip-text text-transparent">
          Geographic Analysis
        </h1>
        <p className="text-muted-foreground">
          Advanced insights into talent migration patterns and regional development centers
        </p>
      </div>

      {/* Métricas rápidas */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card className="bg-card border-border hover:bg-card/80 transition-colors">
          <CardContent className="px-4 py-3 flex items-center gap-3">
            <ArrowRightLeft className="flex-shrink-0 h-5 w-5 text-primary" />
            <div>
              <p className="text-sm font-medium text-muted-foreground">Migration Ratio</p>
              <p className="text-lg font-bold text-foreground">
                {loading ? (
                  <div className="h-6 w-20 bg-muted animate-pulse rounded" />
                ) : (
                  talentMigrationPatterns[0]?.ratio.toFixed(2) || '0.00'
                )}
              </p>
            </div>
          </CardContent>
        </Card>
        
        <Card className="bg-card border-border hover:bg-card/80 transition-colors">
          <CardContent className="px-4 py-3 flex items-center gap-3">
            <Building2 className="flex-shrink-0 h-5 w-5 text-emerald-500" />
            <div>
              <p className="text-sm font-medium text-muted-foreground">Development Centers</p>
              <p className="text-lg font-bold text-foreground">
                {loading ? (
                  <div className="h-6 w-20 bg-muted animate-pulse rounded" />
                ) : (
                  regionalDevelopmentCenters.length
                )}
              </p>
            </div>
          </CardContent>
        </Card>
        
        <Card className="bg-card border-border hover:bg-card/80 transition-colors">
          <CardContent className="px-4 py-3 flex items-center gap-3">
            <MapPin className="flex-shrink-0 h-5 w-5 text-orange-500" />
            <div>
              <p className="text-sm font-medium text-muted-foreground">Cross-Border</p>
              <p className="text-lg font-bold text-foreground">
                {loading ? (
                  <div className="h-6 w-20 bg-muted animate-pulse rounded" />
                ) : (
                  `${(crossBorderDevelopment[0]?.ratio * 100).toFixed(1)}%`
                )}
              </p>
            </div>
          </CardContent>
        </Card>
        
        <Card className="bg-card border-border hover:bg-card/80 transition-colors">
          <CardContent className="px-4 py-3 flex items-center gap-3">
            <Plane className="flex-shrink-0 h-5 w-5 text-purple-500" />
            <div>
              <p className="text-sm font-medium text-muted-foreground">Import/Export</p>
              <p className="text-lg font-bold text-foreground">
                {loading ? (
                  <div className="h-6 w-20 bg-muted animate-pulse rounded" />
                ) : (
                  talentExportImportRatio[0]?.ratio.toFixed(2) || '0.00'
                )}
              </p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Gráficos principales */}
      <div className="space-y-8">
        <FuturisticBarChart
          data={talentMigrationPatterns}
          title="Talent Migration Patterns"
          subtitle="Patrones de migración de talento por país"
          color="primary"
          icon={ArrowRightLeft}
        />
        
        <FuturisticBarChart
          data={regionalDevelopmentCenters}
          title="Regional Development Centers"
          subtitle="Centros de desarrollo regional"
          color="secondary"
          icon={Building2}
        />
        
        <FuturisticBarChart
          data={crossBorderDevelopment}
          title="Cross-Border Development"
          subtitle="Desarrollo transfronterizo por país"
          color="accent"
          icon={MapPin}
        />
        
        <FuturisticBarChart
          data={talentExportImportRatio}
          title="Talent Export/Import Ratio"
          subtitle="Ratio de exportación/importación de talento"
          color="success"
          icon={Plane}
        />
      </div>

      {/* Metodología Detallada */}
      <Card className="bg-card border-border">
        <CardHeader>
          <CardTitle className="text-xl font-bold text-foreground">
            📊 Metodología de Cálculo
          </CardTitle>
          <p className="text-sm text-muted-foreground">
            Detalles técnicos de cómo se calculan cada una de las métricas mostradas
          </p>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Talent Migration Patterns */}
          <div className="space-y-3">
            <h3 className="text-lg font-semibold text-foreground">Talent Migration Patterns</h3>
            <div className="bg-muted/30 p-4 rounded-lg">
              <p className="text-sm text-muted-foreground mb-2">
                <strong>Fórmula:</strong> Análisis de patrones de migración de talento
              </p>
              <ul className="text-sm space-y-1 text-muted-foreground">
                <li>• <strong>from</strong> = jugadores que se formaron en su país de nacimiento</li>
                <li>• <strong>to</strong> = jugadores que migraron a otro país para formarse</li>
                <li>• <strong>net</strong> = to - from (balance migratorio)</li>
                <li>• <strong>ratio</strong> = to / max(from, 1) (ratio importación/exportación)</li>
                <li>• <strong>total</strong> = from + to (total de movimientos)</li>
              </ul>
              <p className="text-xs text-muted-foreground mt-2">
                <strong>Columnas utilizadas:</strong> country_of_birth, youth_club_country
              </p>
            </div>
          </div>

          {/* Regional Development Centers */}
          <div className="space-y-3">
            <h3 className="text-lg font-semibold text-foreground">Regional Development Centers</h3>
            <div className="bg-muted/30 p-4 rounded-lg">
              <p className="text-sm text-muted-foreground mb-2">
                <strong>Fórmula:</strong> Análisis de centros de desarrollo regional
              </p>
              <ul className="text-sm space-y-1 text-muted-foreground">
                <li>• <strong>Mapeo de países a regiones:</strong> 40+ países mapeados a 6 regiones</li>
                <li>• <strong>players</strong> = número total de jugadores en la región</li>
                <li>• <strong>clubs</strong> = número de clubes únicos en la región</li>
                <li>• <strong>countries</strong> = número de países únicos en la región</li>
                <li>• <strong>ratio</strong> = clubs / countries (clubes por país en la región)</li>
              </ul>
              <p className="text-xs text-muted-foreground mt-2">
                <strong>Columnas utilizadas:</strong> youth_club_country, youth_club
              </p>
            </div>
          </div>

          {/* Cross-Border Development */}
          <div className="space-y-3">
            <h3 className="text-lg font-semibold text-foreground">Cross-Border Development</h3>
            <div className="bg-muted/30 p-4 rounded-lg">
              <p className="text-sm text-muted-foreground mb-2">
                <strong>Fórmula:</strong> Análisis de desarrollo transfronterizo
              </p>
              <ul className="text-sm space-y-1 text-muted-foreground">
                <li>• <strong>total</strong> = número total de jugadores del país</li>
                <li>• <strong>crossBorder</strong> = jugadores que se formaron en otro país</li>
                <li>• <strong>ratio</strong> = crossBorder / total (porcentaje de desarrollo transfronterizo)</li>
                <li>• <strong>Filtro:</strong> Solo países con mínimo 5 jugadores</li>
              </ul>
              <p className="text-xs text-muted-foreground mt-2">
                <strong>Columnas utilizadas:</strong> country_of_birth, youth_club_country
              </p>
            </div>
          </div>

          {/* Talent Export/Import Ratio */}
          <div className="space-y-3">
            <h3 className="text-lg font-semibold text-foreground">Talent Export/Import Ratio</h3>
            <div className="bg-muted/30 p-4 rounded-lg">
              <p className="text-sm text-muted-foreground mb-2">
                <strong>Fórmula:</strong> Ratio de exportación/importación de talento
              </p>
              <ul className="text-sm space-y-1 text-muted-foreground">
                <li>• <strong>exported</strong> = jugadores nacidos en el país que se formaron en otro</li>
                <li>• <strong>imported</strong> = jugadores nacidos en otro país que se formaron aquí</li>
                <li>• <strong>ratio</strong> = imported / max(exported, 1)</li>
                <li>• <strong>total</strong> = exported + imported (total de movimientos)</li>
                <li>• <strong>Filtro:</strong> Solo países con mínimo 3 movimientos</li>
              </ul>
              <p className="text-xs text-muted-foreground mt-2">
                <strong>Columnas utilizadas:</strong> country_of_birth, youth_club_country
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

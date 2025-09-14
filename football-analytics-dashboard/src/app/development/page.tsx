"use client"

import { usePlayerData } from '@/hooks/usePlayerData'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Building2, Globe, Target, Zap } from 'lucide-react'
import { useMemo } from 'react'

// Componente para gráfico de barras verticales futurista
function FuturisticBarChart({ 
  data, 
  title, 
  subtitle,
  color = "primary",
  icon: Icon 
}: {
  data: Array<{ name: string; value: number; percentage: number; score?: number }>
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
                  {item.score && (
                    <span className="text-xs font-bold text-primary bg-primary/10 px-2 py-1 rounded-full">
                      {item.score.toFixed(1)}
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

export default function DevelopmentPage() {
  const { players, loading, error } = usePlayerData()

  // Youth Development Index por país
  const youthDevelopmentIndex = useMemo(() => {
    if (!players.length) return []
    
    const countryStats = new Map<string, { players: number; clubs: number; avgAge: number; marketValue: number }>()
    
    players.forEach(player => {
      if (player.youth_club_country && player.youth_club_country !== 'Not found') {
        const country = player.youth_club_country
        const stats = countryStats.get(country) || { players: 0, clubs: 0, avgAge: 0, marketValue: 0 }
        
        stats.players++
        if (player.youth_club && player.youth_club !== 'Not found') {
          stats.clubs++
        }
        
        const age = player.age ? parseInt(player.age) : 0
        if (age > 0) {
          stats.avgAge = (stats.avgAge * (stats.players - 1) + age) / stats.players
        }
        
        const marketValue = player.latest_market_value ? parseFloat(player.latest_market_value.replace(/[€$,\s]/g, '')) : 0
        stats.marketValue += marketValue
        
        countryStats.set(country, stats)
      }
    })
    
    const totalPlayers = players.length
    return Array.from(countryStats.entries())
      .map(([country, stats]) => {
        // Cálculo del Youth Development Index (0-100)
        const playerRatio = (stats.players / totalPlayers) * 100
        const clubDiversity = Math.min(stats.clubs / stats.players * 10, 10) // Máximo 10
        const ageScore = Math.max(0, 25 - stats.avgAge) * 2 // Mejor si son jóvenes
        const marketScore = Math.min(stats.marketValue / 1000000, 50) // Máximo 50
        
        const developmentIndex = Math.min(playerRatio + clubDiversity + ageScore + marketScore, 100)
        
        return {
          name: country.length > 20 ? country.substring(0, 20) + '...' : country,
          value: Math.round(developmentIndex * 100) / 100,
          percentage: (stats.players / totalPlayers) * 100,
          players: stats.players,
          score: developmentIndex
        }
      })
      .sort((a, b) => b.score - a.score)
      .slice(0, 10)
  }, [players])

  // Club Development Score
  const clubDevelopmentScore = useMemo(() => {
    if (!players.length) return []
    
    const clubStats = new Map<string, { players: number; countries: Set<string>; avgAge: number; marketValue: number }>()
    
    players.forEach(player => {
      if (player.youth_club && player.youth_club !== 'Not found' && !player.youth_club.includes(')')) {
        const club = player.youth_club_cleaned || player.youth_club
        const stats = clubStats.get(club) || { players: 0, countries: new Set(), avgAge: 0, marketValue: 0 }
        
        stats.players++
        if (player.nationality) {
          stats.countries.add(player.nationality)
        }
        
        const age = player.age ? parseInt(player.age) : 0
        if (age > 0) {
          stats.avgAge = (stats.avgAge * (stats.players - 1) + age) / stats.players
        }
        
        const marketValue = player.latest_market_value ? parseFloat(player.latest_market_value.replace(/[€$,\s]/g, '')) : 0
        stats.marketValue += marketValue
        
        clubStats.set(club, stats)
      }
    })
    
    const totalPlayers = players.length
    return Array.from(clubStats.entries())
      .map(([club, stats]) => {
        // Cálculo del Club Development Score (0-100)
        const playerCount = stats.players
        const diversityScore = stats.countries.size * 2 // Diversidad de nacionalidades
        const ageScore = Math.max(0, 30 - stats.avgAge) * 1.5 // Mejor si son jóvenes
        const marketScore = Math.min(stats.marketValue / 10000000, 30) // Máximo 30
        
        const developmentScore = Math.min(playerCount + diversityScore + ageScore + marketScore, 100)
        
        return {
          name: club.length > 25 ? club.substring(0, 25) + '...' : club,
          value: Math.round(developmentScore * 100) / 100,
          percentage: (playerCount / totalPlayers) * 100,
          players: playerCount,
          score: developmentScore
        }
      })
      .sort((a, b) => b.score - a.score)
      .slice(0, 10)
  }, [players])

  // Talent Pipeline Strength
  const talentPipelineStrength = useMemo(() => {
    if (!players.length) return []
    
    const ageGroups = {
      'U18': 0,
      'U21': 0,
      'U25': 0,
      'U30': 0,
      '30+': 0
    }
    
    players.forEach(player => {
      const age = player.age ? parseInt(player.age) : 0
      if (age <= 18) ageGroups['U18']++
      else if (age <= 21) ageGroups['U21']++
      else if (age <= 25) ageGroups['U25']++
      else if (age <= 30) ageGroups['U30']++
      else ageGroups['30+']++
    })
    
    const totalPlayers = players.length
    return Object.entries(ageGroups)
      .map(([ageGroup, count]) => ({
        name: ageGroup,
        value: count,
        percentage: (count / totalPlayers) * 100,
        score: count // Fuerza del pipeline por grupo de edad
      }))
      .sort((a, b) => b.value - a.value)
  }, [players])

  // Geographic Talent Density
  const geographicTalentDensity = useMemo(() => {
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
      .map(([region, stats]) => {
        // Densidad = jugadores por país en la región
        const density = stats.players / stats.countries.size
        
        return {
          name: region,
          value: stats.players,
          percentage: (stats.players / totalPlayers) * 100,
          score: density
        }
      })
      .sort((a, b) => b.score - a.score)
      .slice(0, 8)
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
          Development Analysis
        </h1>
        <p className="text-muted-foreground">
          Advanced insights into youth development patterns and talent pipeline strength
        </p>
      </div>

      {/* Métricas rápidas */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card className="bg-card border-border hover:bg-card/80 transition-colors">
          <CardContent className="px-4 py-3 flex items-center gap-3">
            <Target className="flex-shrink-0 h-5 w-5 text-primary" />
            <div>
              <p className="text-sm font-medium text-muted-foreground">Development Index</p>
              <p className="text-lg font-bold text-foreground">
                {loading ? (
                  <div className="h-6 w-20 bg-muted animate-pulse rounded" />
                ) : (
                  youthDevelopmentIndex[0]?.score.toFixed(1) || '0.0'
                )}
              </p>
            </div>
          </CardContent>
        </Card>
        
        <Card className="bg-card border-border hover:bg-card/80 transition-colors">
          <CardContent className="px-4 py-3 flex items-center gap-3">
            <Building2 className="flex-shrink-0 h-5 w-5 text-emerald-500" />
            <div>
              <p className="text-sm font-medium text-muted-foreground">Top Club Score</p>
              <p className="text-lg font-bold text-foreground">
                {loading ? (
                  <div className="h-6 w-20 bg-muted animate-pulse rounded" />
                ) : (
                  clubDevelopmentScore[0]?.score.toFixed(1) || '0.0'
                )}
              </p>
            </div>
          </CardContent>
        </Card>
        
        <Card className="bg-card border-border hover:bg-card/80 transition-colors">
          <CardContent className="px-4 py-3 flex items-center gap-3">
            <Zap className="flex-shrink-0 h-5 w-5 text-orange-500" />
            <div>
              <p className="text-sm font-medium text-muted-foreground">Pipeline Strength</p>
              <p className="text-lg font-bold text-foreground">
                {loading ? (
                  <div className="h-6 w-20 bg-muted animate-pulse rounded" />
                ) : (
                  `${talentPipelineStrength[0]?.value || 0} U18`
                )}
              </p>
            </div>
          </CardContent>
        </Card>
        
        <Card className="bg-card border-border hover:bg-card/80 transition-colors">
          <CardContent className="px-4 py-3 flex items-center gap-3">
            <Globe className="flex-shrink-0 h-5 w-5 text-purple-500" />
            <div>
              <p className="text-sm font-medium text-muted-foreground">Regions</p>
              <p className="text-lg font-bold text-foreground">
                {loading ? (
                  <div className="h-6 w-20 bg-muted animate-pulse rounded" />
                ) : (
                  geographicTalentDensity.length
                )}
              </p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Gráficos principales */}
      <div className="space-y-8">
        <FuturisticBarChart
          data={youthDevelopmentIndex}
          title="Youth Development Index"
          subtitle="Índice de desarrollo juvenil por país (0-100)"
          color="primary"
          icon={Target}
        />
        
        <FuturisticBarChart
          data={clubDevelopmentScore}
          title="Club Development Score"
          subtitle="Puntuación de desarrollo de cada club (0-100)"
          color="secondary"
          icon={Building2}
        />
        
        <FuturisticBarChart
          data={talentPipelineStrength}
          title="Talent Pipeline Strength"
          subtitle="Fuerza del pipeline de talentos por grupo de edad"
          color="accent"
          icon={Zap}
        />
        
        <FuturisticBarChart
          data={geographicTalentDensity}
          title="Geographic Talent Density"
          subtitle="Densidad de talento por región geográfica"
          color="success"
          icon={Globe}
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
          {/* Youth Development Index */}
          <div className="space-y-3">
            <h3 className="text-lg font-semibold text-foreground">Youth Development Index</h3>
            <div className="bg-muted/30 p-4 rounded-lg">
              <p className="text-sm text-muted-foreground mb-2">
                <strong>Fórmula:</strong> Índice compuesto (0-100) basado en 4 variables
              </p>
              <ul className="text-sm space-y-1 text-muted-foreground">
                <li>• <strong>playerRatio</strong> = (jugadores del país / total jugadores) &times; 100</li>
                <li>• <strong>clubDiversity</strong> = min(clubes únicos / jugadores del país &times; 10, 10)</li>
                <li>• <strong>ageScore</strong> = max(0, 25 - edad promedio) &times; 2</li>
                <li>• <strong>marketScore</strong> = min(valor total mercado / 1,000,000, 50)</li>
                <li>• <strong>Índice Final</strong> = min(playerRatio + clubDiversity + ageScore + marketScore, 100)</li>
              </ul>
              <p className="text-xs text-muted-foreground mt-2">
                <strong>Columnas utilizadas:</strong> youth_club_country, youth_club, age, latest_market_value
              </p>
            </div>
          </div>

          {/* Club Development Score */}
          <div className="space-y-3">
            <h3 className="text-lg font-semibold text-foreground">Club Development Score</h3>
            <div className="bg-muted/30 p-4 rounded-lg">
              <p className="text-sm text-muted-foreground mb-2">
                <strong>Fórmula:</strong> Puntuación compuesta (0-100) basada en diversidad y rendimiento
              </p>
              <ul className="text-sm space-y-1 text-muted-foreground">
                <li>• <strong>playerCount</strong> = número total de jugadores del club</li>
                <li>• <strong>diversityScore</strong> = número de nacionalidades únicas &times; 2</li>
                <li>• <strong>ageScore</strong> = max(0, 30 - edad promedio) &times; 1.5</li>
                <li>• <strong>marketScore</strong> = min(valor total mercado / 10,000,000, 30)</li>
                <li>• <strong>Score Final</strong> = min(playerCount + diversityScore + ageScore + marketScore, 100)</li>
              </ul>
              <p className="text-xs text-muted-foreground mt-2">
                <strong>Columnas utilizadas:</strong> youth_club, youth_club_cleaned, nationality, age, latest_market_value
              </p>
            </div>
          </div>

          {/* Talent Pipeline Strength */}
          <div className="space-y-3">
            <h3 className="text-lg font-semibold text-foreground">Talent Pipeline Strength</h3>
            <div className="bg-muted/30 p-4 rounded-lg">
              <p className="text-sm text-muted-foreground mb-2">
                <strong>Fórmula:</strong> Distribución de jugadores por grupos de edad
              </p>
              <ul className="text-sm space-y-1 text-muted-foreground">
                <li>• <strong>U18:</strong> jugadores con age &le; 18</li>
                <li>• <strong>U21:</strong> jugadores con 18 &lt; age &le; 21</li>
                <li>• <strong>U25:</strong> jugadores con 21 &lt; age &le; 25</li>
                <li>• <strong>U30:</strong> jugadores con 25 &lt; age &le; 30</li>
                <li>• <strong>30+:</strong> jugadores con age &gt; 30</li>
                <li>• <strong>Fuerza del Pipeline</strong> = número de jugadores en cada grupo</li>
              </ul>
              <p className="text-xs text-muted-foreground mt-2">
                <strong>Columnas utilizadas:</strong> age
              </p>
            </div>
          </div>

          {/* Geographic Talent Density */}
          <div className="space-y-3">
            <h3 className="text-lg font-semibold text-foreground">Geographic Talent Density</h3>
            <div className="bg-muted/30 p-4 rounded-lg">
              <p className="text-sm text-muted-foreground mb-2">
                <strong>Fórmula:</strong> Densidad de talento por región geográfica
              </p>
              <ul className="text-sm space-y-1 text-muted-foreground">
                <li>• <strong>Mapeo de países a regiones:</strong> Brasil→South America, España→Europe, etc.</li>
                <li>• <strong>players</strong> = número total de jugadores en la región</li>
                <li>• <strong>clubs</strong> = número de clubes únicos en la región</li>
                <li>• <strong>countries</strong> = número de países únicos en la región</li>
                <li>• <strong>Densidad</strong> = players / countries (jugadores por país)</li>
              </ul>
              <p className="text-xs text-muted-foreground mt-2">
                <strong>Columnas utilizadas:</strong> youth_club_country, youth_club
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

"use client"

import { usePlayerData } from '@/hooks/usePlayerData'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { TrendingUp, Star, BarChart3, Target, Users, Zap, DollarSign, Clock } from 'lucide-react'
import { useMemo } from 'react'

// Componente para gráfico de barras verticales futurista
function FuturisticBarChart({ 
  data, 
  title, 
  subtitle,
  color = "primary",
  icon: Icon 
}: {
  data: Array<{ name: string; value: number; percentage: number; potential?: number }>
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
                  {item.potential && (
                    <span className="text-xs font-bold text-primary bg-primary/10 px-2 py-1 rounded-full">
                      {item.potential.toFixed(1)}
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

export default function PredictivePage() {
  const { players, loading, error } = usePlayerData()

  // Future Star Potential
  const futureStarPotential = useMemo(() => {
    if (!players.length) return []
    
    const clubStats = new Map<string, { 
      players: number; 
      youngStars: number; 
      potential: number 
    }>()
    
    players.forEach(player => {
      if (player.youth_club && player.youth_club !== 'Not found' && !player.youth_club.includes(')')) {
        const club = player.youth_club_cleaned || player.youth_club
        const stats = clubStats.get(club) || { players: 0, youngStars: 0, potential: 0 }
        
        stats.players++
        
        const age = player.age ? parseInt(player.age) : 0
        const marketValue = player.latest_market_value ? parseFloat(player.latest_market_value.replace(/[€$,\s]/g, '')) : 0
        
        // Criterios para "future star": joven (&le;25) y con valor de mercado alto (&ge;1M)
        if (age <= 25 && marketValue >= 1000000) {
          stats.youngStars++
        }
        
        clubStats.set(club, stats)
      }
    })
    
    // Calcular potencial: (youngStars / players) * 100
    clubStats.forEach((stats, club) => {
      if (stats.players >= 3) {
        stats.potential = (stats.youngStars / stats.players) * 100
      }
    })
    
    const totalPlayers = players.length
    return Array.from(clubStats.entries())
      .filter(([_, stats]) => stats.players >= 3)
      .map(([club, stats]) => ({
        name: club.length > 25 ? club.substring(0, 25) + '...' : club,
        value: Math.round(stats.potential * 100) / 100,
        percentage: (stats.youngStars / totalPlayers) * 100,
        youngStars: stats.youngStars,
        potential: stats.potential
      }))
      .sort((a, b) => b.potential - a.potential)
      .slice(0, 10)
  }, [players])

  // Development Trajectory
  const developmentTrajectory = useMemo(() => {
    if (!players.length) return []
    
    const ageGroups = new Map<string, { 
      players: number; 
      avgMarketValue: number; 
      trajectory: number 
    }>()
    
    players.forEach(player => {
      const age = player.age ? parseInt(player.age) : 0
      const marketValue = player.latest_market_value ? parseFloat(player.latest_market_value.replace(/[€$,\s]/g, '')) : 0
      
      if (age > 0 && marketValue > 0) {
        let ageGroup = ''
        if (age <= 18) ageGroup = 'U18'
        else if (age <= 21) ageGroup = 'U21'
        else if (age <= 25) ageGroup = 'U25'
        else if (age <= 30) ageGroup = 'U30'
        else ageGroup = '30+'
        
        const stats = ageGroups.get(ageGroup) || { players: 0, avgMarketValue: 0, trajectory: 0 }
        stats.players++
        stats.avgMarketValue = (stats.avgMarketValue * (stats.players - 1) + marketValue) / stats.players
        
        // Trayectoria: crecimiento esperado basado en edad
        const expectedGrowth = ageGroup === 'U18' ? 3.0 : ageGroup === 'U21' ? 2.5 : ageGroup === 'U25' ? 2.0 : ageGroup === 'U30' ? 1.5 : 1.0
        stats.trajectory = stats.avgMarketValue * expectedGrowth
        
        ageGroups.set(ageGroup, stats)
      }
    })
    
    const totalPlayers = players.length
    return Array.from(ageGroups.entries())
      .map(([ageGroup, stats]) => ({
        name: ageGroup,
        value: stats.players,
        percentage: (stats.players / totalPlayers) * 100,
        potential: stats.trajectory
      }))
      .sort((a, b) => b.potential - a.potential)
  }, [players])

  // Market Value Prediction
  const marketValuePrediction = useMemo(() => {
    if (!players.length) return []
    
    const countryStats = new Map<string, { 
      players: number; 
      avgMarketValue: number; 
      prediction: number 
    }>()
    
    players.forEach(player => {
      const country = player.youth_club_country
      const marketValue = player.latest_market_value ? parseFloat(player.latest_market_value.replace(/[€$,\s]/g, '')) : 0
      
      if (country && country !== 'Not found' && marketValue > 0) {
        const stats = countryStats.get(country) || { players: 0, avgMarketValue: 0, prediction: 0 }
        stats.players++
        stats.avgMarketValue = (stats.avgMarketValue * (stats.players - 1) + marketValue) / stats.players
        
        // Predicción: valor promedio * factor de crecimiento basado en número de jugadores
        const growthFactor = Math.min(1 + (stats.players / 100), 2.0) // Máximo 2x
        stats.prediction = stats.avgMarketValue * growthFactor
        
        countryStats.set(country, stats)
      }
    })
    
    const totalPlayers = players.length
    return Array.from(countryStats.entries())
      .filter(([_, stats]) => stats.players >= 5)
      .map(([country, stats]) => ({
        name: country.length > 20 ? country.substring(0, 20) + '...' : country,
        value: Math.round(stats.avgMarketValue),
        percentage: (stats.players / totalPlayers) * 100,
        potential: stats.prediction
      }))
      .sort((a, b) => b.potential - a.potential)
      .slice(0, 10)
  }, [players])

  // Talent Scouting Score
  const talentScoutingScore = useMemo(() => {
    if (!players.length) return []
    
    const clubStats = new Map<string, { 
      players: number; 
      diverseCountries: number; 
      scoutingScore: number 
    }>()
    
    players.forEach(player => {
      if (player.youth_club && player.youth_club !== 'Not found' && !player.youth_club.includes(')')) {
        const club = player.youth_club_cleaned || player.youth_club
        const stats = clubStats.get(club) || { players: 0, diverseCountries: 0, scoutingScore: 0 }
        
        stats.players++
        
        if (player.nationality && player.nationality !== 'Not found') {
          stats.diverseCountries++
        }
        
        clubStats.set(club, stats)
      }
    })
    
    // Calcular score de scouting: diversidad de nacionalidades * log(players)
    clubStats.forEach((stats, club) => {
      if (stats.players >= 2) {
        stats.scoutingScore = stats.diverseCountries * Math.log(stats.players) * 10
      }
    })
    
    const totalPlayers = players.length
    return Array.from(clubStats.entries())
      .filter(([_, stats]) => stats.players >= 2)
      .map(([club, stats]) => ({
        name: club.length > 25 ? club.substring(0, 25) + '...' : club,
        value: stats.diverseCountries,
        percentage: (stats.players / totalPlayers) * 100,
        potential: stats.scoutingScore
      }))
      .sort((a, b) => b.potential - a.potential)
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
          Predictive Analytics
        </h1>
        <p className="text-muted-foreground">
          Advanced predictive insights and future talent potential analysis
        </p>
      </div>

      {/* Métricas rápidas */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card className="bg-card border-border hover:bg-card/80 transition-colors">
          <CardContent className="px-4 py-3 flex items-center gap-3">
            <Star className="flex-shrink-0 h-5 w-5 text-primary" />
            <div>
              <p className="text-sm font-medium text-muted-foreground">Star Potential</p>
              <p className="text-lg font-bold text-foreground">
                {loading ? (
                  <div className="h-6 w-20 bg-muted animate-pulse rounded" />
                ) : (
                  `${futureStarPotential[0]?.potential.toFixed(1)}%` || '0.0%'
                )}
              </p>
            </div>
          </CardContent>
        </Card>
        
        <Card className="bg-card border-border hover:bg-card/80 transition-colors">
          <CardContent className="px-4 py-3 flex items-center gap-3">
            <TrendingUp className="flex-shrink-0 h-5 w-5 text-emerald-500" />
            <div>
              <p className="text-sm font-medium text-muted-foreground">Top Trajectory</p>
              <p className="text-lg font-bold text-foreground">
                {loading ? (
                  <div className="h-6 w-20 bg-muted animate-pulse rounded" />
                ) : (
                  `€${(developmentTrajectory[0]?.potential / 1000000).toFixed(1)}M` || '€0M'
                )}
              </p>
            </div>
          </CardContent>
        </Card>
        
        <Card className="bg-card border-border hover:bg-card/80 transition-colors">
          <CardContent className="px-4 py-3 flex items-center gap-3">
            <DollarSign className="flex-shrink-0 h-5 w-5 text-orange-500" />
            <div>
              <p className="text-sm font-medium text-muted-foreground">Value Prediction</p>
              <p className="text-lg font-bold text-foreground">
                {loading ? (
                  <div className="h-6 w-20 bg-muted animate-pulse rounded" />
                ) : (
                  `€${(marketValuePrediction[0]?.potential / 1000000).toFixed(1)}M` || '€0M'
                )}
              </p>
            </div>
          </CardContent>
        </Card>
        
        <Card className="bg-card border-border hover:bg-card/80 transition-colors">
          <CardContent className="px-4 py-3 flex items-center gap-3">
            <Target className="flex-shrink-0 h-5 w-5 text-purple-500" />
            <div>
              <p className="text-sm font-medium text-muted-foreground">Scouting Score</p>
              <p className="text-lg font-bold text-foreground">
                {loading ? (
                  <div className="h-6 w-20 bg-muted animate-pulse rounded" />
                ) : (
                  talentScoutingScore[0]?.potential.toFixed(0) || '0'
                )}
              </p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Gráficos principales */}
      <div className="space-y-8">
        <FuturisticBarChart
          data={futureStarPotential}
          title="Future Star Potential"
          subtitle="Potencial de futuras estrellas por club"
          color="primary"
          icon={Star}
        />
        
        <FuturisticBarChart
          data={developmentTrajectory}
          title="Development Trajectory"
          subtitle="Trayectoria de desarrollo por grupo de edad"
          color="secondary"
          icon={TrendingUp}
        />
        
        <FuturisticBarChart
          data={marketValuePrediction}
          title="Market Value Prediction"
          subtitle="Predicción de valor de mercado por país"
          color="accent"
          icon={DollarSign}
        />
        
        <FuturisticBarChart
          data={talentScoutingScore}
          title="Talent Scouting Score"
          subtitle="Puntuación de scouting de talentos por club"
          color="success"
          icon={Target}
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
          {/* Future Star Potential */}
          <div className="space-y-3">
            <h3 className="text-lg font-semibold text-foreground">Future Star Potential</h3>
            <div className="bg-muted/30 p-4 rounded-lg">
              <p className="text-sm text-muted-foreground mb-2">
                <strong>Fórmula:</strong> Potencial de futuras estrellas por club
              </p>
              <ul className="text-sm space-y-1 text-muted-foreground">
                <li>• <strong>players</strong> = número total de jugadores del club</li>
                <li>• <strong>youngStars</strong> = jugadores &le;25 años con valor &ge;€1M</li>
                <li>• <strong>potential</strong> = (youngStars / players) &times; 100</li>
                <li>• <strong>Filtro:</strong> Solo clubes con mínimo 3 jugadores</li>
                <li>• <strong>Criterios de &quot;Future Star&quot;:</strong> age &le; 25 AND latest_market_value &ge; 1,000,000</li>
              </ul>
              <p className="text-xs text-muted-foreground mt-2">
                <strong>Columnas utilizadas:</strong> youth_club, youth_club_cleaned, age, latest_market_value
              </p>
            </div>
          </div>

          {/* Development Trajectory */}
          <div className="space-y-3">
            <h3 className="text-lg font-semibold text-foreground">Development Trajectory</h3>
            <div className="bg-muted/30 p-4 rounded-lg">
              <p className="text-sm text-muted-foreground mb-2">
                <strong>Fórmula:</strong> Trayectoria de desarrollo por grupo de edad
              </p>
              <ul className="text-sm space-y-1 text-muted-foreground">
                <li>• <strong>U18:</strong> age &le; 18, expectedGrowth = 3.0x</li>
                <li>• <strong>U21:</strong> 18 &lt; age &le; 21, expectedGrowth = 2.5x</li>
                <li>• <strong>U25:</strong> 21 &lt; age &le; 25, expectedGrowth = 2.0x</li>
                <li>• <strong>U30:</strong> 25 &lt; age &le; 30, expectedGrowth = 1.5x</li>
                <li>• <strong>30+:</strong> age &gt; 30, expectedGrowth = 1.0x</li>
                <li>• <strong>trajectory</strong> = avgMarketValue &times; expectedGrowth</li>
              </ul>
              <p className="text-xs text-muted-foreground mt-2">
                <strong>Columnas utilizadas:</strong> age, latest_market_value
              </p>
            </div>
          </div>

          {/* Market Value Prediction */}
          <div className="space-y-3">
            <h3 className="text-lg font-semibold text-foreground">Market Value Prediction</h3>
            <div className="bg-muted/30 p-4 rounded-lg">
              <p className="text-sm text-muted-foreground mb-2">
                <strong>Fórmula:</strong> Predicción de valor de mercado por país
              </p>
              <ul className="text-sm space-y-1 text-muted-foreground">
                <li>• <strong>players</strong> = número total de jugadores del país</li>
                <li>• <strong>avgMarketValue</strong> = valor promedio de mercado por jugador</li>
                <li>• <strong>growthFactor</strong> = min(1 + (players / 100), 2.0)</li>
                <li>• <strong>prediction</strong> = avgMarketValue &times; growthFactor</li>
                <li>• <strong>Filtro:</strong> Solo países con mínimo 5 jugadores</li>
              </ul>
              <p className="text-xs text-muted-foreground mt-2">
                <strong>Columnas utilizadas:</strong> youth_club_country, latest_market_value
              </p>
            </div>
          </div>

          {/* Talent Scouting Score */}
          <div className="space-y-3">
            <h3 className="text-lg font-semibold text-foreground">Talent Scouting Score</h3>
            <div className="bg-muted/30 p-4 rounded-lg">
              <p className="text-sm text-muted-foreground mb-2">
                <strong>Fórmula:</strong> Puntuación de scouting de talentos por club
              </p>
              <ul className="text-sm space-y-1 text-muted-foreground">
                <li>• <strong>players</strong> = número total de jugadores del club</li>
                <li>• <strong>diverseCountries</strong> = número de nacionalidades únicas</li>
                <li>• <strong>scoutingScore</strong> = diverseCountries &times; log(players) &times; 10</li>
                <li>• <strong>Filtro:</strong> Solo clubes con mínimo 2 jugadores</li>
                <li>• <strong>Factor de diversidad:</strong> Más nacionalidades = mejor scouting</li>
              </ul>
              <p className="text-xs text-muted-foreground mt-2">
                <strong>Columnas utilizadas:</strong> youth_club, youth_club_cleaned, nationality
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

import React from 'react'
import Image from 'next/image'

export function PrimePlayersLogo({ className = "h-8 w-8" }: { className?: string }) {
  return (
    <div 
      className={`relative ${className} rounded-lg overflow-hidden`}
      style={{ backgroundColor: '#181822' }}
    >
      <Image
        src="/logo.png"
        alt="Prime Players Logo"
        fill
        className="object-contain"
        priority
      />
    </div>
  )
}

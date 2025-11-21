import { Cloud, Sun, CloudRain, Wind, Droplets } from 'lucide-react'

interface WeatherCardProps {
  location: string
  temperature: number
  condition: string
  humidity: number
  windSpeed: number
}

export function WeatherCard({
  location,
  temperature,
  condition,
  humidity,
  windSpeed,
}: WeatherCardProps) {
  const getWeatherIcon = () => {
    const conditionLower = condition.toLowerCase()
    if (conditionLower.includes('rain')) {
      return <CloudRain className="w-16 h-16 text-blue-500" />
    }
    if (conditionLower.includes('cloud')) {
      return <Cloud className="w-16 h-16 text-gray-400" />
    }
    return <Sun className="w-16 h-16 text-yellow-500" />
  }

  return (
    <div className="rounded-lg border bg-white shadow-sm p-6 max-w-md">
      <h3 className="text-lg font-semibold mb-4">{location}</h3>

      <div className="flex items-center justify-between mb-6">
        <div>
          <div className="text-5xl font-bold">{temperature}°C</div>
          <div className="text-gray-600 mt-2">{condition}</div>
        </div>
        <div>{getWeatherIcon()}</div>
      </div>

      <div className="grid grid-cols-2 gap-4 pt-4 border-t">
        <div className="flex items-center gap-2">
          <Droplets className="w-5 h-5 text-blue-500" />
          <div>
            <div className="text-sm text-gray-500">Humidity</div>
            <div className="font-medium">{humidity}%</div>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Wind className="w-5 h-5 text-gray-500" />
          <div>
            <div className="text-sm text-gray-500">Wind</div>
            <div className="font-medium">{windSpeed} km/h</div>
          </div>
        </div>
      </div>
    </div>
  )
}

import { Star, MapPin, DollarSign, Clock } from 'lucide-react'

interface RestaurantCardProps {
  name: string
  cuisine: string
  location: string
  rating: number
  reviews: number
  priceRange: number
  openNow: boolean
  hours: string
  description: string
  image?: string
}

export function RestaurantCard({
  name,
  cuisine,
  location,
  rating,
  reviews,
  priceRange,
  openNow,
  hours,
  description,
  image,
}: RestaurantCardProps) {
  const priceSymbol = '$'.repeat(priceRange)

  return (
    <div className="rounded-lg border bg-white shadow-sm p-6 max-w-lg">
      {image && (
        <img
          src={image}
          alt={name}
          className="w-full h-48 object-cover rounded-lg mb-4"
        />
      )}

      <div className="space-y-3">
        <div>
          <div className="flex items-start justify-between mb-1">
            <h3 className="text-xl font-bold">{name}</h3>
            <span
              className={`px-2 py-1 rounded text-xs font-medium ${
                openNow
                  ? 'bg-green-50 text-green-700'
                  : 'bg-red-50 text-red-700'
              }`}
            >
              {openNow ? 'Open Now' : 'Closed'}
            </span>
          </div>

          <p className="text-sm text-gray-600">{cuisine}</p>
        </div>

        <div className="flex items-center gap-4 text-sm">
          <div className="flex items-center gap-1">
            <Star className="w-4 h-4 text-yellow-500 fill-current" />
            <span className="font-medium">{rating.toFixed(1)}</span>
            <span className="text-gray-500">({reviews})</span>
          </div>

          <div className="flex items-center gap-1 text-gray-600">
            <DollarSign className="w-4 h-4" />
            <span className="font-medium">{priceSymbol}</span>
          </div>
        </div>

        <div className="space-y-2">
          <div className="flex items-start gap-2 text-sm text-gray-600">
            <MapPin className="w-4 h-4 mt-0.5 flex-shrink-0" />
            <span>{location}</span>
          </div>

          <div className="flex items-center gap-2 text-sm text-gray-600">
            <Clock className="w-4 h-4 flex-shrink-0" />
            <span>{hours}</span>
          </div>
        </div>

        <p className="text-sm text-gray-600 line-clamp-2">{description}</p>

        <div className="flex gap-2 pt-2">
          <button className="flex-1 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors">
            Reserve Table
          </button>
          <button className="px-4 py-2 border rounded-lg hover:bg-gray-50 transition-colors">
            Directions
          </button>
        </div>
      </div>
    </div>
  )
}

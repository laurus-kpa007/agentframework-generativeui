import { Star, MapPin, Wifi, Coffee, Tv } from 'lucide-react'

interface HotelCardProps {
  name: string
  location: string
  rating: number
  reviews: number
  pricePerNight: number
  amenities: string[]
  description: string
  image?: string
}

export function HotelCard({
  name,
  location,
  rating,
  reviews,
  pricePerNight,
  amenities,
  description,
  image,
}: HotelCardProps) {
  const amenityIcons: Record<string, any> = {
    wifi: Wifi,
    breakfast: Coffee,
    tv: Tv,
  }

  return (
    <div className="rounded-lg border bg-white shadow-sm p-6 max-w-lg">
      {image && (
        <img
          src={image}
          alt={name}
          className="w-full h-48 object-cover rounded-lg mb-4"
        />
      )}

      <div className="space-y-4">
        <div>
          <h3 className="text-xl font-bold mb-1">{name}</h3>
          <div className="flex items-center gap-1 text-sm text-gray-500">
            <MapPin className="w-4 h-4" />
            <span>{location}</span>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1">
            {[...Array(5)].map((_, idx) => (
              <Star
                key={idx}
                className={`w-4 h-4 ${
                  idx < rating
                    ? 'text-yellow-500 fill-current'
                    : 'text-gray-300'
                }`}
              />
            ))}
          </div>
          <span className="text-sm text-gray-600">({reviews} reviews)</span>
        </div>

        <p className="text-sm text-gray-600">{description}</p>

        <div className="flex flex-wrap gap-2">
          {amenities.map((amenity, idx) => {
            const Icon = amenityIcons[amenity.toLowerCase()] || Coffee
            return (
              <div
                key={idx}
                className="flex items-center gap-1 px-3 py-1 bg-gray-100 rounded-full text-xs text-gray-700"
              >
                <Icon className="w-3 h-3" />
                <span className="capitalize">{amenity}</span>
              </div>
            )
          })}
        </div>

        <div className="flex items-center justify-between pt-4 border-t">
          <div>
            <div className="text-sm text-gray-500">Starting from</div>
            <div className="text-2xl font-bold text-gray-900">
              ${pricePerNight}
              <span className="text-sm font-normal text-gray-500">
                /night
              </span>
            </div>
          </div>

          <button className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors">
            Book Now
          </button>
        </div>
      </div>
    </div>
  )
}

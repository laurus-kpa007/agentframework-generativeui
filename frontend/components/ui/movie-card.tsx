import { Star, Clock, Calendar } from 'lucide-react'

interface MovieCardProps {
  title: string
  year: number
  rating: number
  genre: string[]
  runtime: number
  director: string
  plot: string
  poster?: string
}

export function MovieCard({
  title,
  year,
  rating,
  genre,
  runtime,
  director,
  plot,
  poster,
}: MovieCardProps) {
  return (
    <div className="rounded-lg border bg-white shadow-sm p-6 max-w-lg">
      <div className="flex gap-4">
        {poster && (
          <img
            src={poster}
            alt={title}
            className="w-32 h-48 object-cover rounded-lg flex-shrink-0"
          />
        )}

        <div className="flex-1 space-y-3">
          <div>
            <h3 className="text-xl font-bold">{title}</h3>
            <p className="text-sm text-gray-500">{director}</p>
          </div>

          <div className="flex items-center gap-4 text-sm">
            <div className="flex items-center gap-1 text-yellow-600">
              <Star className="w-4 h-4 fill-current" />
              <span className="font-medium">{rating.toFixed(1)}/10</span>
            </div>

            <div className="flex items-center gap-1 text-gray-500">
              <Calendar className="w-4 h-4" />
              <span>{year}</span>
            </div>

            <div className="flex items-center gap-1 text-gray-500">
              <Clock className="w-4 h-4" />
              <span>{runtime} min</span>
            </div>
          </div>

          <div className="flex flex-wrap gap-2">
            {genre.map((g, idx) => (
              <span
                key={idx}
                className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs"
              >
                {g}
              </span>
            ))}
          </div>

          <p className="text-sm text-gray-600 line-clamp-3">{plot}</p>
        </div>
      </div>
    </div>
  )
}

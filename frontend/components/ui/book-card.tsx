import { Star, BookOpen, Calendar } from 'lucide-react'

interface BookCardProps {
  title: string
  author: string
  publishedYear: number
  rating: number
  pages: number
  genre: string[]
  description: string
  isbn?: string
  cover?: string
}

export function BookCard({
  title,
  author,
  publishedYear,
  rating,
  pages,
  genre,
  description,
  isbn,
  cover,
}: BookCardProps) {
  return (
    <div className="rounded-lg border bg-white shadow-sm p-6 max-w-lg">
      <div className="flex gap-4">
        {cover && (
          <img
            src={cover}
            alt={title}
            className="w-24 h-36 object-cover rounded-lg flex-shrink-0 shadow"
          />
        )}

        <div className="flex-1 space-y-3">
          <div>
            <h3 className="text-lg font-bold">{title}</h3>
            <p className="text-sm text-gray-600">by {author}</p>
          </div>

          <div className="flex items-center gap-4 text-sm">
            <div className="flex items-center gap-1 text-yellow-600">
              <Star className="w-4 h-4 fill-current" />
              <span className="font-medium">{rating.toFixed(1)}/5</span>
            </div>

            <div className="flex items-center gap-1 text-gray-500">
              <Calendar className="w-4 h-4" />
              <span>{publishedYear}</span>
            </div>

            <div className="flex items-center gap-1 text-gray-500">
              <BookOpen className="w-4 h-4" />
              <span>{pages} pages</span>
            </div>
          </div>

          <div className="flex flex-wrap gap-2">
            {genre.map((g, idx) => (
              <span
                key={idx}
                className="px-2 py-1 bg-purple-50 text-purple-700 rounded text-xs"
              >
                {g}
              </span>
            ))}
          </div>

          <p className="text-sm text-gray-600 line-clamp-3">{description}</p>

          {isbn && (
            <p className="text-xs text-gray-400">ISBN: {isbn}</p>
          )}
        </div>
      </div>

      <div className="flex gap-2 mt-4 pt-4 border-t">
        <button className="flex-1 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors text-sm">
          Read Sample
        </button>
        <button className="px-4 py-2 border rounded-lg hover:bg-gray-50 transition-colors text-sm">
          Add to Library
        </button>
      </div>
    </div>
  )
}

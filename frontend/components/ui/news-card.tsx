import { Clock, ExternalLink, Newspaper } from 'lucide-react'
import { formatDate, formatTime } from '@/lib/utils'

interface NewsCardProps {
  title: string
  source: string
  author?: string
  publishedAt: string
  description: string
  url?: string
  image?: string
  category?: string
}

export function NewsCard({
  title,
  source,
  author,
  publishedAt,
  description,
  url,
  image,
  category,
}: NewsCardProps) {
  const date = new Date(publishedAt)

  return (
    <div className="rounded-lg border bg-white shadow-sm p-6 max-w-lg">
      {image && (
        <img
          src={image}
          alt={title}
          className="w-full h-48 object-cover rounded-lg mb-4"
        />
      )}

      <div className="space-y-3">
        {category && (
          <span className="inline-block px-2 py-1 bg-blue-50 text-blue-700 rounded text-xs font-medium">
            {category}
          </span>
        )}

        <div>
          <h3 className="text-lg font-bold mb-2">{title}</h3>
          <p className="text-sm text-gray-600 line-clamp-3">{description}</p>
        </div>

        <div className="flex items-center gap-4 text-xs text-gray-500">
          <div className="flex items-center gap-1">
            <Newspaper className="w-3 h-3" />
            <span className="font-medium">{source}</span>
          </div>

          {author && (
            <span>by {author}</span>
          )}

          <div className="flex items-center gap-1">
            <Clock className="w-3 h-3" />
            <span>
              {formatDate(date)} at {formatTime(date)}
            </span>
          </div>
        </div>

        {url && (
          <a
            href={url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors text-sm font-medium"
          >
            <span>Read Full Article</span>
            <ExternalLink className="w-4 h-4" />
          </a>
        )}
      </div>
    </div>
  )
}

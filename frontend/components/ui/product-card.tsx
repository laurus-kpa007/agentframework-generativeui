import { Star, ShoppingCart, Tag } from 'lucide-react'

interface ProductCardProps {
  name: string
  price: number
  originalPrice?: number
  rating: number
  reviews: number
  description: string
  category: string
  inStock: boolean
  image?: string
}

export function ProductCard({
  name,
  price = 0,
  originalPrice,
  rating = 0,
  reviews = 0,
  description,
  category,
  inStock = true,
  image,
}: ProductCardProps) {
  // Ensure values are numbers
  const safePrice = Number(price) || 0
  const safeOriginalPrice = originalPrice ? Number(originalPrice) || 0 : 0
  const safeRating = Number(rating) || 0
  const safeReviews = Number(reviews) || 0

  const discount = safeOriginalPrice > 0
    ? Math.round(((safeOriginalPrice - safePrice) / safeOriginalPrice) * 100)
    : 0

  return (
    <div className="rounded-lg border bg-white shadow-sm p-6 max-w-md">
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
            <h3 className="text-lg font-bold flex-1">{name}</h3>
            {discount > 0 && (
              <span className="px-2 py-1 bg-red-500 text-white rounded text-xs font-medium">
                -{discount}%
              </span>
            )}
          </div>

          <div className="flex items-center gap-1 text-xs text-gray-500">
            <Tag className="w-3 h-3" />
            <span>{category}</span>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1">
            <Star className="w-4 h-4 text-yellow-500 fill-current" />
            <span className="font-medium text-sm">{safeRating.toFixed(1)}</span>
            <span className="text-sm text-gray-500">({safeReviews})</span>
          </div>

          <span
            className={`text-xs px-2 py-1 rounded ${
              inStock
                ? 'bg-green-50 text-green-700'
                : 'bg-red-50 text-red-700'
            }`}
          >
            {inStock ? 'In Stock' : 'Out of Stock'}
          </span>
        </div>

        <p className="text-sm text-gray-600 line-clamp-2">{description}</p>

        <div className="flex items-center justify-between pt-2 border-t">
          <div>
            {safeOriginalPrice > 0 && (
              <span className="text-sm text-gray-400 line-through mr-2">
                ${safeOriginalPrice.toFixed(2)}
              </span>
            )}
            <span className="text-2xl font-bold text-gray-900">
              ${safePrice.toFixed(2)}
            </span>
          </div>

          <button
            disabled={!inStock}
            className="flex items-center gap-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <ShoppingCart className="w-4 h-4" />
            <span className="text-sm font-medium">Add to Cart</span>
          </button>
        </div>
      </div>
    </div>
  )
}

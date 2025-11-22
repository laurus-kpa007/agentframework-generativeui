import { TrendingUp, TrendingDown } from 'lucide-react'
import { cn } from '@/lib/utils'

interface StockCardProps {
  symbol: string
  name: string
  price: number
  change: number
  changePercent: number
}

export function StockCard({
  symbol,
  name,
  price = 0,
  change = 0,
  changePercent = 0,
}: StockCardProps) {
  const isPositive = change >= 0

  // Ensure values are numbers
  const safePrice = Number(price) || 0
  const safeChange = Number(change) || 0
  const safeChangePercent = Number(changePercent) || 0

  return (
    <div className="rounded-lg border bg-white shadow-sm p-4 max-w-md">
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold">{symbol}</h3>
            <p className="text-sm text-gray-500">{name}</p>
          </div>
          <div
            className={cn(
              'flex items-center gap-1 text-sm font-medium px-2 py-1 rounded',
              isPositive
                ? 'bg-green-50 text-green-700'
                : 'bg-red-50 text-red-700'
            )}
          >
            {isPositive ? (
              <TrendingUp className="w-4 h-4" />
            ) : (
              <TrendingDown className="w-4 h-4" />
            )}
            <span>
              {isPositive ? '+' : ''}
              {safeChangePercent.toFixed(2)}%
            </span>
          </div>
        </div>

        <div className="flex items-baseline gap-2">
          <span className="text-3xl font-bold">${safePrice.toFixed(2)}</span>
          <span
            className={cn(
              'text-sm',
              isPositive ? 'text-green-600' : 'text-red-600'
            )}
          >
            {isPositive ? '+' : ''}${safeChange.toFixed(2)}
          </span>
        </div>

        <div className="text-xs text-gray-400">
          Last updated: {new Date().toLocaleTimeString()}
        </div>
      </div>
    </div>
  )
}

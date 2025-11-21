import { Plane, ArrowRight } from 'lucide-react'

interface FlightCardProps {
  flightNumber: string
  airline: string
  departure: string
  arrival: string
  departureTime: string
  arrivalTime: string
  status: string
}

export function FlightCard({
  flightNumber,
  airline,
  departure,
  arrival,
  departureTime,
  arrivalTime,
  status,
}: FlightCardProps) {
  const statusColors = {
    'On Time': 'text-green-600 bg-green-50',
    'Delayed': 'text-orange-600 bg-orange-50',
    'Cancelled': 'text-red-600 bg-red-50',
    'Boarding': 'text-blue-600 bg-blue-50',
  }

  return (
    <div className="rounded-lg border bg-white shadow-sm p-6 max-w-lg">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-lg font-semibold">{flightNumber}</h3>
          <p className="text-sm text-gray-500">{airline}</p>
        </div>
        <span
          className={`px-3 py-1 rounded-full text-sm font-medium ${
            statusColors[status as keyof typeof statusColors] ||
            'text-gray-600 bg-gray-50'
          }`}
        >
          {status}
        </span>
      </div>

      <div className="flex items-center justify-between">
        <div className="flex-1">
          <div className="text-3xl font-bold">{departure}</div>
          <div className="text-sm text-gray-500 mt-1">{departureTime}</div>
        </div>

        <div className="flex-shrink-0 px-4">
          <Plane className="w-6 h-6 text-gray-400 rotate-90" />
          <ArrowRight className="w-6 h-6 text-gray-400 mt-1" />
        </div>

        <div className="flex-1 text-right">
          <div className="text-3xl font-bold">{arrival}</div>
          <div className="text-sm text-gray-500 mt-1">{arrivalTime}</div>
        </div>
      </div>
    </div>
  )
}

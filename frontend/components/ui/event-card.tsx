import { Calendar, MapPin, Clock, Users, Ticket } from 'lucide-react'
import { formatDate, formatTime } from '@/lib/utils'

interface EventCardProps {
  name: string
  date: string
  time: string
  location: string
  venue: string
  attendees: number
  ticketPrice?: number
  category: string
  description: string
  image?: string
}

export function EventCard({
  name,
  date,
  time,
  location,
  venue,
  attendees,
  ticketPrice,
  category,
  description,
  image,
}: EventCardProps) {
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
          <span className="inline-block px-2 py-1 bg-purple-50 text-purple-700 rounded text-xs font-medium mb-2">
            {category}
          </span>
          <h3 className="text-xl font-bold">{name}</h3>
        </div>

        <p className="text-sm text-gray-600">{description}</p>

        <div className="space-y-2 text-sm">
          <div className="flex items-start gap-2 text-gray-600">
            <Calendar className="w-4 h-4 mt-0.5 flex-shrink-0" />
            <span>{date}</span>
          </div>

          <div className="flex items-center gap-2 text-gray-600">
            <Clock className="w-4 h-4 flex-shrink-0" />
            <span>{time}</span>
          </div>

          <div className="flex items-start gap-2 text-gray-600">
            <MapPin className="w-4 h-4 mt-0.5 flex-shrink-0" />
            <div>
              <div className="font-medium">{venue}</div>
              <div className="text-xs text-gray-500">{location}</div>
            </div>
          </div>

          <div className="flex items-center gap-2 text-gray-600">
            <Users className="w-4 h-4 flex-shrink-0" />
            <span>{attendees.toLocaleString()} attending</span>
          </div>
        </div>

        <div className="flex items-center justify-between pt-4 border-t">
          <div>
            {ticketPrice !== undefined && ticketPrice > 0 ? (
              <div>
                <div className="text-xs text-gray-500">Ticket Price</div>
                <div className="text-2xl font-bold text-gray-900">
                  ${ticketPrice}
                </div>
              </div>
            ) : (
              <span className="text-lg font-bold text-green-600">Free Event</span>
            )}
          </div>

          <button className="flex items-center gap-2 px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors">
            <Ticket className="w-4 h-4" />
            <span>Get Tickets</span>
          </button>
        </div>
      </div>
    </div>
  )
}

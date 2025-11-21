import { Dumbbell, Flame, Clock, Target } from 'lucide-react'

interface ExerciseCardProps {
  name: string
  category: string
  difficulty: string
  duration: number
  caloriesBurned: number
  equipment: string[]
  description: string
  sets?: number
  reps?: number
  image?: string
}

export function ExerciseCard({
  name,
  category,
  difficulty,
  duration,
  caloriesBurned,
  equipment,
  description,
  sets,
  reps,
  image,
}: ExerciseCardProps) {
  const difficultyColors = {
    Beginner: 'text-green-600 bg-green-50',
    Intermediate: 'text-yellow-600 bg-yellow-50',
    Advanced: 'text-red-600 bg-red-50',
  }

  return (
    <div className="rounded-lg border bg-white shadow-sm p-6 max-w-md">
      {image && (
        <img
          src={image}
          alt={name}
          className="w-full h-48 object-cover rounded-lg mb-4"
        />
      )}

      <div className="space-y-4">
        <div>
          <div className="flex items-start justify-between mb-2">
            <div>
              <h3 className="text-xl font-bold">{name}</h3>
              <p className="text-sm text-gray-600">{category}</p>
            </div>
            <span
              className={`px-2 py-1 rounded text-xs font-medium ${
                difficultyColors[difficulty as keyof typeof difficultyColors] ||
                'text-gray-600 bg-gray-50'
              }`}
            >
              {difficulty}
            </span>
          </div>

          <p className="text-sm text-gray-600">{description}</p>
        </div>

        <div className="grid grid-cols-2 gap-3 text-sm">
          <div className="flex items-center gap-2 p-3 bg-blue-50 rounded-lg">
            <Clock className="w-5 h-5 text-blue-600" />
            <div>
              <div className="text-xs text-gray-600">Duration</div>
              <div className="font-semibold">{duration} min</div>
            </div>
          </div>

          <div className="flex items-center gap-2 p-3 bg-orange-50 rounded-lg">
            <Flame className="w-5 h-5 text-orange-600" />
            <div>
              <div className="text-xs text-gray-600">Calories</div>
              <div className="font-semibold">{caloriesBurned} kcal</div>
            </div>
          </div>

          {sets && reps && (
            <div className="flex items-center gap-2 p-3 bg-purple-50 rounded-lg col-span-2">
              <Target className="w-5 h-5 text-purple-600" />
              <div>
                <div className="text-xs text-gray-600">Target</div>
                <div className="font-semibold">
                  {sets} sets × {reps} reps
                </div>
              </div>
            </div>
          )}
        </div>

        <div>
          <div className="text-xs font-semibold text-gray-500 uppercase mb-2 flex items-center gap-1">
            <Dumbbell className="w-3 h-3" />
            Equipment
          </div>
          <div className="flex flex-wrap gap-2">
            {equipment.length > 0 ? (
              equipment.map((item, idx) => (
                <span
                  key={idx}
                  className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs"
                >
                  {item}
                </span>
              ))
            ) : (
              <span className="text-xs text-gray-500 italic">
                No equipment needed
              </span>
            )}
          </div>
        </div>

        <button className="w-full px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors font-medium">
          Start Workout
        </button>
      </div>
    </div>
  )
}

import { Clock, Users, ChefHat } from 'lucide-react'

interface RecipeCardProps {
  title: string
  description: string
  prepTime: number
  cookTime: number
  servings: number
  difficulty: string
  ingredients: string[]
  image?: string
}

export function RecipeCard({
  title,
  description,
  prepTime,
  cookTime,
  servings,
  difficulty,
  ingredients,
  image,
}: RecipeCardProps) {
  const difficultyColors = {
    Easy: 'text-green-600 bg-green-50',
    Medium: 'text-yellow-600 bg-yellow-50',
    Hard: 'text-red-600 bg-red-50',
  }

  return (
    <div className="rounded-lg border bg-white shadow-sm p-6 max-w-lg">
      {image && (
        <img
          src={image}
          alt={title}
          className="w-full h-48 object-cover rounded-lg mb-4"
        />
      )}

      <div className="space-y-4">
        <div>
          <div className="flex items-start justify-between mb-2">
            <h3 className="text-xl font-bold">{title}</h3>
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

        <div className="flex items-center gap-4 text-sm text-gray-500">
          <div className="flex items-center gap-1">
            <Clock className="w-4 h-4" />
            <span>{prepTime + cookTime} min</span>
          </div>
          <div className="flex items-center gap-1">
            <Users className="w-4 h-4" />
            <span>{servings} servings</span>
          </div>
          <div className="flex items-center gap-1">
            <ChefHat className="w-4 h-4" />
            <span>Prep: {prepTime}m | Cook: {cookTime}m</span>
          </div>
        </div>

        <div className="border-t pt-4">
          <h4 className="font-semibold mb-2 text-sm">Ingredients:</h4>
          <ul className="text-sm text-gray-600 space-y-1">
            {ingredients.slice(0, 5).map((ingredient, idx) => (
              <li key={idx} className="flex items-start">
                <span className="mr-2">•</span>
                <span>{ingredient}</span>
              </li>
            ))}
            {ingredients.length > 5 && (
              <li className="text-gray-400 italic">
                +{ingredients.length - 5} more ingredients...
              </li>
            )}
          </ul>
        </div>
      </div>
    </div>
  )
}

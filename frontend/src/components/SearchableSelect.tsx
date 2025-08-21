import { useState, useRef, useEffect } from 'react'
import { ChevronDown, Search, Star } from 'lucide-react'

interface Option {
  value: string
  label: string
  description?: string
  recommend?: boolean
}

interface SearchableSelectProps {
  options: Option[]
  value: string
  onChange: (value: string) => void
  placeholder?: string
  label?: string
}

export default function SearchableSelect({ 
  options, 
  value, 
  onChange, 
  placeholder = "Select option...",
  label 
}: SearchableSelectProps) {
  const [isOpen, setIsOpen] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const dropdownRef = useRef<HTMLDivElement>(null)

  const filteredOptions = options.filter(option =>
    option.label.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (option.description && option.description.toLowerCase().includes(searchTerm.toLowerCase()))
  )

  const selectedOption = options.find(option => option.value === value)

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false)
        setSearchTerm('')
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const handleOptionClick = (optionValue: string) => {
    onChange(optionValue)
    setIsOpen(false)
    setSearchTerm('')
  }

  return (
    <div className="relative" ref={dropdownRef}>
      {label && (
        <label className="block text-sm font-medium text-gray-700 mb-2">
          {label}
        </label>
      )}
      
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="w-full p-3 border border-gray-300 rounded-lg bg-white focus:ring-2 focus:ring-blue-500 focus:border-transparent text-left text-sm sm:text-base flex items-center justify-between hover:border-gray-400 transition-colors min-h-[50px]"
      >
        <span className={`flex items-center ${selectedOption ? 'text-gray-900' : 'text-gray-500'}`}>
            {selectedOption ? (
                <>
                    {selectedOption.recommend && (
                        <Star className="w-4 h-4 text-amber-400 mr-2 fill-current" />
                    )}
                    {selectedOption.label}
                </>
            ) : (
                placeholder
            )}
        </span>
        <ChevronDown className={`w-5 h-5 text-gray-400 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {isOpen && (
        <div className="absolute z-[9999] w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg max-h-60 overflow-hidden">
          {/* Search input */}
          <div className="p-3 border-b border-gray-200">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-3 py-2 border border-gray-200 rounded-md text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                autoFocus
              />
            </div>
          </div>

          {/* Options list */}
          <div className="max-h-48 overflow-y-auto">
            {filteredOptions.length > 0 ? (
              filteredOptions.map((option) => (
                <button
                  key={option.value}
                  onClick={() => handleOptionClick(option.value)}
                  className={`w-full text-left px-3 py-2 hover:bg-blue-50 focus:bg-blue-50 transition-colors ${
                    value === option.value ? 'bg-blue-100 text-blue-900' : 'text-gray-900'
                  }`}
                >
                    <div className="font-medium text-sm flex items-center">
                        {option.recommend && (
                            <Star className="w-4 h-4 text-amber-400 mr-2 fill-current" />
                        )}
                        {option.label}
                    </div>
                    {option.description && (
                        <div className="text-xs text-gray-500 mt-1">{option.description}</div>
                    )}
                </button>
              ))
            ) : (
              <div className="px-3 py-4 text-sm text-gray-500 text-center">
                No options found
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
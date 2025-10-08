import { useState, useRef, useEffect } from 'react'
import { ChevronDown, Search, X, Check } from 'lucide-react'

interface Option {
  value: string
  label: string
  description?: string
  disabled?: boolean
}

interface MultiSelectProps {
  options: Option[]
  values: string[]
  onChange: (values: string[]) => void
  placeholder?: string
  label?: string
  maxDisplayCount?: number
}

export default function MultiSelect({ 
  options, 
  values, 
  onChange, 
  placeholder = "Select options...",
  label,
  maxDisplayCount = 2
}: MultiSelectProps) {
  const [isOpen, setIsOpen] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const dropdownRef = useRef<HTMLDivElement>(null)

  const filteredOptions = options.filter(option =>
    option.label.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (option.description && option.description.toLowerCase().includes(searchTerm.toLowerCase()))
  )

  const selectedOptions = options.filter(option => values.includes(option.value))

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

  const handleOptionToggle = (optionValue: string) => {
    const option = options.find(opt => opt.value === optionValue)
    if (option?.disabled) return // Prevent toggling disabled options
    
    const newValues = values.includes(optionValue)
      ? values.filter(v => v !== optionValue)
      : [...values, optionValue]
    onChange(newValues)
  }

  const removeValue = (valueToRemove: string) => {
    const option = options.find(opt => opt.value === valueToRemove)
    if (option?.disabled) return // Prevent removing disabled options
    onChange(values.filter(v => v !== valueToRemove))
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
        <div className="flex flex-wrap gap-1 items-center flex-1 mr-2">
          {selectedOptions.length === 0 ? (
            <span className="text-gray-500">{placeholder}</span>
          ) : selectedOptions.length <= maxDisplayCount ? (
            selectedOptions.map((option) => (
              <span
                key={option.value}
                className={`inline-flex items-center px-2 text-sm sm:text-base rounded-md ${
                  option.disabled
                    ? 'bg-gray-100 text-gray-500'
                    : 'bg-blue-100 text-blue-800'
                }`}
              >
                {option.label}
                {!option.disabled && (
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      removeValue(option.value)
                    }}
                    className="ml-1 hover:text-blue-600"
                  >
                    <X className="w-3 h-3" />
                  </button>
                )}
              </span>
            ))
          ) : (
            <span className="text-gray-900">
              {selectedOptions.slice(0, maxDisplayCount).map(opt => opt.label).join(', ')} 
              <span className="ml-1 px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-md">
                +{selectedOptions.length - maxDisplayCount} more
              </span>
            </span>
          )}
        </div>
        <ChevronDown className={`w-5 h-5 text-gray-400 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {isOpen && (
        <div className="absolute z-[9999] w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg max-h-80 overflow-hidden">
          {/* Search input */}
          <div className="p-3 border-b border-gray-200">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search devices..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-3 py-2 border border-gray-200 rounded-md text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                autoFocus
              />
            </div>
          </div>

          {/* Select All / Deselect All */}
          {filteredOptions.length > 0 && filteredOptions.some(opt => !opt.disabled) && (
            <div className="p-2 border-b border-gray-100">
              <button
                onClick={() => {
                  const enabledFilteredValues = filteredOptions.filter(opt => !opt.disabled).map(opt => opt.value)
                  const hasAllEnabled = enabledFilteredValues.every(val => values.includes(val))
                  if (hasAllEnabled) {
                    onChange(values.filter(v => !enabledFilteredValues.includes(v)))
                  } else {
                    onChange([...new Set([...values, ...enabledFilteredValues])])
                  }
                }}
                className="w-full text-left px-2 py-1 text-sm text-blue-600 hover:text-blue-800 font-medium"
              >
                {filteredOptions.filter(opt => !opt.disabled).every(opt => values.includes(opt.value)) ? 'Deselect All Available' : 'Select All Available'}
              </button>
            </div>
          )}

          {/* Options list */}
          <div className="max-h-48 overflow-y-auto">
            {filteredOptions.length > 0 ? (
              filteredOptions.map((option) => {
                const isSelected = values.includes(option.value)
                const isDisabled = option.disabled
                return (
                  <button
                    key={option.value}
                    onClick={() => handleOptionToggle(option.value)}
                    disabled={isDisabled}
                    className={`w-full text-left px-3 py-2 transition-colors flex items-center ${
                      isDisabled 
                        ? 'cursor-not-allowed opacity-50' 
                        : 'hover:bg-blue-50 focus:bg-blue-50'
                    } ${
                      isSelected && !isDisabled ? 'bg-blue-50' : ''
                    }`}
                  >
                    <div className={`w-4 h-4 border-2 rounded mr-3 flex items-center justify-center ${
                      isSelected 
                        ? isDisabled
                          ? 'bg-gray-400 border-gray-400 text-white'
                          : 'bg-blue-500 border-blue-500 text-white'
                        : isDisabled
                          ? 'border-gray-200'
                          : 'border-gray-300'
                    }`}>
                      {isSelected && <Check className="w-3 h-3" />}
                    </div>
                    <div className="flex-1">
                      <div className={`font-medium text-sm ${
                        isDisabled ? 'text-gray-400' : 'text-gray-900'
                      }`}>{option.label}</div>
                      {option.description && (
                        <div className={`text-xs mt-1 ${
                          isDisabled ? 'text-gray-300' : 'text-gray-500'
                        }`}>{option.description}</div>
                      )}
                    </div>
                  </button>
                )
              })
            ) : (
              <div className="px-3 py-4 text-sm text-gray-500 text-center">
                No devices found
              </div>
            )}
          </div>

          {/* Selected count */}
          {selectedOptions.length > 0 && (
            <div className="p-2 border-t border-gray-100 bg-gray-50">
              <div className="text-sm text-gray-600 text-center">
                {selectedOptions.length} device{selectedOptions.length !== 1 ? 's' : ''} selected
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
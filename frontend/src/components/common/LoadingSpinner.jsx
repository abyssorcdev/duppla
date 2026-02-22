export default function LoadingSpinner({ size = 'md', text = '' }) {
  const sizeClass = { sm: 'h-5 w-5', md: 'h-8 w-8', lg: 'h-12 w-12' }[size]
  return (
    <div className="flex flex-col items-center justify-center gap-3 py-8">
      <div className={`animate-spin rounded-full border-b-2 border-brand-700 ${sizeClass}`} />
      {text && <p className="text-sm text-brand-600">{text}</p>}
    </div>
  )
}

const SIZES = {
  md: 'h-9 w-9 text-lg rounded-xl',
  lg: 'h-12 w-12 text-2xl rounded-2xl',
}

export default function Logo({ size = 'md' }) {
  return (
    <div
      className={`flex items-center justify-center bg-primary font-bold text-white shadow-sm ${SIZES[size]}`}
      aria-label="Kyzen"
    >
      K
    </div>
  )
}

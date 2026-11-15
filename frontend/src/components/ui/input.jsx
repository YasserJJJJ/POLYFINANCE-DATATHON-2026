import { forwardRef } from 'react'
import { cn } from '@/lib/utils'

export const Input = forwardRef(function Input({ className, ...p }, ref) {
  return (
    <input ref={ref} className={cn('h-9 w-full rounded-md border border-input bg-transparent px-2.5 text-[13.5px] placeholder:text-muted-foreground/70 disabled:opacity-50', className)} {...p} />
  )
})

export const Select = forwardRef(function Select({ className, ...p }, ref) {
  return (
    <select ref={ref} className={cn('h-9 w-full rounded-md border border-input bg-transparent px-2.5 text-[13.5px] disabled:opacity-50', className)} {...p} />
  )
})

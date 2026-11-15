import { forwardRef } from 'react'
import { cn } from '@/lib/utils'

export const Textarea = forwardRef(function Textarea({ className, ...p }, ref) {
  return (
    <textarea ref={ref} className={cn('min-h-[68px] w-full resize-none rounded-md border border-input bg-transparent px-2.5 py-2 text-[13.5px] placeholder:text-muted-foreground/70 disabled:opacity-50', className)} {...p} />
  )
})

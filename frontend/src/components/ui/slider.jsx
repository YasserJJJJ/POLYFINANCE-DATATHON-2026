import * as SliderPrimitive from '@radix-ui/react-slider'
import { cn } from '@/lib/utils'

export function Slider({ className, ...p }) {
  return (
    <SliderPrimitive.Root className={cn('relative flex h-5 w-full touch-none select-none items-center data-[disabled]:opacity-50', className)} {...p}>
      <SliderPrimitive.Track className="relative h-1.5 w-full grow overflow-hidden rounded-full border border-border bg-muted">
        <SliderPrimitive.Range className="absolute h-full bg-primary" />
      </SliderPrimitive.Track>
      <SliderPrimitive.Thumb aria-label={p['aria-label']} className="block size-[18px] cursor-grab rounded-full border-2 border-primary bg-card active:cursor-grabbing" />
    </SliderPrimitive.Root>
  )
}

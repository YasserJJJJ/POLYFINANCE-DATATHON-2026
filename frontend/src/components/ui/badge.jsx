import { cva } from 'class-variance-authority'
import { cn } from '@/lib/utils'

const badgeVariants = cva('inline-flex items-center gap-1.5 whitespace-nowrap rounded-full border px-2.5 py-px text-[11.5px] font-medium', {
  variants: {
    variant: {
      outline: 'border-border bg-card text-muted-foreground',
      secondary: 'border-transparent bg-muted text-foreground',
    },
  },
  defaultVariants: { variant: 'outline' },
})

export const Badge = ({ className, variant, ...p }) => <span className={cn(badgeVariants({ variant }), className)} {...p} />

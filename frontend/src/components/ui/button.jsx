import { Slot } from '@radix-ui/react-slot'
import { cva } from 'class-variance-authority'
import { cn } from '@/lib/utils'

const buttonVariants = cva(
  'inline-flex items-center justify-center gap-1.5 whitespace-nowrap rounded-md border border-transparent text-[13px] font-medium transition-[opacity,background-color] disabled:cursor-not-allowed disabled:opacity-45 cursor-pointer',
  {
    variants: {
      variant: {
        default: 'bg-primary text-primary-foreground hover:opacity-90',
        outline: 'border-input bg-transparent text-foreground hover:bg-muted',
        ghost: 'bg-transparent text-muted-foreground hover:bg-muted hover:text-foreground',
        link: 'h-auto px-0 font-normal text-foreground underline decoration-foreground/30 underline-offset-[3px] hover:decoration-foreground',
      },
      size: { default: 'h-9 px-3.5', sm: 'h-[30px] px-2.5 text-xs', lg: 'h-11 px-5 text-sm' },
    },
    defaultVariants: { variant: 'default', size: 'default' },
  },
)

export function Button({ className, variant, size, asChild = false, ...props }) {
  const Comp = asChild ? Slot : 'button'
  return <Comp className={cn(buttonVariants({ variant, size }), variant === 'link' && 'h-auto px-0', className)} {...props} />
}

import { cn } from '@/lib/utils'

export const Card = ({ className, ...p }) => (
  <div className={cn('rounded-lg border border-border bg-card shadow-[0_1px_2px_rgba(0,0,0,.05)]', className)} {...p} />
)
export const CardHeader = ({ className, ...p }) => <div className={cn('px-[18px] pt-4', className)} {...p} />
export const CardTitle = ({ className, ...p }) => <h2 className={cn('text-[15px] font-semibold tracking-[-0.01em]', className)} {...p} />
export const CardDescription = ({ className, ...p }) => <p className={cn('mt-0.5 text-[13px] text-muted-foreground', className)} {...p} />
export const CardContent = ({ className, ...p }) => <div className={cn('px-[18px] py-4', className)} {...p} />
export const CardFooter = ({ className, ...p }) => <div className={cn('border-t border-border px-[18px] py-3.5', className)} {...p} />

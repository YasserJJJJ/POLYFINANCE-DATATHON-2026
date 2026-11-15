import { clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

export const cn = (...entrees) => twMerge(clsx(entrees))

import { forwardRef } from 'react';
import { cn } from '../../lib/utils';
import { Loader2 } from 'lucide-react';

const Button = forwardRef(({ 
  className, 
  variant = 'primary', 
  size = 'md', 
  isLoading = false, 
  leftIcon,
  rightIcon,
  children,
  ...props 
}, ref) => {
  const variants = {
    primary: 'gradient-bg text-white shadow-md hover:shadow-lg hover:scale-[1.02] active:scale-[0.98]',
    secondary: 'bg-slate-100 text-slate-700 hover:bg-slate-200 active:bg-slate-300',
    danger: 'bg-red-500 text-white hover:bg-red-600 active:bg-red-700 shadow-md',
    ghost: 'bg-transparent text-slate-600 hover:bg-slate-100 active:bg-slate-200',
    outline: 'border-2 border-slate-300 text-slate-700 hover:border-slate-400 hover:bg-slate-50',
  };

  const sizes = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2.5 text-sm',
    lg: 'px-6 py-3 text-base',
  };

  return (
    <button
      ref={ref}
      className={cn(
        'inline-flex items-center justify-center gap-2 rounded-lg font-medium transition-all duration-150 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100',
        variants[variant],
        sizes[size],
        className
      )}
      disabled={isLoading || props.disabled}
      {...props}
    >
      {isLoading ? (
        <Loader2 className="w-4 h-4 animate-spin" />
      ) : leftIcon ? (
        <span className="w-4 h-4">{leftIcon}</span>
      ) : null}
      {children}
      {rightIcon && !isLoading && <span className="w-4 h-4">{rightIcon}</span>}
    </button>
  );
});

Button.displayName = 'Button';

export { Button };

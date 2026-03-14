import { forwardRef } from 'react';
import { cn } from '../../lib/utils';

const Card = forwardRef(({ 
  className, 
  variant = 'default',
  children, 
  ...props 
}, ref) => {
  const variants = {
    default: 'bg-white shadow-lg rounded-xl',
    glass: 'glass shadow-xl rounded-xl',
    elevated: 'bg-white shadow-2xl rounded-xl',
  };

  return (
    <div
      ref={ref}
      className={cn(
        'p-6',
        variants[variant],
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
});

Card.displayName = 'Card';

export { Card };
